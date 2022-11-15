#! python3
import os
from argparse import Namespace
from dataclasses import dataclass, field

from . import overview_util as ov_util
from . import util
from .overview_util import DEFAULT_OVERVIEW_FILE
from .pointcloud2map_8bit import pcd_to_png
from .sample_pointcloud import sample_pcd
from .util import AlphaFoldVersion, ColoringModes
from .util import FileTypes as FT
from .util import Logger, ProteinStructure, batch


@dataclass
class AlphafoldDBParser:
    """
    Class to parse PDB files and convert them to ply.
    """

    WD: str = util.WD
    chimerax: str = "chimerax"
    alphafold_ver: AlphaFoldVersion = AlphaFoldVersion.v1.value
    batch_size: int = 50
    chimerax: str = None
    processing: str = ColoringModes.cartoons_ss_coloring.value
    overview_file: str = DEFAULT_OVERVIEW_FILE
    structures: list[ProteinStructure] = field(default_factory=lambda: {})
    not_fetched: list[str] = field(default_factory=lambda: [])
    given_name: bool = False
    keep_temp: dict[FT, bool] = field(
        default_factory=lambda: {
            FT.pdb_file: False,
            FT.glb_file: False,
            FT.ply_file: False,
            FT.ascii_file: False,
        }
    )
    log = Logger("AlphafoldDBParser")

    def update_output_dir(self, output_dir):
        """
        Updates the output directory of resulting images.
        """
        self.OUTPUT_DIR = output_dir
        self.init_dirs()

    def update_existence(self, protein):
        """Updates the existence of the files for each protein structure."""
        if protein in self.structures:
            self.structures[protein].update_existence()

    def __post_init__(self) -> None:
        self.PDB_DIR = os.path.join(self.WD, "processing_files", "pdbs")
        self.PLY_DIR = os.path.join(self.WD, "processing_files", "plys")
        self.GLB_DIR = os.path.join(self.WD, "processing_files", "glbs")
        self.ASCII_DIR = os.path.join(self.WD, "processing_files", "ASCII_clouds")
        self.OUTPUT_DIR = os.path.join(self.WD, "processing_files", "MAPS")

    def init_dirs(self, subs=True) -> None:
        """
        Initialize the directories.
        """
        self.OUTPUT_RGB_DIR = os.path.join(self.OUTPUT_DIR, "rgb")
        self.OUTPUT_XYZ_LOW_DIR = os.path.join(
            self.OUTPUT_DIR, os.path.join("xyz", "low")
        )
        self.OUTPUT_XYZ_HIGH_DIR = os.path.join(
            self.OUTPUT_DIR, os.path.join("xyz", "high")
        )
        directories = [var for var in self.__dict__.keys() if "_DIR" in var]
        if not subs:
            for var in directories:
                if "RGB" in var or "XYZ" in var:
                    directories.remove(var)

        for _dir in directories:
            path = self.__dict__[str(_dir)]
            os.makedirs(path, exist_ok=True)
        self.DIRS = {
            FT.pdb_file: self.PDB_DIR,
            FT.ply_file: self.PLY_DIR,
            FT.glb_file: self.GLB_DIR,
            FT.ascii_file: self.ASCII_DIR,
            "output": self.OUTPUT_DIR,
            FT.rgb_file: self.OUTPUT_RGB_DIR,
            FT.xyz_low_file: self.OUTPUT_XYZ_LOW_DIR,
            FT.xyz_high_file: self.OUTPUT_XYZ_HIGH_DIR,
        }
        self.init_structures_dict(self.structures.keys())

    def get_filename(self, protein: str) -> str:
        """
        Get the filename of the protein.
        """
        return f"AF-{protein}-F1-model_{self.alphafold_ver}"

    def init_structures_dict(self, proteins: list[str]) -> dict[dict[str or dict[str]]]:
        for protein in proteins:
            # Catch cases in which the filename is already given
            file_name = self.get_filename(protein)
            pdb_file = os.path.join(self.PDB_DIR, file_name + ".pdb")
            glb_file = os.path.join(self.GLB_DIR, file_name + ".glb")
            ply_file = os.path.join(self.PLY_DIR, file_name + ".ply")
            ASCII_file = os.path.join(self.ASCII_DIR, file_name + ".xyzrgb")
            output_rgb = os.path.join(self.OUTPUT_RGB_DIR, file_name + ".png")
            output_xyz = file_name + ".bmp"
            output_xyz_low = os.path.join(self.OUTPUT_XYZ_LOW_DIR, output_xyz)
            output_xyz_high = os.path.join(self.OUTPUT_XYZ_HIGH_DIR, output_xyz)
            files = (
                pdb_file,
                glb_file,
                ply_file,
                ASCII_file,
                output_rgb,
                output_xyz_low,
                output_xyz_high,
            )
            structure = ProteinStructure(protein, file_name, *files)
            self.structures[protein] = structure
        return self.structures

    def fetch_pdb(self, proteins: list[str]) -> None:
        """
        Fetches .pdb File from the AlphaFold Server. This function uses the request module from python standard library to directly download pdb files from the AlphaFold server.
        """
        self.init_structures_dict(proteins)
        proteins = self.filter_already_processed(proteins)
        if len(proteins) == 0:
            self.log.info(
                f"All structures of this batch: {proteins} are already processed. Skipping this batch."
            )
            return
        for protein in proteins:
            structure = self.structures[protein]
            if not structure.existing_files[FT.pdb_file]:
                self.log.debug(
                    f"Fetching {protein} from AlphaFold server with version {self.alphafold_ver}."
                )
                if util.fetch_pdb_from_alphafold(
                    protein,
                    self.PDB_DIR,
                    self.alphafold_ver,
                ):
                    structure.existing_files[FT.pdb_file] = True
                else:
                    self.not_fetched.append(protein)

    def chimerax_process(self, proteins: list[str], processing: str or None) -> None:
        """
        Processes the .pdb files using ChimeraX and the bundle chimerax_bundle.py. Default processing mode is ColoringModes.cartoons_sscoloring
        As default, the source pdb file is NOT removed.
        To change this set self.keep_temp[FT.pdb_file] = False.
        """
        if self.chimerax is None:
            self.chimerax = util.search_for_chimerax()

        colors = None
        if processing is None:
            processing = ColoringModes.cartoons_ss_coloring.value
        if processing.find("ss") != -1:
            colors = ["red,green,blue"]

        to_process = set()
        tmp_strucs = []
        for protein in proteins:
            structure = self.structures[protein]
            if (
                not structure.existing_files[FT.glb_file]  # Skip if GLB file is present
                and not structure.existing_files[
                    FT.ply_file
                ]  # Skip if PLY file is present
                and not structure.existing_files[FT.ascii_file]
            ) and structure.existing_files[  # Skip if ASCII file is present
                FT.pdb_file
            ]:
                to_process.add(structure.pdb_file.split("/")[-1])
                tmp_strucs.append(structure)
        # Process all Structures
        if len(to_process) > 0:
            self.log.info(f"Processing Structures:{to_process}")
            util.run_chimerax_coloring_script(
                self.chimerax,
                self.PDB_DIR,
                to_process,
                self.GLB_DIR,
                processing,
                colors,
            )
            for structure in tmp_strucs:
                if not self.keep_temp[FT.pdb_file] and os.path.isfile(structure.pdb_file):
                        os.remove(structure.pdb_file)
                structure.existing_files[FT.glb_file] = True

    def convert_glbs(self, proteins: list[str]) -> None:
        """
        Converts the .glb files to .ply files.
        As default, the source glb file is removed afterwards.
        To change this set self.keep_temp[FT.glb_file] = True.
        """
        for protein in proteins:
            structure = self.structures[protein]
            if (
                not structure.existing_files[FT.ply_file]
                # Skip if PLY file is present
                and not structure.existing_files[
                    FT.ascii_file
                ]  # Skip if ASCII file is present
            ) and structure.existing_files[FT.glb_file]:
                if util.convert_glb_to_ply(structure.glb_file, structure.ply_file):
                    self.log.debug(
                        f"Converted {structure.glb_file} to {structure.ply_file}"
                    )
                    structure.existing_files[FT.ply_file] = True
                    if not self.keep_temp[FT.glb_file]:
                        os.remove(structure.glb_file)  # remove source file

    def sample_pcd(self, proteins: list[str]) -> None:
        """
        Samples the pointcloud form the ply files.
        As default, the source ply file is removed afterwards.
        To change this set self.keep_temp[FT.ply_file] = True.
        """
        for protein in proteins:
            structure = self.structures[protein]
            if (
                not structure.existing_files[FT.ascii_file]
                and structure.existing_files[FT.ply_file]
            ):
                scale = sample_pcd(
                    structure.ply_file,
                    structure.ascii_file,
                )
                structure.existing_files[FT.ascii_file] = True
                structure.scale = scale
                self.write_scale(protein)
                self.log.debug(
                    f"Sampled pcd to {structure.ascii_file} and wrote scale of {scale} to file {self.overview_file}"
                )
                if not self.keep_temp[FT.ply_file]:
                    os.remove(structure.ply_file)

    def gen_maps(self, proteins: list[str]) -> None:
        """
        Generates the maps from the point cloud files.
        If all of the output files already exists, this protein is skipped.
        As default, the source ascii point cloud is removed afterwards.
        To change this set self.keep_temp[FT.ascii_file] = True.
        """
        for protein in proteins:
            structure = self.structures[protein]
            if (
                not (
                    structure.existing_files[FT.rgb_file]
                    and structure.existing_files[FT.xyz_low_file]
                    and structure.existing_files[FT.xyz_high_file]
                )
                and structure.existing_files[FT.ascii_file]
            ):
                pcd_to_png(
                    structure.ascii_file,
                    structure.rgb_file,
                    structure.xyz_low_file,
                    structure.xyz_high_file,
                )
                self.log.debug(
                    f"Generated color maps {structure.rgb_file}, {structure.xyz_low_file} and {structure.xyz_high_file}"
                )
                structure.existing_files[FT.rgb_file] = True
                structure.existing_files[FT.xyz_low_file] = True
                structure.existing_files[FT.xyz_high_file] = True
                if not self.keep_temp[FT.ascii_file]:
                    os.remove(structure.ascii_file)

    def write_scale(self, protein) -> None:
        """
        Writes the scale of the protein to the overview file. This file is used to keep track of the scale of each protein structure.
        """
        structure = self.structures[protein]
        ov_util.write_scale(
            structure.uniprot_id,
            structure.scale,
            structure.pdb_file,
            self.processing,
            self.overview_file,
        )

    def set_version_from_filenames(self) -> None:
        """Iterates over all Directories and searches for files, which have Alphafold version number. If one is found, set the Parser to this version. All files are treated with this version."""
        for dir in self.DIRS.values():
            for file in os.listdir(dir):
                for version in list(AlphaFoldVersion):
                    if file.find(version.value) >= 0:
                        self.alphafold_ver = version.value
                        return

    def proteins_from_list(self, proteins: list[str]) -> None:
        """Add all uniprot_ids from the list to the set of proteins."""
        self.set_version_from_filenames()
        # self.init_structures_dict(proteins)
        batch([self.fetch_pdb, self.pdb_pipeline], proteins, self.batch_size)

    def proteins_from_dir(self, source: str) -> None:
        """
        Processes proteins from a directory. In the source directory, the program will search for each of the available file types. Based on this, the class directories are initialized. The program will then start at the corresponding step for each structure.
        """
        files = []
        for file in tmp:
            self.check_dirs(file, source)
            if file.endswith((".pdb", ".glb", ".ply", ".xyzrgb", ".png", ".bmp")):
                files.append(file)
        del tmp
        self.alphafold_ver = (
            files[0].split("/")[-1].split("_")[1]
        )  # extract the Alphafold version from the first file
        self.alphafold_ver = self.alphafold_ver[: self.alphafold_ver.find(".")]
        proteins = []
        for file in files:
            file_name = file.split("/")[-1]
            proteins.append(file_name.split("-")[1])
        self.init_structures_dict(proteins)
        batch([self.pdb_pipeline], proteins, self.batch_size)

    def pdb_pipeline(self, proteins: list[str]) -> None:
        """Default pipeline which is used in all program modes.
        For each structure, the PDB file we be processed in chimerax and exported as GLB file. This GLB file will be converted into a PLY file.
        The PLY file is used to sample the point cloud which will be saved as an ASCII point cloud. This ASCII point cloud will then be used to generate the color maps (rgb,xyz_low and xyz_high)."""
        tmp = ", ".join(proteins)
        proteins = self.filter_already_processed(proteins)
        if len(proteins) == 0:
            self.log.info(
                f"All structures of this batch: {tmp} are already processed. Skipping this batch."
            )
            return
        self.chimerax_process(proteins, self.processing)
        self.log.debug("Converting GLBs to PLYs...")
        self.convert_glbs(proteins)
        self.log.debug("Sampling PointClouds...")
        self.sample_pcd(proteins)
        self.log.debug("Generating Color Maps...")
        self.gen_maps(proteins)

    def fetch_pipeline(self, proteins: list[str]) -> None:
        """
        Fetch of the structure from the alphafold db.
        """
        self.init_structures_dict(proteins)
        self.log.debug("Structure Dict initialized.")
        proteins = self.filter_already_processed(proteins)
        if len(proteins) == 0:
            self.log.info("All structures are already processed. Skipping this batch.")
            return

        batch([self.fetch_pdb, self.pdb_pipeline], proteins, self.batch_size)
        self.log.info(f"Missing Structures:{self.not_fetched}")

    def filter_already_processed(self, proteins: list[str]) -> list[str]:
        """
        Filter out the proteins that have already been processed.
        """
        return [
            protein
            for protein in proteins
            if not self.output_exists(self.structures[protein])
        ]

    def output_exists(self, structures: ProteinStructure) -> bool:
        """
        Checks if the output files already exist in the  output directory.
        """
        for file in [
            structures.rgb_file,
            structures.xyz_low_file,
            structures.xyz_high_file,
        ]:
            if not os.path.isfile(file):
                return False
        return True

    def check_dirs(self, file: str, source: str) -> None:
        """
        Check wether a source file is in different directory than the default directory. If so set the corresponding directory to the source.
        """
        # TODO reduce to do this only once for each file type.
        if self.PDB_DIR != source:
            if file.endswith(".pdb"):
                self.PDB_DIR = source
        if self.GLB_DIR != source:
            if file.endswith(".glb"):
                self.GLB_DIR = source
        if self.PLY_DIR != source:
            if file.endswith(".ply"):
                self.PLY_DIR = source
        if self.ASCII_DIR != source:
            if file.endswith(".xyzrgb"):
                self.ASCII_DIR = source
        if self.OUTPUT_DIR != source:
            if file.endswith((".png", ".bmp")):
                self.OUTPUT_DIR = source

    def set_dirs(self, args: Namespace) -> None:
        """Uses arguments from the argument parser Namespace and sets the directories to the corresponding values."""
        # Set the directories for the files to be saved
        if args.pdb is not None:
            self.PDB_DIR = args.pdb
        if args.glb is not None:
            self.GLB_DIR = args.glb
        if args.ply is not None:
            self.PLY_DIR = args.ply
        if args.pcd is not None:
            self.ASCII_DIR = args.pcd
        if args.m is not None:
            self.OUTPUT_DIR = args.m
        self.init_dirs()

    def set_keep_tmp(self, args: Namespace) -> None:
        """Uses arguments from the argument parser Namespace and sets the switch to keep or to remove the corresponding file types after a processing step is completed."""
        if args.kpdb is not None:
            self.keep_tmp[FT.pdb_file] = args.kpdb
        if args.kglb is not None:
            self.keep_temp[FT.glb_file] = args.kglb
        if args.kply is not None:
            self.keep_temp[FT.ply_file] = args.kply
        if args.asc is not None:
            self.keep_temp[FT.ascii_file] = args.asc

    def set_batch_size(self, args: Namespace) -> None:
        """Parsers arguments from the argument parser Namespace and sets the batch size to the corresponding value."""
        if args.bs is not None:
            self.batch_size = args.bs

    def set_alphafold_version(self, args: Namespace) -> None:
        """Parsers arguments from the argument parser Namespace and sets the alphafold version to the corresponding value."""
        if args.av is not None:
            for value in AlphaFoldVersion.__members__.keys():
                if value == args.av:
                    self.alphafold_ver = value
                    break

    def set_coloring_mode(self, args: Namespace) -> None:
        if args.cm is not None:
            self.processing = args.cm

    def execute_fetch(self, proteins: str) -> None:
        """Uses a list of proteins to fetch the PDB files from the alphafold db. This PDB files will then be used to generated the color maps."""
        proteins = proteins.split(",")
        self.log.debug(f"Proteins to fetch from Alphafold:{proteins}")
        self.fetch_pipeline(proteins)

    def execute_from_object(self, proteins: list[str]) -> None:
        """Uses a list of proteins which are extracted from a Python object. This assumes that the PDB files of these structures already exist in the PDB directory."""
        self.proteins_from_list(proteins)

    def execute_local(self, source: str) -> None:
        """Will extract all Uniprot IDs from a local directory. Assumes that the file names have a the following format:
        AF-<Uniprot ID>-F1-model-<v1/v2>.[pdb/glb/ply/xyzrgb]"""
        self.proteins_from_dir(source)

    def clear_default_dirs(self) -> None:
        """Clears the default directories."""
        processing_files = os.path.join(
            self.WD,
            "processing_files",
        )
        util.remove_dirs(processing_files)

    def set_chimerax(self, args: Namespace):
        if args.ch is not None:
            self.chimerax = args.ch

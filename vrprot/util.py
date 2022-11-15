import glob
import logging
import ntpath
import os
import platform
import shutil
import subprocess as sp
import sys
from dataclasses import dataclass
from enum import Enum, auto

import requests
import trimesh
from trimesh.exchange import ply

from .exceptions import StructureNotFoundError

wd = os.path.dirname(".")  # for final executable
# wd = os.path.dirname(__file__)  # for development
WD = os.path.abspath(wd)  # for development
FILE_DIR = os.path.dirname(__file__)
SCRITPS = os.path.join(FILE_DIR, "scripts")


class Logger:
    """
    Implementation based on https://dotnettutorials.net/lesson/customized-logging-in-python/
    """

    def __init__(self, name, level=logging.DEBUG):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        consoleHandler = logging.StreamHandler()
        consoleHandler.setLevel(level)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s %(levelname)s: %(message)s",
            datefmt="%m/%d/%Y %I:%M:%S%p",
        )
        consoleHandler.setFormatter(formatter)
        self.logger.addHandler(consoleHandler)

    def info(self, message):
        self.logger.info(message)

    def debug(self, message):
        self.logger.debug(message)

    def warning(self, message):
        self.logger.warning(message)

    def error(self, message):
        self.logger.error(message)


log = Logger("util")


class FileTypes(Enum):
    pdb_file = auto()
    glb_file = auto()
    ply_file = auto()
    ascii_file = auto()
    rgb_file = auto()
    xyz_low_file = auto()
    xyz_high_file = auto()


@dataclass
class ProteinStructure:
    uniprot_id: str
    file_name: str = ""
    pdb_file: str = ""
    glb_file: str = ""
    ply_file: str = ""
    ascii_file: str = ""
    rgb_file: str = ""
    xyz_low_file: str = ""
    xyz_high_file: str = ""
    existing_files: dict = None
    scale: float = 1.0

    def __post_init__(self):
        self.update_existence()

    def update_existence(self):
        """Checks whether a fail is already existance in the corresponding directory, if so they will be skipped in some steps of the process."""
        if self.existing_files is None:
            self.existing_files = {}
        files = [
            self.__dict__[file] for file in self.__dict__.keys() if "_file" in file
        ]
        for file, file_type in zip(files, FileTypes.__members__):
            exists = False
            if os.path.exists(file):
                exists = True
            self.existing_files[FileTypes.__members__[file_type]] = exists


class ColoringModes(Enum):
    cartoons_ss_coloring = "cartoons_ss_coloring"
    cartoons_rainbow_coloring = "cartoons_rainbow_coloring"
    cartoons_heteroatom_coloring = "cartoons_heteroatom_coloring"
    cartoons_polymer_coloring = "cartoons_polymer_coloring"
    cartoons_chain_coloring = "cartoons_chain_coloring"
    cartoons_bFactor_coloring = "cartoons_bFactor_coloring"
    cartoons_nucleotide_coloring = "cartoons_nucleotide_coloring"
    surface_ss_cooloring = "surface_ss_cooloring"
    surface_rainbow_cooloring = "surface_rainbow_cooloring"
    surface_heteroatom_cooloring = "surface_heteroatom_cooloring"
    surface_polymer_cooloring = "surface_polymer_cooloring"
    surface_chain_cooloring = "surface_chain_cooloring"
    surface_electrostatic_coloring = "surface_electrostatic_coloring"
    surface_hydrophic_coloring = "surface_hydrophic_coloring"
    surface_bFactor_coloring = "surface_bFactor_coloring"
    surface_nucleotide_coloring = "cartoons_nucleotide_coloring"
    stick_ss_coloring = "stick_ss_coloring"
    stick_rainbow_coloring = "stick_rainbow_coloring"
    stick_heteroatom_coloring = "stick_heteroatom_coloring"
    stick_polymer_coloring = "stick_polymer_coloring"
    stick_chain_coloring = "stick_chain_coloring"
    stick_bFactor_coloring = "stick_bFactor_coloring"
    stick_nucleotide_coloring = "stick_nucleotide_coloring"
    ball_ss_coloring = "ball_ss_coloring"
    ball_rainbow_coloring = "ball_rainbow_coloring"
    ball_heteroatom_coloring = "ball_heteroatom_coloring"
    ball_polymer_coloring = "ball_polymer_coloring"
    ball_chain_coloring = "ball_chain_coloring"
    ball_bFactor_coloring = "ball_bFactor_coloring"
    ball_nucleotide_coloring = "ball_nucleotide_coloring"
    sphere_ss_coloring = "sphere_ss_coloring"
    sphere_rainbow_coloring = "sphere_rainbow_coloring"
    sphere_heteroatom_coloring = "sphere_heteroatom_coloring"
    sphere_polymer_coloring = "sphere_polymer_coloring"
    sphere_chain_coloring = "sphere_chain_coloring"
    sphere_bFactor_coloring = "sphere_bFactor_coloring"
    sphere_nucleotide_coloring = "sphere_nucleotide_coloring"

    @staticmethod
    def list_of_modes():
        return [mode.value for mode in ColoringModes]


class AlphaFoldVersion(Enum):
    v1 = "v1"
    v2 = "v2"
    v3 = "v3"
    v4 = "v4"

    @staticmethod
    def list_of_versions():
        return list(map(lambda c: c.value, AlphaFoldVersion))


def fetch_pdb_from_rcsb(uniprot_id: str, save_location: str) -> None:
    file_name = uniprot_id + ".pdb"
    url = "https://files.rcsb.org/download/" + file_name
    return fetch_pdb(uniprot_id, url, save_location, file_name)


def fetch_pdb_from_alphafold(
    uniprot_id: str,
    save_location: str,
    db_version: AlphaFoldVersion = AlphaFoldVersion.v1.value,
) -> bool:
    """
    Fetches .pdb File from the AlphaFold Server. This function uses the request module from python standard library to directly download pdb files from the AlphaFold server.

    Requested .pdb files can be found at https://alphafold.ebi.ac.uk/files/AF-<UniProtID>-F1-model_<db_version>.pdb.

    The loaded .pdb file is saved in a subfolder called "pdbs" in the current directory.

    Args:
        uniprot_id (string): UniProtID of the requested protein.
        save_location (string): Path to the directory where the .pdb file should be saved.
        db_version (string): Version of the database.

    Returns:
        success (bool) : tells whether the fetching was successful or not.
    """
    log.debug(f"AlphaFoldDB version: {db_version}.")
    file_name = f"AF-{uniprot_id}-F1-model_{db_version}.pdb"  # Resulting file name which will be downloaded from the alphafold DB
    url = "https://alphafold.ebi.ac.uk/files/" + file_name  # Url to request
    return fetch_pdb(uniprot_id, url, save_location, file_name)


def fetch_pdb(uniprot_id: str, url: str, save_location: str, file_name: str) -> bool:

    success = True
    try:
        # try to fetch the structure from the given url
        r = requests.get(url, allow_redirects=True)  # opens url
        if r.status_code == 404:
            # If the file it not available, an exception will be raised
            raise StructureNotFoundError(
                "StructureNotFoundError: There is no structure on the server with this UniProtID."
            )
        # downloads the pdb file and saves it in the pdbs directory
        os.makedirs(save_location, exist_ok=True)
        open(f"{save_location}/{file_name}", "wb").write(r.content)
        log.debug(
            f"Successfully fetched {uniprot_id} from URL {url}. Saved in {save_location}."
        )
    except StructureNotFoundError as e:
        log.error(f"StructureNotFoundError:{e}")
        log.warning(f"Failed to fetch {uniprot_id} from URL: {url}")
        success = False
    return success


def search_for_chimerax():
    """Will search for the chimerax executeable on the system. Does not work with windows so far."""
    if platform.system() == "Darwin":
        locations = glob.glob(
            "/Applications/ChimeraX*.app/Contents/MacOS/chimerax", recursive=True
        )
        if len(locations) == 0:
            raise Exception("ChimeraX not found. Is it installed?")
        chimerax = locations[0]
    elif platform.system() == "Linux":
        chimerax = "chimerax"
    elif platform.system() == "Windows":
        import win32api

        drives = win32api.GetLogicalDriveStrings()
        drives = drives.split("\000")[:-1]
        for drive in drives:
            drive = drive.replace("\\", "/")
            p = f"{drive}*/ChimeraX*/bin/ChimeraX*-console.exe"
            chimerax = glob.glob(p, recursive=True)
            if len(chimerax) > 0:
                chimerax = f'"{chimerax[0]}"'.replace("/", "\\")
                break
        if len(chimerax) == 0:
            raise Exception("ChimeraX not found. Is it installed?")

    return chimerax


def run_chimerax_coloring_script(
    chimearx: str,
    pdb_dir: str,
    proteins: list[str],
    save_location: str,
    processing: str,
    colors: list or None,
) -> None:
    """
    This will use the give ChimeraX installation to process the .pdb files.It will color the secondary structures in the given colors.
    The offscreen render does only work under linux.

    Args:
        protein (string): UniProtID of the protein which will be processed
        colors (list, optional): List containing three colors. The first is the color of coil. The second will be the color of the helix. And the last color is the color of the strands. Defaults to ["red", "green", "blue"] i.e. coils will be red, helix will be green and stands will be blue.
    """
    # Define script to call.
    bundle = os.path.join(SCRITPS, "chimerax_bundle.py")
    # Setup the arguments to call with the script.
    file_string = ""
    for file in proteins:
        _, file = ntpath.split(file)
        file_string += f"{file},"
    file_string = file_string[:-1]
    os.makedirs(save_location, exist_ok=True)
    if platform.system() == "Windows":
        bundle = bundle
        pdb_dir = pdb_dir.split("\\")
        pdb_dir = "/".join(pdb_dir)
        save_location = save_location.split("\\")
        save_location = "/".join(save_location)
    arg = [
        bundle,  # Path to chimeraX bundle.
        pdb_dir,  # Path to the directory where the .pdb files are stored.
        file_string,  # Filename
        processing,  # Define mode as secondary structure coloring.,  # Path to the directory where the colored .pdb files should be saved.
    ]
    script_arg = [colors, f"target={save_location}"]
    try:
        # Call chimeraX to process the desired object.
        call_ChimeraX_bundle(chimearx, *arg, script_arg=script_arg)
        # Clean tmp files
    except FileNotFoundError:
        # raise an expection if chimeraX could not be found
        log.error(
            "Installation of chimeraX could not be found. Please define the Path to the Application."
        )
        exit()


def call_ChimeraX_bundle(
    chimerax: str,
    script: str,
    working_Directory: str,
    file_names: str,
    mode: str,
    script_arg: list = [],
) -> None:
    """
    Function to call chimeraX and run chimeraX Python script with the mode applied.

    Args:
        script (string): chimeraX python script/bundle which should be called
        working_Directory (string): Define the working directory to which chimeraX should direct to (run(session,"cd "+arg[1]))
        file_name (string): target file which will be processed
        mode (string): Tells which pipline is used during chimeraX processing
        (ss = secondary structures, aa = aminoacids, ch = chain). Only ss is implemented at that moment.
        script_arg (list, strings): all arguments needed by the function used in the chimeraX Python script/bundle (size is dynamic). All Arguments are strings.
    """
    # prepare Arguments for script execution
    arg = list([script, working_Directory, file_names, mode])

    arg.extend(script_arg)
    if platform.system() == "Linux":
        # for Linux we can use off screen render. This does not work on Windows or macOS
        command = (
            '%s --offscreen --script "' % chimerax
            + ("%s " * len(arg)) % (tuple(arg))
            + '"'
        )
    else:
        # call chimeraX with commandline in a subprocess
        command = '%s --script "' % chimerax + ("%s " * len(arg)) % (tuple(arg)) + '"'
    try:
        process = sp.Popen(command, shell=True, stdout=sp.DEVNULL, stdin=sp.PIPE)

    except Exception as e:
        # raise an expecting if chimeraX could not be found
        log.error(
            "Could not run ChimeraX. Is the installation path setup correctly?\n"
            + chimerax
            + "\nIf not please correct it."
        )
    # wait until chimeraX is finished with processing
    process.wait()


def convert_glb_to_ply(glb_file: str, ply_file: str) -> None:
    """
    This function converts a glb file to a ply file.

    Args:
        glb_file (string): Path to the glb file.
    """
    save_location, _ = ntpath.split(glb_file)
    os.makedirs(save_location, exist_ok=True)
    mesh = trimesh.load(glb_file, force="mesh")
    file = ply.export_ply(mesh)
    with open(ply_file, "wb+") as f:
        f.write(file)
    return True


def batch(funcs: list[object], proteins: list[str], batch_size: int) -> None:
    """Will run the functions listed in funcs in a batched process."""
    start = 0
    end = batch_size
    que = proteins.copy()
    while len(que) > 0:
        log.debug(f"Starting Batch form: {start} to {end}")
        batch_proteins = que[:batch_size]
        for func in funcs:
            func(batch_proteins)
        start = end
        end += batch_size
        del que[:batch_size]


def remove_dirs(directory):
    """Removes a directory an all underlying subdirectories. WARNING this can lead to los of data!"""
    if os.path.isdir(directory):
        shutil.rmtree(directory)

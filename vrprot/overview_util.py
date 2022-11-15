import os

import pandas as pd

from .util import WD, ColoringModes, ProteinStructure

STATIC_PATH = os.path.join(WD, "static")
CSV_PATH = os.path.join(STATIC_PATH, "static")
DEFAULT_OVERVIEW_FILE = os.path.join(WD, "static", "csv", "overview.csv")
COLUMNS = ["uniprot_id", "pdb_file", "multi_structure", "parts"]
for mode in ColoringModes.__dict__.values():
    if isinstance(mode, str):
        if mode.endswith("coloring"):
            COLUMNS.append(mode)


def init_overview(columns=None) -> pd.DataFrame:
    """
    Initializes the overview table.
    """
    if columns is None:
        columns = COLUMNS
    overview = pd.DataFrame(columns=columns)
    overview.set_index("uniprot_id", inplace=True)
    return overview


def read_overview(file, index_col="uniprot_id") -> pd.DataFrame:
    """
    Reads the overview table.
    """
    overview = pd.read_csv(file, index_col=index_col)
    return overview


def get_scale(uniprot_ids=[], mode=ColoringModes.cartoons_ss_coloring):
    """look in overview wether there is a pdb file for the uniprot id and the demanded mode."""
    overview = get_overview()
    res = {}
    for id in uniprot_ids:
        if id in overview.index:
            res[id] = overview.loc[id, mode]
    return res


def write_overview(overview, file=None) -> None:
    """
    Writes the overview table.
    """
    os.makedirs(CSV_PATH, exist_ok=True)
    if file is None:
        file = DEFAULT_OVERVIEW_FILE
    if not os.path.exists(file):
        with open(file, "w+") as f:
            pass
    overview.to_csv(file)


def get_overview(file=None) -> pd.DataFrame:
    if file is None:
        file = DEFAULT_OVERVIEW_FILE
    if os.path.isfile(file):
        overview = read_overview(file)
    else:
        overview = init_overview()
    return overview


def write_scale(uniprotid, scale, pdb_file, processing, overview):
    overview = get_overview(overview)
    overview.loc[uniprotid, "pdb_file"] = pdb_file
    overview.loc[uniprotid, processing] = scale
    write_overview(overview)


def add_protein_structure_from_scales(
    overview: pd.DataFrame,
    file: str,
    single_pdb_dir: str,
    processing: str,
    multi_pdb_dir: str = None,
    output: str = DEFAULT_OVERVIEW_FILE,
):
    try:
        scales = pd.read_csv(file, index_col="uniprot_id")
    except:
        scales = pd.read_csv(file, index_col="UniProtID")
    for some_file in os.listdir(single_pdb_dir):
        if some_file.endswith(".pdb"):
            uniprot_id = some_file.split("-")[1]
            overview.loc[uniprot_id, "pdb_file"] = os.path.join(
                single_pdb_dir, some_file
            )
            overview.loc[uniprot_id, "multi_structure"] = False
            overview.loc[uniprot_id, "parts"] = "NA"
    if multi_pdb_dir is not None:
        structures = os.listdir(multi_pdb_dir)
        structures = [struc for struc in structures if struc.endswith(".pdb")]
        while len(structures) > 0:
            structure = structures[0]
            uniprot_id = structure.split("-")[1]
            parts = [file for file in structures if file.find(uniprot_id) != -1]
            for part in parts:
                structures.remove(part)
            parts = [os.path.abspath(part) for part in parts]
            overview.loc[uniprot_id, "pdb_file"] = os.path.join(
                multi_pdb_dir, structure
            )
            overview.loc[uniprot_id, "multi_structure"] = True
            overview.loc[uniprot_id, "parts"] = ";".join(parts)
            print(len(structures))

    for uniprot, row in scales.iterrows():
        overview.loc[uniprot, processing] = row["scale"]
    write_overview(overview, output)


def main(proteins: list[ProteinStructure], mode: str):
    overview = get_overview()
    for protein in proteins:
        overview.loc[protein.uniprot_id, "pdb_file"] = protein.pdb_file
        overview.loc[protein.uniprot_id, mode] = protein.scale
    write_overview(overview)


if __name__ == "__main__":
    overview = get_overview()
    pdbs_single_part_structure = "/Users/till/Documents/Playground/proteins/pdb/"
    pdbs_multi_part_structure = (
        "/Users/till/Documents/Playground/proteins/pdb/multistructures"
    )
    # Add scales from caroon ss coloring
    add_protein_structure_from_scales(
        overview,
        "/Volumes/M2 Backup/Menchelab/scale_cartoon_ss.csv",
        # "/Volumes/M2 Backup/Menchelab/scale_cartoon_ss_Multistru.csv",
        pdbs_single_part_structure,
        ColoringModes.cartoons_ss_coloring,
        multi_pdb_dir=pdbs_multi_part_structure,
    )
    # Add scales from caroon ss coloring Multistructures
    add_protein_structure_from_scales(
        overview,
        "/Volumes/M2 Backup/Menchelab/scale_cartoon_ss_Multistru.csv",
        pdbs_single_part_structure,
        ColoringModes.cartoons_ss_coloring,
        multi_pdb_dir=pdbs_multi_part_structure,
    )
    # Add scales from Electro static coloring
    add_protein_structure_from_scales(
        overview,
        "/Volumes/M2 Backup/Menchelab/scales_surface_electrostatic.csv",
        pdbs_single_part_structure,
        ColoringModes.surface_electrostatic_coloring,
        multi_pdb_dir=pdbs_multi_part_structure,
    )
    # print(init_overview())

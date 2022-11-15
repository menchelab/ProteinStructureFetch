from argparse import ArgumentParser

from .util import AlphaFoldVersion, ColoringModes


def argument_parser(exec_name="main.py"):
    parser = ArgumentParser(prog=exec_name)
    subparsers = parser.add_subparsers(help="mode", dest="mode")
    fetch_parser = subparsers.add_parser(
        "fetch", help="Fetch proteins from the Alphafold database."
    )
    fetch_parser.add_argument(
        "proteins",
        type=str,
        nargs=1,
        help="Proteins to fetch, which are separated by a comma.",
    )
    file_parser = subparsers.add_parser(
        "local",
        help="Process proteins from files (.pdb, .glb, .ply, .xyzrgb) in a directory.",
    )
    file_parser.add_argument(
        "source",
        type=str,
        help="Directory containing the files",
        nargs=1,
        action="store",
    )
    list_parser = subparsers.add_parser(
        "list",
        help="Process proteins from a file containing one UniProt ID in each line.",
    )
    list_parser.add_argument(
        "file",
        type=str,
        nargs=1,
        help="File from which the proteins are extracted from.",
    )
    clear = subparsers.add_parser(
        "clear",
        help="Removes the processing_files directory",
    )
    parser.add_argument(
        "-pdb_file",
        "--pdb",
        nargs="?",
        type=str,
        metavar="PDB_DIRECTORY",
        help="Defines, where to save the PDB Files.",
    )
    parser.add_argument(
        "-glb_file",
        "--glb",
        nargs="?",
        type=str,
        metavar="GLB_DIRECTORY",
        help="Defines, where to save the GLB Files.",
    )
    parser.add_argument(
        "-ply_file",
        "--ply",
        nargs="?",
        type=str,
        metavar="PLY_DIRECTORY",
        help="Defines, where to save the PLY Files.",
    )
    parser.add_argument(
        "-cloud",
        "--pcd",
        type=str,
        nargs="?",
        metavar="PCD_DIRECTORY",
        help="Defines, where to save the ASCII point clouds.",
    )
    parser.add_argument(
        "-map",
        "--m",
        type=str,
        nargs="?",
        metavar="MAP_DIRECTORY",
        help="Defines, where to save the color maps.",
    )
    parser.add_argument(
        "-alphafold_version",
        "--av",
        type=str,
        nargs="?",
        choices=list(AlphaFoldVersion),
        help="Defines, which version of Alphafold to use.",
    )
    parser.add_argument(
        "-batch_size",
        "--bs",
        type=int,
        nargs="?",
        metavar="BATCH_SIZE",
        help="Defines the size of the batch which will be processed",
    )
    parser.add_argument(
        "-keep_pdb",
        "-kpdb",
        type=bool,
        nargs="?",
        choices=[True, False],
        help="Define whether to still keep the PDB files after the GLB file is created. Default is True.",
    )
    parser.add_argument(
        "-keep_glb",
        "-kglb",
        type=bool,
        nargs="?",
        choices=[True, False],
        help="Define whether to still keep the GLB files after the PLY file is created. Default is False.",
    )
    parser.add_argument(
        "-keep_ply",
        "-kply",
        type=bool,
        nargs="?",
        choices=[True, False],
        help="Define whether to still keep the PLY files after the ASCII file is created. Default is False.",
    )
    parser.add_argument(
        "-keep_ascii",
        "-kasc",
        type=bool,
        nargs="?",
        choices=[True, False],
        help="Define whether to still keep the ASCII Point CLoud files after the color maps are generated. Default is False.",
    )
    parser.add_argument(
        "-chimerax",
        "--ch",
        type=str,
        nargs="?",
        metavar="CHIMERAX_EXEC",
        help="Defines, where to find the ChimeraX executable.",
    )
    colormode_choices = ", ".join(list(ColoringModes.__members__.keys())[:5])
    parser.add_argument(
        "-color_mode",
        "--cm",
        type=str,
        nargs="?",
        help=f"Defines the coloring mode which will be used to color the structure. Choices: {colormode_choices}... . For a full list, see README.",
    )

    if parser.parse_args().mode == None:
        parser.parse_args(["-h"])
        exit()
    return parser

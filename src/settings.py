# TODO: REMOVE AFTER
import os
import sys

sys.path.append(
    os.path.join(
        os.path.dirname(__file__), "..", "alphafold_to_vrnetzer", "pypi_project", "src"
    )
)
#################

import os
import shutil
import sys

import vrprot
from vrprot.util import FileTypes as FT

_WORKING_DIR = os.path.dirname(os.path.abspath(__file__))
_FLASK_TEMPLATE_PATH = os.path.join(_WORKING_DIR, "..", "templates")
_FLASK_STATIC_PATH = os.path.join(_WORKING_DIR, "..", "static")
_EXTENSIONS_PATH = os.path.join(_WORKING_DIR, "..", "..")
_THIS_EXTENSION_PATH = os.path.join(_WORKING_DIR, "..")
_VRNETZER_PATH = os.path.join(_EXTENSIONS_PATH, "..")

_STATIC_PATH = os.path.join(_VRNETZER_PATH, "static")
_PROJECTS_PATH = os.path.join(_STATIC_PATH, "projects")
_MAPS_PATH = os.path.join(_STATIC_PATH, "maps")

# vrprot settings:
DEFAULT_MODE = vrprot.util.ColoringModes.cartoons_ss_coloring.value
DEFAULT_ALPHAFOLD_VERSION = vrprot.util.AlphaFoldVersion.v4.value


parser = vrprot.alphafold_db_parser.AlphafoldDBParser(
    WD=_THIS_EXTENSION_PATH,
    alphafold_ver=DEFAULT_ALPHAFOLD_VERSION,
    processing=DEFAULT_MODE,
)
parser.OUTPUT_DIR = _MAPS_PATH
parser.keep_temp = {
    FT.pdb_file: False,
    FT.glb_file: False,
    FT.ply_file: False,
    FT.ascii_file: False,
}
parser.img_size = 256
os.makedirs(_MAPS_PATH, exist_ok=True)


class NodeTags:
    uniprot = "uniprot"

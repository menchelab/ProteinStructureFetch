
# TODO: REMOVE AFTER 
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__),".."))

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
DEFAULT_MODE = vrprot.util.ColoringModes.cartoons_ss_coloring.value

parser = vrprot.alphafold_db_parser.AlphafoldDBParser(WD=_THIS_EXTENSION_PATH)
parser.OUTPUT_DIR = _MAPS_PATH
parser.keep_temp = {
    FT.pdb_file: False,
    FT.glb_file: False,
    FT.ply_file: False,
    FT.ascii_file: False,
}
os.makedirs(_MAPS_PATH, exist_ok=True)


class NodeTags:
    uniprot = "uniprot"

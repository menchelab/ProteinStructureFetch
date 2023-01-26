# TODO: REMOVE AFTER
import ast
import os
import sys

from .classes import ConfigCategories as CC

sys.path.append(
    os.path.join(os.path.dirname(__file__), "..", "vrprot", "pypi_project", "src")
)
#################

import configparser
import os
import shutil
import sys

import configobj
import vrprot
from configobj import validate
from vrprot.classes import FileTypes as FT

_WORKING_DIR = os.path.dirname(os.path.abspath(__file__))
_THIS_EXTENSION_PATH = os.path.join(_WORKING_DIR, "..")
CONFIG_FILE = os.path.join(_THIS_EXTENSION_PATH, "config.ini")
CONFIG_SPEC_FILE = os.path.join(_THIS_EXTENSION_PATH, "config_spec.ini")
_FLASK_TEMPLATE_PATH = os.path.join(_WORKING_DIR, "..", "templates")
_FLASK_STATIC_PATH = os.path.join(_WORKING_DIR, "..", "static")
_EXTENSIONS_PATH = os.path.join(_WORKING_DIR, "..", "..")
_VRNETZER_PATH = os.path.join(_EXTENSIONS_PATH, "..")
_STATIC_PATH = os.path.join(_VRNETZER_PATH, "static")
_PROJECTS_PATH = os.path.join(_STATIC_PATH, "projects")
_MAPS_PATH = os.path.join(_STATIC_PATH, "maps")
_OVERVIEW_FILE = os.path.join(_THIS_EXTENSION_PATH, "overview.csv")
DEFAULT_MODE = vrprot.classes.ColoringModes.cartoons_ss_coloring.value
DEFAULT_ALPHAFOLD_VERSION = vrprot.classes.AlphaFoldVersion.v4.value

VDT = validate.Validator()
config = configobj.ConfigObj(CONFIG_FILE, configspec=CONFIG_SPEC_FILE)
config.validate(VDT, copy=True)
config.write()

# Directory settings
directories = config[CC.dirs]


def get_val(var, default=None):
    if var is None or var == "None":
        return default
    return var


_WORKING_DIR = get_val(directories[CC.DirKeys.WD], _WORKING_DIR)
_FLASK_TEMPLATE_PATH = get_val(
    directories[CC.DirKeys.flaskTemplates], _FLASK_TEMPLATE_PATH
)

_FLASK_STATIC_PATH = get_val(directories[CC.DirKeys.flaskStatic], _FLASK_STATIC_PATH)
_EXTENSIONS_PATH = get_val(directories[CC.DirKeys.extensions], _EXTENSIONS_PATH)
_STATIC_PATH = get_val(directories[CC.DirKeys.vrnetzerStatic], _STATIC_PATH)
_PROJECTS_PATH = get_val(directories[CC.DirKeys.vrnetzerProjects], _PROJECTS_PATH)
_MAPS_PATH = get_val(directories[CC.DirKeys.maps], _MAPS_PATH)
_OVERVIEW_FILE = get_val(directories[CC.DirKeys.overviewFile], _OVERVIEW_FILE)
# Parser settings
parser_cfg = config[CC.parser]

DEFAULT_MODE = parser_cfg.get(CC.ParserKeys.colorMode)
DEFAULT_ALPHAFOLD_VERSION = parser_cfg.get(CC.ParserKeys.alphafoldVersion)

num_cached = get_val(parser_cfg[CC.ParserKeys.numCached])

parser = vrprot.alphafold_db_parser.AlphafoldDBParser(
    WD=_THIS_EXTENSION_PATH,
    alphafold_ver=DEFAULT_ALPHAFOLD_VERSION,
    processing=DEFAULT_MODE,
    overview_file=_OVERVIEW_FILE,
    images=bool(parser_cfg.get(CC.ParserKeys.thumbnails)),
    num_cached=num_cached,
)
parser.keep_temp = {
    FT.pdb_file: parser_cfg.get(CC.ParserKeys.keepPDB),
    FT.glb_file: parser_cfg.get(CC.ParserKeys.keepGLB),
    FT.ply_file: parser_cfg.get(CC.ParserKeys.keepPLY),
    FT.ascii_file: parser_cfg.get(CC.ParserKeys.keepASCII),
}
parser.img_size = parser_cfg.get(CC.ParserKeys.imageSize)
parser.overwrite = parser_cfg.get(CC.ParserKeys.overwrite)
parser.OUTPUT_DIR = _MAPS_PATH
os.makedirs(_MAPS_PATH, exist_ok=True)

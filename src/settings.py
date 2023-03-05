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

from configobj import ConfigObj
from configobj.validate import Validator
from vrprot.classes import FileTypes as FT

import vrprot

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

configspec = ConfigObj(
    CONFIG_SPEC_FILE,
    encoding="UTF8",
    list_values=True,
    _inspec=True,
    interpolation=False,
)
config = ConfigObj(CONFIG_FILE, configspec=configspec)
VDT = Validator()
config = ConfigObj(CONFIG_FILE, configspec=CONFIG_SPEC_FILE)
config.validate(VDT, copy=True)
config.write()

# Directory settings
directories = config[CC.dirs]


def remove_none(_dict):
    """Remove None values from dict as they are saved as strings...Just why?
    Args:
        _dict (dict): dict that contains config values

    Returns:
        dict: cleared dict
    """
    for k, v in _dict.items():
        if v is None or v == "None":
            _dict.pop(k)
    return _dict


directories = remove_none(directories)

_WORKING_DIR = directories.get(CC.DirKeys.WD, _WORKING_DIR)
_FLASK_TEMPLATE_PATH = directories.get(CC.DirKeys.flaskTemplates, _FLASK_TEMPLATE_PATH)
_FLASK_STATIC_PATH = directories.get(CC.DirKeys.flaskStatic, _FLASK_STATIC_PATH)
_EXTENSIONS_PATH = directories.get(CC.DirKeys.extensions, _EXTENSIONS_PATH)
_STATIC_PATH = directories.get(CC.DirKeys.flaskStatic, _STATIC_PATH)
_PROJECTS_PATH = directories.get(CC.DirKeys.vrnetzerProjects, _PROJECTS_PATH)
_MAPS_PATH = directories.get(CC.DirKeys.maps, _MAPS_PATH)
_OVERVIEW_FILE = directories.get(CC.DirKeys.overviewFile, _OVERVIEW_FILE)
# Parser settings

parser_cfg = config[CC.parser]
parser_cfg = remove_none(parser_cfg)

DEFAULT_MODE = parser_cfg.get(CC.ParserKeys.colorMode)
DEFAULT_ALPHAFOLD_VERSION = parser_cfg.get(CC.ParserKeys.alphafoldVersion)

num_cached = parser_cfg.get(CC.ParserKeys.numCached)

parser = vrprot.alphafold_db_parser.AlphafoldDBParser(
    WD=_THIS_EXTENSION_PATH,
    alphafold_ver=DEFAULT_ALPHAFOLD_VERSION,
    processing=DEFAULT_MODE,
    overview_file=_OVERVIEW_FILE,
    images=parser_cfg.get(CC.ParserKeys.thumbnails),
    num_cached=num_cached,
)
parser.keep_temp = {
    FT.pdb_file: parser_cfg.get(CC.ParserKeys.keepPDB),
    FT.glb_file: parser_cfg.get(CC.ParserKeys.keepGLB),
    FT.ply_file: parser_cfg.get(CC.ParserKeys.keepPLY),
    FT.ascii_file: parser_cfg.get(CC.ParserKeys.keepASCII),
}
parser.colors = parser_cfg.get(CC.ParserKeys.colors)
parser.img_size = parser_cfg.get(CC.ParserKeys.imageSize)
parser.overwrite = parser_cfg.get(CC.ParserKeys.overwrite)
parser.OUTPUT_DIR = _MAPS_PATH
vrprot.classes.LOG_LEVEL = parser_cfg.get(CC.ParserKeys.logLevel)
os.makedirs(_MAPS_PATH, exist_ok=True)

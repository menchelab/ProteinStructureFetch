# TODO: REMOVE AFTER
import ast
import os
import sys

from .classes import ConfigCategories as CC

sys.path.append(
    os.path.join(
        os.path.dirname(__file__), "..", "alphafold_to_vrnetzer", "pypi_project", "src"
    )
)
#################

import configparser
import os
import shutil
import sys

import vrprot
from vrprot.classes import FileTypes as FT

_WORKING_DIR = os.path.dirname(os.path.abspath(__file__))
_THIS_EXTENSION_PATH = os.path.join(_WORKING_DIR, "..")

# vrprot settings:
config = configparser.ConfigParser()
config.read(os.path.join(_THIS_EXTENSION_PATH, "config.ini"))
directories = config[CC.dirs]

# Directory settings
_WORKING_DIR = directories.get(CC.DirKeys.WD, _WORKING_DIR)
_FLASK_TEMPLATE_PATH = directories.get(
    CC.DirKeys.flaskTemplates,
    os.path.join(_WORKING_DIR, "..", "templates"),
)
_FLASK_STATIC_PATH = directories.get(
    CC.DirKeys.flaskStatic, os.path.join(_WORKING_DIR, "..", "static")
)
_EXTENSIONS_PATH = directories.get(
    CC.DirKeys.extensions, os.path.join(_WORKING_DIR, "..", "..")
)
_VRNETZER_PATH = directories.get(
    CC.DirKeys.vrnetzer, os.path.join(_EXTENSIONS_PATH, "..")
)
_STATIC_PATH = directories.get(
    CC.DirKeys.vrnetzerStatic, os.path.join(_VRNETZER_PATH, "static")
)
_PROJECTS_PATH = directories.get(
    CC.DirKeys.vrnetzerProjects, os.path.join(_STATIC_PATH, "projects")
)
_MAPS_PATH = directories.get(CC.DirKeys.maps, os.path.join(_STATIC_PATH, "maps"))
_OVERVIEW_FILE = directories.get(
    CC.DirKeys.overviewFile,
    os.path.join(_THIS_EXTENSION_PATH, "overview.csv"),
)

# Parser settings
parser_cfg = config[CC.parser]
DEFAULT_MODE = parser_cfg.get(
    CC.ParserKeys.colorMode,
    vrprot.classes.ColoringModes.cartoons_ss_coloring.value,
)
DEFAULT_ALPHAFOLD_VERSION = parser_cfg.get(
    CC.ParserKeys.alphafoldVersion, vrprot.classes.AlphaFoldVersion.v4.value
)
parser = vrprot.alphafold_db_parser.AlphafoldDBParser(
    WD=_THIS_EXTENSION_PATH,
    alphafold_ver=DEFAULT_ALPHAFOLD_VERSION,
    processing=DEFAULT_MODE,
    overview_file=_OVERVIEW_FILE,
)
parser.keep_temp = {
    FT.pdb_file: parser_cfg.getboolean(CC.ParserKeys.keepPDB, False),
    FT.glb_file: parser_cfg.getboolean(CC.ParserKeys.keepGLB, False),
    FT.ply_file: parser_cfg.getboolean(CC.ParserKeys.keepPLY, False),
    FT.ascii_file: parser_cfg.getboolean(CC.ParserKeys.keepASCII, False),
}
parser.img_size = parser_cfg.getint(CC.ParserKeys.imageSize, 256)
parser.overwrite = parser_cfg.getboolean(CC.ParserKeys.overwrite, False)
parser.OUTPUT_DIR = _MAPS_PATH
os.makedirs(_MAPS_PATH, exist_ok=True)

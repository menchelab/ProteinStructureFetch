# TODO: REMOVE AFTER
import configparser
import os
import sys

sys.path.append(
    os.path.join(
        os.path.dirname(__file__), "..", "alphafold_to_vrnetzer", "pypi_project", "src"
    )
)
#################

import time

import flask
import GlobalData as GD
from bs4 import BeautifulSoup as bs
from vrprot.alphafold_db_parser import AlphafoldDBParser
from vrprot.util import AlphaFoldVersion, ColoringModes

from . import settings as st
from .classes import ConfigCategories as CC


def asnyc_time_ex(func, *args, **kwargs):
    import asyncio

    """Time the execution of a function and return the result and the time taken."""
    start = time.time()
    res = asyncio.run(func(*args, **kwargs))
    end = time.time()
    return res, end - start


def time_ex(func, *args, **kwargs):
    """Time the execution of a function and return the result and the time taken."""
    start = time.time()
    res = func(*args, **kwargs)
    end = time.time()
    return res, end - start


def parse_request(
    parser: AlphafoldDBParser, request: flask.Request
) -> AlphafoldDBParser:
    """Extract processing mode and alphafold version from request."""
    mode = request.args.get("mode")
    alphafold_ver = request.args.get("ver")
    overwrite = request.args.get("overwrite")
    if mode is None:
        mode = st.DEFAULT_MODE
    if mode not in ColoringModes.list_of_modes():
        return {
            "error": "Invalid coloring mode.",
            "possible_modes": ColoringModes.list_of_modes(),
        }
    if mode is None:
        mode = st.DEFAULT_MODE

    parser.overwrite = st.parser_cfg.getboolean(CC.ParserKeys.overwrite, False)
    if overwrite:
        if overwrite.lower() == "true":
            parser.overwrite = True

    parser.processing = mode

    if alphafold_ver is not None:
        if alphafold_ver in AlphaFoldVersion.list_of_versions():
            parser.alphafold_ver = alphafold_ver
        else:
            parser.alphafold_ver = st.parser_cfg.get(
                CC.ParserKeys.alphafoldVersion, AlphaFoldVersion.v4.value
            )
    return parser


def setup() -> None:
    """Write vrprot settings to GD.vrprot"""
    config = read_config()
    vrprot_config = {}
    vrprot_config["mode"] = config[CC.parser][CC.ParserKeys.colorMode]
    vrprot_config["currVer"] = config[CC.parser][CC.ParserKeys.alphafoldVersion]
    vrprot_config["availVer"] = [ver.value for ver in AlphaFoldVersion]
    vrprot_config["colorModes"] = [mode.value for mode in ColoringModes]
    GD.sessionData["vrprot"] = vrprot_config
    # with open(
    #     os.path.join(st._FLASK_TEMPLATE_PATH, "psf_nodepanel_tab_template.html"), "r"
    # ) as f:
    #     soup = bs(f, "html.parser")
    # # Add layout options to the layout dropdown menu
    # selector = soup.find("select", {"id": "psf_mode"})
    # for mode in ColoringModes:
    #     mode = mode.value
    #     selector.append(
    #         bs(f"""<option value="{mode}">{mode}</option>""", "html.parser")
    #     )
    # selector = soup.find("select", {"id": "psf_alphafold_ver"})

    # for ver in AlphaFoldVersion:
    #     ver = ver.value
    #     selector.append(bs(f"""<option value="{ver}">{ver}</option>""", "html.parser"))

    # with open(
    #     os.path.join(st._FLASK_TEMPLATE_PATH, "psf_nodepanel_tab.html"), "w"
    # ) as f:
    #     f.write(str(soup.prettify()))


def write_to_config(category: str, key: str, value: str) -> None:
    config = configparser.ConfigParser()
    config.read(os.path.join(st._THIS_EXTENSION_PATH, "config.ini"))
    config[category][key] = value
    with open(os.path.join(st._THIS_EXTENSION_PATH, "config.ini"), "w") as f:
        config.write(f)


def read_config() -> str:
    config = configparser.ConfigParser()
    config.read(os.path.join(st._THIS_EXTENSION_PATH, "config.ini"))
    return config

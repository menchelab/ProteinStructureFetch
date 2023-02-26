# TODO: REMOVE AFTER
import configparser
import json
import os
import sys

import configobj

sys.path.append(
    os.path.join(os.path.dirname(__file__), "..", "vrprot", "pypi_project", "src")
)
#################

import time

import configobj
import flask
import GlobalData as GD
from vrprot.alphafold_db_parser import AlphafoldDBParser
from vrprot.classes import AlphaFoldVersion, ColoringModes

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
    configured_settings = GD.sessionData.get("vrprot")
    mode = request.args.get("mode")
    alphafold_ver = request.args.get("ver")
    overwrite = request.args.get("overwrite")
    if mode is None:
        if configured_settings:
            mode = configured_settings.get(CC.ParserKeys.colorMode, st.DEFAULT_MODE)
        else:
            mode = st.DEFAULT_MODE
    if mode not in ColoringModes.list_of_modes():
        return {
            "error": "Invalid coloring mode.",
            "possible_modes": ColoringModes.list_of_modes(),
        }

    if not overwrite:
        overwrite = configured_settings.get(CC.ParserKeys.overwrite, False)
    if isinstance(overwrite, str):
        if overwrite.lower() == "true":
            overwrite = True
        else:
            overwrite = False

    default_ver = configured_settings.get(
        CC.ParserKeys.alphafoldVersion, AlphaFoldVersion.v2.value
    )
    if alphafold_ver is not None:
        if alphafold_ver not in AlphaFoldVersion.list_of_versions():
            alphafold_ver = default_ver
    else:
        alphafold_ver = default_ver

    parser.overwrite = overwrite
    parser.processing = mode
    parser.alphafold_ver = alphafold_ver
    return parser


def setup() -> None:
    """Write vrprot settings to GD.vrprot"""
    vrprot_config = {}
    vrprot_config[CC.ParserKeys.colorMode] = st.config[CC.parser][
        CC.ParserKeys.colorMode
    ]
    vrprot_config[CC.ParserKeys.alphafoldVersion] = st.config[CC.parser][
        CC.ParserKeys.alphafoldVersion
    ]
    vrprot_config["availVer"] = [ver.value for ver in AlphaFoldVersion]
    vrprot_config["colorModes"] = [mode.value for mode in ColoringModes]
    vrprot_config[CC.ParserKeys.overwrite] = st.config[CC.parser][
        CC.ParserKeys.overwrite
    ]
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
    st.config[category][key] = value
    st.config.validate(st.VDT)
    st.config.write()


def update_uniprot(request: flask.request):
    """Used to update uniprot entries if they deprecated and merged to a new id.

    Returns:
        str: Message telling whether the update was successful or not.
    """
    old = request.args.get("old")
    uniprot = request.args.get("uniprot")
    node_id = request.args.get("id")
    project = GD.sessionData.get("actPro")
    for var in [uniprot, node_id, project]:
        if var is None:
            return "Missing variable"
    # first check in nodes.json
    node_id = int(node_id)
    updated = {"nodes": False, "names": False}
    nodes_file = f"./static/projects/{project}/nodes.json"
    names_file = f"./static/projects/{project}/names.json"
    if os.path.isfile(nodes_file):
        print("Updating nodes.json")
        with open(nodes_file, "r") as f:
            nodes = json.load(f)
            node = nodes["nodes"][node_id]
            if "uniprot" in node:
                for i, id in enumerate(node["uniprot"]):
                    if id == old:
                        node["uniprot"][i] = uniprot
                        updated["nodes"] = True
            if "attrlist" in node and len(node["attrlist"]) >= 2:
                if node["attrlist"][1] == old:
                    node["attrlist"][1] = uniprot
                    nodes["nodes"][node_id] = node
                    updated["nodes"] = True
            if updated["nodes"]:
                with open(nodes_file, "w") as f:
                    json.dump(nodes, f)

    if os.path.isfile(names_file):
        print("Updating names.json")
        with open(names_file, "r") as f:
            names = json.load(f)
            node = names["names"][node_id]
            if len(node) >= 2:
                if node[1] == old:
                    node[1] = uniprot
                    names["names"][node_id] = node
                    updated["names"] = True
                    with open(names_file, "w") as f:
                        json.dump(names, f)

    return json.dumps(updated)

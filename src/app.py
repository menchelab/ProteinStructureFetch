# TODO: REMOVE AFTER
import json
import os
import sys

from .classes import ConfigCategories as CC

sys.path.append(
    os.path.join(os.path.dirname(__file__), "..", "vrprot", "pypi_project", "src")
)
#################
import flask
import GlobalData as GD
from PIL import Image
from vrprot.classes import AlphaFoldVersion, ColoringModes

from . import settings as st
from . import util, workflows
from .util import time_ex

url_prefix = "/vrprot"
nodepanelppi_tabs = ["psf_nodepanel_tab.html"]

from io_blueprint import IOBlueprint

blueprint = IOBlueprint(
    "ProteinStructureFetch",
    __name__,
    url_prefix=url_prefix,
    template_folder=st._FLASK_TEMPLATE_PATH,
    static_folder=st._FLASK_STATIC_PATH,
)


@blueprint.before_app_first_request
def psf_setup():
    """Setup the extension."""
    util.setup()


@blueprint.route("/fetch", methods=["GET", "POST"])
def fetch():
    """Fetches the image from the server and returns it as a response."""
    job = time_ex(workflows.fetch_from_request, flask.request, st.parser)
    res, runtime = job
    res["runtime"] = f"{runtime} s"
    if flask.request.method == "POST":
        return flask.jsonify(res)
    return f"<h4>{res}</h4>"


@blueprint.route("/list", methods=["GET"])
def fetch_list() -> flask.Response:
    """Fetches protein structures from a list of uniprot ids.

    Returns:
        flask.Response: Report the missing, and fetched structures, as well as the runtime.
    """
    job = time_ex(workflows.fetch_list_from_request, flask.request, st.parser)
    res, runtime = job
    res["runtime"] = f"{runtime} s"
    return flask.jsonify(res)


@blueprint.route("/project", methods=["GET"])
def fetch_structures_for_project() -> flask.Response:
    """Will fetch all protein structures for a certain project. The nodes in the nodes.json file of this project have to have the "uniprot" key with a list of protein structures as values.

    Returns:
        flask.Response: Report the missing, and fetched structures, as well as the runtime.
    """

    job = time_ex(
        workflows.for_project,
        flask.request,
        st.parser,
    )
    res, runtime = job
    res["runtime"] = f"{runtime} s"
    return flask.jsonify(res)


@blueprint.route("/changeMode", methods=["GET", "POST"])
def change_mode() -> str:
    """Changes the coloring mode which is used during the ChimeraX processing.

    Returns:
        str: Message telling whether the mode change was successfully executed or not.
    """
    mode = flask.request.args.get("mode")

    if mode is None:
        modes = ColoringModes.list_of_modes()
        error = (
            "<h4 style='color:red';>Error : No mode provided</h4>"
            + f"<h4;>Example :<a href='/vrprot/changeMode?mode=cartoon_ss_coloring'>{flask.request.base_url}/vrprot/changeMode?mode=cartoon_ss_coloring</a>"
            + f"<h4>Possible Modes:{modes}"
        )
        return error
    st.parser.processing = mode
    GD.sessionData["vrprot"][CC.ParserKeys.colorMode] = mode
    util.write_to_config(CC.parser, CC.ParserKeys.colorMode, mode)
    return f"Mode changed to {mode}!"


@blueprint.route("/changeAFVer", methods=["GET", "POST"])
def change_alphafold_ver() -> str:
    """Changes the version of the AlphaFold database from which the structures are fetched from.

    Returns:
        str: Message telling whether the mode change was successfully executed or not.
    """
    ver = flask.request.args.get("ver")
    if ver is None:
        modes = AlphaFoldVersion.list_of_versions()
        error = (
            "<h4 style='color:red';>Error : No version provided</h4>"
            + f"<h4;>Example :<a href='/vrprot/changeAFVer?ver=v1'>{flask.request.base_url}/vrprot/changeAFVer?ver=v1</a>"
            + f"<h4>Possible Modes:{modes}"
        )
        return error
    st.parser.alphafold_ver = ver
    GD.sessionData["vrprot"][CC.ParserKeys.alphafoldVersion] = ver
    util.write_to_config(CC.parser, CC.ParserKeys.alphafoldVersion, ver)
    return f"AlphaFold DB version changed to {ver}!"


@blueprint.route("/settings/overwrite", methods=["GET", "POST"])
def overwrite_settings() -> str:
    """Turns on or off the overwrite mode.

    Returns:
        str: Message telling whether the settings change was successfully executed or not.
    """
    overwrite = flask.request.args.get("value")
    if overwrite is None:
        error = (
            "<h4 style='color:red';>Error : No overwrite value provided</h4>"
            + f"<h4;>Example :<a href='/vrprot/settings/overwrite?value=true'>{flask.request.base_url}/vrprot/settings/overwrite?value=true</a>"
        )
        return error
    st.parser.overwrite = overwrite
    GD.sessionData["vrprot"][CC.ParserKeys.overwrite] = overwrite
    util.write_to_config(CC.parser, CC.ParserKeys.overwrite, overwrite)
    return f"Overwrite set to {overwrite}!"


@blueprint.route("/settings", methods=["GET", "POST"])
def psf_settings() -> str:
    """Displays a WebUI to change the settings of the ProteinStructureFetch extension.

    Returns:
        str: HTML string containing the settings.
    """
    return flask.render_template(
        "psf_settings.html", sessionData=json.dumps(GD.sessionData)
    )


@blueprint.route("/update_uniprot", methods=["GET", "POST"])
def psf_update_uniprot() -> str:
    return util.update_uniprot(flask.request)

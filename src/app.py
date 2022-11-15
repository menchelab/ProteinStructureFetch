
# TODO: REMOVE AFTER 
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__),".."))

import flask
from PIL import Image
from vrprot.util import AlphaFoldVersion

import GlobalData as GD

from . import settings as st
from . import util, workflows
from .util import time_ex

url_prefix = "/vrprot"

blueprint = flask.Blueprint(
    "vrprot",
    __name__,
    url_prefix=url_prefix,
    template_folder=st._FLASK_TEMPLATE_PATH,
    static_folder=st._FLASK_STATIC_PATH,
)


@blueprint.route("/fetch", methods=["GET"])
def fetch():
    """Fetches the image from the server and returns it as a response."""
    job = time_ex(workflows.fetch, st.parser, flask.request)
    res, runtime = job
    res["runtime"] = f"{runtime} s"
    return flask.jsonify(res)


@blueprint.route("/project", methods=["GET"])
def fetch_structures_for_project():
    job = time_ex(workflows.for_project, st.parser, flask.request)
    res, runtime = job
    res["runtime"] = f"{runtime} s"
    return flask.jsonify(res)


@blueprint.route("/list", methods=["GET"])
def fetch_list():
    job = time_ex(workflows.fetch_list, st.parser, flask.request)
    res, runtime = job
    res["runtime"] = f"{runtime} s"
    return flask.jsonify(res)

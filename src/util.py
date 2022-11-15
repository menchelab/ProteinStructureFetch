
# TODO: REMOVE AFTER 
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__),".."))

import time

import flask
from vrprot.alphafold_db_parser import AlphafoldDBParser
from vrprot.util import AlphaFoldVersion, ColoringModes

from . import settings as st


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
    if mode is None:
        mode = st.DEFAULT_MODE
    if mode not in ColoringModes.list_of_modes():
        return {
            "error": "Invalid coloring mode.",
            "possible_modes": ColoringModes.list_of_modes(),
        }
    if mode is None:
        mode = st.DEFAULT_MODE

    parser.processing = mode

    if alphafold_ver is not None:
        if alphafold_ver in AlphaFoldVersion.list_of_versions():
            parser.alphafold_ver = alphafold_ver
        else:
            parser.alphafold_ver = AlphaFoldVersion.v4.value
    return parser

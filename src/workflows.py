
# TODO: REMOVE AFTER 
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__),".."))
import json

import flask
import vrprot
from vrprot.alphafold_db_parser import AlphafoldDBParser
from vrprot.util import AlphaFoldVersion, batch

from . import settings as st
from . import util
from .settings import NodeTags as NT


def get_scales(uniprot_ids=[], mode=st.DEFAULT_MODE):
    return vrprot.overview_util.get_scale(uniprot_ids, mode)


def run_pipeline(parser: AlphafoldDBParser, proteins: list):
    # create the output directory for the corresponding coloring mode if they do not exist
    output_dir = os.path.join(st._MAPS_PATH, parser.processing)
    parser.update_output_dir(output_dir)

    # initialize the structures dictionary of the parser and check wether some processing files do already exist
    parser.init_structures_dict(proteins)
    for protein in proteins:
        parser.update_existence(protein)

    # run the batched process
    batch([parser.fetch_pdb, parser.pdb_pipeline], proteins, parser.batch_size)
    result = get_scales(proteins, parser.processing)

    # update the existence of the processed files
    for protein in proteins:
        parser.update_existence(protein)

    return result


def fetch(parser: AlphafoldDBParser, request: flask.Request):
    # get information from request
    pdb_id = request.args.get("id")
    if pdb_id is None:
        return {"error": "No PDB ID provided."}

    # extract processing mode and alphafold version from request
    parser = util.parse_request(parser, request)
    # if mode is not part of the list of available modes, return an error
    if isinstance(parser, dict):
        return parser

    # create a list of proteins to be processed
    proteins = [pdb_id]

    # run the batched process
    result = run_pipeline(parser, proteins)

    return {"not_fetched": parser.not_fetched, "results": result}


def for_project(parser: AlphafoldDBParser, request: flask.request):
    # get information from request
    project = request.args.get("project")
    if project is None:
        return {"error": "No project provided."}

    # extract processing mode and alphafold version from request
    parser = util.parse_request(parser, request)

    # if mode is not part of the list of available modes, return an error
    if isinstance(parser, dict):
        return parser

    # extract node data from the projects nodes.json file
    nodes_files = os.path.join(st._PROJECTS_PATH, project, "nodes.json")
    with open(nodes_files, "r") as f:
        nodes = json.load(f)["nodes"]

    # extract the uniprot ids from the nodes
    proteins = [",".join(node[NT.uniprot]) for node in nodes if node.get(NT.uniprot)]

    # run the batched process
    result = run_pipeline(parser, proteins)

    return {"not_fetched": parser.not_fetched, "results": result}


def fetch_list(parser: AlphafoldDBParser, request: flask.Request):
    # get information from request
    pdb_ids = request.args.get("ids")
    if pdb_ids is None:
        return {"error": "No PDB IDs provided."}

    # extract processing mode and alphafold version from request
    parser = util.parse_request(parser, request)
    # if mode is not part of the list of available modes, return an error
    if isinstance(parser, dict):
        return parser

    # create a list of proteins to be processed
    proteins = [id for id in pdb_ids.split(",")]

    # run the batched process
    result = run_pipeline(parser, proteins)

    return {"not_fetched": parser.not_fetched, "results": result}

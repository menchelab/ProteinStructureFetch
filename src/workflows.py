# TODO: REMOVE AFTER
import os
import sys

sys.path.append(
    os.path.join(os.path.dirname(__file__), "..", "vrprot", "pypi_project", "src")
)
#################

import json
import traceback

import flask
from vrprot.alphafold_db_parser import AlphafoldDBParser
from vrprot.classes import AlphaFoldVersion
from vrprot.util import batch

import vrprot

from . import map_uniprot
from . import settings as st
from . import util
from .classes import NodeTags as NT


def get_scales(uniprot_ids=[], mode=st.DEFAULT_MODE):
    return vrprot.overview_util.get_scale(uniprot_ids, mode)


def run_pipeline(proteins: list, parser: AlphafoldDBParser = st.parser, **kwargs):
    # create the output directory for the corresponding coloring mode if they do not exist
    # output_dir = os.path.join(st._MAPS_PATH, parser.processing)
    output_dir = os.path.join(st._MAPS_PATH)  # TODO: REMOVE BEFRE RELEASE
    parser.update_output_dir(output_dir)

    # initialize the structures dictionary of the parser and check wether some processing files do already exist
    parser.init_structures_dict(proteins)
    for protein in proteins:
        parser.update_existence(protein)
    # run the batched process
    try:
        parser.fetch_pipeline(proteins, **kwargs)
        # batch([parser.fetch_pdb, parser.pdb_pipeline], proteins, parser.batch_size)
    except vrprot.exceptions.ChimeraXException as e:
        return {"error": "ChimeraX could not be found. Is it installed?"}
    result = get_scales(proteins, parser.processing)

    # update the existence of the processed files
    for protein in proteins:
        parser.update_existence(protein)

    return result


def fetch_from_request(request: flask.Request, parser: AlphafoldDBParser = st.parser):
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
    return fetch(proteins, parser)


def fetch(proteins: list[str], parser: AlphafoldDBParser = st.parser):
    # run the batched process
    parser.not_fetched = set()
    parser.already_exists = set()
    result = run_pipeline(proteins, parser)
    # Try whether you can find an updated UniProt id
    second_try = {}
    if len(parser.not_fetched) > 0:
        try:
            mapped_ac = map_uniprot.main(
                parser.not_fetched,
                source_db=map_uniprot.Databases.uniprot_ac,
                target_db=map_uniprot.Databases.uniprot,
            )
            for re in mapped_ac["results"]:
                a, b = True, True
                while a and b:
                    a = re.get("from")
                    b = re.get("to")
                    b = b.get("uniProtKBCrossReferences")
                    for entry in b:
                        if entry.get("database") == "AlphaFoldDB":
                            b = entry.get("id")
                            second_try[b] = a
                            if a in parser.not_fetched:
                                parser.not_fetched.remove(a)
                            break
                    break
            result.update(run_pipeline(second_try, parser))
            tmp = parser.not_fetched.copy()
            for ac in tmp:
                if ac in second_try:
                    parser.not_fetched.remove(ac)
                    parser.not_fetched.add(second_try[ac])
        except Exception as e:
            print(e)
    return {
        "not_fetched": list(parser.not_fetched),
        "already_exists": list(parser.already_processed),
        "results": result,
        "alternative_ids": {v: k for k, v in second_try.items()},
    }


def for_project(request: flask.request, parser: AlphafoldDBParser = st.parser):
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
    if not os.path.isfile(nodes_files):
        return {"error": "Project does not exist."}

    with open(nodes_files, "r") as f:
        nodes = json.load(f)["nodes"]

    # extract the uniprot ids from the nodes
    proteins = [",".join(node[NT.uniprot]) for node in nodes if node.get(NT.uniprot)]

    # run the batched process
    result = run_pipeline(proteins, parser, on_demand=False)
    return {"not_fetched": list(parser.not_fetched), "results": result}


def fetch_list_from_request(
    request: flask.Request, parser: AlphafoldDBParser = st.parser
):
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

    return fetch_list(proteins, parser)


def fetch_list(proteins: list[str], parser: AlphafoldDBParser = st.parser):
    # run the batched process
    result = run_pipeline(proteins, parser, on_demand=False)

    return {"not_fetched": list(parser.not_fetched), "results": result}

import asyncio
import json
import os

import aiofiles
import aiohttp
import flask
import requests

from . import settings as st
from . import util


async def fetch_list(parser, ids):
    # create a list of proteins to be processed
    proteins = [id for id in ids.split(",")]
    # create the output directory for the corresponding coloring mode if they do not exist
    output_dir = os.path.join(st._MAPS_PATH, parser.processing)
    parser.update_output_dir(output_dir)

    # initialize the structures dictionary of the parser and check wether some processing files do already exist
    parser.init_structures_dict(proteins)
    for protein in proteins:
        parser.update_existence(protein)

    async with aiohttp.ClientSession() as session:
        for id in proteins:
            file_name = f"AF-{id}-F1-model_{parser.alphafold_ver}.pdb"  # Resulting file name which will be downloaded from the alphafold DB
            url = "https://alphafold.ebi.ac.uk/files/" + file_name  # Url to request
            success = True
            save_location = parser.structures[id].pdb_file
            try:
                # try to fetch the structure from the given url
                r = await session.get(url, allow_redirects=True)  # opens url
                if r.status == 404:
                    # If the file it not available, an exception will be raised
                    raise KeyError(
                        "StructureNotFoundError: There is no structure on the server with this UniProtID."
                    )
                # downloads the pdb file and saves it in the pdbs directory
                os.makedirs(parser.PDB_DIR, exist_ok=True)
                async for data in r.content.iter_chunked(1024):
                    async with aiofiles.open(save_location, "ba") as f:
                        await f.write(data)
            except KeyError as e:
                success = False

        return


def sync_fetch_list(parser, ids):
    # create a list of proteins to be processed
    proteins = [id for id in ids.split(",")]
    # create the output directory for the corresponding coloring mode if they do not exist
    output_dir = os.path.join(st._MAPS_PATH, parser.processing)
    parser.update_output_dir(output_dir)

    # initialize the structures dictionary of the parser and check wether some processing files do already exist
    parser.init_structures_dict(proteins)
    for protein in proteins:
        parser.update_existence(protein)

    for id in proteins:
        file_name = f"AF-{id}-F1-model_{parser.alphafold_ver}.pdb"  # Resulting file name which will be downloaded from the alphafold DB
        url = "https://alphafold.ebi.ac.uk/files/" + file_name  # Url to uccess = True
        save_location = parser.structures[id].pdb_file
        try:
            # try to fetch the structure from the given url
            r = requests.get(url, allow_redirects=True)  # opens url
            if r.status_code == 404:
                # If the file it not available, an exception will be raised
                raise KeyError(
                    "StructureNotFoundError: There is no structure on the server with this UniProtID."
                )
            # downloads the pdb file and saves it in the pdbs directory
            os.makedirs(parser.PDB_DIR, exist_ok=True)
            open(f"{save_location}", "wb").write(r.content)
        except KeyError as e:
            success = False
            return success


def main(parser, ids):
    _, time = util.asnyc_time_ex(fetch_list, parser, ids)
    print("Async", time)
    _, time = util.time_ex(sync_fetch_list, parser, ids)
    print("sync", time)

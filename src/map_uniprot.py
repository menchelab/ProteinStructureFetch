"""
Small script to map identifiers on UniProt IDs.

Implementation based on:

https://www.uniprot.org/help/id_mapping

"""

import json
import os
import re
import sys
import time
import zlib
from urllib.parse import parse_qs, urlencode, urlparse
from xml.etree import ElementTree

import requests
from requests.adapters import HTTPAdapter, Retry

POLLING_INTERVAL = 3
API_URL = "https://rest.uniprot.org"


retries = Retry(total=5, backoff_factor=0.25, status_forcelist=[500, 502, 503, 504])
session = requests.Session()
session.mount("https://", HTTPAdapter(max_retries=retries))


def check_response(response):
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        raise


def submit_id_mapping(
    ids: list[str],
    taxId: str = None,
    from_db: str = None,
    to_db: str = None,
):
    """! Submit the id mapping job to the UniProt ID mapping API.
    @param form_db   Define the db the ids come from.
    @param to_db   Define the db to which the ids should be mapped on.
    @param ids   List of ids to query.
    @param taxId Taxonomic ID from which the ids originate from.
    @return  The Job Id of the submitted job.
    """
    data = {"ids": ",".join(ids)}
    if taxId:
        data["taxId"] = taxId
    if from_db:
        data["from"] = from_db
    if to_db:
        data["to"] = to_db
    request = requests.post(
        f"{API_URL}/idmapping/run",
        data=data,
    )
    check_response(request)
    return request.json()["jobId"]


def get_next_link(headers):

    re_next_link = re.compile(r'<(.+)>; rel="next"')
    if "Link" in headers:
        match = re_next_link.match(headers["Link"])
        if match:
            return match.group(1)


def check_id_mapping_results_ready(job_id):
    while True:
        request = session.get(f"{API_URL}/idmapping/status/{job_id}")
        check_response(request)
        j = request.json()
        if "jobStatus" in j:
            if j["jobStatus"] == "RUNNING":
                print(f"Retrying in {POLLING_INTERVAL}s")
                time.sleep(POLLING_INTERVAL)
            else:
                raise Exception(j["jobStatus"])
        else:
            return bool(j["results"] or j["failedIds"])


def get_batch(batch_response, file_format, compressed):
    batch_url = get_next_link(batch_response.headers)
    while batch_url:
        batch_response = session.get(batch_url)
        batch_response.raise_for_status()
        yield decode_results(batch_response, file_format, compressed)
        batch_url = get_next_link(batch_response.headers)


def combine_batches(all_results, batch_results, file_format):
    if file_format == "json":
        for key in ("results", "failedIds"):
            if key in batch_results and batch_results[key]:
                all_results[key] += batch_results[key]
    elif file_format == "tsv":
        return all_results + batch_results[1:]
    else:
        return all_results + batch_results
    return all_results


def get_id_mapping_results_link(job_id):
    url = f"{API_URL}/idmapping/details/{job_id}"
    request = session.get(url)
    check_response(request)
    return request.json()["redirectURL"]


def decode_results(response, file_format, compressed):
    if compressed:
        decompressed = zlib.decompress(response.content, 16 + zlib.MAX_WBITS)
        if file_format == "json":
            j = json.loads(decompressed.decode("utf-8"))
            return j
        elif file_format == "tsv":
            return [line for line in decompressed.decode("utf-8").split("\n") if line]
        elif file_format == "xlsx":
            return [decompressed]
        elif file_format == "xml":
            return [decompressed.decode("utf-8")]
        else:
            return decompressed.decode("utf-8")
    elif file_format == "json":
        return response.json()
    elif file_format == "tsv":
        return [line for line in response.text.split("\n") if line]
    elif file_format == "xlsx":
        return [response.content]
    elif file_format == "xml":
        return [response.text]
    return response.text


def get_xml_namespace(element):
    m = re.match(r"\{(.*)\}", element.tag)
    return m.groups()[0] if m else ""


def merge_xml_results(xml_results):
    merged_root = ElementTree.fromstring(xml_results[0])
    for result in xml_results[1:]:
        root = ElementTree.fromstring(result)
        for child in root.findall("{http://uniprot.org/uniprot}entry"):
            merged_root.insert(-1, child)
    ElementTree.register_namespace("", get_xml_namespace(merged_root[0]))
    return ElementTree.tostring(merged_root, encoding="utf-8", xml_declaration=True)


def print_progress_batches(batch_index, size, total):
    n_fetched = min((batch_index + 1) * size, total)
    print(f"Fetched: {n_fetched} / {total}")


def get_id_mapping_results_search(url):
    parsed = urlparse(url)
    query = parse_qs(parsed.query)
    file_format = query["format"][0] if "format" in query else "json"
    if "size" in query:
        size = int(query["size"][0])
    else:
        size = 500
        query["size"] = size
    compressed = (
        query["compressed"][0].lower() == "true" if "compressed" in query else False
    )
    parsed = parsed._replace(query=urlencode(query, doseq=True))
    url = parsed.geturl()
    request = session.get(url)
    check_response(request)
    results = decode_results(request, file_format, compressed)
    total = int(request.headers["x-total-results"])
    print_progress_batches(0, size, total)
    for i, batch in enumerate(get_batch(request, file_format, compressed), 1):
        results = combine_batches(results, batch, file_format)
        print_progress_batches(i, size, total)
    if file_format == "xml":
        return merge_xml_results(results)
    return results


def get_id_mapping_results_stream(url):
    if "/stream/" not in url:
        url = url.replace("/results/", "/results/stream/")
    request = session.get(url)
    check_response(request)
    parsed = urlparse(url)
    query = parse_qs(parsed.query)
    file_format = query["format"][0] if "format" in query else "json"
    compressed = (
        query["compressed"][0].lower() == "true" if "compressed" in query else False
    )
    return decode_results(request, file_format, compressed)


def construct_nodes(results, nodes, nodes_map, nodes_f, secondary=False):
    """Will write nodes to new nodes file."""
    # print(results)
    res: dict
    lengths = {}
    with open(os.path.join("static", "csv", "scales_Cartoon.csv"), "r") as f:
        lines = f.readlines()
        ids = [line.split(",")[0] for line in lines]
    for res in results["results"]:
        f = res["from"]
        idx = nodes_map[f]
        uniprot = nodes["nodes"][idx].get("uniprot")
        if uniprot and len(uniprot) > 30:
            """Cap the number of possible structures to 30"""
            continue
        to = res.get("to")

        if isinstance(res["to"], dict):
            """For larger queries only one identifier is saved."""
            pa = [to.get("primaryAccession")]
            if secondary:
                """Will also extract secondary Accessions, for most of them there is no PDB. Default: its skipped"""
                sa = res["to"].get("secondaryAccessions")
                if sa:
                    pa += sa
        else:
            pa = [to]
        pa = [acc for acc in pa if acc in ids]
        if nodes["nodes"][idx].get("uniprot") is None:
            nodes["nodes"][idx]["uniprot"] = []

        nodes["nodes"][idx]["uniprot"] += pa

    with open(f"{nodes_f[:-5]}_with_uniprot.json", "w") as f:
        json.dump(nodes, f)

    return nodes


def main(ids, taxid=None, source_db=None, target_db=None):
    results = query_from_to(ids, taxid, source_db, target_db)
    return results


def query_from_to(
    ids: list[str], taxId: str = None, from_db: str = None, to_db: str = "UniProtKB"
):
    job_id = submit_id_mapping(
        from_db=from_db,
        to_db=to_db,
        ids=ids,
        taxId=taxId,
    )
    if check_id_mapping_results_ready(job_id):
        link = get_id_mapping_results_link(job_id)
        results = get_id_mapping_results_search(link)
        # Equivalently using the stream endpoint which is more demanding
        # on the API and so is less stable:
        # results = get_id_mapping_results_stream(link)
        print("Results are here!")
    return results


class Databases:
    gene_name = "Gene_Name"
    uniprot = "UniProtKB"
    uniprot_ac = "UniProtKB_AC-ID"
    gene_id = "GeneID"


if __name__ == "__main__":
    main(
        ["A0A0j3WCK1"],
        source_db=Databases.uniprot_ac,
        target_db=Databases.uniprot,
    )

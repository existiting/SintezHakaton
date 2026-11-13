import json
import re
from typing import Any
from urllib.parse import quote

import requests


def get_protein_structure(id: str, operation: str = "entry") -> Any:
    # ID — PDB ID ("4HHB"); для entity/assembly — "4HHB/1"; для chemcomp — код лиганда ("HEM");
    #      для search — произвольный текст ("hemoglobin").
    # OPERATION — что вернуть: search, entry, polymer_entity, nonpolymer_entity,
    #             assembly, chemcomp, fasta, pdb, cif.

    if operation == "search":  # полнотекстовый поиск структур
        query = {
            "query": {
                "type": "terminal",
                "service": "full_text",
                "parameters": {"value": id},
            },
            "return_type": "entry",
            "request_options": {"paginate": {"start": 0, "rows": 10}},
        }
        url = "https://search.rcsb.org/rcsbsearch/v2/query"
        r = requests.get(url, params={"json": json.dumps(query)}, timeout=30)
        if r.status_code == 204:  # ничего не найдено
            return {"total_count": 0, "result_set": []}
        r.raise_for_status()
        return r.json()

    if operation in ("pdb", "cif"):  # файл 3D-координат (простой текст!)
        url = f"https://files.rcsb.org/download/{id.upper()}.{operation}"
        r = requests.get(url, timeout=60)
    elif operation == "fasta":  # последовательности цепей
        url = f"https://www.rcsb.org/fasta/entry/{id.upper()}"
        r = requests.get(url, timeout=30)
    else:  # метаданные JSON (Data API)
        url = f"https://data.rcsb.org/rest/v1/core/{operation}/{id.upper()}"
        r = requests.get(url, timeout=15)

    if r.status_code == 404:  # структура/запись не найдена
        return {
            "error": "Not found",
            "message": "No such record or file. Check id/operation. "
            "Large structures have no legacy .pdb file — use 'cif'.",
            "url": url,
        }

    r.raise_for_status()
    if operation in ("pdb", "cif", "fasta"):
        return r.text  # координаты/FASTA — текст, не JSON
    return r.json()


PUBCHEM_PROPERTIES = {
    "MolecularFormula",
    "MolecularWeight",
    "CanonicalSMILES",
    "SMILES",
    "IsomericSMILES",
    "InChI",
    "InChIKey",
    "IUPACName",
    "Title",
    "XLogP",
    "ExactMass",
    "MonoisotopicMass",
    "TPSA",
    "Complexity",
    "Charge",
    "HBondDonorCount",
    "HBondAcceptorCount",
    "RotatableBondCount",
    "HeavyAtomCount",
}


def get_pubchem(
    domain: str,
    identifier_type: str,
    identifier: str,
    operation: str,
):
    base = "https://pubchem.ncbi.nlm.nih.gov/rest/pug"

    if operation.startswith("property/"):
        properties = operation.removeprefix("property/").split(",")

        invalid = set(properties) - PUBCHEM_PROPERTIES
        if invalid:
            return {
                "error": "Invalid properties",
                "invalid_properties": sorted(invalid),
                "available_properties": sorted(PUBCHEM_PROPERTIES),
            }

    url = (
        f"{base}/{quote(domain)}/"
        f"{quote(identifier_type)}/"
        f"{quote(identifier)}/"
        f"{quote(operation, safe='/,')}/JSON"
    )

    try:
        response = requests.get(url, timeout=20)

        if response.status_code == 404:
            return {"error": "Not found", "url": url}

        response.raise_for_status()
        return response.json()

    except requests.RequestException as exc:
        return {
            "error": "PubChem request failed",
            "message": str(exc),
            "url": url,
        }


ACCESSION = re.compile(
    r"[OPQ][0-9][A-Z0-9]{3}[0-9]|[A-NR-Z][0-9]([A-Z][A-Z0-9]{2}[0-9]){1,2}"
)


def get_uniprot(
    query: str,
    fields: str = "accession,id,protein_name,gene_names,organism_name,length",
    size: int = 5,
    format: str = "json",
) -> Any:
    # QUERY  — accession (P00533) или запрос: gene:EGFR AND organism_id:9606 AND reviewed:true
    # FIELDS — какие поля вернуть; "" = полный JSON записи (огромный, не надо)
    # SIZE   — сколько результатов, 1–500
    # FORMAT — json | tsv | fasta | list

    q = query.strip()
    if ACCESSION.fullmatch(q):  # одиночный accession → точный запрос
        q, size = f"accession:{q}", 1

    params = {"query": q, "format": format, "size": max(1, min(int(size), 500))}
    if fields:
        params["fields"] = fields

    r = requests.get(
        "https://rest.uniprot.org/uniprotkb/search", params=params, timeout=20
    )

    if r.status_code == 400:  # кривой синтаксис — пусть модель исправит
        return {"error": "Bad request", "message": r.json().get("messages"), "query": q}
    if r.status_code == 404:
        return {"error": "Not found", "query": q}
    r.raise_for_status()
    return r.json() if format == "json" else r.text

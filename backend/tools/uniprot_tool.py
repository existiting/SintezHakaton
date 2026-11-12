import requests
import re
from typing import Any

ACCESSION = re.compile(r"[OPQ][0-9][A-Z0-9]{3}[0-9]|[A-NR-Z][0-9]([A-Z][A-Z0-9]{2}[0-9]){1,2}")


def get_uniprot(query: str, fields: str = "accession,id,protein_name,gene_names,organism_name,length", size: int = 5, format: str = "json") -> Any: 
    # QUERY  — accession (P00533) или запрос: gene:EGFR AND organism_id:9606 AND reviewed:true
    # FIELDS — какие поля вернуть; "" = полный JSON записи (огромный, не надо)
    # SIZE   — сколько результатов, 1–500
    # FORMAT — json | tsv | fasta | list

    q = query.strip()
    if ACCESSION.fullmatch(q):                 # одиночный accession → точный запрос
        q, size = f"accession:{q}", 1

    params = {"query": q, "format": format, "size": max(1, min(int(size), 500))}
    if fields:
        params["fields"] = fields

    r = requests.get("https://rest.uniprot.org/uniprotkb/search", params=params, timeout=20)

    if r.status_code == 400:                   # кривой синтаксис — пусть модель исправит
        return {"error": "Bad request", "message": r.json().get("messages"), "query": q}
    if r.status_code == 404:
        return {"error": "Not found", "query": q}
    r.raise_for_status()
    return r.json() if format == "json" else r.text

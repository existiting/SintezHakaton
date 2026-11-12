from urllib.parse import quote
import requests

def get_pubchem(domain: str, input: str, operation: str, request: str):
# DOMAIN — по какому объекту запрос: compound (молекулы), substance (депонированные записи), assay (биоанализы).
# INPUT — по чему ищем: name, smiles, cid, formula, inchikey, listkey.
# OPERATION — что вернуть: cids, aids, properties, synonyms, xrefs, summary, targets, PNG…
# OUTPUT — формат: JSON, XML, CSV, SDF, TXT, PNG.
  
    url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/{quote(domain)}/{quote(input)}/{quote(request)}/{quote(operation)}/JSON"
    r = requests.get(url, timeout=15)

    if r.status_code == 404:          # вещество не найдено
        return {
            "error": "Not found",
            "message": "No such record or API endpoint. Check domain/input/request/operation.",
            "url": url,
        }


    r.raise_for_status()
    return r.json()



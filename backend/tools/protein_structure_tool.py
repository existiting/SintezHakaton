import json
import requests
from typing import Any

def get_protein_structure(id: str, operation: str = "entry") -> Any:
    # ID — PDB ID ("4HHB"); для entity/assembly — "4HHB/1"; для chemcomp — код лиганда ("HEM");
    #      для search — произвольный текст ("hemoglobin").
    # OPERATION — что вернуть: search, entry, polymer_entity, nonpolymer_entity,
    #             assembly, chemcomp, fasta, pdb, cif.

    if operation == "search":                      # полнотекстовый поиск структур
        query = {
            "query": {"type": "terminal", "service": "full_text",
                      "parameters": {"value": id}},
            "return_type": "entry",
            "request_options": {"paginate": {"start": 0, "rows": 10}},
        }
        url = "https://search.rcsb.org/rcsbsearch/v2/query"
        r = requests.get(url, params={"json": json.dumps(query)}, timeout=30)
        if r.status_code == 204:                   # ничего не найдено
            return {"total_count": 0, "result_set": []}
        r.raise_for_status()
        return r.json()

    if operation in ("pdb", "cif"):                # файл 3D-координат (простой текст!)
        url = f"https://files.rcsb.org/download/{id.upper()}.{operation}"
        r = requests.get(url, timeout=60)
    elif operation == "fasta":                     # последовательности цепей
        url = f"https://www.rcsb.org/fasta/entry/{id.upper()}"
        r = requests.get(url, timeout=30)
    else:                                          # метаданные JSON (Data API)
        url = f"https://data.rcsb.org/rest/v1/core/{operation}/{id.upper()}"
        r = requests.get(url, timeout=15)

    if r.status_code == 404:                       # структура/запись не найдена
        return {
            "error": "Not found",
            "message": "No such record or file. Check id/operation. "
                       "Large structures have no legacy .pdb file — use 'cif'.",
            "url": url,
        }

    r.raise_for_status()
    if operation in ("pdb", "cif", "fasta"):
        return r.text                              # координаты/FASTA — текст, не JSON
    return r.json()

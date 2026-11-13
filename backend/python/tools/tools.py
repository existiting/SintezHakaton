from tools import ftools

TOOLS_FUNTIONS_REGISTRY = {
    "get_pubchem": ftools.get_pubchem,
    "get_uniprot": ftools.get_uniprot,
    "get_protein_structure": ftools.get_protein_structure,
}

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_pubchem",
            "description": (
                "Query the PubChem PUG REST API for chemical information.\n\n"
                "IMPORTANT: Follow this exact workflow for compound names:\n"
                "1. Resolve the compound name to a CID using operation='cids'.\n"
                "2. After receiving the CID, retrieve ALL required compound "
                "properties in ONE single request.\n"
                "3. Do NOT make additional property requests if the first "
                "property request succeeds.\n"
                "4. Do NOT retry with different property combinations.\n\n"
                "IDENTIFIER ARGUMENTS:\n"
                "- identifier_type: format of the identifier (name, cid, smiles, inchikey).\n"
                "- identifier: actual identifier value (e.g. aspirin or 2244).\n"
                "- Never put the identifier value in identifier_type.\n\n"
                "SUPPORTED OPERATIONS:\n"
                "- cids: resolve a compound name to PubChem CID.\n"
                "- synonyms: retrieve compound synonyms.\n"
                "- property/PROPERTY1,PROPERTY2: retrieve compound properties.\n\n"
                "VALID PROPERTY NAMES:\n"
                "MolecularFormula, MolecularWeight, CanonicalSMILES, SMILES,\n"
                "IsomericSMILES, InChI, InChIKey, IUPACName, XLogP,\n"
                "ExactMass, MonoisotopicMass, TPSA, Complexity, Charge,\n"
                "HBondDonorCount, HBondAcceptorCount,\n"
                "RotatableBondCount, HeavyAtomCount.\n\n"
                "IMPORTANT PROPERTY RULES:\n"
                "- Separate property names with commas, without spaces.\n"
                "- Use XLogP, NOT XLogP3-AA.\n"
                "- Use HBondAcceptorCount, NOT HydrogenBondAcceptorCount.\n"
                "- Use HBondDonorCount, NOT HydrogenBondDonorCount.\n"
                "- Use TPSA, NOT TopologicalPolarSurfaceArea.\n"
                "- Do not invent property names.\n"
                "- Do not include synonyms in a property request.\n\n"
                "For a general compound information request, use this exact "
                "property set:\n"
                "property/MolecularFormula,MolecularWeight,CanonicalSMILES,"
                "IsomericSMILES,InChI,InChIKey,IUPACName,XLogP,TPSA,"
                "HBondDonorCount,HBondAcceptorCount,RotatableBondCount,"
                "ExactMass,HeavyAtomCount.\n\n"
                "If a property request fails, report the error. Do not "
                "repeatedly retry or generate alternative property lists."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "domain": {
                        "type": "string",
                        "enum": ["compound", "substance", "assay"],
                    },
                    "identifier_type": {
                        "type": "string",
                        "enum": [
                            "name",
                            "cid",
                            "smiles",
                            "inchikey",
                            "formula",
                            "listkey",
                            "sid",
                            "aid",
                        ],
                    },
                    "identifier": {
                        "type": "string",
                        "description": "Actual identifier value, e.g. aspirin or 2244.",
                    },
                    "operation": {
                        "type": "string",
                        "description": (
                            "Requested data: cids, synonyms, "
                            "property/..., assaysummary, summary, targets, etc."
                        ),
                    },
                },
                "required": ["domain", "identifier_type", "identifier", "operation"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_uniprot",
            "description": (
                "UniProtKB REST client (proteins). GET https://rest.uniprot.org/uniprotkb/search "
                "-> {'results': [...]}; empty list = nothing found.\n"
                "'query': a bare accession ('P00533') is auto-converted to accession:P00533; "
                "otherwise UniProt syntax 'field:value' with AND/OR/NOT, e.g. "
                "'gene:EGFR AND organism_id:9606 AND reviewed:true'. Free text ('EGFR human') "
                "works but is noisy — prefer field queries.\n"
                "Query fields: gene, protein_name, organism_id (9606=human, 10090=mouse), "
                "organism_name, reviewed:true (curated Swiss-Prot — prefer it), accession, "
                "length:[100 TO 500], keyword, cc_function.\n"
                "'fields' = comma-separated columns to return (default is compact). Add as needed: "
                "sequence, cc_function, cc_subcellular_location, cc_catalytic_activity, "
                "ft_binding, ft_act_site, go_p, xref_pdb, keyword. Empty '' = full entry (huge, avoid).\n"
                "Workflow: 1) query='gene:EGFR AND organism_id:9606 AND reviewed:true' -> "
                "results[0].primaryAccession='P00533'  2) query='P00533', "
                "fields='accession,sequence,cc_function' -> details.\n"
                "format: json (default), tsv, fasta (sequence as text), list (accessions only). "
                "size max 500. Summarize results, do not dump raw JSON."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": (
                            "Accession ('P00533') or query "
                            "('gene:TP53 AND organism_id:9606 AND reviewed:true'). "
                            "AND/OR/NOT, quotes for phrases, ranges: length:[100 TO *]."
                        ),
                    },
                    "fields": {
                        "type": "string",
                        "description": (
                            "Comma-separated return fields. Default: "
                            "accession,id,protein_name,gene_names,organism_name,length. "
                            "For sequence/function add: sequence,cc_function."
                        ),
                    },
                    "size": {
                        "type": "integer",
                        "description": "Number of results, default 5, max 500.",
                    },
                    "format": {
                        "type": "string",
                        "enum": ["json", "tsv", "fasta", "list"],
                        "description": "Response format. Non-json returns plain text.",
                    },
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_protein_structure",
            "description": (
                "Universal RCSB PDB client for protein 3D structures. Routes by 'operation':\n"
                "- search -> GET https://search.rcsb.org/rcsbsearch/v2/query (full-text) -> JSON\n"
                "- entry/polymer_entity/nonpolymer_entity/assembly/chemcomp -> "
                "GET https://data.rcsb.org/rest/v1/core/{operation}/{id} -> JSON metadata\n"
                "- pdb/cif -> GET https://files.rcsb.org/download/{id}.{operation} -> coordinate file as TEXT\n"
                "- fasta -> GET https://www.rcsb.org/fasta/entry/{id} -> TEXT\n"
                "Returns an error dict on 404.\n"
                "Standard workflow for a named protein:\n"
                "1) operation='search', id='hemoglobin' -> result_set[].identifier (PDB IDs)\n"
                "2) operation='entry', id='4HHB' -> title, method, resolution, entity/ligand ids\n"
                "3) operation='polymer_entity', id='4HHB/1' -> protein name, sequence, UniProt, organism\n"
                "4) operation='pdb' or 'cif', id='4HHB' -> actual 3D coordinates "
                "(ONLY when the user needs the structure file itself)\n"
                "Response shapes:\n"
                "- search -> total_count + result_set[] of {identifier, score}; top-10 by relevance; "
                "no hits -> total_count=0. Refine queries with keywords/organism, e.g. 'human insulin receptor'\n"
                "- entry -> struct.title; exptl[].method (X-RAY DIFFRACTION / ELECTRON MICROSCOPY / "
                "SOLUTION NMR); rcsb_entry_info.resolution_combined (Angstrom); "
                "rcsb_entry_container_identifiers.polymer_entity_ids / non_polymer_entity_ids (ligands); "
                "rcsb_primary_citation.title\n"
                "- polymer_entity -> rcsb_polymer_entity.pdbx_description (name); "
                "entity_poly.pdbx_seq_one_letter_code_can (sequence); "
                "rcsb_entity_source_organism[].scientific_name; "
                "rcsb_polymer_entity_container_identifiers.reference_sequence_identifiers[]"
                ".database_accession (UniProt)\n"
                "- chemcomp -> chem_comp.name / chem_comp.formula; rcsb_chem_comp_descriptor.SMILES\n"
                "- fasta -> '>4HHB_1|Chains A, C|name|organism' + sequence lines\n"
                "IMPORTANT: 'pdb'/'cif' return the FULL coordinate file (often 0.5-50 MB of text). "
                "NEVER print it into the chat: save it to a file or pass it to a parser. "
                "To answer questions about a structure use 'entry'/'polymer_entity' instead. "
                "Very large structures have no legacy .pdb file (404) -> use 'cif'. "
                "NMR entries contain multiple models. PDB IDs are case-insensitive."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "id": {
                        "type": "string",
                        "description": (
                            "Identifier VALUE, always a string. For entry/fasta/pdb/cif: "
                            "PDB ID, e.g. '4HHB'. For polymer_entity/nonpolymer_entity/assembly: "
                            "'PDBID/N', e.g. '4HHB/1' (take N from entry's entity_ids/assembly_ids). "
                            "For chemcomp: ligand code, e.g. 'HEM', 'ATP', 'STI'. "
                            "For search: free text, e.g. 'hemoglobin', 'spike protein SARS-CoV-2'."
                        ),
                    },
                    "operation": {
                        "type": "string",
                        "enum": [
                            "search",
                            "entry",
                            "polymer_entity",
                            "nonpolymer_entity",
                            "assembly",
                            "chemcomp",
                            "fasta",
                            "pdb",
                            "cif",
                        ],
                        "description": (
                            "What to return:\n"
                            "- 'search' — find PDB IDs by free text (use FIRST if only a protein name is known)\n"
                            "- 'entry' — structure summary: title, method, resolution, entities, ligands, citation\n"
                            "- 'polymer_entity' — one unique protein/DNA/RNA molecule: name, sequence, UniProt, organism\n"
                            "- 'nonpolymer_entity' — ligand/ion entity inside an entry\n"
                            "- 'assembly' — biological assembly info (e.g. tetramer vs single chain)\n"
                            "- 'chemcomp' — ligand dictionary record: name, formula, SMILES\n"
                            "- 'fasta' — sequences of all chains as FASTA text\n"
                            "- 'pdb' — 3D coordinates, legacy PDB format text (not available for huge structures)\n"
                            "- 'cif' — 3D coordinates, mmCIF format text (available for ALL structures)"
                        ),
                    },
                },
                "required": ["id", "operation"],
            },
        },
    },
]

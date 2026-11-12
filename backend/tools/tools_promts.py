TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_pubchem",
            "description": (
                "Universal PubChem PUG-REST client. Performs "
                "GET https://pubchem.ncbi.nlm.nih.gov/rest/pug/{domain}/{input}/{request}/{operation}/JSON "
                "and returns parsed JSON, or null if nothing found (404).\n"
                "ARGUMENT ROLES (important): 'request' is the identifier VALUE "
                "(e.g. 'aspirin', '2244'), 'operation' is WHAT to return (e.g. 'cids', 'property/...').\n"
                "Standard workflow for a named substance:\n"
                "1) domain='compound', input='name', request='aspirin', operation='cids' -> CID 2244\n"
                "2) domain='compound', input='cid', request='2244', "
                "operation='property/MolecularFormula,MolecularWeight,SMILES,XLogP,TPSA,HBondDonorCount,HBondAcceptorCount'\n"
                "3) domain='compound', input='cid', request='2244', operation='assaysummary' -> bioassay results\n"
                "4) domain='assay', input='aid', request='92967', operation='summary' -> details of one assay\n"
                "Response shapes:\n"
                "- cids/sids/aids -> IdentifierList.CID[] (or SID[]/AID[])\n"
                "- property/... -> PropertyTable.Properties[] (list of dicts)\n"
                "- synonyms, xrefs/... -> InformationList.Information[]\n"
                "- assaysummary -> Table.Columns.Column[] + Table.Row[].Cell[] "
                "(zip columns with cells; columns: AID, Activity Outcome, Activity Name, "
                "Activity Value [uM], Target GeneID, Target Accession, Assay Name, Assay Type)\n"
                "- assay summary -> AssaySummaries.AssaySummary[]\n"
                "Resolve names to CID first. Request all needed properties in ONE call "
                "(comma-separated). assaysummary can return thousands of rows: summarize, "
                "do not repeat raw data."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "domain": {
                        "type": "string",
                        "enum": ["compound", "substance", "assay"],
                        "description": (
                            "Record type. 'compound' = standardized molecules "
                            "(drugs, chemicals — use this by default); "
                            "'substance' = deposited records (SID); "
                            "'assay' = bioassay experiments (AID)."
                        )
                    },
                    "input": {
                        "type": "string",
                        "enum": ["name", "cid", "smiles", "inchikey", "formula",
                                 "listkey", "sid", "aid"],
                        "description": (
                            "Identifier type. With domain='compound': name, cid, smiles, "
                            "inchikey, formula, listkey. With domain='substance': sid, name. "
                            "With domain='assay': aid. Prefer 'name' or 'cid'. Avoid 'smiles' "
                            "if the string contains '/' — it breaks the URL."
                        )
                    },
                    "request": {
                        "type": "string",
                        "description": (
                            "The identifier VALUE, always a string: 'aspirin', '2244', "
                            "'C9H8O4', 'BSYNRYMUTXBXSQ-UHFFFAOYSA-N', '92967'. "
                            "Comma-separated lists are allowed for cid/sid/aid, e.g. '2244,2519'."
                        )
                    },
                    "operation": {
                        "type": "string",
                        "description": (
                            "What to return. Available operations:\n"
                            "- 'cids' / 'sids' / 'aids' — identifier lists "
                            "('aids' = assays a compound was tested in)\n"
                            "- 'synonyms' — names and synonyms\n"
                            "- 'property/<P1,P2,...>' — computed properties; names: "
                            "MolecularFormula, MolecularWeight, SMILES, ConnectivitySMILES, "
                            "InChI, InChIKey, IUPACName, XLogP, TPSA, HBondDonorCount, "
                            "HBondAcceptorCount, RotatableBondCount, HeavyAtomCount, Charge, "
                            "Complexity, ExactMass. Example: 'property/MolecularWeight,XLogP'\n"
                            "- 'assaysummary' — all bioassay results for a compound "
                            "(outcome Active/Inactive, IC50/EC50/Ki in uM, targets)\n"
                            "- 'summary' — assay summary (domain='assay')\n"
                            "- 'description' — assay description (domain='assay')\n"
                            "- 'targets' — assay protein/gene targets (domain='assay')\n"
                            "- 'xrefs/RegistryID' — external database IDs"
                        )
                    }
                },
                "required": ["domain", "input", "request", "operation"]
            }
        }
    },
    {
    "type": "function",
    "function": {
        "name": "get_chembl",
        "description": (
            "Universal ChEMBL REST client (EMBL-EBI; curated bioactivity / drug-discovery database). "
            "Performs GET https://www.ebi.ac.uk/chembl/api/data/{resource}.json and returns parsed JSON. "
            "Entities use ChEMBL IDs: molecule CHEMBL25 (aspirin), target CHEMBL231, assay CHEMBL1909156.\n"
            "ARGUMENT ROLES: 'resource' = which table; 'id' = ONE record (ChEMBL ID, or SMILES/InChIKey "
            "for similarity/substructure); 'filters' = semicolon-separated 'field__lookup=value' pairs; "
            "'search' = full-text query.\n"
            "FILTER LOOKUPS: exact (default, omit), iexact, contains, icontains, startswith, istartswith, "
            "endswith, iendswith, regex, iregex, gt, gte, lt, lte, range ('200,500'), in (comma list), "
            "isnull (true/false). Nested fields joined with '__': "
            "molecule_properties__full_mwt__lte=300, target_components__accession=P00533.\n"
            "Standard workflow for a named drug:\n"
            "1) resource='molecule', filters='pref_name__iexact=aspirin' -> molecules[0].molecule_chembl_id='CHEMBL25' "
            "(fallback: search='aspirin')\n"
            "2) resource='molecule', id='CHEMBL25' -> molecule_structures.canonical_smiles/standard_inchi_key, "
            "molecule_properties (full_mwt, alogp, psa, hba, hbd, rtb, num_ro5_violations), "
            "max_phase (4=approved), first_approval\n"
            "3) resource='mechanism', filters='molecule_chembl_id=CHEMBL25' -> mechanism_of_action, "
            "action_type, target_chembl_id (efficacy target)\n"
            "4) resource='activity', filters='molecule_chembl_id=CHEMBL25;target_chembl_id=<from step 3>;"
            "standard_type=IC50', order_by='-pchembl_value' -> potency measurements\n"
            "5) resource='target', id='<target_chembl_id>' -> pref_name, organism, "
            "target_components[].accession (UniProt)\n"
            "Other recipes: approved drugs: molecule filters='max_phase=4'; indications: drug_indication "
            "filters='molecule_chembl_id=CHEMBL25'; target by UniProt: target "
            "filters='target_components__accession=P00533'; binding assays for a target: assay "
            "filters='target_chembl_id=CHEMBL231;assay_type=B'.\n"
            "Response shapes: list endpoints -> {'page_meta': {total_count, limit, offset, next, previous}, "
            "'<resources>': [...]} with a plural key (molecules, activities, assays, targets, mechanisms, "
            "drug_indications...). Single record (with id) -> flat dict. Empty result = empty list, NOT an error.\n"
            "Data semantics: activity.standard_value is in standard_units (usually nM); "
            "pchembl_value = -log10(molar value): 6 = 1 uM, 9 = 1 nM, higher = more potent "
            "(use pchembl_value__gte=6 to keep potent hits). standard_type: IC50, EC50, Ki, Kd, Potency, CL... "
            "assay_type: B=binding, F=functional, A=ADMET, T=toxicity, P=physicochemical. "
            "max_phase: 4=approved, 3=phase 3, 2=phase 2, 1=phase 1.\n"
            "mechanism/drug/drug_indication/drug_warning aggregate data on the PARENT molecule — "
            "use the parent ChEMBL ID.\n"
            "Use 'only' to shrink responses; paginate with limit/offset (max limit 1000); keep __in lists "
            "short (<50 IDs). SMILES are percent-encoded automatically — pass them raw, '/' is fine. "
            "Summarize results, do not repeat raw data."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "resource": {
                    "type": "string",
                    "enum": ["molecule", "activity", "assay", "target", "target_component",
                             "document", "mechanism", "drug", "drug_indication", "drug_warning",
                             "molecule_form", "cell_line", "tissue", "organism",
                             "protein_classification", "atc_class", "biotherapeutic", "metabolism",
                             "binding_site", "compound_structural_alert", "target_relation",
                             "source", "chembl_id_lookup", "similarity", "substructure",
                             "image", "status"],
                    "description": (
                        "Which table to query. 'molecule' = compounds, structures, properties "
                        "(default choice); 'activity' = measured values (IC50/Ki/...) linking "
                        "molecule+assay+target; 'assay' = experiment protocols; 'target' = protein/"
                        "organism targets; 'document' = source papers; 'mechanism' = mechanism of "
                        "action of approved drugs; 'drug' / 'drug_indication' / 'drug_warning' = "
                        "approved-drug info, drug-disease links (MeSH/EFO), safety warnings; "
                        "'molecule_form' = parent/salt relations; 'cell_line', 'tissue', 'organism' = "
                        "biology; 'chembl_id_lookup' = resolve any CHEMBL ID to its entity type; "
                        "'similarity' / 'substructure' = chemical search (require 'id'); "
                        "'image' = molecule structure picture URL (requires 'id'); "
                        "'status' = DB version and API health."
                    )
                },
                "id": {
                    "type": "string",
                    "description": (
                        "Identifier of ONE record. Usually a ChEMBL ID: 'CHEMBL25' (molecule), "
                        "'CHEMBL231' (target), 'CHEMBL1909156' (assay). For 'similarity'/'substructure': "
                        "SMILES ('CC(=O)Oc1ccccc1C(=O)O'), InChIKey ('BSYNRYMUTXBXSQ-UHFFFAOYSA-N') "
                        "or a molecule ChEMBL ID. For 'image': molecule ChEMBL ID. "
                        "Leave empty to list/filter the whole resource."
                    )
                },
                "filters": {
                    "type": "string",
                    "description": (
                        "Semicolon-separated 'field=value' or 'field__lookup=value' pairs (AND logic). "
                        "Examples: 'pref_name__iexact=aspirin'; 'molecule_chembl_id=CHEMBL25;"
                        "standard_type=IC50;pchembl_value__gte=6'; 'target_components__accession=P00533;"
                        "organism=Homo sapiens'; 'molecule_chembl_id__in=CHEMBL25,CHEMBL941'. "
                        "Common fields — molecule: pref_name, molecule_chembl_id, max_phase, molecule_type, "
                        "molecule_properties__{full_mwt,alogp,psa,hba,hbd,num_ro5_violations}; "
                        "activity: molecule_chembl_id, target_chembl_id, assay_chembl_id, standard_type, "
                        "standard_value, pchembl_value, assay_type, target_organism; "
                        "assay: target_chembl_id, assay_type, description, assay_organism, document_chembl_id; "
                        "target: pref_name, target_type, organism, target_components__accession; "
                        "mechanism: molecule_chembl_id, target_chembl_id, mechanism_of_action, action_type."
                    )
                },
                "search": {
                    "type": "string",
                    "description": (
                        "Full-text search query, e.g. 'aspirin', 'EGFR inhibitor'. Works on molecule, "
                        "target, assay, activity, document, chembl_id_lookup. Use as fallback when "
                        "pref_name__iexact finds nothing. Do not combine with 'id'."
                    )
                },
                "order_by": {
                    "type": "string",
                    "description": (
                        "Sort field; prefix '-' for descending. E.g. '-pchembl_value' (most potent "
                        "first), 'pref_name', '-molecule_properties__full_mwt'."
                    )
                },
                "only": {
                    "type": "string",
                    "description": (
                        "Comma-separated fields to return, to keep responses small. E.g. "
                        "'molecule_chembl_id,pref_name,max_phase' or "
                        "'molecule_chembl_id,pchembl_value,standard_type,standard_value,target_chembl_id'."
                    )
                },
                "limit": {
                    "type": "integer",
                    "description": "Page size for list endpoints. Default 20, max 1000."
                },
                "offset": {
                    "type": "integer",
                    "description": (
                        "Skip N records (pagination). page_meta.total_count in the response "
                        "tells how many records match in total."
                    )
                },
                "similarity": {
                    "type": "integer",
                    "description": (
                        "Tanimoto similarity cutoff in percent for resource='similarity' only. "
                        "Range 70-100, default 70. Ignored for other resources."
                    )
                }
            },
            "required": ["resource"]
        }
    }
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
                    )
                },
                "fields": {
                    "type": "string",
                    "description": (
                        "Comma-separated return fields. Default: "
                        "accession,id,protein_name,gene_names,organism_name,length. "
                        "For sequence/function add: sequence,cc_function."
                    )
                },
                "size": {
                    "type": "integer",
                    "description": "Number of results, default 5, max 500."
                },
                "format": {
                    "type": "string",
                    "enum": ["json", "tsv", "fasta", "list"],
                    "description": "Response format. Non-json returns plain text."
                }
            },
            "required": ["query"]
        }
    }
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
                        )
                    },
                    "operation": {
                        "type": "string",
                        "enum": ["search", "entry", "polymer_entity", "nonpolymer_entity",
                                 "assembly", "chemcomp", "fasta", "pdb", "cif"],
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
                        )
                    }
                },
                "required": ["id", "operation"]
            }
        }
    }
]

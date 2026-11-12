from rdkit import Chem
from rdkit.Chem import Descriptors, QED, rdMolDescriptors

def analyze_molecule(smiles: str, operation: str = "descriptors", pattern: str = "") -> dict:
    # SMILES — молекула строкой ("CCO" — этанол, "c1ccccc1" — бензол). Названия не понимает!
    # OPERATION — что посчитать: descriptors, druglikeness, identifiers, match.
    # PATTERN — SMARTS-шаблон подструктуры, только для operation="match".

    mol = Chem.MolFromSmiles(smiles)
    if mol is None:                                # невалидный SMILES (или это было название)
        return {"error": "Invalid SMILES",
                "message": "RDKit could not parse the string. Resolve names via PubChem first.",
                "smiles": smiles}

    if operation == "identifiers":                 # канонический вид + InChI
        return {"canonical_smiles": Chem.MolToSmiles(mol),
                "inchi": Chem.MolToInchi(mol),
                "inchikey": Chem.MolToInchiKey(mol)}

    if operation == "match":                       # есть ли подструктура (SMARTS)
        patt = Chem.MolFromSmarts(pattern)
        if patt is None:
            return {"error": "Invalid SMARTS", "pattern": pattern}
        return {"match": mol.HasSubstructMatch(patt),
                "matches": len(mol.GetSubstructMatches(patt))}

    if operation == "druglikeness":                # «лекарственность»
        mw, logp = Descriptors.MolWt(mol), Descriptors.MolLogP(mol)
        hbd, hba = Descriptors.NumHDonors(mol), Descriptors.NumHAcceptors(mol)
        return {
            "qed": round(QED.qed(mol), 3),
            "lipinski_violations": sum([mw > 500, logp > 5, hbd > 5, hba > 10]),
            "lipinski": {"MW<=500": mw <= 500, "LogP<=5": logp <= 5,
                         "HBD<=5": hbd <= 5, "HBA<=10": hba <= 10},
            "veber_pass": Descriptors.TPSA(mol) <= 140 and Descriptors.NumRotatableBonds(mol) <= 10,
        }

    return {
        "formula": rdMolDescriptors.CalcMolFormula(mol),
        "molecular_weight": round(Descriptors.MolWt(mol), 3),        
        "exact_mass": round(Descriptors.ExactMolWt(mol), 5),
        "logp": round(Descriptors.MolLogP(mol), 3),
        "tpsa": round(Descriptors.TPSA(mol), 2),
        "h_bond_donors": Descriptors.NumHDonors(mol),
        "h_bond_acceptors": Descriptors.NumHAcceptors(mol),
        "rotatable_bonds": Descriptors.NumRotatableBonds(mol),
        "ring_count": Descriptors.RingCount(mol),
        "aromatic_rings": Descriptors.NumAromaticRings(mol),
        "heavy_atoms": Descriptors.HeavyAtomCount(mol),
        "fraction_csp3": round(Descriptors.FractionCSP3(mol), 3),
        "formal_charge": Chem.GetFormalCharge(mol),
    }

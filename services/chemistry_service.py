from __future__ import annotations

from dataclasses import dataclass
from typing import Any

try:
    from rdkit import Chem
    from rdkit.Chem import Descriptors, rdMolDescriptors
except ImportError:  # pragma: no cover - fallback behavior is tested instead.
    Chem = None
    Descriptors = None
    rdMolDescriptors = None

from utils.models import ChemistrySummary


FEATURE_SMARTS: dict[str, str] = {
    "heteroaromatic_ring_present": "[n,o,s;a;r]",
    "tertiary_amine_present": "[NX3;H0;!$(NC=O);!$(N=*);!$([N+])]",
    "secondary_amine_present": "[NX3;H1;!$(NC=O);!$(N=*);!$([N+])]",
    "primary_amine_present": "[NX3;H2;!$(NC=O);!$(N=*);!$([N+])]",
    "alcohol_present": "[OX2H][CX4;!$(C=O)]",
    "phenol_present": "[c][OX2H]",
    "sulfur_present": "[S,s]",
    "thiophene_like_present": "[s;r5]",
    "thioether_present": "[SX2]([#6])[#6]",
    "amide_present": "[CX3](=[OX1])[NX3]",
    "ester_present": "[CX3](=[OX1])[OX2][#6]",
    "halogen_present": "[F,Cl,Br,I]",
    "carboxylic_acid_present": "[CX3](=[OX1])[OX2H1]",
    "basic_nitrogen_present": "[N;H0,H1,H2;+0;!$(NC=O);!$(n)]",
    "aniline_like_present": "[NX3;!$(NC=O)]-[c]",
    "catechol_like_present": "c([OX2H])c([OX2H])",
}


@dataclass(slots=True)
class ChemistryService:
    def is_rdkit_available(self) -> bool:
        return all(component is not None for component in (Chem, Descriptors, rdMolDescriptors))

    def parse_smiles(self, smiles: str) -> Any:
        if not self.is_rdkit_available() or not smiles.strip():
            return None
        try:
            return Chem.MolFromSmiles(smiles)
        except Exception:
            return None

    def analyze_structure(self, smiles: str) -> dict[str, Any]:
        mol = self.parse_smiles(smiles)
        if mol is None:
            return {
                "smiles_valid": False,
                "rdkit_used": self.is_rdkit_available(),
                "mol": None,
            }

        structural_features = self.detect_structural_features(mol)
        return {
            "smiles_valid": True,
            "rdkit_used": True,
            "mol": mol,
            "molecular_formula": rdMolDescriptors.CalcMolFormula(mol) if rdMolDescriptors else "",
            "molecular_weight": round(float(Descriptors.MolWt(mol)), 2) if Descriptors else None,
            "tpsa": round(float(rdMolDescriptors.CalcTPSA(mol)), 2) if rdMolDescriptors else None,
            "logp_like_value": round(float(Descriptors.MolLogP(mol)), 2) if Descriptors else None,
            "structural_features": structural_features,
            "feature_flags": [
                key
                for key, value in structural_features.items()
                if isinstance(value, bool) and value
            ],
        }

    def detect_structural_features(self, mol: Any) -> dict[str, bool | int | float]:
        if not self.is_rdkit_available() or mol is None:
            return {}

        heavy_atoms = max(mol.GetNumHeavyAtoms(), 1)
        aromatic_atoms = sum(1 for atom in mol.GetAtoms() if atom.GetIsAromatic())
        features: dict[str, bool | int | float] = {
            "aromatic_ring_count": int(rdMolDescriptors.CalcNumAromaticRings(mol)),
            "ring_count": int(mol.GetRingInfo().NumRings()),
            "rotatable_bond_count": int(rdMolDescriptors.CalcNumRotatableBonds(mol)),
            "aromaticity_ratio": round(aromatic_atoms / heavy_atoms, 2),
            "heteroatom_count": int(rdMolDescriptors.CalcNumHeteroatoms(mol)),
            "hydrogen_bond_donor_count": int(rdMolDescriptors.CalcNumHBD(mol)),
            "hydrogen_bond_acceptor_count": int(rdMolDescriptors.CalcNumHBA(mol)),
            "tpsa": round(float(rdMolDescriptors.CalcTPSA(mol)), 2),
        }
        for feature_name, smarts in FEATURE_SMARTS.items():
            pattern = Chem.MolFromSmarts(smarts) if Chem is not None else None
            features[feature_name] = bool(pattern and mol.HasSubstructMatch(pattern))
        logp_value = round(float(Descriptors.MolLogP(mol)), 2) if Descriptors else None
        features["logp_like_hint"] = self._categorize_logp(logp_value)
        features["cationic_center_hint"] = bool(features.get("basic_nitrogen_present") or features.get("tertiary_amine_present") or features.get("secondary_amine_present"))
        features["anionic_center_hint"] = bool(features.get("carboxylic_acid_present"))
        features["zwitterion_like_hint"] = bool(features.get("cationic_center_hint") and features.get("anionic_center_hint"))
        return features

    def infer_soft_spots(self, features: dict[str, Any]) -> list[dict[str, str]]:
        hints: list[dict[str, str]] = []
        if features.get("tertiary_amine_present"):
            hints.append({
                "label": "Potential N-dealkylation soft spot",
                "rationale": "A tertiary amine often increases susceptibility to CYP-mediated N-dealkylation.",
                "confidence": "high",
                "pathway_type": "phase1",
            })
        if features.get("secondary_amine_present"):
            hints.append({
                "label": "Potential N-dealkylation or N-oxidation soft spot",
                "rationale": "Secondary amines can support oxidative N-dealkylation or N-oxidation.",
                "confidence": "medium",
                "pathway_type": "phase1",
            })
        if int(features.get("aromatic_ring_count", 0) or 0) > 0:
            hints.append({
                "label": "Potential aromatic hydroxylation soft spot",
                "rationale": "Aromatic rings create plausible sites for Phase I hydroxylation.",
                "confidence": "medium",
                "pathway_type": "phase1",
            })
        if features.get("heteroaromatic_ring_present"):
            hints.append({
                "label": "Potential heteroaromatic oxidation site",
                "rationale": "Heteroaromatic motifs can carry context-dependent oxidation liability.",
                "confidence": "medium",
                "pathway_type": "phase1",
            })
        if features.get("phenol_present") or features.get("alcohol_present"):
            hints.append({
                "label": "Potential glucuronidation or sulfation site",
                "rationale": "Free hydroxyl functionality often increases Phase II conjugation susceptibility.",
                "confidence": "high" if features.get("phenol_present") else "medium",
                "pathway_type": "phase2",
            })
        if features.get("carboxylic_acid_present"):
            hints.append({
                "label": "Possible acyl glucuronidation liability",
                "rationale": "Carboxylic acids can support acyl glucuronide formation in relevant systems.",
                "confidence": "medium",
                "pathway_type": "phase2",
            })
        if features.get("sulfur_present") or features.get("thioether_present"):
            hints.append({
                "label": "Potential sulfur oxidation soft spot",
                "rationale": "Sulfur-containing motifs may undergo oxidation or sulfoxidation.",
                "confidence": "medium",
                "pathway_type": "phase1",
            })
        if features.get("thiophene_like_present"):
            hints.append({
                "label": "Thiophene-like oxidation and reactive-risk soft spot",
                "rationale": "Thiophene-like aromatic sulfur can carry oxidative and reactive-metabolite concern.",
                "confidence": "high",
                "pathway_type": "reactive_risk",
            })
        if features.get("ester_present"):
            hints.append({
                "label": "Potential hydrolysis soft spot",
                "rationale": "Esters often increase susceptibility to hydrolysis in plasma or tissue systems.",
                "confidence": "high",
                "pathway_type": "phase1",
            })
        if features.get("amide_present"):
            hints.append({
                "label": "Possible amidase susceptibility",
                "rationale": "Amides are usually more stable than esters, but amidase turnover can still matter in some scaffolds.",
                "confidence": "low",
                "pathway_type": "phase1",
            })
        return hints

    def infer_phase1_liabilities(self, features: dict[str, Any]) -> list[str]:
        liabilities: list[str] = []
        if int(features.get("aromatic_ring_count", 0) or 0) > 0:
            liabilities.append("Aromatic hydroxylation is plausible due to aromatic ring features.")
        if features.get("tertiary_amine_present"):
            liabilities.append("CYP-mediated N-dealkylation is likely because a tertiary amine is present.")
        if features.get("secondary_amine_present"):
            liabilities.append("N-dealkylation or N-oxidation is possible because a secondary amine is present.")
        if features.get("heteroaromatic_ring_present"):
            liabilities.append("Heteroaromatic oxidation is plausible depending on local electronic context.")
        if features.get("sulfur_present") or features.get("thioether_present"):
            liabilities.append("Sulfur oxidation or sulfoxidation is possible for sulfur-containing motifs.")
        if features.get("ester_present"):
            liabilities.append("Hydrolysis should be considered because an ester functionality is present.")
        if features.get("amide_present"):
            liabilities.append("Amide hydrolysis is less likely than ester hydrolysis but can still be considered as a lower-priority pathway.")
        return liabilities

    def infer_phase2_liabilities(self, features: dict[str, Any]) -> list[str]:
        liabilities: list[str] = []
        if features.get("phenol_present"):
            liabilities.append("Glucuronidation is likely and sulfation is plausible because a phenolic hydroxyl is present.")
        elif features.get("alcohol_present"):
            liabilities.append("Glucuronidation is plausible because an alcohol functionality is present.")
        if features.get("carboxylic_acid_present"):
            liabilities.append("Acyl glucuronidation should be considered because a carboxylic acid is present.")
        if any(features.get(flag) for flag in ("phenol_present", "alcohol_present", "carboxylic_acid_present")):
            liabilities.append("Phase II conjugation potential is increased by exposed polar functionality.")
        return liabilities

    def infer_reactive_metabolite_risks(self, features: dict[str, Any]) -> list[str]:
        risks: list[str] = []
        if features.get("aniline_like_present"):
            risks.append("Possible reactive metabolite risk due to aniline-like motif.")
        if features.get("catechol_like_present"):
            risks.append("Catechol-like motif may support quinone-type reactive metabolite awareness.")
        if features.get("thiophene_like_present"):
            risks.append("Possible reactive metabolite risk due to thiophene-like sulfur-containing aromatic motif.")
        if features.get("sulfur_present") and not features.get("thiophene_like_present"):
            risks.append("Sulfur oxidation could warrant reactive intermediate awareness depending on the surrounding scaffold.")
        if int(features.get("aromatic_ring_count", 0) or 0) >= 2 and features.get("heteroaromatic_ring_present"):
            risks.append("Multiple aromatic oxidation liabilities may warrant reactive metabolite awareness in electron-rich regions.")
        return risks

    def infer_cyp_preference_hints(self, features: dict[str, Any]) -> list[dict[str, str]]:
        hints: list[dict[str, str]] = []
        if features.get("tertiary_amine_present"):
            hints.append({
                "label": "Oxidative amine liability worth checking early",
                "rationale": "A tertiary amine can support oxidative metabolism and N-dealkylation in microsomes and hepatocytes.",
                "confidence": "medium",
                "assay_implication": "Prioritize microsomes, hepatocytes, and CYP phenotyping.",
                "optional_isoform_hint": "CYP3A-mediated oxidation may be worth checking first in vitro.",
            })
        if features.get("secondary_amine_present"):
            hints.append({
                "label": "Broad CYP oxidation screen may be informative",
                "rationale": "Secondary amines can support N-dealkylation or N-oxidation without implying isoform certainty.",
                "confidence": "medium",
                "assay_implication": "Use microsomes plus hepatocytes before making stronger CYP assumptions.",
                "optional_isoform_hint": "Broad CYP screening is more appropriate than isoform certainty.",
            })
        if int(features.get("aromatic_ring_count", 0) or 0) > 0:
            hints.append({
                "label": "Aromatic oxidation deserves priority coverage",
                "rationale": "Aromatic ring features make oxidative metabolism worth checking in microsomes and hepatocytes.",
                "confidence": "medium",
                "assay_implication": "Include oxidative coverage with microsomes or hepatocytes and HRMS.",
                "optional_isoform_hint": "Multiple lipophilic oxidation liabilities suggest broad CYP screening rather than isoform certainty.",
            })
        if features.get("heteroaromatic_ring_present") or features.get("thiophene_like_present"):
            hints.append({
                "label": "Heteroaromatic oxidation should be explored conservatively",
                "rationale": "Heteroaromatic or thiophene-like motifs can increase context-dependent oxidation and reactive-risk attention.",
                "confidence": "medium",
                "assay_implication": "Use hepatocytes or microsomes with reactive-metabolite awareness.",
                "optional_isoform_hint": "Oxidative metabolism is worth checking first in vitro without claiming isoform specificity.",
            })
        if any(features.get(flag) for flag in ("phenol_present", "alcohol_present", "carboxylic_acid_present")):
            hints.append({
                "label": "Conjugation may compete with oxidative pathways",
                "rationale": "Exposed polar functionality can shift metabolism toward Phase II conjugation rather than exclusive CYP turnover.",
                "confidence": "medium",
                "assay_implication": "Pair oxidative assays with S9 or hepatocyte conjugation-aware incubations.",
                "optional_isoform_hint": "Conjugation competition may reduce the value of over-interpreting CYP preference.",
            })
        if features.get("ester_present"):
            hints.append({
                "label": "Hydrolysis may compete with CYP oxidation",
                "rationale": "Ester hydrolysis can reduce the apparent importance of oxidative pathways in early screens.",
                "confidence": "high",
                "assay_implication": "Check plasma stability early before over-weighting CYP-driven routes.",
                "optional_isoform_hint": "Hydrolysis competition argues for cautious CYP interpretation.",
            })
        return hints

    def infer_transporter_hints(self, features: dict[str, Any]) -> list[dict[str, str]]:
        hints: list[dict[str, str]] = []
        polar_features = (
            float(features.get("tpsa", 0.0) or 0.0) >= 90.0
            or int(features.get("heteroatom_count", 0) or 0) >= 5
            or int(features.get("hydrogen_bond_donor_count", 0) or 0) >= 2
        )
        if features.get("cationic_center_hint") or features.get("tertiary_amine_present"):
            hints.append({
                "label": "Basic or cationic transporter-awareness hint",
                "rationale": "Basic nitrogen features can justify uptake or efflux awareness if passive permeability is not dominant.",
                "confidence": "medium",
                "assay_implication": "P-gp or broader transporter-aware permeability follow-up may be worth considering if cell permeability is limited.",
                "caution_note": "This is not evidence of a specific transporter substrate assignment.",
            })
        if features.get("anionic_center_hint"):
            hints.append({
                "label": "Anionic uptake-transporter awareness hint",
                "rationale": "Acidic functionality can justify keeping hepatic or renal transporter contribution in mind if metabolism alone does not explain clearance.",
                "confidence": "medium",
                "assay_implication": "Transporter-aware follow-up may be useful if hepatocyte or in vivo clearance appears higher than microsomal turnover alone would suggest.",
                "caution_note": "This should be treated as a conservative follow-up flag rather than a transporter prediction.",
            })
        if polar_features:
            hints.append({
                "label": "Polar-feature transporter contribution awareness",
                "rationale": "Higher polarity can reduce passive permeability and make transporter contribution relatively more important.",
                "confidence": "low",
                "assay_implication": "Interpret permeability and clearance together rather than assuming passive diffusion dominates.",
                "caution_note": "Transporter relevance should be confirmed experimentally if it becomes decision-critical.",
            })
        if (
            features.get("cationic_center_hint")
            and int(features.get("aromatic_ring_count", 0) or 0) > 0
            and features.get("logp_like_hint") in {"moderately_lipophilic", "lipophilic"}
        ):
            hints.append({
                "label": "Efflux-awareness hint for lipophilic basic chemistry",
                "rationale": "Aromatic and basic features can justify efflux-awareness in cell-based disposition assays.",
                "confidence": "medium",
                "assay_implication": "MDCK-MDR1 or related efflux-aware permeability follow-up may be worth checking.",
                "caution_note": "This does not imply confirmed efflux liability.",
            })
        return self._deduplicate_dicts(hints, key_fields=("label",))

    def infer_permeability_hints(self, features: dict[str, Any]) -> list[dict[str, str]]:
        hints: list[dict[str, str]] = []
        tpsa = float(features.get("tpsa", 0.0) or 0.0)
        hbd = int(features.get("hydrogen_bond_donor_count", 0) or 0)
        hba = int(features.get("hydrogen_bond_acceptor_count", 0) or 0)
        logp_hint = str(features.get("logp_like_hint", "unknown"))

        if tpsa >= 90.0 or hbd >= 2 or hba >= 6 or features.get("anionic_center_hint"):
            hints.append({
                "label": "Passive permeability may be limited",
                "rationale": "Higher polarity or acidic functionality can reduce passive membrane diffusion and shift interpretation toward permeability-aware assays.",
                "confidence": "medium",
                "assay_implication": "Add Caco-2 or equivalent permeability follow-up and interpret any transporter effect conservatively.",
            })
        if (
            features.get("cationic_center_hint")
            and int(features.get("aromatic_ring_count", 0) or 0) > 0
            and logp_hint in {"moderately_lipophilic", "lipophilic"}
        ):
            hints.append({
                "label": "Permeability may be plausible but efflux should still be considered",
                "rationale": "Lipophilic aromatic/basic chemistry can support membrane permeation, but apparent permeability may still be shaped by efflux.",
                "confidence": "medium",
                "assay_implication": "Use transporter-aware permeability interpretation rather than relying on a single passive-permeability readout.",
            })
        if features.get("ester_present"):
            hints.append({
                "label": "Hydrolysis can complicate permeability interpretation",
                "rationale": "Ester-containing chemistry can blur whether observed exposure changes arise from permeability, hydrolysis, or both.",
                "confidence": "medium",
                "assay_implication": "Compare permeability-oriented assays with plasma stability or hepatocyte follow-up.",
            })
        if int(features.get("ring_count", 0) or 0) >= 3 and logp_hint in {"moderately_lipophilic", "lipophilic"}:
            hints.append({
                "label": "Solubility-permeability balance may need attention",
                "rationale": "More rigid lipophilic ring systems can justify checking whether apparent permeability is limited by solubility or nonspecific binding effects.",
                "confidence": "low",
                "assay_implication": "Check solubility-permeability balance before over-interpreting low exposure as purely metabolic.",
            })
        return self._deduplicate_dicts(hints, key_fields=("label",))

    def infer_clearance_route_hints(self, features: dict[str, Any], species: str) -> list[dict[str, str]]:
        species_key = (species or "").strip().lower()
        hints: list[dict[str, str]] = []
        oxidation = any(features.get(flag) for flag in ("tertiary_amine_present", "secondary_amine_present", "aromatic_ring_count", "heteroaromatic_ring_present", "sulfur_present"))
        conjugation = any(features.get(flag) for flag in ("phenol_present", "alcohol_present", "carboxylic_acid_present"))
        transporter_awareness = any(features.get(flag) for flag in ("anionic_center_hint", "cationic_center_hint")) or float(features.get("tpsa", 0.0) or 0.0) >= 90.0

        if oxidation:
            hints.append({
                "route_label": "oxidative_metabolic_clearance",
                "priority": "high",
                "rationale": "Oxidation-prone substructures make metabolic clearance worth prioritizing early in microsomes and hepatocytes.",
                "supporting_features": "oxidation liabilities and basic/aromatic features",
                "species_context_note": self._species_context_note(species_key, "oxidation"),
            })
        if conjugation:
            hints.append({
                "route_label": "conjugative_mixed_clearance",
                "priority": "medium",
                "rationale": "Polar conjugation-prone functionality suggests mixed oxidative and conjugative clearance routes may need empirical clarification.",
                "supporting_features": "phenol/alcohol/acid features",
                "species_context_note": self._species_context_note(species_key, "conjugation"),
            })
        if features.get("ester_present"):
            hints.append({
                "route_label": "hydrolytic_clearance_component",
                "priority": "high",
                "rationale": "Ester chemistry can add a hydrolytic clearance component that competes with oxidative turnover.",
                "supporting_features": "ester_present",
                "species_context_note": self._species_context_note(species_key, "hydrolysis"),
            })
        if transporter_awareness:
            hints.append({
                "route_label": "renal_or_transporter_contribution_awareness",
                "priority": "medium",
                "rationale": "Polar or ionizable features justify keeping transporter or renal contribution in mind if clearance is not fully explained by metabolism.",
                "supporting_features": "cationic/anionic or high-polarity disposition cues",
                "species_context_note": "Human-relevant uptake or efflux follow-up may matter." if species_key == "human" else "Transporter contribution should be interpreted conservatively until empirical data are available.",
            })
        if conjugation and features.get("anionic_center_hint"):
            hints.append({
                "route_label": "biliary_excretion_awareness",
                "priority": "medium",
                "rationale": "Acidic or conjugation-prone chemistry can justify checking whether biliary versus renal contribution needs clarification.",
                "supporting_features": "carboxylic acid and conjugation-prone polarity",
                "species_context_note": "Rat bile, urine, and feces collection can be especially informative." if species_key == "rat" else "Route balance should be verified in species-relevant systems.",
            })
        return hints

    def infer_hotspot_evidence_tags(self, features: dict[str, Any], focus: str) -> list[str]:
        tags: list[str] = []
        if features.get("tertiary_amine_present") or features.get("secondary_amine_present"):
            tags.extend(["oxidation", "n_dealkylation", "cyp_phenotyping", "microsome", "hepatocyte"])
        if int(features.get("aromatic_ring_count", 0) or 0) > 0:
            tags.extend(["oxidation", "aromatic_hydroxylation", "microsome", "hepatocyte"])
        if any(features.get(flag) for flag in ("phenol_present", "alcohol_present", "carboxylic_acid_present")):
            tags.extend(["glucuronidation", "s9", "hepatocyte"])
            if features.get("phenol_present"):
                tags.append("sulfation")
        if any(features.get(flag) for flag in ("sulfur_present", "thiophene_like_present", "thioether_present")):
            tags.extend(["oxidation", "reactive_metabolite", "hepatocyte", "lc_ms"])
        if features.get("ester_present"):
            tags.extend(["hydrolysis", "plasma_stability"])
        if any(features.get(flag) for flag in ("cationic_center_hint", "anionic_center_hint")):
            tags.extend(["transporter_awareness", "efflux_awareness" if features.get("cationic_center_hint") else "transporter_awareness"])
        if float(features.get("tpsa", 0.0) or 0.0) >= 90.0:
            tags.append("permeability")
        if (focus or "").strip().lower() == "metid":
            tags.extend(["metabolite_profiling", "lc_ms"])
        return self._deduplicate(tags)

    def build_hotspot_summary(self, features: dict[str, Any], chemistry_summary: dict[str, Any]) -> list[dict[str, Any]]:
        hotspots: list[dict[str, Any]] = []
        if features.get("tertiary_amine_present") or features.get("secondary_amine_present"):
            hotspots.append({
                "hotspot_label": "Tertiary or secondary amine hotspot",
                "hotspot_type": "oxidative_amine_hotspot",
                "feature_basis": "tertiary_amine_present" if features.get("tertiary_amine_present") else "secondary_amine_present",
                "rationale": "Amine functionality supports oxidative N-dealkylation or related CYP-mediated follow-up.",
                "confidence": "high" if features.get("tertiary_amine_present") else "medium",
                "linked_pathways": ["N-dealkylation", "Oxidative metabolism"],
                "linked_assays": ["Liver microsomes", "Hepatocytes", "CYP phenotyping"],
                "linked_evidence_tags": ["oxidation", "n_dealkylation", "microsome", "hepatocyte", "cyp_phenotyping"],
            })
        if int(features.get("aromatic_ring_count", 0) or 0) > 0:
            hotspots.append({
                "hotspot_label": "Aromatic oxidation hotspot",
                "hotspot_type": "aromatic_oxidation_hotspot",
                "feature_basis": "aromatic_ring_count",
                "rationale": "Aromatic ring features justify aromatic hydroxylation and broader oxidative metabolism awareness.",
                "confidence": "medium",
                "linked_pathways": ["Oxidative metabolism including aromatic hydroxylation"],
                "linked_assays": ["Liver microsomes", "Hepatocytes", "High-resolution MS metabolite profiling"],
                "linked_evidence_tags": ["oxidation", "aromatic_hydroxylation", "microsome", "hepatocyte", "lc_ms", "metabolite_profiling"],
            })
        if features.get("phenol_present") or features.get("alcohol_present") or features.get("carboxylic_acid_present"):
            hotspots.append({
                "hotspot_label": "Phenolic or polar conjugation hotspot",
                "hotspot_type": "conjugation_hotspot",
                "feature_basis": "phenol_present" if features.get("phenol_present") else "alcohol_or_acid_present",
                "rationale": "Polar exposed functionality makes conjugation and mixed clearance pathways worth checking.",
                "confidence": "high" if features.get("phenol_present") else "medium",
                "linked_pathways": ["Conjugation including glucuronidation"],
                "linked_assays": ["S9 or conjugation-aware incubation", "Hepatocytes"],
                "linked_evidence_tags": ["glucuronidation", "sulfation", "s9", "hepatocyte"],
            })
        if any(features.get(flag) for flag in ("sulfur_present", "thiophene_like_present", "thioether_present")):
            hotspots.append({
                "hotspot_label": "Sulfur oxidation or reactive hotspot",
                "hotspot_type": "sulfur_reactive_hotspot",
                "feature_basis": "thiophene_like_present" if features.get("thiophene_like_present") else "sulfur_present",
                "rationale": "Sulfur-linked motifs justify oxidation and reactive-metabolite awareness follow-up.",
                "confidence": "high" if features.get("thiophene_like_present") else "medium",
                "linked_pathways": ["Sulfur oxidation and reactive-metabolite awareness"],
                "linked_assays": ["Hepatocytes", "GSH trapping consideration", "High-resolution MS metabolite profiling"],
                "linked_evidence_tags": ["oxidation", "reactive_metabolite", "hepatocyte", "lc_ms"],
            })
        if features.get("ester_present"):
            hotspots.append({
                "hotspot_label": "Ester hydrolysis hotspot",
                "hotspot_type": "hydrolysis_hotspot",
                "feature_basis": "ester_present",
                "rationale": "Ester functionality creates a plausible hydrolytic liability that can compete with metabolism-driven exposure changes.",
                "confidence": "high",
                "linked_pathways": ["Hydrolysis"],
                "linked_assays": ["Plasma stability", "Hepatocyte clearance comparison"],
                "linked_evidence_tags": ["hydrolysis", "plasma_stability", "hepatocyte"],
            })
        if not hotspots and chemistry_summary.get("feature_flags"):
            hotspots.append({
                "hotspot_label": "General chemistry hotspot",
                "hotspot_type": "general_hotspot",
                "feature_basis": "feature_flags",
                "rationale": "Detected structural features support broad metabolism and disposition follow-up even without a dominant hotspot.",
                "confidence": "low",
                "linked_pathways": ["Broad metabolism screen"],
                "linked_assays": ["Hepatocytes", "Liver microsomes"],
                "linked_evidence_tags": self.infer_hotspot_evidence_tags(features, "MetID"),
            })
        return hotspots

    def map_hotspots_to_assays(self, hotspots: list[dict[str, Any]], focus: str, species: str) -> list[dict[str, Any]]:
        species_label = self.infer_species_chemistry_interpretation({}, species).get("species_label", "Unknown")
        links: list[dict[str, Any]] = []
        for hotspot in hotspots:
            links.append({
                "hotspot_label": hotspot.get("hotspot_label", "Unspecified hotspot"),
                "assays": list(hotspot.get("linked_assays", [])),
                "focus": focus or "MetID",
                "species": species_label,
                "why_linked": hotspot.get("rationale", "Linked by heuristic chemistry support."),
            })
        return links

    def compute_chemistry_confidence(self, features: dict[str, Any], hotspot: dict[str, Any]) -> float:
        hotspot_type = str(hotspot.get("hotspot_type", "general_hotspot"))
        score = 0.0
        if not features:
            confidence_text = str(hotspot.get("confidence", "low"))
            score += {"high": 8.0, "medium": 5.5, "low": 2.5}.get(confidence_text, 2.5)
        if hotspot_type == "oxidative_amine_hotspot":
            if features.get("tertiary_amine_present"):
                score += 8.5
            elif features.get("secondary_amine_present"):
                score += 6.5
            if features.get("basic_nitrogen_present"):
                score += 1.0
        elif hotspot_type == "aromatic_oxidation_hotspot":
            aromatic_count = int(features.get("aromatic_ring_count", 0) or 0)
            if aromatic_count > 0:
                score += 6.0
            if features.get("heteroaromatic_ring_present"):
                score += 1.0
        elif hotspot_type == "conjugation_hotspot":
            if features.get("phenol_present"):
                score += 7.0
            elif features.get("alcohol_present") or features.get("carboxylic_acid_present"):
                score += 5.5
        elif hotspot_type == "sulfur_reactive_hotspot":
            if features.get("thiophene_like_present"):
                score += 7.5
            elif features.get("sulfur_present") or features.get("thioether_present"):
                score += 5.5
        elif hotspot_type == "hydrolysis_hotspot":
            if features.get("ester_present"):
                score += 8.0
        elif hotspot_type == "general_hotspot":
            score += 3.0 if features else 1.0

        linked_pathways = hotspot.get("linked_pathways", []) or []
        linked_assays = hotspot.get("linked_assays", []) or []
        if linked_pathways:
            score += 0.5
        if linked_assays:
            score += 0.5
        return round(min(score, 10.0), 2)

    @staticmethod
    def classify_chemistry_confidence(score: float) -> str:
        if score >= 7.0:
            return "high"
        if score >= 4.0:
            return "medium"
        return "low"

    def summarize_chemistry_confidence(self, hotspots: list[dict[str, Any]]) -> dict[str, Any]:
        if not hotspots:
            return {
                "summary": "No SMILES-backed hotspot chemistry confidence could be generated.",
                "high": 0,
                "medium": 0,
                "low": 0,
            }
        counts = {"high": 0, "medium": 0, "low": 0}
        for hotspot in hotspots:
            level = str(hotspot.get("chemistry_confidence", "low"))
            if level in counts:
                counts[level] += 1
        return {
            "summary": (
                f"Chemistry confidence across hotspots: high={counts['high']}, "
                f"medium={counts['medium']}, low={counts['low']}."
            ),
            **counts,
        }

    @staticmethod
    def _combine_confidence_level(score: float) -> str:
        if score >= 7.0:
            return "high"
        if score >= 4.5:
            return "medium"
        return "exploratory"

    def calibrate_hotspot_confidence(
        self,
        hotspot_priorities: list[dict[str, Any]],
        linked_evidence: dict[str, Any],
        species: str,
        focus: str,
    ) -> list[dict[str, Any]]:
        calibrated: list[dict[str, Any]] = []
        for hotspot in hotspot_priorities:
            label = str(hotspot.get("hotspot_label", "Unspecified hotspot"))
            evidence = linked_evidence.get(label, {})
            chemistry_level = str(hotspot.get("chemistry_confidence", "low"))
            evidence_level = str(hotspot.get("evidence_confidence", hotspot.get("evidence_support_level", "low")))
            species_level = str(evidence.get("species_alignment_confidence", "low"))
            chemistry_score = {"high": 8.0, "medium": 5.5, "low": 2.5}.get(chemistry_level, 2.5)
            evidence_score = {"high": 8.0, "medium": 5.0, "low": 2.0}.get(evidence_level, 2.0)
            species_score = {"high": 7.0, "medium": 4.5, "low": 2.0}.get(species_level, 2.0)
            combined = (chemistry_score * 0.45) + (evidence_score * 0.4) + (species_score * 0.15)
            overall = self._combine_confidence_level(combined)
            enriched = dict(hotspot)
            enriched["overall_confidence"] = overall
            enriched["confidence_rationale"] = (
                f"{label} is {overall}-confidence because chemistry support is {chemistry_level}, "
                f"literature support is {evidence_level}, and {species}/{focus} alignment is {species_level}."
            )
            calibrated.append(enriched)
        return calibrated

    def calibrate_assay_confidence(
        self,
        assay_priorities: list[dict[str, Any]],
        assay_support_links: dict[str, Any],
        species: str,
        focus: str,
    ) -> list[dict[str, Any]]:
        calibrated: list[dict[str, Any]] = []
        for assay in assay_priorities:
            assay_name = str(assay.get("assay_name", "Unspecified assay"))
            support = assay_support_links.get(assay_name, {})
            support_level = str(support.get("recommendation_confidence", assay.get("support_strength", "low")))
            priority_level = str(assay.get("priority", "medium"))
            hotspot_count = len(assay.get("supporting_hotspots", []))
            priority_score = {"high": 7.5, "medium": 5.0, "low": 3.0}.get(priority_level, 4.0)
            support_score = {"high": 8.0, "medium": 5.0, "low": 2.0, "exploratory": 2.0}.get(support_level, 2.0)
            hotspot_score = min(float(hotspot_count) * 1.5, 3.0)
            combined = (priority_score * 0.35) + (support_score * 0.45) + (hotspot_score * 0.20)
            recommendation_confidence = self._combine_confidence_level(combined)
            enriched = dict(assay)
            enriched["recommendation_confidence"] = recommendation_confidence
            enriched["confidence_rationale"] = (
                f"{assay_name} is {recommendation_confidence} because structural support is "
                f"{'strong' if hotspot_count >= 2 else 'present' if hotspot_count == 1 else 'limited'}, "
                f"literature support is {support_level}, and the current {species}/{focus} context favors this assay."
            )
            calibrated.append(enriched)
        return calibrated

    def calibrate_pathway_confidence(
        self,
        pathway_priorities: list[dict[str, Any]],
        linked_evidence: dict[str, Any],
        species: str,
        focus: str,
    ) -> list[dict[str, Any]]:
        calibrated: list[dict[str, Any]] = []
        for pathway in pathway_priorities:
            pathway_name = str(pathway.get("pathway", "Unspecified pathway")).lower()
            matched_support = "low"
            matched_records: list[str] = []
            for hotspot_label, support in linked_evidence.items():
                label_text = hotspot_label.lower()
                if (
                    ("amine" in label_text and "dealkyl" in pathway_name)
                    or ("aromatic" in label_text and "oxid" in pathway_name)
                    or ("conjugation" in label_text and "conjug" in pathway_name)
                    or ("sulfur" in label_text and ("sulfur" in pathway_name or "reactive" in pathway_name))
                    or ("hydrolysis" in label_text and "hydrolysis" in pathway_name)
                ):
                    matched_support = str(support.get("support_level", "low"))
                    matched_records = list(support.get("record_titles", []))
                    break
            priority_level = str(pathway.get("priority", "medium"))
            priority_score = {"high": 7.5, "medium": 5.0, "low": 3.0}.get(priority_level, 4.0)
            support_score = {"high": 8.0, "medium": 5.0, "low": 2.0}.get(matched_support, 2.0)
            combined = (priority_score * 0.5) + (support_score * 0.5)
            overall = self._combine_confidence_level(combined)
            enriched = dict(pathway)
            enriched["evidence_support_level"] = matched_support
            enriched["overall_confidence"] = overall
            enriched["confidence_rationale"] = (
                f"{pathway.get('pathway', 'This pathway')} is {overall}-confidence because the chemistry-led pathway priority "
                f"is {priority_level} and literature support is {matched_support} for the current {species}/{focus} context."
            )
            if matched_records:
                enriched["supported_by_records"] = matched_records
            calibrated.append(enriched)
        return calibrated

    def build_recommendation_confidence_summary(
        self,
        hotspot_priorities: list[dict[str, Any]],
        assay_priorities: list[dict[str, Any]],
        pathway_priorities: list[dict[str, Any]],
    ) -> dict[str, list[str] | str]:
        high_items: list[str] = []
        medium_items: list[str] = []
        exploratory_items: list[str] = []
        for collection, label_key in (
            (hotspot_priorities, "hotspot_label"),
            (assay_priorities, "assay_name"),
            (pathway_priorities, "pathway"),
        ):
            for item in collection:
                level = str(item.get("overall_confidence") or item.get("recommendation_confidence") or "exploratory")
                label = str(item.get(label_key, "Unspecified item"))
                if level == "high":
                    high_items.append(label)
                elif level == "medium":
                    medium_items.append(label)
                else:
                    exploratory_items.append(label)
        return {
            "high_confidence_priorities": self._deduplicate(high_items),
            "medium_confidence_priorities": self._deduplicate(medium_items),
            "exploratory_priorities": self._deduplicate(exploratory_items),
            "confidence_caveats": (
                "Confidence levels are heuristic and combine chemistry clarity, literature support, and species/context alignment. "
                "Priority does not automatically imply high confidence."
            ),
        }

    def prioritize_hotspots(
        self,
        hotspots: list[dict[str, Any]],
        linked_evidence: dict[str, Any],
        species: str,
        focus: str,
    ) -> list[dict[str, Any]]:
        _ = species
        _ = focus
        prioritized: list[dict[str, Any]] = []
        confidence_weights = {"high": 3, "medium": 2, "low": 1}
        for hotspot in hotspots:
            label = str(hotspot.get("hotspot_label", "Unspecified hotspot"))
            support = linked_evidence.get(label, {})
            support_level = str(support.get("support_level", "low"))
            support_weight = {"high": 3, "medium": 2, "low": 1}.get(support_level, 1)
            chemistry_score = self.compute_chemistry_confidence({}, hotspot)
            chemistry_level = self.classify_chemistry_confidence(chemistry_score)
            chemistry_weight = confidence_weights.get(chemistry_level, 1)
            total = chemistry_weight + support_weight
            priority = "high" if total >= 5 else "medium" if total >= 3 else "low"
            prioritized.append({
                "hotspot_label": label,
                "priority": priority,
                "chemistry_basis": str(hotspot.get("rationale", "")),
                "evidence_support_level": support_level,
                "chemistry_confidence": chemistry_level,
                "evidence_confidence": support_level,
                "supported_by_records": list(support.get("record_titles", [])),
                "recommended_follow_up": ", ".join(hotspot.get("linked_assays", [])) or "Broad metabolism/disposition follow-up",
                "linked_pathways": list(hotspot.get("linked_pathways", [])),
            })
        prioritized.sort(
            key=lambda item: (
                {"high": 3, "medium": 2, "low": 1}.get(str(item.get("priority", "low")), 1),
                {"high": 3, "medium": 2, "low": 1}.get(str(item.get("evidence_support_level", "low")), 1),
            ),
            reverse=True,
        )
        return prioritized

    def annotate_assay_priorities_with_support(
        self,
        assay_priorities: list[dict[str, Any]],
        assay_support_links: dict[str, Any],
        hotspots: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        annotated: list[dict[str, Any]] = []
        for assay in assay_priorities:
            assay_name = str(assay.get("assay_name", "Unspecified assay"))
            support = assay_support_links.get(assay_name, {})
            supporting_hotspots = [
                str(hotspot.get("hotspot_label"))
                for hotspot in hotspots
                if assay_name in hotspot.get("linked_assays", [])
                or any(
                    assay_name.lower() in str(linked).lower() or str(linked).lower() in assay_name.lower()
                    for linked in hotspot.get("linked_assays", [])
                )
            ]
            support_strength = str(support.get("support_strength", "low"))
            titles = list(support.get("record_titles", []))
            why_prioritized = support.get("why_prioritized") or (
                f"Prioritized because {assay.get('rationale', 'the chemistry profile suggests this assay is useful').rstrip('.')} "
                f"and the linked hotspots are {', '.join(supporting_hotspots[:2]) or 'currently limited'}."
            )
            enriched = dict(assay)
            enriched["supporting_hotspots"] = supporting_hotspots
            enriched["supporting_evidence_titles"] = titles
            enriched["support_strength"] = support_strength
            enriched["why_prioritized"] = str(why_prioritized).strip()
            annotated.append(enriched)
        return annotated

    def infer_disposition_assay_priorities(self, features: dict[str, Any], species: str, focus: str) -> list[dict[str, str]]:
        species_key = (species or "").strip().lower()
        focus_key = (focus or "").strip().lower() or "metid"
        assays: list[dict[str, str]] = []
        transporter_hints = self.infer_transporter_hints(features)
        permeability_hints = self.infer_permeability_hints(features)
        clearance_hints = self.infer_clearance_route_hints(features, species)
        species_label = self.infer_species_chemistry_interpretation(features, species)["species_label"]

        if permeability_hints:
            assays.append({
                "assay_name": "Caco-2 permeability",
                "priority": "high" if any("limited" in hint["label"].lower() for hint in permeability_hints) else "medium",
                "rationale": "Permeability uncertainty is worth checking because polarity and disposition cues may influence apparent exposure.",
                "chemistry_basis": "polarity/permeability heuristics",
                "disposition_basis": "passive-permeability awareness",
                "species_basis": species_label,
            })
        if any("efflux" in hint["label"].lower() or "transporter" in hint["label"].lower() for hint in transporter_hints):
            assays.append({
                "assay_name": "MDCK or MDR1-aware permeability follow-up",
                "priority": "medium",
                "rationale": "Basic or lipophilic chemistry justifies efflux-aware interpretation if apparent permeability is not straightforward.",
                "chemistry_basis": "basic or aromatic transporter-awareness cues",
                "disposition_basis": "efflux/transporter awareness",
                "species_basis": species_label,
            })
            assays.append({
                "assay_name": "Transporter screening awareness",
                "priority": "medium",
                "rationale": "Transporter involvement may be worth checking if metabolism alone does not explain clearance or exposure behavior.",
                "chemistry_basis": "cationic or anionic disposition cues",
                "disposition_basis": "uptake/efflux awareness",
                "species_basis": "Human" if species_key == "human" else species_label,
            })
        if any(route["route_label"] == "oxidative_metabolic_clearance" for route in clearance_hints):
            assays.append({
                "assay_name": "Hepatocyte clearance comparison",
                "priority": "high",
                "rationale": "Microsome and hepatocyte comparison helps decide whether oxidative turnover dominates the overall disposition picture.",
                "chemistry_basis": "oxidation liabilities",
                "disposition_basis": "metabolic-clearance route clarification",
                "species_basis": species_label,
            })
        if features.get("ester_present"):
            assays.append({
                "assay_name": "Plasma stability",
                "priority": "high",
                "rationale": "Hydrolysis risk should be checked early because it can materially shape apparent disposition.",
                "chemistry_basis": "ester present",
                "disposition_basis": "hydrolytic clearance awareness",
                "species_basis": species_label,
            })
        if any(route["route_label"] in {"biliary_excretion_awareness", "renal_or_transporter_contribution_awareness"} for route in clearance_hints):
            assays.append({
                "assay_name": "Plasma protein binding",
                "priority": "medium",
                "rationale": "Binding and distribution context can help interpret whether route-of-clearance uncertainty is metabolic, transporter-related, or mixed.",
                "chemistry_basis": "ionizable or polar disposition cues",
                "disposition_basis": "route-of-clearance interpretation",
                "species_basis": species_label,
            })
        if focus_key == "metid" and species_key == "rat":
            assays.append({
                "assay_name": "Bile/urine/feces recovery context",
                "priority": "medium",
                "rationale": "Rat MetID work often benefits from route-of-clearance context beyond plasma alone.",
                "chemistry_basis": "mixed metabolism/disposition liabilities",
                "disposition_basis": "excretion-route clarification",
                "species_basis": "Rat",
            })
        return self._deduplicate_dicts(assays, key_fields=("assay_name", "priority"))

    def build_disposition_summary(self, features: dict[str, Any], species: str, focus: str) -> dict[str, Any]:
        transporter_hints = self.infer_transporter_hints(features)
        permeability_hints = self.infer_permeability_hints(features)
        clearance_hints = self.infer_clearance_route_hints(features, species)
        assay_priorities = self.infer_disposition_assay_priorities(features, species, focus)
        summary_parts: list[str] = []
        if transporter_hints:
            summary_parts.append("Transporter awareness may be worth keeping in mind if exposure or clearance is not explained by metabolism alone.")
        if permeability_hints:
            summary_parts.append("Passive permeability should be treated cautiously until cell-based follow-up clarifies whether polarity or efflux is limiting.")
        if clearance_hints:
            summary_parts.append("Route-of-clearance assignment should remain empirical because oxidative, conjugative, hydrolytic, or transporter-linked components may coexist.")
        return {
            "summary": " ".join(summary_parts) or "No additional disposition-oriented chemistry interpretation was generated.",
            "transporter_summary": "; ".join(hint["label"] for hint in transporter_hints) if transporter_hints else "No transporter-oriented hint generated.",
            "permeability_summary": "; ".join(hint["label"] for hint in permeability_hints) if permeability_hints else "No permeability-oriented hint generated.",
            "clearance_route_summary": "; ".join(hint["route_label"] for hint in clearance_hints) if clearance_hints else "No disposition-oriented clearance-route hint generated.",
            "assay_summary": "; ".join(item["assay_name"] for item in assay_priorities) if assay_priorities else "No additional disposition assay priority generated.",
        }

    def infer_species_chemistry_interpretation(self, features: dict[str, Any], species: str) -> dict[str, str | list[str]]:
        species_key = (species or "").strip().lower()
        oxidation_liability = any(features.get(flag) for flag in ("tertiary_amine_present", "secondary_amine_present", "aromatic_ring_count", "heteroaromatic_ring_present", "sulfur_present"))
        conjugation_liability = any(features.get(flag) for flag in ("phenol_present", "alcohol_present", "carboxylic_acid_present"))
        if species_key == "human":
            return {
                "species_label": "Human",
                "interpretation_summary": "Human-relevant interpretation should emphasize HLM and human hepatocyte confirmation, with cautious DDI and translation attention.",
                "assay_biases": [
                    "Prioritize human liver microsomes and human hepatocytes for oxidation and conjugation coverage.",
                    "Keep CYP phenotyping visible when oxidative liabilities are broad.",
                ],
                "extrapolation_cautions": [
                    "Human translation should remain cautious if multiple oxidative and conjugative routes appear plausible.",
                    "Potential human-specific metabolite awareness increases when oxidation liabilities are broad.",
                ],
                "preferred_contexts": [
                    "human liver microsomes",
                    "human hepatocytes",
                    "CYP phenotyping" if oxidation_liability else "hepatocyte comparison",
                ],
            }
        if species_key == "rat":
            return {
                "species_label": "Rat",
                "interpretation_summary": "Rat interpretation should emphasize preclinical metabolite coverage and sample-matrix richness before extrapolating to human.",
                "assay_biases": [
                    "Rat liver microsomes and rat hepatocytes are useful for early oxidation and soft-spot screening.",
                    "In vivo rat bile, urine, and feces can add practical metabolite-coverage value for MetID work.",
                ],
                "extrapolation_cautions": [
                    "Rat metabolism patterns should be checked against human systems before drawing translation conclusions.",
                    "Conjugation-heavy chemistry may show species differences that need confirmation outside rat.",
                ],
                "preferred_contexts": [
                    "rat liver microsomes",
                    "rat hepatocytes",
                    "bile/urine/feces profiling",
                ],
            }
        if species_key == "mouse":
            return {
                "species_label": "Mouse",
                "interpretation_summary": "Mouse interpretation is best treated as preclinical metabolism screening with limited direct human translation confidence.",
                "assay_biases": [
                    "Mouse microsomes and hepatocytes can help rank liabilities early.",
                    "Use mouse findings to inform screening rather than human extrapolation certainty.",
                ],
                "extrapolation_cautions": [
                    "Mouse data should be bridged to human systems before strong translation claims.",
                ],
                "preferred_contexts": [
                    "mouse liver microsomes",
                    "mouse hepatocytes",
                    "comparative species screening",
                ],
            }
        if species_key in {"dog", "monkey"}:
            species_label = "Dog" if species_key == "dog" else "Monkey"
            return {
                "species_label": species_label,
                "interpretation_summary": f"{species_label} interpretation is most useful for cross-species nonclinical translation support rather than standalone pathway certainty.",
                "assay_biases": [
                    f"Use {species_label.lower()} hepatocytes or microsomes when cross-species comparison is needed.",
                    "Compare with human systems before over-interpreting species-specific chemistry.",
                ],
                "extrapolation_cautions": [
                    f"{species_label} data can support nonclinical translation but should not replace human chemistry confirmation.",
                ],
                "preferred_contexts": [
                    f"{species_label.lower()} microsomes",
                    f"{species_label.lower()} hepatocytes",
                    "cross-species comparison",
                ],
            }
        return {
            "species_label": "Unknown",
            "interpretation_summary": "Species-specific chemistry interpretation remains neutral because no explicit species focus was supplied.",
            "assay_biases": [
                "Use a balanced microsome, hepatocyte, and conjugation-aware screen until species priorities are clearer."
            ],
            "extrapolation_cautions": [
                "Species differences cannot be interpreted confidently until a primary species is defined."
            ],
            "preferred_contexts": [
                "balanced species panel",
                "microsomes",
                "hepatocytes",
            ],
        }

    def infer_assay_priorities(self, features: dict[str, Any], species: str, focus: str) -> list[dict[str, str]]:
        species_key = (species or "").strip().lower()
        focus_key = (focus or "").strip().lower() or "metid"
        species_basis = self.infer_species_chemistry_interpretation(features, species)["species_label"]
        assays: list[dict[str, str]] = []
        oxidation = any(features.get(flag) for flag in ("tertiary_amine_present", "secondary_amine_present", "aromatic_ring_count", "heteroaromatic_ring_present", "sulfur_present"))
        conjugation = any(features.get(flag) for flag in ("phenol_present", "alcohol_present", "carboxylic_acid_present"))
        reactive = any(features.get(flag) for flag in ("sulfur_present", "thiophene_like_present", "thioether_present", "aniline_like_present", "catechol_like_present"))

        microsome_name = {
            "human": "Human liver microsomes",
            "rat": "Rat liver microsomes",
            "mouse": "Mouse liver microsomes",
            "dog": "Dog liver microsomes",
            "monkey": "Monkey liver microsomes",
        }.get(species_key, "Liver microsomes")

        hepatocyte_name = {
            "human": "Human hepatocytes",
            "rat": "Rat hepatocytes",
            "mouse": "Mouse hepatocytes",
            "dog": "Dog hepatocytes",
            "monkey": "Monkey hepatocytes",
        }.get(species_key, "Hepatocytes")

        if oxidation:
            assays.append({
                "assay_name": microsome_name,
                "priority": "high",
                "rationale": "Oxidative liabilities make microsomal turnover and soft-spot coverage worth checking early.",
                "chemistry_basis": "oxidation-prone substructures detected",
                "species_basis": species_basis,
            })
            assays.append({
                "assay_name": hepatocyte_name,
                "priority": "high",
                "rationale": "Hepatocytes can confirm broader oxidative pathways and soft-spot ranking beyond microsomes.",
                "chemistry_basis": "oxidation liabilities with possible competing pathways",
                "species_basis": species_basis,
            })
        if focus_key == "metid":
            assays.append({
                "assay_name": "High-resolution MS metabolite profiling",
                "priority": "high",
                "rationale": "MetID focus benefits from broad metabolite coverage and confident soft-spot readout.",
                "chemistry_basis": "MetID focus with chemistry-driven pathway diversity",
                "species_basis": species_basis,
            })
        if focus_key == "ddi" or oxidation:
            assays.append({
                "assay_name": "CYP phenotyping",
                "priority": "high" if focus_key == "ddi" else "medium",
                "rationale": "Oxidative liabilities and DDI questions make CYP phenotyping worth prioritizing.",
                "chemistry_basis": "amine or aromatic oxidation liabilities",
                "species_basis": "Human" if species_key == "human" else species_basis,
            })
        if conjugation:
            assays.append({
                "assay_name": "S9 or conjugation-aware incubation",
                "priority": "high" if focus_key == "metid" else "medium",
                "rationale": "Polar functionality increases the value of Phase II-aware metabolism coverage.",
                "chemistry_basis": "phenol/alcohol/acid features",
                "species_basis": species_basis,
            })
        if features.get("ester_present"):
            assays.append({
                "assay_name": "Plasma stability",
                "priority": "high",
                "rationale": "Ester functionality can create early hydrolysis liability that competes with oxidation.",
                "chemistry_basis": "ester present",
                "species_basis": species_basis,
            })
        if reactive:
            assays.append({
                "assay_name": "GSH trapping consideration",
                "priority": "medium",
                "rationale": "Reactive-risk motifs justify conservative trapping or bioactivation awareness work.",
                "chemistry_basis": "sulfur, thiophene, or reactive-risk motif present",
                "species_basis": species_basis,
            })
        if focus_key == "metid" and species_key == "rat":
            assays.append({
                "assay_name": "Rat bile/urine/feces metabolite coverage",
                "priority": "medium",
                "rationale": "Rat MetID work benefits from richer in vivo metabolite coverage matrices.",
                "chemistry_basis": "MetID focus with likely multiple pathways",
                "species_basis": "Rat",
            })
        return self._deduplicate_dicts(assays, key_fields=("assay_name", "priority"))

    def infer_pathway_priorities(self, features: dict[str, Any], species: str, focus: str) -> list[dict[str, str]]:
        species_key = (species or "").strip().lower()
        focus_key = (focus or "").strip().lower() or "metid"
        entries: list[dict[str, str]] = []

        if int(features.get("aromatic_ring_count", 0) or 0) > 0:
            entries.append({
                "pathway": "Oxidative metabolism including aromatic hydroxylation",
                "priority": "high" if focus_key in {"metid", "pk"} else "medium",
                "rationale": "Aromatic ring features make oxidation a plausible early route to verify.",
                "supporting_features": "aromatic_ring_count",
                "species_context_note": self._species_context_note(species_key, "oxidation"),
            })
        if features.get("tertiary_amine_present"):
            entries.append({
                "pathway": "N-dealkylation",
                "priority": "high",
                "rationale": "A tertiary amine creates a strong heuristic basis for oxidative N-dealkylation follow-up.",
                "supporting_features": "tertiary_amine_present",
                "species_context_note": self._species_context_note(species_key, "amine_oxidation"),
            })
        elif features.get("secondary_amine_present"):
            entries.append({
                "pathway": "N-dealkylation or N-oxidation",
                "priority": "medium",
                "rationale": "Secondary amines support oxidative amine metabolism, but often with lower certainty than tertiary amines.",
                "supporting_features": "secondary_amine_present",
                "species_context_note": self._species_context_note(species_key, "amine_oxidation"),
            })
        if any(features.get(flag) for flag in ("phenol_present", "alcohol_present", "carboxylic_acid_present")):
            entries.append({
                "pathway": "Conjugation including glucuronidation",
                "priority": "medium" if focus_key == "metid" else "high",
                "rationale": "Exposed polar functionality makes conjugation worth checking alongside oxidative pathways.",
                "supporting_features": "phenol_present/alcohol_present/carboxylic_acid_present",
                "species_context_note": self._species_context_note(species_key, "conjugation"),
            })
        if features.get("ester_present"):
            entries.append({
                "pathway": "Hydrolysis",
                "priority": "high",
                "rationale": "Ester functionality can drive early instability and compete with oxidative turnover.",
                "supporting_features": "ester_present",
                "species_context_note": self._species_context_note(species_key, "hydrolysis"),
            })
        if any(features.get(flag) for flag in ("sulfur_present", "thiophene_like_present", "thioether_present")):
            entries.append({
                "pathway": "Sulfur oxidation and reactive-metabolite awareness",
                "priority": "medium",
                "rationale": "Sulfur-linked motifs can support oxidation with added reactive-metabolite attention.",
                "supporting_features": "sulfur_present/thiophene_like_present/thioether_present",
                "species_context_note": self._species_context_note(species_key, "reactive"),
            })
        return entries

    def build_species_chemistry_summary(self, features: dict[str, Any], species: str, focus: str) -> dict[str, Any]:
        interpretation = self.infer_species_chemistry_interpretation(features, species)
        assays = self.infer_assay_priorities(features, species, focus)
        pathways = self.infer_pathway_priorities(features, species, focus)
        cyp_hints = self.infer_cyp_preference_hints(features)
        transporter_hints = self.infer_transporter_hints(features)
        permeability_hints = self.infer_permeability_hints(features)
        clearance_route_hints = self.infer_clearance_route_hints(features, species)
        disposition_assay_priorities = self.infer_disposition_assay_priorities(features, species, focus)
        disposition_summary = self.build_disposition_summary(features, species, focus)
        risk_notes = self._build_chemistry_risk_notes(features, species, focus)
        return {
            "species_chemistry_interpretation": interpretation,
            "assay_priorities": assays,
            "pathway_priorities": pathways,
            "cyp_preference_hints": cyp_hints,
            "transporter_hints": transporter_hints,
            "permeability_hints": permeability_hints,
            "clearance_route_hints": clearance_route_hints,
            "disposition_assay_priorities": disposition_assay_priorities,
            "disposition_summary": disposition_summary,
            "chemistry_driven_risk_notes": risk_notes,
        }

    def build_chemistry_summary(self, smiles: str) -> ChemistrySummary:
        if not smiles.strip():
            return ChemistrySummary(
                smiles=smiles,
                smiles_valid=False,
                rdkit_used=False,
                feature_flags=[],
                structural_features={},
                soft_spot_hints=[],
                phase1_liabilities=[],
                phase2_liabilities=[],
                reactive_metabolite_risks=[],
                cyp_preference_hints=[],
                transporter_hints=[],
                permeability_hints=[],
                clearance_route_hints=[],
                species_chemistry_interpretation={},
                assay_priorities=[],
                disposition_assay_priorities=[],
                pathway_priorities=[],
                disposition_summary={},
                chemistry_driven_risk_notes=[],
                chemistry_summary_text="No SMILES was provided, so the chemistry intelligence layer fell back to text-only heuristics.",
                limitations=["No SMILES provided; RDKit-based structure analysis was skipped."],
                protocol_implications=[],
            )

        if not self.is_rdkit_available():
            return ChemistrySummary(
                smiles=smiles,
                smiles_valid=False,
                rdkit_used=False,
                feature_flags=[],
                structural_features={},
                soft_spot_hints=[],
                phase1_liabilities=[],
                phase2_liabilities=[],
                reactive_metabolite_risks=[],
                cyp_preference_hints=[],
                transporter_hints=[],
                permeability_hints=[],
                clearance_route_hints=[],
                species_chemistry_interpretation={},
                assay_priorities=[],
                disposition_assay_priorities=[],
                pathway_priorities=[],
                disposition_summary={},
                chemistry_driven_risk_notes=[],
                chemistry_summary_text="RDKit is not available, so the chemistry intelligence layer fell back to text-only heuristics.",
                limitations=["RDKit unavailable; structure parsing and feature detection were skipped."],
                protocol_implications=[],
            )

        analyzed = self.analyze_structure(smiles)
        if not analyzed.get("smiles_valid"):
            return ChemistrySummary(
                smiles=smiles,
                smiles_valid=False,
                rdkit_used=True,
                feature_flags=[],
                structural_features={},
                soft_spot_hints=[],
                phase1_liabilities=[],
                phase2_liabilities=[],
                reactive_metabolite_risks=[],
                cyp_preference_hints=[],
                transporter_hints=[],
                permeability_hints=[],
                clearance_route_hints=[],
                species_chemistry_interpretation={},
                assay_priorities=[],
                disposition_assay_priorities=[],
                pathway_priorities=[],
                disposition_summary={},
                chemistry_driven_risk_notes=[],
                chemistry_summary_text="SMILES parsing failed, so the chemistry intelligence layer fell back to text-only heuristics.",
                limitations=["Invalid or unparsable SMILES; RDKit analysis could not proceed."],
                protocol_implications=[],
            )

        features = dict(analyzed.get("structural_features", {}))
        soft_spots = self.infer_soft_spots(features)
        phase1 = self.infer_phase1_liabilities(features)
        phase2 = self.infer_phase2_liabilities(features)
        reactive = self.infer_reactive_metabolite_risks(features)
        protocol_implications = self._build_protocol_implications(features, phase1, phase2, reactive)
        cyp_hints = self.infer_cyp_preference_hints(features)
        transporter_hints = self.infer_transporter_hints(features)
        permeability_hints = self.infer_permeability_hints(features)
        clearance_route_hints = self.infer_clearance_route_hints(features, species="")
        disposition_assay_priorities = self.infer_disposition_assay_priorities(features, species="", focus="MetID")
        disposition_summary = self.build_disposition_summary(features, species="", focus="MetID")
        chemistry_risk_notes = self._build_chemistry_risk_notes(features, species="", focus="MetID")
        key_flags = analyzed.get("feature_flags", []) or []

        summary_parts = []
        if key_flags:
            summary_parts.append(f"RDKit detected key structural flags: {', '.join(key_flags[:6])}.")
        if soft_spots:
            summary_parts.append(f"Primary soft-spot hints include {', '.join(hint['label'].lower() for hint in soft_spots[:3])}.")
        if reactive:
            summary_parts.append(reactive[0])

        return ChemistrySummary(
            smiles=smiles,
            smiles_valid=True,
            rdkit_used=True,
            molecular_formula=str(analyzed.get("molecular_formula", "")),
            molecular_weight=analyzed.get("molecular_weight"),
            feature_flags=list(key_flags),
            structural_features=features,
            soft_spot_hints=soft_spots,
            phase1_liabilities=phase1,
            phase2_liabilities=phase2,
            reactive_metabolite_risks=reactive,
            cyp_preference_hints=cyp_hints,
            transporter_hints=transporter_hints,
            permeability_hints=permeability_hints,
            clearance_route_hints=clearance_route_hints,
            species_chemistry_interpretation={},
            assay_priorities=[],
            disposition_assay_priorities=disposition_assay_priorities,
            pathway_priorities=[],
            disposition_summary=disposition_summary,
            chemistry_driven_risk_notes=chemistry_risk_notes,
            chemistry_summary_text=" ".join(summary_parts) or "RDKit-based structure analysis completed.",
            limitations=[],
            protocol_implications=protocol_implications,
        )

    @staticmethod
    def _build_protocol_implications(
        features: dict[str, Any],
        phase1_liabilities: list[str],
        phase2_liabilities: list[str],
        reactive_risks: list[str],
    ) -> list[str]:
        implications: list[str] = []
        if any(features.get(flag) for flag in ("tertiary_amine_present", "secondary_amine_present", "basic_nitrogen_present")) or any(
            "CYP" in hint for hint in phase1_liabilities
        ):
            implications.append("Prioritize microsome incubation, hepatocyte confirmation, and CYP phenotyping because oxidative amine liability is plausible.")
        if any(features.get(flag) for flag in ("phenol_present", "alcohol_present", "carboxylic_acid_present")):
            implications.append("Add Phase II conjugation assessment in S9 or hepatocyte systems, ideally with glucuronidation-aware conditions.")
        if any(features.get(flag) for flag in ("sulfur_present", "thiophene_like_present", "thioether_present")) or reactive_risks:
            implications.append("Add reactive-metabolite awareness and consider GSH trapping if sulfur or reactive-risk motifs are present.")
        if features.get("ester_present"):
            implications.append("Plasma stability and hydrolysis assessment should be included because an ester functionality is present.")
        if any(features.get(flag) for flag in ("cationic_center_hint", "anionic_center_hint")) or float(features.get("tpsa", 0.0) or 0.0) >= 90.0:
            implications.append("Add disposition-aware permeability and transporter follow-up if exposure or clearance is not explained by metabolism alone.")
        liability_count = sum(bool(item) for item in (
            phase1_liabilities,
            phase2_liabilities,
            reactive_risks,
        ))
        if liability_count >= 2:
            implications.append("Use hepatocytes plus high-resolution MS to broaden metabolite coverage when multiple liabilities are present.")
        return implications

    def _build_chemistry_risk_notes(self, features: dict[str, Any], species: str, focus: str) -> list[str]:
        notes: list[str] = []
        if any(features.get(flag) for flag in ("sulfur_present", "thiophene_like_present", "thioether_present")):
            notes.append("Sulfur-linked oxidation liability warrants conservative reactive-metabolite awareness.")
        if features.get("ester_present"):
            notes.append("Hydrolysis may compete with oxidative pathways, so plasma stability should be interpreted early.")
        if any(features.get(flag) for flag in ("phenol_present", "alcohol_present", "carboxylic_acid_present")):
            notes.append("Conjugation pathways may compete with oxidation and can create species-dependent interpretation complexity.")
        if any(features.get(flag) for flag in ("cationic_center_hint", "anionic_center_hint")):
            notes.append("Disposition interpretation should retain transporter awareness if exposure or clearance is not fully explained by metabolism.")
        if float(features.get("tpsa", 0.0) or 0.0) >= 90.0:
            notes.append("Higher polarity may limit passive permeability, so low exposure should not automatically be attributed to metabolism alone.")
        if (species or "").strip().lower() == "rat" and focus.strip().lower() == "metid":
            notes.append("Rat MetID interpretation should emphasize bile, urine, and feces coverage before human extrapolation.")
        if (species or "").strip().lower() == "human":
            notes.append("Human-focused chemistry interpretation should retain DDI and translation caution when oxidative liabilities are broad.")
        return notes

    @staticmethod
    def _species_context_note(species_key: str, pathway_kind: str) -> str:
        if species_key == "human":
            if pathway_kind == "oxidation":
                return "Human microsomes and hepatocytes are the most relevant confirmation systems."
            if pathway_kind == "conjugation":
                return "Human conjugation balance should be checked because translation impact can be material."
            if pathway_kind == "hydrolysis":
                return "Human plasma stability and hepatocyte comparison can help clarify the hydrolysis contribution."
            return "Human translation should remain cautious until pathway balance is confirmed in vitro."
        if species_key == "rat":
            if pathway_kind == "oxidation":
                return "Rat microsomes and hepatocytes can rank this pathway early, but human confirmation is still needed."
            if pathway_kind == "conjugation":
                return "Rat conjugation findings should be compared with human because species differences can matter."
            if pathway_kind == "hydrolysis":
                return "Rat plasma and hepatocyte comparison can help clarify whether hydrolysis materially shapes exposure."
            return "Rat in vivo metabolite coverage can help clarify pathway relevance."
        if species_key in {"mouse", "dog", "monkey"}:
            return "Cross-species comparison is useful before drawing stronger translation conclusions."
        return "Species context is neutral because no explicit species focus was supplied."

    @staticmethod
    def _categorize_logp(logp_value: float | None) -> str:
        if logp_value is None:
            return "unknown"
        if logp_value < 1.0:
            return "low_lipophilicity"
        if logp_value < 3.0:
            return "moderately_lipophilic"
        return "lipophilic"

    @staticmethod
    def _deduplicate(items: list[str]) -> list[str]:
        seen: set[str] = set()
        ordered: list[str] = []
        for item in items:
            normalized = item.strip()
            if normalized and normalized not in seen:
                seen.add(normalized)
                ordered.append(normalized)
        return ordered

    @staticmethod
    def _deduplicate_dicts(items: list[dict[str, str]], key_fields: tuple[str, ...]) -> list[dict[str, str]]:
        seen: set[tuple[str, ...]] = set()
        ordered: list[dict[str, str]] = []
        for item in items:
            key = tuple(str(item.get(field, "")) for field in key_fields)
            if key not in seen:
                seen.add(key)
                ordered.append(item)
        return ordered

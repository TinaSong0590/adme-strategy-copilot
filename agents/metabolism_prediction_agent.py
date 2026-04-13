from __future__ import annotations

import re
from dataclasses import dataclass

from utils.models import ADMERequest, ChemistrySummary, MetabolismPrediction


KNOWN_COMPOUND_HINTS: dict[str, dict[str, list[str] | str]] = {
    "ibrutinib": {
        "motifs": [
            "aromatic ring",
            "tertiary amine",
            "acrylamide electrophile",
            "heteroaromatic nitrogens",
        ],
        "cyp": ["CYP3A"],
        "reactive": ["Michael acceptor liability may warrant reactive metabolite awareness."],
        "notes": [
            "Ibrutinib often shows oxidative metabolism and CYP3A sensitivity in preclinical ADME discussions.",
        ],
    },
}


@dataclass(slots=True)
class MetabolismPredictionAgent:
    def run(self, request: ADMERequest, chemistry: ChemistrySummary | None = None) -> MetabolismPrediction:
        chemistry = chemistry or ChemistrySummary()
        hints = self._collect_hints(request=request, chemistry=chemistry)
        pathways: list[str] = []
        warnings: list[str] = []
        rationale: list[str] = []
        cyp_flags: list[str] = []
        risk_factors = 0

        if hints["aromatic_ring"]:
            pathways.append("Aromatic hydroxylation is plausible due to aromatic ring features.")
            rationale.append("Aromatic motifs often increase the likelihood of Phase I ring oxidation.")
            risk_factors += 1

        if hints["tertiary_amine"]:
            pathways.append("N-dealkylation may occur because a tertiary amine is present.")
            warnings.append("Potential CYP-mediated N-dealkylation may contribute to DDI sensitivity.")
            rationale.append("Tertiary amines commonly undergo oxidative dealkylation in microsomes and hepatocytes.")
            cyp_flags.append("CYP3A")
            risk_factors += 1

        if hints["secondary_amine"]:
            pathways.append("Secondary amine functionality suggests possible N-dealkylation or N-oxidation.")
            rationale.append("Secondary amines often warrant oxidation-focused microsome and hepatocyte assessment.")
            risk_factors += 1

        if hints["phenol_or_oh"]:
            pathways.append("Glucuronidation liability is plausible given hydroxyl or phenolic functionality.")
            rationale.append("Phenol or alcohol motifs are frequent substrates for UGT-mediated clearance.")
            risk_factors += 1

        if hints["sulfur_or_thiophene"]:
            pathways.append("Sulfur oxidation should be considered due to sulfur-containing motif features.")
            warnings.append("Sulfur-containing motifs can increase oxidative liability and reactive intermediate concern.")
            rationale.append("Thiophene and sulfur motifs are often flagged for oxidative turnover.")
            risk_factors += 1

        if hints["ester"]:
            pathways.append("Hydrolysis should be considered because an ester functionality is present.")
            rationale.append("Esters are more susceptible to hydrolysis than amides in plasma and tissue systems.")
            risk_factors += 1

        if hints["amide"]:
            rationale.append("Amides are often more stable than esters, but lower-priority amidase susceptibility can still be assessed.")

        if hints["carboxylic_acid"]:
            pathways.append("Acyl glucuronidation is plausible because a carboxylic acid functionality is present.")
            rationale.append("Carboxylic acids can introduce Phase II acyl glucuronidation liability.")
            risk_factors += 1

        if hints["aniline_or_catechol"]:
            warnings.append("Aniline or catechol-like motifs raise reactive metabolite concerns.")
            rationale.append("These motifs can generate quinone-imine or related electrophilic intermediates.")
            risk_factors += 1

        compound_key = request.drug_name.strip().lower()
        compound_profile = KNOWN_COMPOUND_HINTS.get(compound_key)
        if compound_profile:
            for pathway in compound_profile.get("notes", []):
                rationale.append(str(pathway))
            for cyp in compound_profile.get("cyp", []):
                if cyp not in cyp_flags:
                    cyp_flags.append(str(cyp))
            for warning in compound_profile.get("reactive", []):
                warnings.append(str(warning))
            if "CYP3A" in cyp_flags:
                warnings.append("Known or suspected CYP3A contribution suggests DDI focus during phenotyping.")

        prioritized_pathways = self._format_pathway_priorities(chemistry.pathway_priorities or [])
        if prioritized_pathways:
            pathways.extend(prioritized_pathways)
        else:
            for liability in chemistry.phase1_liabilities or []:
                pathways.append(liability)
            for liability in chemistry.phase2_liabilities or []:
                pathways.append(liability)

        for pathway_priority in chemistry.pathway_priorities or []:
            species_note = pathway_priority.get("species_context_note", "")
            if species_note:
                rationale.append(species_note)
            overall_confidence = pathway_priority.get("overall_confidence", "")
            if overall_confidence:
                rationale.append(
                    f"Pathway confidence: {pathway_priority.get('pathway', 'This pathway')} is {overall_confidence}-confidence."
                )
            confidence_rationale = pathway_priority.get("confidence_rationale", "")
            if confidence_rationale:
                rationale.append(confidence_rationale)
            supported_by_records = pathway_priority.get("supported_by_records", [])
            if supported_by_records:
                rationale.append(
                    f"Pathway literature direction: {', '.join(str(title) for title in supported_by_records[:2])}."
                )
        for hotspot in chemistry.hotspot_priorities or []:
            linked_pathways = [str(pathway).lower() for pathway in hotspot.get("linked_pathways", [])]
            if any(
                pathway_term in " ".join(linked_pathways)
                for pathway_term in ("oxidative", "hydroxylation", "n-dealkylation", "glucuronidation", "hydrolysis", "sulfur oxidation")
            ):
                rationale.append(
                    f"Hotspot-backed priority: {hotspot.get('hotspot_label', 'Unspecified hotspot')} "
                    f"({hotspot.get('priority', 'low')} priority, evidence {hotspot.get('evidence_support_level', 'low')})."
                )
                supported_by = hotspot.get("supported_by_records", [])
                if supported_by:
                    rationale.append(
                        f"Supporting literature direction: {', '.join(str(title) for title in supported_by[:2])}."
                    )
        for clearance_hint in chemistry.clearance_route_hints or []:
            route_label = clearance_hint.get("route_label", "")
            if route_label in {"oxidative_metabolic_clearance", "hydrolytic_clearance_component", "conjugative_mixed_clearance"}:
                rationale.append(
                    f"Clearance-route context: {clearance_hint.get('rationale', '')}"
                )
        for cyp_hint in chemistry.cyp_preference_hints or []:
            rationale.append(
                f"CYP preference hint: {cyp_hint.get('label', 'Unspecified oxidative liability')}. {cyp_hint.get('rationale', '')}".strip()
            )
            assay_implication = cyp_hint.get("assay_implication", "")
            if assay_implication:
                rationale.append(f"Assay implication: {assay_implication}")
            optional_isoform_hint = cyp_hint.get("optional_isoform_hint", "")
            if optional_isoform_hint:
                warnings.append(optional_isoform_hint)
            label = cyp_hint.get("label", "").lower()
            if "cyp3a" in optional_isoform_hint.lower() or "cyp3a" in label:
                cyp_flags.append("CYP3A")
        for risk in chemistry.reactive_metabolite_risks or []:
            warnings.append(risk)
        for risk_note in chemistry.chemistry_driven_risk_notes or []:
            warnings.append(risk_note)
        if chemistry.chemistry_summary_text:
            rationale.append(chemistry.chemistry_summary_text)

        if not pathways:
            pathways.append("No strong motif-specific alert was detected, so broad oxidative metabolism screening is recommended.")
            rationale.append("The MVP fallback mode uses simple heuristics and should be supplemented with wet-lab data.")

        clearance_risk = self._estimate_clearance_risk(risk_factors=risk_factors, cyp_flags=cyp_flags)
        reactive_risk = "Elevated" if any("reactive" in warning.lower() or "electrophile" in warning.lower() for warning in warnings) else "Moderate"

        if clearance_risk in {"Moderate", "High"}:
            warnings.append(f"{clearance_risk} clearance risk: prioritize intrinsic clearance readouts in microsomes and hepatocytes.")

        return MetabolismPrediction(
            pathways=self._deduplicate(pathways),
            warnings=self._deduplicate(warnings),
            rationale=self._deduplicate(rationale),
            cyp_flags=self._deduplicate(cyp_flags),
            clearance_risk=clearance_risk,
            reactive_metabolite_risk=reactive_risk,
            detected_features=self._deduplicate(
                [key for key, value in hints.items() if value] + list(chemistry.feature_flags or [])
            ),
        )

    def _collect_hints(self, request: ADMERequest, chemistry: ChemistrySummary) -> dict[str, bool]:
        source = f"{request.drug_name} {request.smiles}".lower()
        compound_profile = KNOWN_COMPOUND_HINTS.get(request.drug_name.strip().lower(), {})
        motif_text = " ".join(str(item) for item in compound_profile.get("motifs", []))
        search_text = f"{source} {motif_text}".lower()
        chemistry_features = chemistry.structural_features or {}

        return {
            "aromatic_ring": bool(chemistry_features.get("aromatic_ring_count")) or bool(request.smiles and "c" in request.smiles) or "aromatic ring" in search_text or "phenyl" in search_text,
            "tertiary_amine": bool(chemistry_features.get("tertiary_amine_present")) or bool(re.search(r"n\(", request.smiles.lower())) or "tertiary amine" in search_text or "piperidine" in search_text,
            "secondary_amine": bool(chemistry_features.get("secondary_amine_present")),
            "phenol_or_oh": bool(chemistry_features.get("phenol_present")) or bool(chemistry_features.get("alcohol_present")) or "oh" in search_text or "[oh]" in search_text or "phenol" in search_text,
            "sulfur_or_thiophene": bool(chemistry_features.get("sulfur_present")) or bool(chemistry_features.get("thiophene_like_present")) or "s" in request.smiles.lower() or "thiophene" in search_text or "sulfur" in search_text,
            "aniline_or_catechol": bool(chemistry_features.get("aniline_like_present")) or bool(chemistry_features.get("catechol_like_present")) or "aniline" in search_text or "catechol" in search_text,
            "ester": bool(chemistry_features.get("ester_present")),
            "amide": bool(chemistry_features.get("amide_present")),
            "carboxylic_acid": bool(chemistry_features.get("carboxylic_acid_present")),
        }

    @staticmethod
    def _estimate_clearance_risk(risk_factors: int, cyp_flags: list[str]) -> str:
        if risk_factors >= 3 or cyp_flags:
            return "High"
        if risk_factors == 2:
            return "Moderate"
        return "Low"

    @staticmethod
    def _format_pathway_priorities(pathway_priorities: list[dict[str, str]]) -> list[str]:
        entries: list[str] = []
        for pathway_priority in pathway_priorities:
            pathway = pathway_priority.get("pathway", "Unspecified pathway")
            priority = pathway_priority.get("priority", "exploratory").capitalize()
            rationale = pathway_priority.get("rationale", "").strip()
            if rationale:
                entries.append(f"{priority}-priority: {pathway}. Rationale: {rationale}")
            else:
                entries.append(f"{priority}-priority: {pathway}.")
        return entries

    @staticmethod
    def _deduplicate(items: list[str]) -> list[str]:
        seen: set[str] = set()
        ordered: list[str] = []
        for item in items:
            if item and item not in seen:
                seen.add(item)
                ordered.append(item)
        return ordered

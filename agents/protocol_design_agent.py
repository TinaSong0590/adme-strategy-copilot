from __future__ import annotations

from dataclasses import dataclass

from utils.models import ADMEProtocol, ADMERequest, ChemistrySummary, MetabolismPrediction


@dataclass(slots=True)
class ProtocolDesignAgent:
    def run(self, request: ADMERequest, metabolism: MetabolismPrediction, chemistry: ChemistrySummary | None = None) -> ADMEProtocol:
        chemistry = chemistry or ChemistrySummary()
        interpretation = chemistry.species_chemistry_interpretation or {}
        in_vitro = [
            "Human liver microsomes: measure intrinsic clearance, metabolite soft spots, and time-dependent turnover.",
            "S9 fraction: capture mixed Phase I and Phase II turnover, especially if glucuronidation is suspected.",
            "Cryopreserved hepatocytes: profile intact-cell metabolism and compare qualitative metabolites across species.",
            "Plasma stability: check parent stability and binding-related loss in species-matched plasma.",
            "CYP phenotyping: use recombinant CYPs or selective inhibitors to map isoform contribution and DDI risk.",
        ]

        in_vivo = [
            f"{request.species} cassette or single-compound PK study with dense early sampling (for example 0.25, 0.5, 1, 2, 4, 8, 24 h).",
            "Collect plasma plus optional urine/bile or feces pools when feasible to support clearance route interpretation.",
            "Include metabolite profiling around Tmax and terminal phase to distinguish formation-limited versus elimination-limited species.",
        ]

        translation = [
            "Scale microsomal and hepatocyte intrinsic clearance to human hepatic clearance using standard IVIVE assumptions.",
            "Compare qualitative human versus preclinical metabolites to flag disproportionate human metabolite risk early.",
            "If systemic clearance appears high in rodent, prioritize hepatocyte and plasma protein binding data before projecting human exposure.",
        ]

        risk_flags = [
            f"Predicted clearance risk: {metabolism.clearance_risk}.",
            f"Predicted reactive metabolite risk: {metabolism.reactive_metabolite_risk}.",
        ]

        if "CYP3A" in metabolism.cyp_flags:
            in_vitro.append("Expand CYP3A-focused inhibition and induction package because a CYP3A liability signal is present.")
            risk_flags.append("CYP3A involvement suspected: assess victim and perpetrator DDI scenarios early.")

        if metabolism.clearance_risk == "High":
            in_vitro.append("Add hepatocyte relay or extended incubation work if rapid turnover obscures metabolite identification.")
            in_vivo.append("Consider IV plus PO arms to separate bioavailability limitations from true systemic clearance.")
            risk_flags.append("High metabolic liability may translate to high clearance risk and limited oral exposure.")

        if metabolism.reactive_metabolite_risk == "Elevated":
            in_vitro.append("Run glutathione or cyanide trapping in microsomes/S9 to screen for reactive intermediates.")
            risk_flags.append("Reactive metabolite concern: add trapping experiments and targeted bioactivation review.")

        if any("glucuronidation" in pathway.lower() for pathway in metabolism.pathways):
            translation.append("UGT involvement should be checked because species differences in conjugation can distort translation.")

        chemistry_features = chemistry.structural_features or {}
        if any(chemistry_features.get(flag) for flag in ("tertiary_amine_present", "secondary_amine_present", "basic_nitrogen_present")):
            in_vitro.append("Use microsome incubation plus hepatocyte confirmation because amine oxidation and CYP turnover are plausible.")
            in_vitro.append("Retain CYP phenotyping emphasis because structure-based oxidative liability is present.")

        if any(chemistry_features.get(flag) for flag in ("phenol_present", "alcohol_present", "carboxylic_acid_present")):
            in_vitro.append("Add Phase II conjugation assessment with S9 or hepatocytes and glucuronidation-aware conditions.")
            translation.append("Check conjugation-driven species differences because exposed polar functionality may alter human translation.")

        if any(chemistry_features.get(flag) for flag in ("sulfur_present", "thiophene_like_present", "thioether_present")) or chemistry.reactive_metabolite_risks:
            in_vitro.append("Consider glutathione trapping or other reactive-metabolite awareness work when sulfur-linked liability is present.")
            risk_flags.append("Structure-based reactive metabolite awareness is warranted due to sulfur or reactive-risk motifs.")

        if chemistry_features.get("ester_present"):
            in_vitro.append("Include explicit plasma stability and hydrolysis assessment because an ester functionality is present.")
            risk_flags.append("Hydrolysis liability should be checked because ester-mediated instability is plausible.")

        for assay in chemistry.assay_priorities or []:
            in_vitro.append(self._format_assay_priority(assay))
        for assay in chemistry.disposition_assay_priorities or []:
            in_vitro.append(self._format_assay_priority(assay))
        if any(
            assay.get("recommendation_confidence", "").strip().lower() in {"high", "medium"}
            for assay in chemistry.assay_priorities or []
        ):
            in_vitro.append(
                "Action-oriented note: start with the highest-confidence metabolism-facing assay pair first, then widen the package only after that first-pass readout clarifies the main pathway question."
            )
        if any(
            assay.get("recommendation_confidence", "").strip().lower() == "exploratory"
            for assay in chemistry.disposition_assay_priorities or []
        ):
            in_vitro.append(
                "Action-oriented note: keep transporter- or permeability-aware follow-up as secondary unless early exposure or clearance behavior indicates metabolism alone is not explaining the phenotype."
            )

        interpretation_summary = interpretation.get("interpretation_summary")
        if isinstance(interpretation_summary, str) and interpretation_summary:
            translation.append(interpretation_summary)
        for caution in interpretation.get("extrapolation_cautions", []):
            if caution:
                translation.append(str(caution))
                risk_flags.append(str(caution))
        preferred_contexts = interpretation.get("preferred_contexts", [])
        if request.focus.strip().lower() == "metid" and request.species.strip().lower() == "rat" and preferred_contexts:
            in_vivo.append(
                "Rat-focused metabolite coverage: collect bile, urine, and feces when feasible because the chemistry profile supports broader metabolite mapping."
            )
        if any(hint.get("route_label") == "biliary_excretion_awareness" for hint in chemistry.clearance_route_hints or []):
            in_vivo.append("Route-of-clearance follow-up: retain bile, urine, and feces collection when feasible because biliary versus renal contribution may need clarification.")
        if any("transporter" in hint.get("label", "").lower() or "efflux" in hint.get("label", "").lower() for hint in chemistry.transporter_hints or []):
            risk_flags.append("Transporter or efflux awareness may be worth checking if exposure or clearance is not fully explained by metabolism alone.")
            translation.append("Human translation should remain cautious until transporter versus metabolic contribution is better separated in relevant in vitro systems.")
        if chemistry.permeability_hints:
            risk_flags.append("Passive permeability uncertainty should be kept in mind when interpreting low exposure or mixed clearance behavior.")
        if chemistry.clearance_route_hints:
            risk_flags.append("Route-of-clearance assignment remains heuristic and should be verified with metabolism-plus-disposition follow-up.")

        for implication in chemistry.protocol_implications or []:
            in_vitro.append(implication)
        for risk_note in chemistry.chemistry_driven_risk_notes or []:
            risk_flags.append(risk_note)

        assay_work_package_summary = self._build_assay_work_package_summary(
            assay_priorities=list(chemistry.assay_priorities or []) + list(chemistry.disposition_assay_priorities or [])
        )
        proposed_first_pass_package = self._build_proposed_first_pass_package(
            assay_priorities=list(chemistry.assay_priorities or []) + list(chemistry.disposition_assay_priorities or [])
        )
        optional_followup_package = self._build_optional_followup_package(
            assay_priorities=list(chemistry.assay_priorities or []) + list(chemistry.disposition_assay_priorities or [])
        )

        return ADMEProtocol(
            in_vitro=self._deduplicate(in_vitro),
            in_vivo=self._deduplicate(in_vivo),
            translation=self._deduplicate(translation),
            risk_flags=self._deduplicate(risk_flags),
            assay_work_package_summary=assay_work_package_summary,
            proposed_first_pass_package=proposed_first_pass_package,
            optional_followup_package=optional_followup_package,
        )

    @staticmethod
    def _format_assay_priority(assay: dict[str, str]) -> str:
        assay_name = assay.get("assay_name", "Unspecified assay")
        priority = assay.get("priority", "medium").capitalize()
        rationale = assay.get("rationale", "").strip()
        chemistry_basis = assay.get("chemistry_basis", "").strip()
        disposition_basis = assay.get("disposition_basis", "").strip()
        species_basis = assay.get("species_basis", "").strip()
        why_prioritized = assay.get("why_prioritized", "").strip()
        supporting_hotspots = ", ".join(assay.get("supporting_hotspots", []))
        supporting_titles = "; ".join(assay.get("supporting_evidence_titles", [])[:2])
        support_strength = assay.get("support_strength", "").strip()
        recommendation_confidence = assay.get("recommendation_confidence", "").strip()
        confidence_rationale = assay.get("confidence_rationale", "").strip()

        detail_parts = [part for part in (rationale, chemistry_basis, disposition_basis, species_basis) if part]
        if why_prioritized:
            detail_parts.append(f"why prioritized: {why_prioritized}")
        if supporting_hotspots:
            detail_parts.append(f"structural support: {supporting_hotspots}")
        if support_strength:
            detail_parts.append(f"literature support strength: {support_strength}")
        if recommendation_confidence:
            detail_parts.append(f"recommendation confidence: {recommendation_confidence}")
        if confidence_rationale:
            detail_parts.append(f"confidence rationale: {confidence_rationale}")
        if supporting_titles:
            detail_parts.append(f"literature direction: {supporting_titles}")
        if detail_parts:
            return f"{priority}-priority: {assay_name}. {'; '.join(detail_parts)}."
        return f"{priority}-priority: {assay_name}."

    @staticmethod
    def _deduplicate(items: list[str]) -> list[str]:
        seen: set[str] = set()
        ordered: list[str] = []
        for item in items:
            if item not in seen:
                seen.add(item)
                ordered.append(item)
        return ordered

    @staticmethod
    def _build_assay_work_package_summary(assay_priorities: list[dict[str, str]]) -> str:
        if not assay_priorities:
            return "No chemistry-backed assay work package was generated."
        top = assay_priorities[:4]
        return "; ".join(
            f"{item.get('assay_name', 'Assay')} ({item.get('priority', 'medium')} priority, {item.get('recommendation_confidence', 'medium')} confidence)"
            for item in top
        )

    @staticmethod
    def _build_proposed_first_pass_package(assay_priorities: list[dict[str, str]]) -> str:
        first_pass = [
            item.get("assay_name", "Assay")
            for item in assay_priorities
            if item.get("recommendation_confidence", "").strip().lower() in {"high", "medium"}
        ][:3]
        if not first_pass:
            return "Start with the most direct metabolism-facing assay before expanding to broader follow-up."
        return "Suggested first-pass package: " + ", ".join(first_pass) + "."

    @staticmethod
    def _build_optional_followup_package(assay_priorities: list[dict[str, str]]) -> str:
        followups = [
            item.get("assay_name", "Assay")
            for item in assay_priorities
            if item.get("recommendation_confidence", "").strip().lower() == "exploratory"
        ][:3]
        if not followups:
            return "No optional exploratory assay package was generated."
        return "Optional follow-up package: " + ", ".join(followups) + "."

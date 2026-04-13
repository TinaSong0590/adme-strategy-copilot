from __future__ import annotations

from dataclasses import dataclass

from utils.models import ADMEProtocol, ADMEReport, ADMERequest, ChemistrySummary, LiteratureReference, LiteratureSearchResult, MetabolismPrediction


@dataclass(slots=True)
class SynthesisAgent:
    def run(
        self,
        request: ADMERequest,
        chemistry: ChemistrySummary,
        metabolism: MetabolismPrediction,
        protocol: ADMEProtocol,
        literature_search: LiteratureSearchResult,
        skill_sources: dict[str, str],
    ) -> ADMEReport:
        literature = literature_search.records
        predicted_pathways = self._to_bullets(metabolism.pathways + metabolism.rationale)
        recommended_in_vitro = self._to_bullets(protocol.in_vitro)
        suggested_in_vivo = self._to_bullets(protocol.in_vivo)
        potential_risks = self._to_bullets(protocol.risk_flags + metabolism.warnings)
        translation = self._to_bullets(protocol.translation)
        chemistry_section = self._format_chemistry(chemistry=chemistry)
        evidence_prioritization = self._format_evidence_prioritization(
            chemistry=chemistry,
            literature_search=literature_search,
        )
        confidence_prioritization = self._format_confidence_prioritization(
            chemistry=chemistry,
            literature_search=literature_search,
        )
        do_now_actions = self.build_do_now_actions(chemistry=chemistry)
        verify_next_actions = self.build_verify_next_actions(
            chemistry=chemistry,
            do_now_actions=do_now_actions,
        )
        exploratory_followups = self.build_exploratory_followups(
            chemistry=chemistry,
            do_now_actions=do_now_actions,
            verify_next_actions=verify_next_actions,
        )
        uncertainty_register = self.build_uncertainty_register(
            request=request,
            chemistry=chemistry,
            literature_search=literature_search,
        )
        next_step_plan = self.build_next_step_plan(
            do_now_actions=do_now_actions,
            verify_next_actions=verify_next_actions,
            exploratory_followups=exploratory_followups,
        )
        executive_priority_summary = self.build_executive_priority_summary(
            request=request,
            chemistry=chemistry,
            literature_search=literature_search,
            do_now_actions=do_now_actions,
            verify_next_actions=verify_next_actions,
            exploratory_followups=exploratory_followups,
            uncertainty_register=uncertainty_register,
        )
        decision_ready_summary = self.build_decision_ready_summary(
            do_now_actions=do_now_actions,
            verify_next_actions=verify_next_actions,
            exploratory_followups=exploratory_followups,
            uncertainty_register=uncertainty_register,
            next_step_plan=next_step_plan,
        )
        mode_view = self.build_mode_aware_summary(
            request=request,
            chemistry=chemistry,
            protocol=protocol,
            literature_search=literature_search,
        )

        skill_summary = ", ".join(
            f"{name} ({location})" for name, location in sorted(skill_sources.items())
        ) or "No external skill context loaded."

        disclaimer = (
            "This report is an MVP-generated preclinical planning aid that uses heuristic metabolism rules, "
            "template-driven protocol logic, and a real-first literature retrieval pipeline with automatic fallback. It is not a substitute for medicinal "
            "chemistry judgment, wet-lab data, or formal regulatory advice.\n\n"
            f"Skill context loaded from: {skill_summary}."
        )

        quality_summary = self._build_quality_summary(literature)
        literature_section = self._format_literature(references=literature)
        if request.smiles.strip() and not request.drug_name.strip():
            literature_section = (
                "- Note: SMILES-only input triggered a generic ADME literature query, so evidence specificity may be limited.\n"
                f"{literature_section}"
            )

        return ADMEReport(
            report_mode=request.report_mode,
            report_mode_summary=str(mode_view.get("report_mode_summary", "")),
            audience_focus=str(mode_view.get("audience_focus", "")),
            selected_sections=list(mode_view.get("selected_sections", [])),
            assay_work_package_summary=protocol.assay_work_package_summary,
            proposed_first_pass_package=protocol.proposed_first_pass_package,
            optional_followup_package=protocol.optional_followup_package,
            executive_priority_summary=self._format_executive_priority_summary(executive_priority_summary),
            do_now_actions=self._format_action_section(
                title="Do now",
                actions=do_now_actions,
                action_key="action",
                why_key="why_now",
                clarify_key="expected_clarification",
            ),
            verify_next_actions=self._format_action_section(
                title="Verify next",
                actions=verify_next_actions,
                action_key="action",
                why_key="why_next",
                clarify_key="what_to_confirm",
            ),
            exploratory_followups=self._format_action_section(
                title="Exploratory follow-up",
                actions=exploratory_followups,
                action_key="action",
                why_key="why_exploratory",
                clarify_key="trigger_condition",
            ),
            uncertainty_register=self._format_uncertainty_register(uncertainty_register),
            next_step_plan=self._format_next_step_plan(next_step_plan),
            decision_ready_summary=self._format_decision_ready_summary(decision_ready_summary),
            input_summary={
                "Drug": request.drug_name or "N/A",
                "SMILES": request.smiles or "N/A",
                "Species": request.species,
                "Focus": request.focus,
            },
            chemistry_intelligence=chemistry_section,
            evidence_linked_prioritization=evidence_prioritization,
            confidence_calibrated_prioritization=confidence_prioritization,
            predicted_metabolic_pathways=predicted_pathways,
            recommended_in_vitro_studies=recommended_in_vitro,
            suggested_in_vivo_design=suggested_in_vivo,
            potential_risks=potential_risks,
            translation_to_human=translation,
            literature_primary_provider=literature_search.primary_provider,
            literature_provider_used=literature_search.provider_used,
            literature_query_set_used="; ".join(literature_search.queries_used),
            literature_retrieval_mode=literature_search.retrieval_mode_summary,
            literature_focus_profile_summary=literature_search.focus_profile_summary,
            literature_focus_relevance_summary=self._build_focus_summary(
                focus=request.focus,
                references=literature,
                base_summary=f"{literature_search.focus_relevance_summary} Keyword hits: {literature_search.focus_keyword_hits_summary}.",
            ),
            literature_species_profile_summary=literature_search.species_profile_summary,
            literature_matrix_profile_summary=literature_search.matrix_profile_summary,
            literature_species_relevance_summary=self._build_species_summary(
                species=request.species,
                references=literature,
                base_summary=literature_search.species_match_summary,
            ),
            literature_matrix_relevance_summary=self._build_matrix_summary(
                focus=request.focus,
                references=literature,
                base_summary=literature_search.matrix_relevance_summary,
            ),
            literature_compound_relation_summary=literature_search.compound_relation_summary,
            literature_title_target_status_summary=self._build_title_status_summary(
                references=literature,
                base_summary=literature_search.title_target_status_summary,
            ),
            literature_title_centric_boost_summary=self._build_title_boost_summary(
                references=literature,
                base_summary=literature_search.title_centric_boost_summary,
            ),
            literature_mention_only_penalty_summary=self._build_mention_summary(
                references=literature,
                base_summary=literature_search.mention_only_penalty_summary,
            ),
            literature_evidence_bucket_summary=literature_search.evidence_bucket_summary,
            literature_neighbor_suppression_summary=self._build_neighbor_summary(
                references=literature,
                base_summary=literature_search.neighbor_suppression_summary,
            ),
            literature_match_summary=literature_search.match_distribution_summary,
            literature_article_type_summary=literature_search.article_type_summary,
            literature_quality_summary=quality_summary,
            supporting_literature=literature_section,
            disclaimer=disclaimer,
        )

    @staticmethod
    def _to_bullets(lines: list[str]) -> str:
        return "\n".join(f"- {line}" for line in lines)

    @staticmethod
    def _format_chemistry(chemistry: ChemistrySummary) -> str:
        feature_flags = chemistry.feature_flags or []
        soft_spot_hints = chemistry.soft_spot_hints or []
        phase1 = chemistry.phase1_liabilities or []
        phase2 = chemistry.phase2_liabilities or []
        reactive = chemistry.reactive_metabolite_risks or []
        cyp_hints = chemistry.cyp_preference_hints or []
        transporter_hints = chemistry.transporter_hints or []
        permeability_hints = chemistry.permeability_hints or []
        clearance_route_hints = chemistry.clearance_route_hints or []
        pathway_priorities = chemistry.pathway_priorities or []
        assay_priorities = chemistry.assay_priorities or []
        disposition_assay_priorities = chemistry.disposition_assay_priorities or []
        disposition_summary = chemistry.disposition_summary or {}
        hotspot_summary = chemistry.hotspot_summary or []
        hotspot_priorities = chemistry.hotspot_priorities or []
        structure_to_assay_links = chemistry.structure_to_assay_links or []
        chemistry_confidence_summary = chemistry.chemistry_confidence_summary or {}
        hotspot_confidence_summary = chemistry.hotspot_confidence_summary or ""
        recommendation_confidence_summary = chemistry.recommendation_confidence_summary or {}
        species_interpretation = chemistry.species_chemistry_interpretation or {}
        risk_notes = chemistry.chemistry_driven_risk_notes or []
        limitations = chemistry.limitations or []
        implications = chemistry.protocol_implications or []
        molecular_weight = (
            f"{chemistry.molecular_weight:.2f}"
            if isinstance(chemistry.molecular_weight, float)
            else (str(chemistry.molecular_weight) if chemistry.molecular_weight is not None else "N/A")
        )

        lines = [
            f"- SMILES validity: {'valid' if chemistry.smiles_valid else 'not valid or not provided'}",
            f"- RDKit used: {'yes' if chemistry.rdkit_used else 'no'}",
            f"- Molecular formula: {chemistry.molecular_formula or 'N/A'}",
            f"- Molecular weight: {molecular_weight}",
            f"- Key structural features: {', '.join(feature_flags) if feature_flags else 'No RDKit-derived structural flags available.'}",
            "- Pathway priorities:",
        ]
        if pathway_priorities:
            lines.extend(
                [
                    f"  - {priority.get('priority', 'medium').capitalize()}: {priority.get('pathway', 'Unspecified pathway')}."
                    f" {priority.get('rationale', '').strip()}"
                    f"{(' Species context: ' + priority.get('species_context_note', '').strip()) if priority.get('species_context_note') else ''}"
                    f"{(' Confidence: ' + priority.get('overall_confidence', 'exploratory')) if priority.get('overall_confidence') else ''}"
                    f"{(' Confidence rationale: ' + priority.get('confidence_rationale', '').strip()) if priority.get('confidence_rationale') else ''}"
                    for priority in pathway_priorities
                ]
            )
        else:
            lines.append("  - No chemistry-driven pathway prioritization was generated.")
        lines.append(
            f"- Chemistry confidence summary: {chemistry_confidence_summary.get('summary', 'No hotspot chemistry confidence summary was generated.')}"
        )
        lines.append(
            f"- Hotspot confidence summary: {hotspot_confidence_summary or 'No hotspot confidence summary was generated.'}"
        )
        if recommendation_confidence_summary:
            lines.append(
                f"- Recommendation confidence summary: high={len(recommendation_confidence_summary.get('high_confidence_priorities', []))}, "
                f"medium={len(recommendation_confidence_summary.get('medium_confidence_priorities', []))}, "
                f"exploratory={len(recommendation_confidence_summary.get('exploratory_priorities', []))}."
            )

        lines.extend([
            "- Hotspot summary:",
        ])
        if hotspot_summary:
            lines.extend(
                [
                    f"  - {hotspot.get('hotspot_label', 'Unspecified hotspot')}: {hotspot.get('rationale', '').strip()}"
                    f" Linked pathways: {', '.join(hotspot.get('linked_pathways', [])) or 'N/A'}."
                    f" Linked assays: {', '.join(hotspot.get('linked_assays', [])) or 'N/A'}."
                    for hotspot in hotspot_summary
                ]
            )
        else:
            lines.append("  - No SMILES-backed hotspot summary was generated.")

        lines.extend([
            "- Hotspot priorities:",
        ])
        if hotspot_priorities:
            lines.extend(
                [
                    f"  - {hotspot.get('priority', 'low').capitalize()}: {hotspot.get('hotspot_label', 'Unspecified hotspot')}."
                    f" Chemistry basis: {hotspot.get('chemistry_basis', '').strip()}"
                    f" Chemistry confidence: {hotspot.get('chemistry_confidence', 'low')}"
                    f" Evidence support: {hotspot.get('evidence_support_level', 'low')}"
                    f" Evidence confidence: {hotspot.get('evidence_confidence', hotspot.get('evidence_support_level', 'low'))}"
                    f" Overall confidence: {hotspot.get('overall_confidence', 'exploratory')}"
                    f"{(' Confidence rationale: ' + hotspot.get('confidence_rationale', '').strip()) if hotspot.get('confidence_rationale') else ''}"
                    f"{(' Supporting records: ' + '; '.join(hotspot.get('supported_by_records', [])[:2])) if hotspot.get('supported_by_records') else ''}"
                    for hotspot in hotspot_priorities
                ]
            )
        else:
            lines.append("  - No hotspot-backed prioritization was generated.")

        lines.extend([
            "- Structure-to-assay links:",
        ])
        if structure_to_assay_links:
            lines.extend(
                [
                    f"  - {link.get('hotspot_label', 'Unspecified hotspot')} -> {', '.join(link.get('assays', [])) or 'N/A'}."
                    f" {link.get('why_linked', '').strip()}"
                    for link in structure_to_assay_links
                ]
            )
        else:
            lines.append("  - No structure-to-assay links were generated.")

        lines.extend([
            "- CYP preference hints:",
        ])
        if cyp_hints:
            lines.extend(
                [
                    f"  - {hint.get('label', 'Unspecified hint')}: {hint.get('rationale', '').strip()}"
                    f"{(' Assay implication: ' + hint.get('assay_implication', '').strip()) if hint.get('assay_implication') else ''}"
                    f"{(' Conservative isoform note: ' + hint.get('optional_isoform_hint', '').strip()) if hint.get('optional_isoform_hint') else ''}"
                    f" (confidence: {hint.get('confidence', 'n/a')})"
                    for hint in cyp_hints
                ]
            )
        else:
            lines.append("  - No additional CYP-oriented chemistry hint was generated.")

        lines.extend([
            "- Transporter hints:",
        ])
        if transporter_hints:
            lines.extend(
                [
                    f"  - {hint.get('label', 'Unspecified hint')}: {hint.get('rationale', '').strip()}"
                    f"{(' Assay implication: ' + hint.get('assay_implication', '').strip()) if hint.get('assay_implication') else ''}"
                    f"{(' Caution: ' + hint.get('caution_note', '').strip()) if hint.get('caution_note') else ''}"
                    f" (confidence: {hint.get('confidence', 'n/a')})"
                    for hint in transporter_hints
                ]
            )
        else:
            lines.append("  - No transporter-oriented chemistry hint was generated.")

        lines.extend([
            "- Permeability hints:",
        ])
        if permeability_hints:
            lines.extend(
                [
                    f"  - {hint.get('label', 'Unspecified hint')}: {hint.get('rationale', '').strip()}"
                    f"{(' Assay implication: ' + hint.get('assay_implication', '').strip()) if hint.get('assay_implication') else ''}"
                    f" (confidence: {hint.get('confidence', 'n/a')})"
                    for hint in permeability_hints
                ]
            )
        else:
            lines.append("  - No permeability-oriented chemistry hint was generated.")

        lines.extend([
            "- Clearance-route hints:",
        ])
        if clearance_route_hints:
            lines.extend(
                [
                    f"  - {hint.get('priority', 'medium').capitalize()}: {hint.get('route_label', 'unspecified_route')}."
                    f" {hint.get('rationale', '').strip()}"
                    f"{(' Supporting features: ' + hint.get('supporting_features', '').strip()) if hint.get('supporting_features') else ''}"
                    f"{(' Species context: ' + hint.get('species_context_note', '').strip()) if hint.get('species_context_note') else ''}"
                    for hint in clearance_route_hints
                ]
            )
        else:
            lines.append("  - No disposition-oriented clearance-route hint was generated.")

        lines.extend([
            "- Species-aware chemistry interpretation:",
            f"  - Summary: {species_interpretation.get('interpretation_summary', 'No species-aware chemistry interpretation generated.')}",
            f"  - Preferred contexts: {', '.join(species_interpretation.get('preferred_contexts', [])) if species_interpretation.get('preferred_contexts') else 'No species-preferred context highlighted.'}",
            f"  - Assay biases: {'; '.join(species_interpretation.get('assay_biases', [])) if species_interpretation.get('assay_biases') else 'No species-specific assay bias highlighted.'}",
            f"  - Extrapolation cautions: {'; '.join(species_interpretation.get('extrapolation_cautions', [])) if species_interpretation.get('extrapolation_cautions') else 'No additional species extrapolation caution generated.'}",
            "- Assay priorities:",
        ])
        if assay_priorities:
            lines.extend(
                [
                    f"  - {assay.get('priority', 'medium').capitalize()}: {assay.get('assay_name', 'Unspecified assay')}."
                    f" {assay.get('rationale', '').strip()}"
                    f"{(' Chemistry basis: ' + assay.get('chemistry_basis', '').strip()) if assay.get('chemistry_basis') else ''}"
                    f"{(' Species basis: ' + assay.get('species_basis', '').strip()) if assay.get('species_basis') else ''}"
                    f"{(' Recommendation confidence: ' + assay.get('recommendation_confidence', 'exploratory')) if assay.get('recommendation_confidence') else ''}"
                    f"{(' Confidence rationale: ' + assay.get('confidence_rationale', '').strip()) if assay.get('confidence_rationale') else ''}"
                    for assay in assay_priorities
                ]
            )
        else:
            lines.append("  - No chemistry-driven assay prioritization was generated.")
        lines.append("- Disposition summary:")
        lines.append(
            f"  - Summary: {disposition_summary.get('summary', 'No additional disposition-oriented chemistry interpretation was generated.')}"
        )
        lines.append(
            f"  - Transporter summary: {disposition_summary.get('transporter_summary', 'No transporter-oriented hint generated.')}"
        )
        lines.append(
            f"  - Permeability summary: {disposition_summary.get('permeability_summary', 'No permeability-oriented hint generated.')}"
        )
        lines.append(
            f"  - Clearance-route summary: {disposition_summary.get('clearance_route_summary', 'No disposition-oriented clearance-route hint generated.')}"
        )
        lines.append("- Disposition assay priorities:")
        if disposition_assay_priorities:
            lines.extend(
                [
                    f"  - {assay.get('priority', 'medium').capitalize()}: {assay.get('assay_name', 'Unspecified assay')}."
                    f" {assay.get('rationale', '').strip()}"
                    f"{(' Chemistry basis: ' + assay.get('chemistry_basis', '').strip()) if assay.get('chemistry_basis') else ''}"
                    f"{(' Disposition basis: ' + assay.get('disposition_basis', '').strip()) if assay.get('disposition_basis') else ''}"
                    f"{(' Species basis: ' + assay.get('species_basis', '').strip()) if assay.get('species_basis') else ''}"
                    f"{(' Recommendation confidence: ' + assay.get('recommendation_confidence', 'exploratory')) if assay.get('recommendation_confidence') else ''}"
                    f"{(' Confidence rationale: ' + assay.get('confidence_rationale', '').strip()) if assay.get('confidence_rationale') else ''}"
                    for assay in disposition_assay_priorities
                ]
            )
        else:
            lines.append("  - No additional disposition assay priority was generated.")

        lines.extend([
            "- Soft spot hints:",
        ])
        if soft_spot_hints:
            lines.extend(
                [
                    f"  - {hint.get('label', 'Unspecified hint')}: {hint.get('rationale', '')} "
                    f"(confidence: {hint.get('confidence', 'n/a')}; pathway: {hint.get('pathway_type', 'n/a')})"
                    for hint in soft_spot_hints
                ]
            )
        else:
            lines.append("  - No structure-driven soft-spot hints were generated.")

        lines.append(f"- Phase I liabilities: {'; '.join(phase1) if phase1 else 'No specific Phase I liability hint generated.'}")
        lines.append(f"- Phase II liabilities: {'; '.join(phase2) if phase2 else 'No specific Phase II liability hint generated.'}")
        lines.append(f"- Reactive metabolite awareness: {'; '.join(reactive) if reactive else 'No specific reactive metabolite alert generated.'}")
        lines.append(
            f"- Chemistry-derived risk notes: {'; '.join(risk_notes) if risk_notes else 'No additional chemistry-derived risk note generated.'}"
        )
        lines.append(
            f"- Chemistry-derived protocol implications: {'; '.join(implications) if implications else 'No additional chemistry-driven protocol implication beyond the base ADME template.'}"
        )
        lines.append(
            f"- Chemistry limitations: {'; '.join(limitations) if limitations else 'No major chemistry-layer limitation detected for this run.'}"
        )
        if chemistry.chemistry_summary_text:
            lines.append(f"- Chemistry summary: {chemistry.chemistry_summary_text}")
        return "\n".join(lines)

    @staticmethod
    def _format_evidence_prioritization(
        chemistry: ChemistrySummary,
        literature_search: LiteratureSearchResult,
    ) -> str:
        hotspots = chemistry.hotspot_priorities or []
        traced_assays = list(chemistry.assay_priorities or []) + list(chemistry.disposition_assay_priorities or [])
        lines = [
            f"- Structure-to-evidence summary: {literature_search.hotspot_linking_summary or 'No hotspot linkage summary generated.'}",
            f"- Assay traceability summary: {literature_search.assay_support_linking_summary or 'No assay traceability summary generated.'}",
            f"- Evidence tag summary: {literature_search.evidence_tag_summary or 'No evidence tags summarized.'}",
            f"- Literature confidence summary: {literature_search.literature_confidence_summary or 'No literature confidence summary generated.'}",
            f"- Evidence alignment summary: {literature_search.evidence_alignment_summary or 'No evidence alignment summary generated.'}",
            "- Top hotspot-backed priorities:",
        ]
        if hotspots:
            lines.extend(
                [
                    f"  - {hotspot.get('hotspot_label', 'Unspecified hotspot')} ({hotspot.get('priority', 'low')} priority, evidence {hotspot.get('evidence_support_level', 'low')}). "
                    f"{hotspot.get('chemistry_basis', '').strip()}"
                    f"{(' Supported by: ' + '; '.join(hotspot.get('supported_by_records', [])[:2])) if hotspot.get('supported_by_records') else ''}"
                    for hotspot in hotspots[:4]
                ]
            )
        else:
            lines.append("  - No hotspot-backed priority was generated.")

        lines.append("- Assay recommendation traceability:")
        if traced_assays:
            lines.extend(
                [
                    f"  - {assay.get('assay_name', 'Unspecified assay')} ({assay.get('priority', 'medium')} priority; support {assay.get('support_strength', 'low')}). "
                    f"{assay.get('why_prioritized', assay.get('rationale', '')).strip()}"
                    f"{(' Structural support: ' + ', '.join(assay.get('supporting_hotspots', [])[:2])) if assay.get('supporting_hotspots') else ''}"
                    f"{(' Literature direction: ' + '; '.join(assay.get('supporting_evidence_titles', [])[:2])) if assay.get('supporting_evidence_titles') else ''}"
                    for assay in traced_assays[:6]
                ]
            )
        else:
            lines.append("  - No assay traceability entry was generated.")
        return "\n".join(lines)

    @staticmethod
    def _format_confidence_prioritization(
        chemistry: ChemistrySummary,
        literature_search: LiteratureSearchResult,
    ) -> str:
        summary = chemistry.recommendation_confidence_summary or {}
        high_items = summary.get("high_confidence_priorities", []) or []
        medium_items = summary.get("medium_confidence_priorities", []) or []
        exploratory_items = summary.get("exploratory_priorities", []) or []
        caveat = summary.get(
            "confidence_caveats",
            "Confidence levels are heuristic and combine chemistry clarity, literature support, and species/context alignment.",
        )
        lines = [
            f"- High-confidence priorities: {', '.join(high_items) if high_items else 'No item currently reaches high-confidence status.'}",
            f"- Medium-confidence priorities: {', '.join(medium_items) if medium_items else 'No medium-confidence priority was generated.'}",
            f"- Exploratory follow-up items: {', '.join(exploratory_items) if exploratory_items else 'No exploratory item was generated.'}",
            f"- Confidence caveats: {caveat}",
            f"- Cross-source calibration note: {literature_search.literature_confidence_summary or 'Literature confidence remains limited.'}",
            f"- Species/context alignment note: {literature_search.evidence_alignment_summary or 'Species/context alignment remains neutral.'}",
        ]
        return "\n".join(lines)

    @staticmethod
    def _format_literature(references: list[LiteratureReference]) -> str:
        if not references:
            return "- No literature retained."

        sections: list[str] = []
        ordered_buckets = [
            ("core_target_evidence", "### Core Target Evidence"),
            ("supporting_target_evidence", "### Supporting Target Evidence"),
            ("neighbor_supporting_evidence", "### Neighbor Supporting Evidence"),
            ("background_evidence", "### Background Evidence"),
        ]
        for bucket_key, heading in ordered_buckets:
            bucket_references = [reference for reference in references if reference.evidence_bucket == bucket_key]
            if not bucket_references:
                continue
            lines = [heading]
            for reference in bucket_references:
                lines.append(
                    "\n".join(
                        [
                            f"- {reference.title}",
                            f"  Journal: {reference.journal or reference.source or 'Unknown journal'}",
                            f"  Year: {reference.year if reference.year else 'Year not available'}",
                            f"  Authors: {reference.authors or 'Authors not available'}",
                            f"  Retrieval mode: {reference.retrieval_mode}",
                            f"  Compound relation: {reference.compound_relation}",
                            f"  Title target status: {reference.title_target_status}",
                            f"  Evidence bucket: {reference.evidence_bucket}",
                            f"  Match type: {reference.match_type}",
                            f"  Article type: {reference.article_type}",
                            f"  Base score: {reference.base_score:.2f}",
                            f"  Focus relevance score: {reference.focus_relevance_score:.2f}",
                            f"  Species relevance score: {reference.species_relevance_score:.2f}",
                            f"  Matrix relevance score: {reference.matrix_relevance_score:.2f}",
                            f"  Title exactness boost: {reference.title_exactness_boost:.2f}",
                            f"  Mention-only penalty: {reference.target_mention_only_penalty:.2f}",
                            f"  Title compound centrality: {reference.title_compound_centrality:.2f}",
                            f"  Species-specific exactness boost: {reference.species_specific_exactness_boost:.2f}",
                            f"  Neighbor suppression penalty: {reference.neighbor_suppression_penalty:.2f}",
                            f"  Final score: {reference.final_score:.2f}",
                            f"  Relevance: {reference.relevance_explanation}",
                            f"  URL: {reference.url or 'N/A'}",
                            f"  Summary: {reference.summary}",
                        ]
                    )
                )
            sections.append("\n".join(lines))
        return "\n\n".join(sections)

    @staticmethod
    def _build_quality_summary(references: list[LiteratureReference]) -> str:
        exact_count = sum(1 for reference in references if reference.match_type == "exact_name_match")
        alias_count = sum(1 for reference in references if reference.match_type == "alias_match")
        class_count = sum(1 for reference in references if reference.match_type == "class_level_match")
        target_exact = sum(1 for reference in references if reference.compound_relation == "target_exact")
        target_alias = sum(1 for reference in references if reference.compound_relation == "target_alias")
        neighbor_count = sum(1 for reference in references if reference.compound_relation == "neighbor_compound")
        title_centered = sum(
            1
            for reference in references
            if reference.title_target_status in {"target_exact_in_title", "target_alias_in_title"}
        )
        mention_only = sum(1 for reference in references if reference.title_target_status == "target_only_in_abstract_or_summary")
        non_target_title = sum(1 for reference in references if reference.title_target_status == "non_target_title_center")
        review_count = sum(1 for reference in references if reference.article_type == "review")
        clinical_count = sum(1 for reference in references if reference.article_type == "clinical_study")
        preclinical_count = sum(1 for reference in references if reference.article_type == "preclinical_study")
        core_target = sum(1 for reference in references if reference.evidence_bucket == "core_target_evidence")
        supporting_target = sum(1 for reference in references if reference.evidence_bucket == "supporting_target_evidence")
        neighbor_support = sum(1 for reference in references if reference.evidence_bucket == "neighbor_supporting_evidence")

        if core_target >= 2:
            dominance = "Top evidence remains target-compound led."
        elif neighbor_support > core_target + supporting_target:
            dominance = "Neighbor-compound evidence still contributes materially as supporting background."
        elif class_count > exact_count + alias_count:
            dominance = "Results are dominated by class-level matches."
        else:
            dominance = "Results retain compound-specific support."
        return (
            f"Exact matches: {exact_count}; alias matches: {alias_count}; class-level matches: {class_count}; "
            f"target exact: {target_exact}; target alias: {target_alias}; neighbor compounds: {neighbor_count}; "
            f"title-centered target records: {title_centered}; abstract-mention records: {mention_only}; non-target title-centered records: {non_target_title}; "
            f"core target evidence: {core_target}; supporting target evidence: {supporting_target}; neighbor supporting evidence: {neighbor_support}; "
            f"review articles: {review_count}; clinical studies: {clinical_count}; preclinical studies: {preclinical_count}. {dominance}"
        )

    @staticmethod
    def _build_focus_summary(focus: str, references: list[LiteratureReference], base_summary: str) -> str:
        if not references:
            return f"Focus-aware ranking enabled for {focus}. No literature retained."

        top_three = references[:3]
        strong_focus = sum(1 for reference in top_three if reference.focus_relevance_score >= 6.0)
        weak_exact = sum(
            1
            for reference in top_three
            if reference.match_type == "exact_name_match" and reference.focus_relevance_score < 4.0
        )
        if strong_focus >= 2:
            top_bias = f"Top literature is strongly aligned with {focus}."
        elif weak_exact >= 2:
            top_bias = f"Top literature still contains several exact-name but weak-{focus} articles."
        else:
            top_bias = f"Top literature is partially aligned with {focus}."

        return f"{base_summary} {top_bias}"

    @staticmethod
    def _build_species_summary(species: str, references: list[LiteratureReference], base_summary: str) -> str:
        if not references:
            return f"Species-aware ranking enabled for {species or 'Unknown'}. No literature retained."

        if not species.strip():
            return f"{base_summary} Species was not specified, so species-aware reranking remained neutral."

        top_three = references[:3]
        aligned = sum(1 for reference in top_three if reference.species_relevance_score >= 3.0)
        mismatched = sum(
            1
            for reference in top_three
            if reference.species_relevance_score < 1.0 and reference.context_mismatch_penalty >= 3.0
        )
        if aligned >= 2:
            top_bias = f"Top evidence is enriched for {species}-aligned species context."
        elif mismatched >= 2:
            top_bias = f"Top evidence still contains several non-{species} or species-neutral records."
        else:
            top_bias = f"Top evidence is partially aligned with {species} species context."
        return f"{base_summary} {top_bias}"

    @staticmethod
    def _build_matrix_summary(focus: str, references: list[LiteratureReference], base_summary: str) -> str:
        if not references:
            return f"Matrix-aware ranking enabled for {focus}. No literature retained."

        top_three = references[:3]
        strong_context = sum(1 for reference in top_three if reference.matrix_relevance_score >= 4.0)
        weak_context = sum(1 for reference in top_three if reference.matrix_relevance_score < 2.0)
        if strong_context >= 2:
            top_bias = f"Top evidence is strongly aligned with {focus}-relevant assay and matrix context."
        elif weak_context >= 2:
            top_bias = f"Top evidence still includes several records with weak {focus} matrix context."
        else:
            top_bias = f"Top evidence is partially aligned with {focus}-relevant matrix context."
        return f"{base_summary} {top_bias}"

    @staticmethod
    def _build_neighbor_summary(references: list[LiteratureReference], base_summary: str) -> str:
        if not references:
            return "Target-compound prioritization enabled. No literature retained."

        top_three = references[:3]
        target_led = sum(
            1
            for reference in top_three
            if reference.compound_relation in {"target_exact", "target_alias"}
        )
        neighbor_mixed = sum(1 for reference in top_three if reference.compound_relation == "neighbor_compound")
        if target_led >= 2:
            top_bias = "Top evidence is clearly target-compound led."
        elif neighbor_mixed >= 2:
            top_bias = "Neighbor-compound articles still mix into the top evidence and should be read as supporting only."
        else:
            top_bias = "Top evidence contains a mix of target and supporting context."
        return f"{base_summary} {top_bias}"

    @staticmethod
    def _build_title_status_summary(references: list[LiteratureReference], base_summary: str) -> str:
        if not references:
            return "Title-centric target detection enabled. No literature retained."

        top_three = references[:3]
        title_centered = sum(
            1
            for reference in top_three
            if reference.title_target_status in {"target_exact_in_title", "target_alias_in_title"}
        )
        mention_only = sum(1 for reference in top_three if reference.title_target_status == "target_only_in_abstract_or_summary")
        if title_centered >= 2:
            top_bias = "Top evidence is mostly title-centered on the target compound."
        elif mention_only >= 2:
            top_bias = "Top evidence still contains several abstract-mention-only records."
        else:
            top_bias = "Top evidence shows a mixed level of title target-centrality."
        return f"{base_summary} {top_bias}"

    @staticmethod
    def _build_title_boost_summary(references: list[LiteratureReference], base_summary: str) -> str:
        if not references:
            return "No title-centric boost applied."

        top_three = references[:3]
        boosted = sum(1 for reference in top_three if reference.title_exactness_boost > 0.0)
        if boosted >= 2:
            top_bias = "Title-exact or title-alias boosts materially shape the top evidence."
        else:
            top_bias = "Title boosts contribute, but they do not dominate the full ranking."
        return f"{base_summary} {top_bias}"

    @staticmethod
    def _build_mention_summary(references: list[LiteratureReference], base_summary: str) -> str:
        if not references:
            return "No mention-only penalties applied."

        top_three = references[:3]
        mention_only = sum(1 for reference in top_three if reference.target_mention_only_penalty > 0.0)
        non_target_title = sum(1 for reference in top_three if reference.title_target_status == "non_target_title_center")
        if mention_only >= 2 or non_target_title >= 1:
            top_bias = "Mention-only or non-target-title records are actively demoted from the top evidence pool."
        else:
            top_bias = "Top evidence is only lightly affected by mention-only demotion."
        return f"{base_summary} {top_bias}"

    def build_executive_priority_summary(
        self,
        request: ADMERequest,
        chemistry: ChemistrySummary,
        literature_search: LiteratureSearchResult,
        do_now_actions: list[dict[str, str]],
        verify_next_actions: list[dict[str, str]],
        exploratory_followups: list[dict[str, str]],
        uncertainty_register: list[dict[str, str]],
    ) -> dict[str, object]:
        top_priority_items: list[dict[str, str]] = []
        for action in do_now_actions[:3]:
            top_priority_items.append(
                {
                    "top_priority_label": action.get("action", "Unspecified action"),
                    "why_it_matters": action.get("why_now", "This is the clearest immediate experiment from the current chemistry and evidence package."),
                    "confidence_level": action.get("confidence", "medium"),
                    "evidence_basis": action.get("linked_support", "Evidence linkage remains limited."),
                    "immediate_action": action.get("expected_clarification", "Use this first-pass experiment to clarify the leading ADME hypothesis."),
                }
            )

        highest_confidence_action = do_now_actions[0].get("action", "No immediate high-confidence action identified.") if do_now_actions else "No immediate high-confidence action identified."
        main_uncertainty = uncertainty_register[0].get("uncertainty_label", "Residual ADME uncertainty remains.") if uncertainty_register else "Residual ADME uncertainty remains."
        recommended_next_step = do_now_actions[0].get("action", "Start with the most directly target- and species-aligned profiling experiment.") if do_now_actions else (
            verify_next_actions[0].get("action", "Start with a first-pass metabolism screen to reduce the largest uncertainty.")
            if verify_next_actions
            else "Start with a first-pass metabolism screen to reduce the largest uncertainty."
        )

        species = request.species or "the selected species"
        focus = request.focus or "ADME"
        literature_note = literature_search.literature_confidence_summary or "Literature support remains partly heuristic."
        summary_text = (
            f"The current package is most decision-ready around {species}-aligned {focus} profiling where chemistry, context, "
            f"and retained evidence converge best. Immediate work should stay centered on first-pass assays that can clarify the "
            f"leading clearance and metabolite-coverage hypotheses, while secondary follow-up remains gated by what the first "
            f"round of data confirms. {literature_note}"
        )
        return {
            "top_priorities": top_priority_items,
            "highest_confidence_action": highest_confidence_action,
            "main_uncertainty": main_uncertainty,
            "recommended_immediate_next_step": recommended_next_step,
            "summary_text": summary_text,
        }

    def build_mode_aware_summary(
        self,
        request: ADMERequest,
        chemistry: ChemistrySummary,
        protocol: ADMEProtocol,
        literature_search: LiteratureSearchResult,
    ) -> dict[str, object]:
        mode = (request.report_mode or "scientist").strip().lower()
        if mode == "executive":
            return self.build_executive_view(request=request, chemistry=chemistry, protocol=protocol, literature_search=literature_search)
        if mode == "cro_proposal":
            return self.build_cro_proposal_view(request=request, chemistry=chemistry, protocol=protocol, literature_search=literature_search)
        if mode == "regulatory_prep":
            return self.build_regulatory_prep_view(request=request, chemistry=chemistry, protocol=protocol, literature_search=literature_search)
        return self.build_scientist_view(request=request, chemistry=chemistry, protocol=protocol, literature_search=literature_search)

    def build_scientist_view(
        self,
        request: ADMERequest,
        chemistry: ChemistrySummary,
        protocol: ADMEProtocol,
        literature_search: LiteratureSearchResult,
    ) -> dict[str, object]:
        return {
            "report_mode_summary": "Scientist mode keeps the fullest technical view, including chemistry, evidence-linking, confidence layering, and literature traceability.",
            "audience_focus": "Internal DMPK, ADME, and project-science discussion.",
            "selected_sections": [
                "executive_summary",
                "decision_actions",
                "uncertainties",
                "next_step_plan",
                "chemistry_intelligence",
                "evidence_linked_prioritization",
                "confidence_calibrated_prioritization",
                "technical_sections",
                "supporting_literature",
            ],
        }

    def build_executive_view(
        self,
        request: ADMERequest,
        chemistry: ChemistrySummary,
        protocol: ADMEProtocol,
        literature_search: LiteratureSearchResult,
    ) -> dict[str, object]:
        return {
            "report_mode_summary": "Executive mode compresses the report to the few actions, main risks, and next steps most useful for project-level decision-making.",
            "audience_focus": "Project lead, portfolio discussion, or management review.",
            "selected_sections": [
                "executive_summary",
                "decision_actions",
                "uncertainties",
                "next_step_plan",
                "technical_synopsis",
            ],
        }

    def build_cro_proposal_view(
        self,
        request: ADMERequest,
        chemistry: ChemistrySummary,
        protocol: ADMEProtocol,
        literature_search: LiteratureSearchResult,
    ) -> dict[str, object]:
        return {
            "report_mode_summary": "CRO proposal mode emphasizes proposed work packages, why each assay is prioritized, and what each experiment is expected to clarify.",
            "audience_focus": "CRO scoping, assay-package alignment, and work-order discussion.",
            "selected_sections": [
                "executive_summary",
                "decision_actions",
                "cro_work_packages",
                "recommended_in_vitro_studies",
                "next_step_plan",
                "condensed_evidence",
            ],
        }

    def build_regulatory_prep_view(
        self,
        request: ADMERequest,
        chemistry: ChemistrySummary,
        protocol: ADMEProtocol,
        literature_search: LiteratureSearchResult,
    ) -> dict[str, object]:
        return {
            "report_mode_summary": "Regulatory-prep mode emphasizes evidence strength, confidence caveats, translation limits, and what remains unverified.",
            "audience_focus": "More conservative internal review ahead of formal evidence packaging.",
            "selected_sections": [
                "executive_summary",
                "verify_next",
                "uncertainties",
                "confidence_calibrated_prioritization",
                "evidence_linked_prioritization",
                "translation",
                "regulatory_caveats",
            ],
        }

    def build_do_now_actions(self, chemistry: ChemistrySummary) -> list[dict[str, str]]:
        actions: list[dict[str, str]] = []
        seen: set[str] = set()
        assay_priorities = list(chemistry.assay_priorities or []) + list(chemistry.disposition_assay_priorities or [])
        for assay in self._sort_assays_for_actioning(assay_priorities):
            confidence = self._normalize_confidence(assay.get("recommendation_confidence", "medium"))
            if confidence != "high":
                continue
            assay_name = assay.get("assay_name", "Unspecified assay")
            if assay_name in seen:
                continue
            seen.add(assay_name)
            actions.append(
                {
                    "action": f"Run {assay_name}.",
                    "why_now": assay.get(
                        "why_prioritized",
                        assay.get("rationale", "This is the most direct assay for the leading chemistry-backed hypothesis."),
                    ),
                    "expected_clarification": self._build_expected_clarification(assay),
                    "confidence": confidence,
                    "linked_support": self._build_linked_support(assay),
                }
            )
            if len(actions) >= 3:
                break

        if not actions:
            for assay in self._sort_assays_for_actioning(assay_priorities):
                confidence = self._normalize_confidence(assay.get("recommendation_confidence", "medium"))
                if confidence != "medium":
                    continue
                assay_name = assay.get("assay_name", "Unspecified assay")
                if assay_name in seen:
                    continue
                seen.add(assay_name)
                actions.append(
                    {
                        "action": f"Start with {assay_name}.",
                        "why_now": assay.get(
                            "why_prioritized",
                            assay.get("rationale", "This is the clearest immediate next experiment from the current package."),
                        ),
                        "expected_clarification": self._build_expected_clarification(assay),
                        "confidence": confidence,
                        "linked_support": self._build_linked_support(assay),
                    }
                )
                break
        return actions

    def build_verify_next_actions(
        self,
        chemistry: ChemistrySummary,
        do_now_actions: list[dict[str, str]],
    ) -> list[dict[str, str]]:
        actions: list[dict[str, str]] = []
        blocked = {self._extract_assay_name(action.get("action", "")) for action in do_now_actions}
        assay_priorities = list(chemistry.assay_priorities or []) + list(chemistry.disposition_assay_priorities or [])
        for assay in self._sort_assays_for_actioning(assay_priorities):
            confidence = self._normalize_confidence(assay.get("recommendation_confidence", "medium"))
            assay_name = assay.get("assay_name", "Unspecified assay")
            if confidence != "medium" or assay_name in blocked:
                continue
            actions.append(
                {
                    "action": f"Verify with {assay_name}.",
                    "why_next": assay.get(
                        "why_prioritized",
                        assay.get("rationale", "This is relevant, but it is better used as a follow-up after the first-pass work."),
                    ),
                    "what_to_confirm": self._build_verify_goal(assay),
                    "confidence": confidence,
                    "linked_support": self._build_linked_support(assay),
                }
            )
            if len(actions) >= 3:
                break
        return actions

    def build_exploratory_followups(
        self,
        chemistry: ChemistrySummary,
        do_now_actions: list[dict[str, str]],
        verify_next_actions: list[dict[str, str]],
    ) -> list[dict[str, str]]:
        actions: list[dict[str, str]] = []
        blocked = {
            self._extract_assay_name(action.get("action", ""))
            for action in (do_now_actions + verify_next_actions)
        }
        assay_priorities = list(chemistry.assay_priorities or []) + list(chemistry.disposition_assay_priorities or [])
        for assay in self._sort_assays_for_actioning(assay_priorities):
            confidence = self._normalize_confidence(assay.get("recommendation_confidence", "exploratory"))
            assay_name = assay.get("assay_name", "Unspecified assay")
            if confidence != "exploratory" or assay_name in blocked:
                continue
            actions.append(
                {
                    "action": f"Keep {assay_name} as exploratory follow-up.",
                    "why_exploratory": assay.get(
                        "why_prioritized",
                        assay.get("rationale", "This is useful as secondary awareness rather than the first experiment to run."),
                    ),
                    "trigger_condition": self._build_exploratory_trigger(assay),
                    "confidence": confidence,
                    "linked_support": self._build_linked_support(assay),
                }
            )
            if len(actions) >= 3:
                break
        return actions

    def build_uncertainty_register(
        self,
        request: ADMERequest,
        chemistry: ChemistrySummary,
        literature_search: LiteratureSearchResult,
    ) -> list[dict[str, str]]:
        uncertainties: list[dict[str, str]] = []
        literature_summary = (literature_search.literature_confidence_summary or "").lower()
        evidence_alignment = literature_search.evidence_alignment_summary or "Species and focus alignment remain only partially established."
        records = literature_search.records

        if not request.smiles.strip():
            uncertainties.append(
                {
                    "uncertainty_label": "No-SMILES limitation",
                    "why_it_remains_uncertain": "The chemistry layer is operating without structure-resolved feature detection, so pathway and assay prioritization remain more template-led.",
                    "what_data_would_reduce_it": "Provide a valid SMILES so structure-driven hotspot and liability logic can anchor the next recommendation cycle.",
                    "current_confidence_impact": "This keeps several recommendations closer to medium or exploratory confidence.",
                }
            )
        elif request.smiles.strip() and not chemistry.smiles_valid:
            uncertainties.append(
                {
                    "uncertainty_label": "Invalid-SMILES chemistry limitation",
                    "why_it_remains_uncertain": "A SMILES string was supplied, but it could not be parsed into a stable chemistry interpretation.",
                    "what_data_would_reduce_it": "Correct the SMILES and rerun the report so structure-driven reasoning can be restored.",
                    "current_confidence_impact": "This weakens hotspot-backed prioritization and keeps chemistry confidence conservative.",
                }
            )
        elif request.smiles.strip() and not chemistry.rdkit_used:
            uncertainties.append(
                {
                    "uncertainty_label": "RDKit unavailable",
                    "why_it_remains_uncertain": "The workflow fell back to non-RDKit logic, so chemistry interpretation remains lighter than intended.",
                    "what_data_would_reduce_it": "Restore RDKit availability and rerun to regain structure-backed hotspot and disposition interpretation.",
                    "current_confidence_impact": "Structure-led priorities are retained only cautiously.",
                }
            )

        target_anchor_strength = sum(
            1
            for record in records
            if record.compound_relation in {"target_exact", "target_alias"}
        )
        if target_anchor_strength == 0 or "low" in literature_summary:
            uncertainties.append(
                {
                    "uncertainty_label": "Target-anchored literature weakness",
                    "why_it_remains_uncertain": "The retained evidence is only weakly anchored to the exact target compound or remains mostly class-level/background support.",
                    "what_data_would_reduce_it": "Stronger target-specific metabolism or disposition evidence would improve confidence calibration.",
                    "current_confidence_impact": "This keeps structure-led recommendations from being overstated as high-confidence.",
                }
            )

        if request.species.strip().lower() != "human":
            uncertainties.append(
                {
                    "uncertainty_label": "Species translation uncertainty",
                    "why_it_remains_uncertain": evidence_alignment,
                    "what_data_would_reduce_it": "Add human-relevant microsome, hepatocyte, or translation-focused follow-up before making stronger human assumptions.",
                    "current_confidence_impact": "Human-facing implications remain more provisional than the current preclinical recommendation set.",
                }
            )

        if chemistry.transporter_hints:
            uncertainties.append(
                {
                    "uncertainty_label": "Transporter involvement uncertainty",
                    "why_it_remains_uncertain": "Transporter or efflux awareness is currently structure-led and not yet strongly anchored by target-specific evidence.",
                    "what_data_would_reduce_it": "Permeability plus transporter-aware follow-up can separate passive permeability limitations from active transport effects.",
                    "current_confidence_impact": "Disposition-oriented follow-up stays medium-confidence or exploratory unless exposure data point that way.",
                }
            )

        if len(chemistry.clearance_route_hints or []) > 1:
            uncertainties.append(
                {
                    "uncertainty_label": "Clearance route ambiguity",
                    "why_it_remains_uncertain": "More than one plausible clearance route remains in play from the current chemistry and evidence package.",
                    "what_data_would_reduce_it": "Pair hepatocyte or microsome turnover with route-of-recovery or stability data to clarify which component dominates.",
                    "current_confidence_impact": "Route-specific interpretation remains less certain than the leading first-pass profiling recommendation.",
                }
            )

        if chemistry.reactive_metabolite_risks:
            uncertainties.append(
                {
                    "uncertainty_label": "Reactive metabolite uncertainty",
                    "why_it_remains_uncertain": "Reactive risk is being flagged heuristically from motif-level chemistry rather than direct trapping data.",
                    "what_data_would_reduce_it": "Reactive-metabolite trapping or orthogonal bioactivation follow-up would narrow this uncertainty.",
                    "current_confidence_impact": "Reactive-risk recommendations should be read as awareness items rather than confirmed liabilities.",
                }
            )

        if chemistry.phase2_liabilities:
            uncertainties.append(
                {
                    "uncertainty_label": "Conjugation contribution uncertainty",
                    "why_it_remains_uncertain": "Phase II handling looks plausible from the current chemistry, but the relative contribution versus oxidative clearance is not yet empirically separated.",
                    "what_data_would_reduce_it": "S9 or hepatocyte follow-up under conjugation-aware conditions would help determine how much conjugation matters.",
                    "current_confidence_impact": "Conjugation-related follow-up remains important but may sit behind first-pass oxidative profiling.",
                }
            )

        return uncertainties[:6]

    def build_next_step_plan(
        self,
        do_now_actions: list[dict[str, str]],
        verify_next_actions: list[dict[str, str]],
        exploratory_followups: list[dict[str, str]],
    ) -> list[dict[str, str]]:
        steps: list[dict[str, str]] = []
        step_number = 1
        for action in do_now_actions[:2]:
            steps.append(
                {
                    "step_number": str(step_number),
                    "recommended_action": action.get("action", "Unspecified action"),
                    "purpose": action.get("expected_clarification", "Use this to reduce the top-ranked ADME uncertainty."),
                    "confidence": action.get("confidence", "high"),
                    "dependency_or_trigger": "Run immediately because it is part of the first-pass package.",
                }
            )
            step_number += 1
        for action in verify_next_actions[:2]:
            steps.append(
                {
                    "step_number": str(step_number),
                    "recommended_action": action.get("action", "Unspecified action"),
                    "purpose": action.get("what_to_confirm", "Use this to confirm whether the secondary hypothesis should be upgraded."),
                    "confidence": action.get("confidence", "medium"),
                    "dependency_or_trigger": "Best used after the first-pass experiments clarify the leading pathway.",
                }
            )
            step_number += 1
        if exploratory_followups:
            action = exploratory_followups[0]
            steps.append(
                {
                    "step_number": str(step_number),
                    "recommended_action": action.get("action", "Unspecified action"),
                    "purpose": "Retain this as conditional follow-up rather than part of the immediate package.",
                    "confidence": action.get("confidence", "exploratory"),
                    "dependency_or_trigger": action.get("trigger_condition", "Escalate only if early data point toward this mechanism."),
                }
            )
        return steps

    def build_decision_ready_summary(
        self,
        do_now_actions: list[dict[str, str]],
        verify_next_actions: list[dict[str, str]],
        exploratory_followups: list[dict[str, str]],
        uncertainty_register: list[dict[str, str]],
        next_step_plan: list[dict[str, str]],
    ) -> dict[str, object]:
        do_now_headline = do_now_actions[0].get("action", "No immediate do-now action was identified.") if do_now_actions else "No immediate do-now action was identified."
        verify_headline = verify_next_actions[0].get("action", "No verify-next action was identified.") if verify_next_actions else "No verify-next action was identified."
        exploratory_headline = exploratory_followups[0].get("action", "No exploratory follow-up is currently emphasized.") if exploratory_followups else "No exploratory follow-up is currently emphasized."
        primary_uncertainty = uncertainty_register[0].get("uncertainty_label", "Residual uncertainty remains.") if uncertainty_register else "Residual uncertainty remains."
        step_count = len(next_step_plan)
        summary_text = (
            f"Decision-ready framing points to {do_now_headline.lower()} as the clearest immediate move. "
            f"Secondary validation should center on {verify_headline.lower()} once first-pass data arrive, while "
            f"{exploratory_headline.lower()} remains conditional rather than front-loaded. The main caveat is {primary_uncertainty.lower()}, "
            f"so the current next-step plan is intentionally staged across {step_count} ordered step{'s' if step_count != 1 else ''}."
        )
        return {
            "summary_text": summary_text,
            "primary_do_now": do_now_headline,
            "primary_verify_next": verify_headline,
            "primary_exploratory": exploratory_headline,
            "primary_uncertainty": primary_uncertainty,
        }

    @staticmethod
    def _format_executive_priority_summary(summary: dict[str, object]) -> str:
        top_priorities = summary.get("top_priorities", []) or []
        lines = ["Top 3 priorities:"]
        if top_priorities:
            for priority in top_priorities:
                lines.append(
                    f"- {priority.get('top_priority_label', 'Unspecified priority')} "
                    f"(confidence: {priority.get('confidence_level', 'medium')}). "
                    f"Why it matters: {priority.get('why_it_matters', '')} "
                    f"Evidence basis: {priority.get('evidence_basis', '')} "
                    f"Immediate action: {priority.get('immediate_action', '')}"
                )
        else:
            lines.append("- No top priority was generated.")
        lines.extend(
            [
                f"Highest-confidence action: {summary.get('highest_confidence_action', 'No high-confidence action identified.')}",
                f"Main uncertainty: {summary.get('main_uncertainty', 'Residual uncertainty remains.')}",
                f"Recommended immediate next step: {summary.get('recommended_immediate_next_step', 'Start with the most direct first-pass experiment.')}",
                f"Decision framing: {summary.get('summary_text', 'No executive summary was generated.')}",
            ]
        )
        return "\n".join(lines)

    @staticmethod
    def _format_action_section(
        title: str,
        actions: list[dict[str, str]],
        action_key: str,
        why_key: str,
        clarify_key: str,
    ) -> str:
        if not actions:
            return f"- No {title.lower()} item was generated."
        lines: list[str] = []
        for action in actions:
            lines.append(
                f"- {action.get(action_key, 'Unspecified action')} "
                f"(confidence: {action.get('confidence', 'medium')}). "
                f"{action.get(why_key, '')} "
                f"{action.get(clarify_key, '')} "
                f"Linked support: {action.get('linked_support', 'Evidence linkage remains limited.')}"
            )
        return "\n".join(lines)

    @staticmethod
    def _format_uncertainty_register(uncertainties: list[dict[str, str]]) -> str:
        if not uncertainties:
            return "- No major uncertainty was explicitly registered for this run."
        lines: list[str] = []
        for item in uncertainties:
            lines.append(
                f"- {item.get('uncertainty_label', 'Unspecified uncertainty')}: "
                f"{item.get('why_it_remains_uncertain', '')} "
                f"Data that would reduce it: {item.get('what_data_would_reduce_it', '')} "
                f"Confidence impact: {item.get('current_confidence_impact', '')}"
            )
        return "\n".join(lines)

    @staticmethod
    def _format_next_step_plan(steps: list[dict[str, str]]) -> str:
        if not steps:
            return "1. No next-step plan was generated."
        lines: list[str] = []
        for step in steps:
            lines.append(
                f"{step.get('step_number', '?')}. {step.get('recommended_action', 'Unspecified action')} "
                f"Purpose: {step.get('purpose', '')} "
                f"Confidence: {step.get('confidence', 'medium')} "
                f"Dependency or trigger: {step.get('dependency_or_trigger', '')}"
            )
        return "\n".join(lines)

    @staticmethod
    def _format_decision_ready_summary(summary: dict[str, object]) -> str:
        return str(summary.get("summary_text", "No additional decision-ready summary was generated."))

    @staticmethod
    def _sort_assays_for_actioning(assays: list[dict[str, str]]) -> list[dict[str, str]]:
        return sorted(
            assays,
            key=lambda assay: (
                -SynthesisAgent._confidence_rank(assay.get("recommendation_confidence", "medium")),
                -SynthesisAgent._priority_rank(assay.get("priority", "medium")),
                assay.get("assay_name", ""),
            ),
        )

    @staticmethod
    def _build_expected_clarification(assay: dict[str, str]) -> str:
        assay_name = assay.get("assay_name", "this assay")
        if assay.get("why_prioritized"):
            return f"This should clarify whether the leading chemistry-led hypothesis is supported in {assay_name}."
        if assay.get("disposition_basis"):
            return f"This should help separate metabolism-driven behavior from disposition-driven uncertainty in {assay_name}."
        return f"This should clarify the leading ADME uncertainty in {assay_name}."

    @staticmethod
    def _build_verify_goal(assay: dict[str, str]) -> str:
        if assay.get("disposition_basis"):
            return "Use this to confirm whether the disposition signal is strong enough to move from awareness into the core package."
        return "Use this to confirm whether the secondary pathway or assay signal should be upgraded after first-pass data."

    @staticmethod
    def _build_exploratory_trigger(assay: dict[str, str]) -> str:
        assay_name = assay.get("assay_name", "this follow-up")
        if "permeability" in assay_name.lower() or "mdck" in assay_name.lower() or "caco-2" in assay_name.lower():
            return "Escalate if early exposure, recovery, or clearance data suggest permeability or efflux may matter."
        if "protein binding" in assay_name.lower():
            return "Escalate if exposure interpretation remains unclear after first-pass turnover work."
        return "Escalate if first-pass profiling leaves the mechanism materially unresolved."

    @staticmethod
    def _build_linked_support(assay: dict[str, str]) -> str:
        support_parts: list[str] = []
        hotspots = assay.get("supporting_hotspots", []) or []
        titles = assay.get("supporting_evidence_titles", []) or []
        support_strength = assay.get("support_strength", "") or "limited"
        if hotspots:
            support_parts.append(f"structural support from {', '.join(hotspots[:2])}")
        if titles:
            support_parts.append(f"literature direction from {'; '.join(titles[:2])}")
        support_parts.append(f"support strength {support_strength}")
        return "; ".join(support_parts)

    @staticmethod
    def _extract_assay_name(action_text: str) -> str:
        text = action_text.strip().removeprefix("Run ").removeprefix("Start with ").removeprefix("Verify with ").removeprefix("Keep ")
        return text.removesuffix(".").replace(" as exploratory follow-up", "").strip()

    @staticmethod
    def _normalize_confidence(value: str) -> str:
        lowered = (value or "").strip().lower()
        if lowered in {"high", "medium", "exploratory"}:
            return lowered
        if lowered == "low":
            return "exploratory"
        return "medium"

    @staticmethod
    def _confidence_rank(value: str) -> int:
        return {
            "high": 3,
            "medium": 2,
            "exploratory": 1,
            "low": 1,
        }.get((value or "").strip().lower(), 2)

    @staticmethod
    def _priority_rank(value: str) -> int:
        return {
            "high": 3,
            "medium": 2,
            "low": 1,
        }.get((value or "").strip().lower(), 2)

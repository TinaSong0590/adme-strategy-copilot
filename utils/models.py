from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class ADMERequest:
    drug_name: str = ""
    smiles: str = ""
    species: str = "Rat"
    focus: str = "MetID"
    report_mode: str = "scientist"


@dataclass(slots=True)
class LiteratureReference:
    title: str
    source: str
    year: int
    summary: str
    authors: str = ""
    journal: str = ""
    url: str = ""
    retrieval_mode: str = "mock_fallback"
    score: float = 0.0
    base_score: float = 0.0
    focus_relevance_score: float = 0.0
    species_relevance_score: float = 0.0
    matrix_relevance_score: float = 0.0
    focus_mismatch_penalty: float = 0.0
    context_mismatch_penalty: float = 0.0
    title_exactness_boost: float = 0.0
    target_mention_only_penalty: float = 0.0
    title_compound_centrality: float = 0.0
    species_specific_exactness_boost: float = 0.0
    neighbor_suppression_penalty: float = 0.0
    final_score: float = 0.0
    query_used: str = ""
    match_type: str = "no_clear_match"
    compound_relation: str = "no_clear_compound_relation"
    title_target_status: str = "unclear_title_target_status"
    evidence_bucket: str = "background_evidence"
    article_type: str = "unknown"
    relevance_explanation: str = ""
    focus_keyword_hits: str = ""
    species_keyword_hits: str = ""
    matrix_keyword_hits: str = ""


@dataclass(slots=True)
class LiteratureSearchResult:
    records: list[LiteratureReference]
    queries_used: list[str]
    aliases_used: list[str]
    provider_used: str
    primary_provider: str
    retrieval_mode_summary: str
    focus_profile_summary: str
    focus_keyword_hits_summary: str
    focus_relevance_summary: str
    species_profile_summary: str
    matrix_profile_summary: str
    species_match_summary: str
    matrix_relevance_summary: str
    compound_relation_summary: str
    title_target_status_summary: str
    title_centric_boost_summary: str
    mention_only_penalty_summary: str
    evidence_bucket_summary: str
    neighbor_suppression_summary: str
    match_distribution_summary: str
    article_type_summary: str
    evidence_tag_summary: str = ""
    hotspot_linking_summary: str = ""
    assay_support_linking_summary: str = ""
    literature_confidence_summary: str = ""
    evidence_alignment_summary: str = ""


@dataclass(slots=True)
class ChemistrySummary:
    smiles: str = ""
    smiles_valid: bool = False
    rdkit_used: bool = False
    molecular_formula: str = ""
    molecular_weight: float | None = None
    feature_flags: list[str] | None = None
    structural_features: dict[str, bool | int | float | str] | None = None
    soft_spot_hints: list[dict[str, str]] | None = None
    phase1_liabilities: list[str] | None = None
    phase2_liabilities: list[str] | None = None
    reactive_metabolite_risks: list[str] | None = None
    cyp_preference_hints: list[dict[str, str]] | None = None
    transporter_hints: list[dict[str, str]] | None = None
    permeability_hints: list[dict[str, str]] | None = None
    clearance_route_hints: list[dict[str, str]] | None = None
    species_chemistry_interpretation: dict[str, str | list[str]] | None = None
    assay_priorities: list[dict[str, str]] | None = None
    disposition_assay_priorities: list[dict[str, str]] | None = None
    pathway_priorities: list[dict[str, str]] | None = None
    disposition_summary: dict[str, str | list[str]] | None = None
    hotspot_summary: list[dict[str, str | list[str]]] | None = None
    hotspot_priorities: list[dict[str, str | list[str]]] | None = None
    structure_to_assay_links: list[dict[str, str | list[str]]] | None = None
    chemistry_confidence_summary: dict[str, str | list[str]] | None = None
    hotspot_confidence_summary: str = ""
    recommendation_confidence_summary: dict[str, str | list[str]] | None = None
    chemistry_driven_risk_notes: list[str] | None = None
    chemistry_summary_text: str = ""
    limitations: list[str] | None = None
    protocol_implications: list[str] | None = None


@dataclass(slots=True)
class MetabolismPrediction:
    pathways: list[str]
    warnings: list[str]
    rationale: list[str]
    cyp_flags: list[str]
    clearance_risk: str
    reactive_metabolite_risk: str
    detected_features: list[str]


@dataclass(slots=True)
class ADMEProtocol:
    in_vitro: list[str]
    in_vivo: list[str]
    translation: list[str]
    risk_flags: list[str]
    assay_work_package_summary: str = ""
    proposed_first_pass_package: str = ""
    optional_followup_package: str = ""


@dataclass(slots=True)
class ADMEReport:
    report_mode: str
    report_mode_summary: str
    audience_focus: str
    selected_sections: list[str]
    assay_work_package_summary: str
    proposed_first_pass_package: str
    optional_followup_package: str
    executive_priority_summary: str
    do_now_actions: str
    verify_next_actions: str
    exploratory_followups: str
    uncertainty_register: str
    next_step_plan: str
    decision_ready_summary: str
    input_summary: dict[str, str]
    chemistry_intelligence: str
    evidence_linked_prioritization: str
    confidence_calibrated_prioritization: str
    predicted_metabolic_pathways: str
    recommended_in_vitro_studies: str
    suggested_in_vivo_design: str
    potential_risks: str
    translation_to_human: str
    literature_primary_provider: str
    literature_provider_used: str
    literature_query_set_used: str
    literature_retrieval_mode: str
    literature_focus_profile_summary: str
    literature_focus_relevance_summary: str
    literature_species_profile_summary: str
    literature_matrix_profile_summary: str
    literature_species_relevance_summary: str
    literature_matrix_relevance_summary: str
    literature_compound_relation_summary: str
    literature_title_target_status_summary: str
    literature_title_centric_boost_summary: str
    literature_mention_only_penalty_summary: str
    literature_evidence_bucket_summary: str
    literature_neighbor_suppression_summary: str
    literature_match_summary: str
    literature_article_type_summary: str
    literature_quality_summary: str
    supporting_literature: str
    disclaimer: str


@dataclass(slots=True)
class SkillDocument:
    name: str
    path: Path
    content: str
    source: str


@dataclass(slots=True)
class PipelineResult:
    request: ADMERequest
    chemistry: ChemistrySummary
    metabolism: MetabolismPrediction
    protocol: ADMEProtocol
    literature: list[LiteratureReference]
    literature_search: LiteratureSearchResult
    report: ADMEReport
    report_path: Path
    loaded_skills: dict[str, SkillDocument]

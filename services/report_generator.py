from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from utils.models import ADMEReport, ADMERequest
from utils.text import slugify


@dataclass(slots=True)
class ReportGenerator:
    reports_dir: Path

    def write_report(self, request: ADMERequest, report: ADMEReport) -> Path:
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        slug = slugify(request.drug_name or request.smiles or "unknown_compound")
        mode_slug = slugify(report.report_mode or "scientist")
        path = self.reports_dir / f"{slug}_adme_strategy_{mode_slug}.md"
        path.write_text(self.render_markdown(report), encoding="utf-8")
        return path

    @staticmethod
    def render_markdown(report: ADMEReport) -> str:
        mode = (report.report_mode or "scientist").strip().lower()
        if mode == "executive":
            return ReportGenerator.render_executive_report(report)
        if mode == "cro_proposal":
            return ReportGenerator.render_cro_proposal_report(report)
        if mode == "regulatory_prep":
            return ReportGenerator.render_regulatory_prep_report(report)
        return ReportGenerator.render_scientist_report(report)

    @staticmethod
    def render_scientist_report(report: ADMEReport) -> str:
        summary_lines = "\n".join(
            f"- {key}: {value}" for key, value in report.input_summary.items()
        )
        return f"""# Executive Decision Summary

Mode: {report.report_mode}
Audience focus: {report.audience_focus}
Mode summary: {report.report_mode_summary}

{report.executive_priority_summary}

Decision-ready take: {report.decision_ready_summary}

## What to Do Now
{report.do_now_actions}

## What to Verify Next
{report.verify_next_actions}

## Exploratory Follow-up
{report.exploratory_followups}

## Key Uncertainties
{report.uncertainty_register}

## Suggested Next-Step Plan
{report.next_step_plan}

# ADME Strategy Report

## Input Summary
{summary_lines}

## Chemistry Intelligence
{report.chemistry_intelligence}

## Evidence-Linked Prioritization
{report.evidence_linked_prioritization}

## Confidence-Calibrated Prioritization
{report.confidence_calibrated_prioritization}

## 1. Predicted Metabolic Pathways
{report.predicted_metabolic_pathways}

## 2. Recommended In Vitro Studies
{report.recommended_in_vitro_studies}

## 3. Suggested In Vivo Design
{report.suggested_in_vivo_design}

## 4. Potential Risks
{report.potential_risks}

## 5. Translation to Human
{report.translation_to_human}

## 6. Supporting Literature
Focus-aware ranking enabled: yes
Context-aware ranking enabled: yes
Target-compound prioritization enabled: yes
Title-centric target detection enabled: yes
Focus: {report.input_summary.get("Focus", "N/A")}
Species: {report.input_summary.get("Species", "N/A")}
Primary provider: {report.literature_primary_provider}
Provider used: {report.literature_provider_used}
Query set used: {report.literature_query_set_used}
Retrieval mode summary: {report.literature_retrieval_mode}
Focus profile summary: {report.literature_focus_profile_summary}
Focus relevance summary: {report.literature_focus_relevance_summary}
Species profile summary: {report.literature_species_profile_summary}
Matrix profile summary: {report.literature_matrix_profile_summary}
Species relevance summary: {report.literature_species_relevance_summary}
Matrix/context relevance summary: {report.literature_matrix_relevance_summary}
Compound relation summary: {report.literature_compound_relation_summary}
Title target status summary: {report.literature_title_target_status_summary}
Title-centric boost summary: {report.literature_title_centric_boost_summary}
Mention-only penalty summary: {report.literature_mention_only_penalty_summary}
Evidence bucket summary: {report.literature_evidence_bucket_summary}
Neighbor suppression summary: {report.literature_neighbor_suppression_summary}
Exact/alias/class-level match summary: {report.literature_match_summary}
Article type summary: {report.literature_article_type_summary}
Literature quality summary: {report.literature_quality_summary}

{report.supporting_literature}

## 7. Disclaimer
{report.disclaimer}
"""

    @staticmethod
    def render_executive_report(report: ADMEReport) -> str:
        summary_lines = "\n".join(
            f"- {key}: {value}" for key, value in report.input_summary.items()
        )
        executive_headline = ReportGenerator._take_nonempty_lines(report.executive_priority_summary, 6)
        return f"""# Executive Decision Summary

Mode: {report.report_mode}
Audience focus: {report.audience_focus}
Mode summary: {report.report_mode_summary}

{executive_headline}

Decision-ready take: {report.decision_ready_summary}

## What to Do Now
{report.do_now_actions}

## What to Verify Next
{report.verify_next_actions}

## Key Uncertainties
{report.uncertainty_register}

## Suggested Next-Step Plan
{report.next_step_plan}

## Technical Snapshot
Input context:
{summary_lines}

Pathway snapshot:
{ReportGenerator._take_bullets(report.predicted_metabolic_pathways, 3)}

Recommended study snapshot:
{ReportGenerator._take_bullets(report.recommended_in_vitro_studies, 4)}

Risk snapshot:
{ReportGenerator._take_bullets(report.potential_risks, 4)}

Translation snapshot:
{ReportGenerator._take_bullets(report.translation_to_human, 3)}

## Disclaimer
{report.disclaimer}
"""

    @staticmethod
    def render_cro_proposal_report(report: ADMEReport) -> str:
        summary_lines = "\n".join(
            f"- {key}: {value}" for key, value in report.input_summary.items()
        )
        return f"""# Executive Decision Summary

Mode: {report.report_mode}
Audience focus: {report.audience_focus}
Mode summary: {report.report_mode_summary}

{report.executive_priority_summary}

## Proposed Work Package Framing
Input context:
{summary_lines}

Assay work package summary:
{report.assay_work_package_summary}

Proposed first-pass package:
{report.proposed_first_pass_package}

Optional follow-up package:
{report.optional_followup_package}

## First-Pass Experiments
{report.do_now_actions}

## Confirmatory Follow-up
{report.verify_next_actions}

## Optional Exploratory Package
{report.exploratory_followups}

## Recommended In Vitro Studies
{report.recommended_in_vitro_studies}

## Suggested Next-Step Plan
{report.next_step_plan}

## Assay Traceability Snapshot
{ReportGenerator._extract_traceability_lines(report.evidence_linked_prioritization)}

## Key Uncertainties
{report.uncertainty_register}

## Disclaimer
{report.disclaimer}
"""

    @staticmethod
    def render_regulatory_prep_report(report: ADMEReport) -> str:
        summary_lines = "\n".join(
            f"- {key}: {value}" for key, value in report.input_summary.items()
        )
        return f"""# Executive Decision Summary

Mode: {report.report_mode}
Audience focus: {report.audience_focus}
Mode summary: {report.report_mode_summary}

{report.executive_priority_summary}

## What to Verify Next
{report.verify_next_actions}

## Key Uncertainties
{report.uncertainty_register}

## Confidence-Calibrated Prioritization
{report.confidence_calibrated_prioritization}

## Evidence-Linked Prioritization
{ReportGenerator._shorten_section(report.evidence_linked_prioritization, 10)}

## Translation to Human
{report.translation_to_human}

## Evidence Boundary Summary
Supported now:
{ReportGenerator._extract_confidence_line(report.confidence_calibrated_prioritization, "High-confidence priorities")}

Plausible but still unverified:
{ReportGenerator._extract_confidence_line(report.confidence_calibrated_prioritization, "Medium-confidence priorities")}

Exploratory only:
{ReportGenerator._extract_confidence_line(report.confidence_calibrated_prioritization, "Exploratory follow-up items")}

## Conservative Evidence Notes
Input context:
{summary_lines}

Focus-aware evidence note: {report.literature_focus_relevance_summary}

Species/context note: {report.literature_species_relevance_summary}

Literature quality note: {report.literature_quality_summary}

## Disclaimer
{report.disclaimer}
"""

    @staticmethod
    def _take_bullets(section: str, count: int) -> str:
        lines = [line for line in section.splitlines() if line.strip()]
        if not lines:
            return "- No content available."
        selected: list[str] = []
        for line in lines:
            if line.lstrip().startswith("-"):
                selected.append(line)
            if len(selected) >= count:
                break
        if not selected:
            return "\n".join(lines[:count])
        return "\n".join(selected)

    @staticmethod
    def _shorten_section(section: str, max_lines: int) -> str:
        lines = [line for line in section.splitlines() if line.strip()]
        if len(lines) <= max_lines:
            return "\n".join(lines)
        return "\n".join(lines[:max_lines]) + "\n- Additional detail retained in scientist mode."

    @staticmethod
    def _extract_traceability_lines(section: str) -> str:
        lines = [line for line in section.splitlines() if line.strip()]
        keep: list[str] = []
        capture = False
        for line in lines:
            if "Assay recommendation traceability" in line:
                capture = True
                keep.append(line)
                continue
            if capture:
                if line.startswith("- ") and "Assay recommendation traceability" not in line and keep:
                    break
                keep.append(line)
        return "\n".join(keep) if keep else ReportGenerator._take_bullets(section, 4)

    @staticmethod
    def _take_nonempty_lines(section: str, count: int) -> str:
        lines = [line for line in section.splitlines() if line.strip()]
        return "\n".join(lines[:count]) if lines else "- No content available."

    @staticmethod
    def _extract_confidence_line(section: str, label: str) -> str:
        for line in section.splitlines():
            if line.strip().startswith(f"- {label}:"):
                return line.strip()[2:]
        return f"{label}: No explicit summary available."

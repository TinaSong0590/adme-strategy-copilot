from __future__ import annotations

from dataclasses import fields
from dataclasses import dataclass

from agents.chemistry_agent import ChemistryAgent
from agents.literature_agent import LiteratureAgent
from agents.metabolism_prediction_agent import MetabolismPredictionAgent
from agents.protocol_design_agent import ProtocolDesignAgent
from agents.synthesis_agent import SynthesisAgent
from services.report_generator import ReportGenerator
from services.skill_loader import SkillLoader
from utils.models import ADMERequest, PipelineResult


@dataclass(slots=True)
class LeadAgent:
    skill_loader: SkillLoader
    chemistry_agent: ChemistryAgent
    metabolism_agent: MetabolismPredictionAgent
    literature_agent: LiteratureAgent
    protocol_design_agent: ProtocolDesignAgent
    synthesis_agent: SynthesisAgent
    report_generator: ReportGenerator

    def run(self, request: ADMERequest) -> PipelineResult:
        skill_names = [
            "adme_preclinical_design",
            "adme_metabolism_prediction_rules",
            "adme_human_translation_rules",
        ]
        loaded_skills = self.skill_loader.load_many(skill_names)
        chemistry = self.chemistry_agent.run(request)
        placeholder_metabolism = self.metabolism_agent.run(request=request, chemistry=chemistry)
        literature_search = self.literature_agent.run(request=request, metabolism=placeholder_metabolism)
        self._apply_linking(
            request=request,
            chemistry=chemistry,
            literature_search=literature_search,
        )
        metabolism = self.metabolism_agent.run(request=request, chemistry=chemistry)
        protocol = self.protocol_design_agent.run(request=request, metabolism=metabolism, chemistry=chemistry)
        report = self.synthesis_agent.run(
            request=request,
            chemistry=chemistry,
            metabolism=metabolism,
            protocol=protocol,
            literature_search=literature_search,
            skill_sources={name: doc.source for name, doc in loaded_skills.items()},
        )
        report_path = self.report_generator.write_report(request=request, report=report)
        return PipelineResult(
            request=request,
            chemistry=chemistry,
            metabolism=metabolism,
            protocol=protocol,
            literature=literature_search.records,
            literature_search=literature_search,
            report=report,
            report_path=report_path,
            loaded_skills=loaded_skills,
        )

    def _apply_linking(
        self,
        request: ADMERequest,
        chemistry,
        literature_search,
    ) -> None:
        literature_service = self.literature_agent.literature_service
        chemistry_service = self.chemistry_agent.chemistry_service
        record_dicts = [self._reference_to_dict(reference) for reference in literature_search.records]
        hotspots = chemistry.hotspot_summary or []
        if not hotspots:
            literature_search.hotspot_linking_summary = "No hotspot linking was generated because no SMILES-backed hotspot summary was available."
            literature_search.assay_support_linking_summary = "No assay support linking was generated because no chemistry-backed assay priorities were available."
            literature_search.literature_confidence_summary = "Literature confidence remained low because no SMILES-backed hotspots were available for cross-source calibration."
            literature_search.evidence_alignment_summary = "Evidence alignment remained neutral because hotspot-level cross-source linking was not available."
            chemistry.chemistry_confidence_summary = {"summary": "No hotspot chemistry confidence summary was generated."}
            chemistry.hotspot_confidence_summary = "No hotspot confidence summary was generated."
            chemistry.recommendation_confidence_summary = {
                "high_confidence_priorities": [],
                "medium_confidence_priorities": [],
                "exploratory_priorities": [],
                "confidence_caveats": "Confidence calibration was limited because hotspot-backed evidence linking was unavailable.",
            }
            return

        linked_hotspots = literature_service.link_records_to_hotspots(
            records=record_dicts,
            hotspots=hotspots,
            focus=request.focus,
            species=request.species,
        )
        evidence_confidence = literature_service.summarize_evidence_confidence(
            linked_evidence=linked_hotspots,
            species=request.species,
            focus=request.focus,
        )
        chemistry.hotspot_priorities = chemistry_service.prioritize_hotspots(
            hotspots=hotspots,
            linked_evidence=linked_hotspots,
            species=request.species,
            focus=request.focus,
        )
        for hotspot in chemistry.hotspot_priorities or []:
            label = str(hotspot.get("hotspot_label", ""))
            hotspot["evidence_confidence"] = evidence_confidence.get(label, {}).get(
                "literature_support_confidence",
                hotspot.get("evidence_support_level", "low"),
            )
        chemistry.hotspot_priorities = chemistry_service.calibrate_hotspot_confidence(
            hotspot_priorities=list(chemistry.hotspot_priorities or []),
            linked_evidence={
                label: {
                    **linked_hotspots.get(label, {}),
                    **evidence_confidence.get(label, {}),
                }
                for label in linked_hotspots
            },
            species=request.species,
            focus=request.focus,
        )
        chemistry.pathway_priorities = chemistry_service.calibrate_pathway_confidence(
            pathway_priorities=list(chemistry.pathway_priorities or []),
            linked_evidence=linked_hotspots,
            species=request.species,
            focus=request.focus,
        )

        combined_assays = list(chemistry.assay_priorities or []) + list(chemistry.disposition_assay_priorities or [])
        assay_support_links = literature_service.build_assay_support_links(
            records=record_dicts,
            assay_priorities=combined_assays,
            focus=request.focus,
            species=request.species,
        )
        chemistry.assay_priorities = chemistry_service.annotate_assay_priorities_with_support(
            assay_priorities=list(chemistry.assay_priorities or []),
            assay_support_links=assay_support_links,
            hotspots=hotspots,
        )
        chemistry.disposition_assay_priorities = chemistry_service.annotate_assay_priorities_with_support(
            assay_priorities=list(chemistry.disposition_assay_priorities or []),
            assay_support_links=assay_support_links,
            hotspots=hotspots,
        )
        chemistry.assay_priorities = chemistry_service.calibrate_assay_confidence(
            assay_priorities=list(chemistry.assay_priorities or []),
            assay_support_links=assay_support_links,
            species=request.species,
            focus=request.focus,
        )
        chemistry.disposition_assay_priorities = chemistry_service.calibrate_assay_confidence(
            assay_priorities=list(chemistry.disposition_assay_priorities or []),
            assay_support_links=assay_support_links,
            species=request.species,
            focus=request.focus,
        )
        chemistry.structure_to_assay_links = chemistry_service.map_hotspots_to_assays(
            hotspots=hotspots,
            focus=request.focus,
            species=request.species,
        )
        chemistry.chemistry_confidence_summary = chemistry_service.summarize_chemistry_confidence(
            chemistry.hotspot_priorities or []
        )
        chemistry.hotspot_confidence_summary = self._format_hotspot_confidence_summary(
            chemistry.hotspot_priorities or []
        )
        chemistry.recommendation_confidence_summary = chemistry_service.build_recommendation_confidence_summary(
            hotspot_priorities=list(chemistry.hotspot_priorities or []),
            assay_priorities=list(chemistry.assay_priorities or []) + list(chemistry.disposition_assay_priorities or []),
            pathway_priorities=list(chemistry.pathway_priorities or []),
        )

        literature_search.hotspot_linking_summary = self._format_hotspot_linking_summary(chemistry.hotspot_priorities or [])
        literature_search.assay_support_linking_summary = self._format_assay_linking_summary(
            list(chemistry.assay_priorities or []) + list(chemistry.disposition_assay_priorities or [])
        )
        literature_search.literature_confidence_summary = self._format_literature_confidence_summary(
            evidence_confidence
        )
        literature_search.evidence_alignment_summary = self._format_evidence_alignment_summary(
            evidence_confidence
        )

    @staticmethod
    def _reference_to_dict(reference) -> dict[str, object]:
        return {field.name: getattr(reference, field.name) for field in fields(reference)}

    @staticmethod
    def _format_hotspot_linking_summary(hotspot_priorities: list[dict[str, object]]) -> str:
        if not hotspot_priorities:
            return "No hotspot-backed prioritization was generated."
        top = hotspot_priorities[:3]
        return "; ".join(
            f"{item.get('hotspot_label', 'Hotspot')} ({item.get('priority', 'low')}, evidence {item.get('evidence_support_level', 'low')})"
            for item in top
        )

    @staticmethod
    def _format_assay_linking_summary(assay_priorities: list[dict[str, object]]) -> str:
        if not assay_priorities:
            return "No assay recommendation traceability was generated."
        top = assay_priorities[:4]
        return "; ".join(
            f"{item.get('assay_name', 'Assay')} ({item.get('support_strength', 'low')} support)"
            for item in top
        )

    @staticmethod
    def _format_hotspot_confidence_summary(hotspot_priorities: list[dict[str, object]]) -> str:
        if not hotspot_priorities:
            return "No hotspot confidence summary was generated."
        top = hotspot_priorities[:3]
        return "; ".join(
            f"{item.get('hotspot_label', 'Hotspot')} ({item.get('overall_confidence', 'exploratory')} overall, "
            f"chemistry {item.get('chemistry_confidence', 'low')}, evidence {item.get('evidence_confidence', 'low')})"
            for item in top
        )

    @staticmethod
    def _format_literature_confidence_summary(evidence_confidence: dict[str, object]) -> str:
        if not evidence_confidence:
            return "Literature confidence remained low because no hotspot-linked evidence bundle was available."
        return "; ".join(
            f"{label} (literature {details.get('literature_support_confidence', 'low')})"
            for label, details in list(evidence_confidence.items())[:3]
        )

    @staticmethod
    def _format_evidence_alignment_summary(evidence_confidence: dict[str, object]) -> str:
        if not evidence_confidence:
            return "Evidence alignment remained neutral because no hotspot-linked bundle was available."
        return "; ".join(
            f"{label} ({details.get('species_alignment_confidence', 'low')} species/context alignment)"
            for label, details in list(evidence_confidence.items())[:3]
        )

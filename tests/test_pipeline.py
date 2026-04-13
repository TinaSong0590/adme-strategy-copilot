from __future__ import annotations

from pathlib import Path
import unittest
from unittest.mock import patch

from agents.chemistry_agent import ChemistryAgent
from agents.lead_agent import LeadAgent
from agents.literature_agent import LiteratureAgent
from agents.metabolism_prediction_agent import MetabolismPredictionAgent
from agents.protocol_design_agent import ProtocolDesignAgent
from agents.synthesis_agent import SynthesisAgent
from services.chemistry_service import ChemistryService
from services.literature_service import LiteratureService
from services.report_generator import ReportGenerator
from services.skill_loader import SkillLoader
from utils.models import ADMERequest


class PipelineSmokeTests(unittest.TestCase):
    def test_known_compound_has_cyp3a_flag(self) -> None:
        agent = MetabolismPredictionAgent()
        result = agent.run(ADMERequest(drug_name="Ibrutinib"))
        self.assertIn("CYP3A", result.cyp_flags)

    def test_literature_agent_builds_adme_query(self) -> None:
        metabolism = MetabolismPredictionAgent().run(ADMERequest(drug_name="Ibrutinib"))
        agent = LiteratureAgent(literature_service=LiteratureService(enable_real_search=False))
        queries = agent.build_query(ADMERequest(drug_name="Ibrutinib", species="Rat", focus="MetID"), metabolism)

        self.assertIn("Ibrutinib metabolite identification", queries)
        self.assertIn("Ibrutinib metabolism", queries)

    def test_literature_service_falls_back_to_mock(self) -> None:
        service = LiteratureService(enable_real_search=True, enable_secondary_provider=False)

        with patch.object(LiteratureService, "search_europe_pmc", return_value=[]):
            results = service.search(
                query="Ibrutinib metabolism",
                max_results=3,
                drug_name="Ibrutinib",
                focus="MetID",
                species="Rat",
            )

        self.assertEqual(len(results), 3)
        self.assertTrue(all(result["retrieval_mode"] == "mock_fallback" for result in results))

    def test_literature_service_handles_real_search_exception(self) -> None:
        service = LiteratureService(enable_real_search=True, enable_secondary_provider=False)

        with patch.object(LiteratureService, "search_europe_pmc", side_effect=RuntimeError("network down")):
            results = service.search(
                query="Ibrutinib metabolism",
                max_results=3,
                drug_name="Ibrutinib",
                focus="MetID",
                species="Rat",
            )

        self.assertEqual(len(results), 3)
        self.assertTrue(all(result["retrieval_mode"] == "mock_fallback" for result in results))

    def test_literature_agent_returns_match_and_article_summaries(self) -> None:
        metabolism = MetabolismPredictionAgent().run(ADMERequest(drug_name="Ibrutinib"))
        agent = LiteratureAgent(literature_service=LiteratureService(enable_real_search=False))
        result = agent.run(ADMERequest(drug_name="Ibrutinib", species="Rat", focus="MetID"), metabolism)

        self.assertTrue(result.queries_used)
        self.assertTrue(result.aliases_used)
        self.assertTrue(result.focus_profile_summary)
        self.assertTrue(result.focus_relevance_summary)
        self.assertTrue(result.species_profile_summary)
        self.assertTrue(result.matrix_profile_summary)
        self.assertTrue(result.species_match_summary)
        self.assertTrue(result.matrix_relevance_summary)
        self.assertTrue(result.compound_relation_summary)
        self.assertTrue(result.title_target_status_summary)
        self.assertTrue(result.title_centric_boost_summary)
        self.assertTrue(result.mention_only_penalty_summary)
        self.assertTrue(result.evidence_bucket_summary)
        self.assertTrue(result.neighbor_suppression_summary)
        self.assertIn("match", result.match_distribution_summary)
        self.assertTrue(result.article_type_summary)
        self.assertTrue(result.evidence_tag_summary)
        self.assertTrue(result.literature_confidence_summary)
        self.assertTrue(result.evidence_alignment_summary)

    def test_pipeline_with_valid_smiles_includes_chemistry_intelligence(self) -> None:
        request = ADMERequest(
            drug_name="ModelCompound",
            smiles="CCN(CC)CC",
            species="Rat",
            focus="MetID",
        )
        chemistry = ChemistryAgent(chemistry_service=ChemistryService()).run(request)
        metabolism = MetabolismPredictionAgent().run(request=request, chemistry=chemistry)
        protocol = ProtocolDesignAgent().run(request=request, metabolism=metabolism, chemistry=chemistry)
        literature = LiteratureAgent(literature_service=LiteratureService(enable_real_search=False)).run(request=request, metabolism=metabolism)
        report = SynthesisAgent().run(
            request=request,
            chemistry=chemistry,
            metabolism=metabolism,
            protocol=protocol,
            literature_search=literature,
            skill_sources={},
        )
        markdown = ReportGenerator.render_markdown(report)

        self.assertEqual(report.report_mode, "scientist")
        self.assertIn("# Executive Decision Summary", markdown)
        self.assertIn("## What to Do Now", markdown)
        self.assertIn("## What to Verify Next", markdown)
        self.assertIn("## Exploratory Follow-up", markdown)
        self.assertIn("## Key Uncertainties", markdown)
        self.assertIn("## Suggested Next-Step Plan", markdown)
        self.assertIn("## Chemistry Intelligence", markdown)
        self.assertIn("RDKit used", markdown)
        self.assertIn("Pathway priorities", markdown)
        self.assertIn("CYP preference hints", markdown)
        self.assertIn("Species-aware chemistry interpretation", markdown)
        self.assertIn("Assay priorities", markdown)
        self.assertIn("Transporter hints", markdown)
        self.assertIn("Permeability hints", markdown)
        self.assertIn("Clearance-route hints", markdown)
        self.assertIn("Disposition assay priorities", markdown)
        self.assertIn("Hotspot summary", markdown)
        self.assertIn("Structure-to-assay links", markdown)
        self.assertIn("Confidence-Calibrated Prioritization", markdown)
        self.assertIn("High-confidence priorities", markdown)
        self.assertIn("Medium-confidence priorities", markdown)
        self.assertIn("Exploratory follow-up items", markdown)
        self.assertIn("Decision-ready take:", markdown)

    def test_lead_pipeline_with_valid_smiles_includes_evidence_linked_prioritization(self) -> None:
        request = ADMERequest(
            drug_name="ModelCompound",
            smiles="CCN(CC)CC",
            species="Rat",
            focus="MetID",
        )
        lead = LeadAgent(
            skill_loader=SkillLoader(
                primary_dir=Path("/home/knan/.openclaw/workspace/skills"),
                fallback_dir=Path("/home/knan/adme_strategy_copilot/skills"),
            ),
            chemistry_agent=ChemistryAgent(chemistry_service=ChemistryService()),
            metabolism_agent=MetabolismPredictionAgent(),
            literature_agent=LiteratureAgent(literature_service=LiteratureService(enable_real_search=False)),
            protocol_design_agent=ProtocolDesignAgent(),
            synthesis_agent=SynthesisAgent(),
            report_generator=ReportGenerator(reports_dir=Path("/tmp/adme_strategy_copilot_test_reports")),
        )

        result = lead.run(request)
        markdown = result.report_path.read_text(encoding="utf-8")

        self.assertTrue(result.report_path.name.endswith("_scientist.md"))
        self.assertTrue(result.chemistry.hotspot_summary)
        self.assertIsNotNone(result.chemistry.hotspot_priorities)
        self.assertIn("# Executive Decision Summary", markdown)
        self.assertIn("## What to Do Now", markdown)
        self.assertIn("## What to Verify Next", markdown)
        self.assertIn("## Exploratory Follow-up", markdown)
        self.assertIn("## Key Uncertainties", markdown)
        self.assertIn("## Suggested Next-Step Plan", markdown)
        self.assertIn("## Evidence-Linked Prioritization", markdown)
        self.assertIn("## Confidence-Calibrated Prioritization", markdown)
        self.assertIn("Hotspot priorities", markdown)
        self.assertIn("Assay recommendation traceability", markdown)
        self.assertTrue(result.chemistry.chemistry_confidence_summary)
        self.assertTrue(result.chemistry.recommendation_confidence_summary)

    def test_pipeline_without_smiles_still_runs(self) -> None:
        request = ADMERequest(drug_name="Ibrutinib", smiles="", species="Rat", focus="MetID")
        chemistry = ChemistryAgent(chemistry_service=ChemistryService()).run(request)
        metabolism = MetabolismPredictionAgent().run(request=request, chemistry=chemistry)

        self.assertFalse(chemistry.smiles_valid)
        self.assertIsNotNone(chemistry.species_chemistry_interpretation)
        self.assertIsNotNone(chemistry.disposition_summary)
        self.assertEqual(chemistry.hotspot_summary, [])
        self.assertTrue(metabolism.pathways)

        literature = LiteratureAgent(literature_service=LiteratureService(enable_real_search=False)).run(request=request, metabolism=metabolism)
        protocol = ProtocolDesignAgent().run(request=request, metabolism=metabolism, chemistry=chemistry)
        report = SynthesisAgent().run(
            request=request,
            chemistry=chemistry,
            metabolism=metabolism,
            protocol=protocol,
            literature_search=literature,
            skill_sources={},
        )
        markdown = ReportGenerator.render_markdown(report)
        self.assertIn("No-SMILES limitation", markdown)

    def test_pipeline_with_invalid_smiles_still_runs_and_reports_limitation(self) -> None:
        request = ADMERequest(drug_name="ModelCompound", smiles="bad_smiles", species="Rat", focus="MetID")
        chemistry = ChemistryAgent(chemistry_service=ChemistryService()).run(request)
        metabolism = MetabolismPredictionAgent().run(request=request, chemistry=chemistry)

        self.assertFalse(chemistry.smiles_valid)
        self.assertTrue(chemistry.limitations)
        self.assertIsNotNone(chemistry.species_chemistry_interpretation)
        self.assertIsNotNone(chemistry.disposition_summary)
        self.assertEqual(chemistry.hotspot_summary, [])
        self.assertTrue(metabolism.pathways)

        literature = LiteratureAgent(literature_service=LiteratureService(enable_real_search=False)).run(request=request, metabolism=metabolism)
        protocol = ProtocolDesignAgent().run(request=request, metabolism=metabolism, chemistry=chemistry)
        report = SynthesisAgent().run(
            request=request,
            chemistry=chemistry,
            metabolism=metabolism,
            protocol=protocol,
            literature_search=literature,
            skill_sources={},
        )
        markdown = ReportGenerator.render_markdown(report)
        self.assertIn("Invalid-SMILES chemistry limitation", markdown)

    def test_pipeline_with_rdkit_unavailable_still_runs(self) -> None:
        request = ADMERequest(drug_name="ModelCompound", smiles="CCN(CC)CC", species="Rat", focus="MetID")
        service = ChemistryService()

        with patch.object(ChemistryService, "is_rdkit_available", return_value=False):
            chemistry = ChemistryAgent(chemistry_service=service).run(request)
            metabolism = MetabolismPredictionAgent().run(request=request, chemistry=chemistry)

        self.assertFalse(chemistry.rdkit_used)
        self.assertIsNotNone(chemistry.species_chemistry_interpretation)
        self.assertIsNotNone(chemistry.disposition_summary)
        self.assertEqual(chemistry.hotspot_summary, [])
        self.assertTrue(metabolism.pathways)


class DecisionReadySynthesisTests(unittest.TestCase):
    def test_synthesis_routes_actions_by_confidence(self) -> None:
        agent = SynthesisAgent()
        chemistry = ChemistryAgent(chemistry_service=ChemistryService()).run(
            ADMERequest(drug_name="ModelCompound", smiles="CCN(CC)CC", species="Rat", focus="MetID")
        )
        chemistry.assay_priorities = [
            {
                "assay_name": "Rat liver microsomes",
                "priority": "high",
                "why_prioritized": "Oxidative metabolism is the clearest first-pass question.",
                "rationale": "Microsomal oxidation coverage is directly relevant.",
                "supporting_hotspots": ["aromatic oxidation hotspot"],
                "supporting_evidence_titles": ["Rat microsome metabolite profiling study"],
                "support_strength": "high",
                "recommendation_confidence": "high",
                "confidence_rationale": "Chemistry, species, and evidence are aligned.",
            },
            {
                "assay_name": "S9 conjugation follow-up",
                "priority": "medium",
                "why_prioritized": "Conjugation may contribute but is not yet first-line.",
                "rationale": "This is secondary to oxidative profiling.",
                "supporting_hotspots": ["phenolic conjugation hotspot"],
                "supporting_evidence_titles": ["Conjugation-aware metabolite profiling study"],
                "support_strength": "medium",
                "recommendation_confidence": "medium",
                "confidence_rationale": "Useful after first-pass turnover data.",
            },
        ]
        chemistry.disposition_assay_priorities = [
            {
                "assay_name": "MDCK-MDR1 follow-up",
                "priority": "medium",
                "why_prioritized": "Disposition uncertainty is present but not front-line.",
                "rationale": "Use only if permeability or efflux becomes relevant.",
                "supporting_hotspots": ["cationic disposition hotspot"],
                "supporting_evidence_titles": ["Transporter-aware follow-up reference"],
                "support_strength": "low",
                "recommendation_confidence": "exploratory",
                "confidence_rationale": "This is still mostly structure-led.",
                "disposition_basis": "Efflux awareness may matter if exposure is lower than expected.",
            }
        ]

        do_now = agent.build_do_now_actions(chemistry)
        verify_next = agent.build_verify_next_actions(chemistry, do_now)
        exploratory = agent.build_exploratory_followups(chemistry, do_now, verify_next)

        self.assertTrue(do_now)
        self.assertIn("Rat liver microsomes", do_now[0]["action"])
        self.assertTrue(verify_next)
        self.assertIn("S9 conjugation follow-up", verify_next[0]["action"])
        self.assertTrue(exploratory)
        self.assertIn("MDCK-MDR1 follow-up", exploratory[0]["action"])

    def test_uncertainty_register_captures_target_anchoring_and_species_translation(self) -> None:
        request = ADMERequest(drug_name="ModelCompound", smiles="CCN(CC)CC", species="Rat", focus="MetID")
        chemistry = ChemistryAgent(chemistry_service=ChemistryService()).run(request)
        metabolism = MetabolismPredictionAgent().run(request=request, chemistry=chemistry)
        literature = LiteratureAgent(literature_service=LiteratureService(enable_real_search=False)).run(request=request, metabolism=metabolism)

        uncertainties = SynthesisAgent().build_uncertainty_register(
            request=request,
            chemistry=chemistry,
            literature_search=literature,
        )
        labels = {item["uncertainty_label"] for item in uncertainties}

        self.assertIn("Target-anchored literature weakness", labels)
        self.assertIn("Species translation uncertainty", labels)

    def test_next_step_plan_keeps_exploratory_items_later(self) -> None:
        agent = SynthesisAgent()
        steps = agent.build_next_step_plan(
            do_now_actions=[
                {
                    "action": "Run Rat liver microsomes.",
                    "expected_clarification": "Clarify the leading oxidative liability.",
                    "confidence": "high",
                }
            ],
            verify_next_actions=[
                {
                    "action": "Verify with S9 conjugation follow-up.",
                    "what_to_confirm": "Clarify whether conjugation needs to be upgraded.",
                    "confidence": "medium",
                }
            ],
            exploratory_followups=[
                {
                    "action": "Keep MDCK-MDR1 follow-up as exploratory follow-up.",
                    "trigger_condition": "Escalate only if permeability concerns appear.",
                    "confidence": "exploratory",
                }
            ],
        )

        self.assertEqual(steps[0]["step_number"], "1")
        self.assertIn("Rat liver microsomes", steps[0]["recommended_action"])
        self.assertIn("exploratory", steps[-1]["confidence"])


class ReportModeTests(unittest.TestCase):
    def _build_report_for_mode(self, report_mode: str) -> tuple[ADMERequest, object, str]:
        request = ADMERequest(
            drug_name="ModelCompound",
            smiles="CCN(CC)CC",
            species="Rat",
            focus="MetID",
            report_mode=report_mode,
        )
        chemistry = ChemistryAgent(chemistry_service=ChemistryService()).run(request)
        metabolism = MetabolismPredictionAgent().run(request=request, chemistry=chemistry)
        protocol = ProtocolDesignAgent().run(request=request, metabolism=metabolism, chemistry=chemistry)
        literature = LiteratureAgent(literature_service=LiteratureService(enable_real_search=False)).run(request=request, metabolism=metabolism)
        report = SynthesisAgent().run(
            request=request,
            chemistry=chemistry,
            metabolism=metabolism,
            protocol=protocol,
            literature_search=literature,
            skill_sources={},
        )
        markdown = ReportGenerator.render_markdown(report)
        return request, report, markdown

    def test_scientist_mode_renders_full_technical_sections(self) -> None:
        _, report, markdown = self._build_report_for_mode("scientist")

        self.assertEqual(report.report_mode, "scientist")
        self.assertIn("## Chemistry Intelligence", markdown)
        self.assertIn("## Evidence-Linked Prioritization", markdown)
        self.assertIn("## Confidence-Calibrated Prioritization", markdown)

    def test_executive_mode_renders_compact_view(self) -> None:
        _, report, markdown = self._build_report_for_mode("executive")

        self.assertEqual(report.report_mode, "executive")
        self.assertIn("# Executive Decision Summary", markdown)
        self.assertIn("## What to Do Now", markdown)
        self.assertIn("## Technical Snapshot", markdown)
        self.assertNotIn("## Chemistry Intelligence", markdown)
        self.assertNotIn("## Evidence-Linked Prioritization", markdown)

    def test_cro_proposal_mode_emphasizes_work_packages(self) -> None:
        _, report, markdown = self._build_report_for_mode("cro_proposal")

        self.assertEqual(report.report_mode, "cro_proposal")
        self.assertIn("## Proposed Work Package Framing", markdown)
        self.assertIn("Assay work package summary", markdown)
        self.assertIn("Proposed first-pass package", markdown)
        self.assertIn("Optional follow-up package", markdown)
        self.assertIn("## First-Pass Experiments", markdown)
        self.assertIn("## Confirmatory Follow-up", markdown)
        self.assertIn("## Optional Exploratory Package", markdown)
        self.assertIn("## Recommended In Vitro Studies", markdown)

    def test_regulatory_prep_mode_emphasizes_uncertainty_and_confidence(self) -> None:
        _, report, markdown = self._build_report_for_mode("regulatory_prep")

        self.assertEqual(report.report_mode, "regulatory_prep")
        self.assertIn("## Key Uncertainties", markdown)
        self.assertIn("## Confidence-Calibrated Prioritization", markdown)
        self.assertIn("## Evidence Boundary Summary", markdown)
        self.assertIn("## Conservative Evidence Notes", markdown)
        self.assertNotIn("## Chemistry Intelligence", markdown)

    def test_report_file_name_includes_mode_suffix(self) -> None:
        request, report, _ = self._build_report_for_mode("executive")
        generator = ReportGenerator(reports_dir=Path("/tmp/adme_strategy_copilot_mode_reports"))

        report_path = generator.write_report(request=request, report=report)

        self.assertTrue(report_path.name.endswith("_executive.md"))

    def test_executive_mode_without_smiles_still_falls_back_cleanly(self) -> None:
        request = ADMERequest(drug_name="Ibrutinib", smiles="", species="Rat", focus="MetID", report_mode="executive")
        chemistry = ChemistryAgent(chemistry_service=ChemistryService()).run(request)
        metabolism = MetabolismPredictionAgent().run(request=request, chemistry=chemistry)
        protocol = ProtocolDesignAgent().run(request=request, metabolism=metabolism, chemistry=chemistry)
        literature = LiteratureAgent(literature_service=LiteratureService(enable_real_search=False)).run(request=request, metabolism=metabolism)
        report = SynthesisAgent().run(
            request=request,
            chemistry=chemistry,
            metabolism=metabolism,
            protocol=protocol,
            literature_search=literature,
            skill_sources={},
        )
        markdown = ReportGenerator.render_markdown(report)

        self.assertIn("# Executive Decision Summary", markdown)
        self.assertIn("## Key Uncertainties", markdown)
        self.assertIn("No-SMILES limitation", markdown)

    def test_all_modes_keep_fallback_behavior_consistent(self) -> None:
        for mode in ["scientist", "executive", "cro_proposal", "regulatory_prep"]:
            request = ADMERequest(
                drug_name="Ibrutinib",
                smiles="",
                species="Rat",
                focus="MetID",
                report_mode=mode,
            )
            chemistry = ChemistryAgent(chemistry_service=ChemistryService()).run(request)
            metabolism = MetabolismPredictionAgent().run(request=request, chemistry=chemistry)
            protocol = ProtocolDesignAgent().run(request=request, metabolism=metabolism, chemistry=chemistry)
            literature = LiteratureAgent(literature_service=LiteratureService(enable_real_search=False)).run(request=request, metabolism=metabolism)
            report = SynthesisAgent().run(
                request=request,
                chemistry=chemistry,
                metabolism=metabolism,
                protocol=protocol,
                literature_search=literature,
                skill_sources={},
            )
            markdown = ReportGenerator.render_markdown(report)

            self.assertEqual(report.report_mode, mode)
            self.assertIn("# Executive Decision Summary", markdown)
            self.assertIn("No-SMILES limitation", markdown)


if __name__ == "__main__":
    unittest.main()

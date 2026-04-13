from __future__ import annotations

import unittest
from unittest.mock import patch

from services.chemistry_service import ChemistryService


class ChemistryServiceTests(unittest.TestCase):
    def test_valid_smiles_can_be_parsed_when_rdkit_available(self) -> None:
        service = ChemistryService()
        if not service.is_rdkit_available():
            self.skipTest("RDKit unavailable in current environment.")

        mol = service.parse_smiles("CCN(CC)CC")

        self.assertIsNotNone(mol)

    def test_invalid_smiles_does_not_crash(self) -> None:
        service = ChemistryService()

        summary = service.build_chemistry_summary("not_a_real_smiles")

        self.assertFalse(summary.smiles_valid)
        self.assertTrue(summary.limitations)

    def test_rdkit_unavailable_falls_back_gracefully(self) -> None:
        service = ChemistryService()

        with patch.object(ChemistryService, "is_rdkit_available", return_value=False):
            summary = service.build_chemistry_summary("CCN(CC)CC")

        self.assertFalse(summary.rdkit_used)
        self.assertFalse(summary.smiles_valid)
        self.assertIn("RDKit unavailable", summary.limitations[0])

    def test_detects_tertiary_amine_features(self) -> None:
        service = ChemistryService()
        if not service.is_rdkit_available():
            self.skipTest("RDKit unavailable in current environment.")

        summary = service.build_chemistry_summary("CCN(CC)CC")

        self.assertTrue(summary.smiles_valid)
        self.assertTrue(summary.structural_features["tertiary_amine_present"])

    def test_detects_phenol_features(self) -> None:
        service = ChemistryService()
        if not service.is_rdkit_available():
            self.skipTest("RDKit unavailable in current environment.")

        summary = service.build_chemistry_summary("c1ccccc1O")

        self.assertTrue(summary.structural_features["phenol_present"])
        self.assertTrue(any("glucuronidation" in item.lower() for item in summary.phase2_liabilities or []))

    def test_detects_ester_features(self) -> None:
        service = ChemistryService()
        if not service.is_rdkit_available():
            self.skipTest("RDKit unavailable in current environment.")

        summary = service.build_chemistry_summary("CC(=O)OC")

        self.assertTrue(summary.structural_features["ester_present"])
        self.assertTrue(any("hydrolysis" in item.lower() for item in summary.phase1_liabilities or []))

    def test_detects_thiophene_and_sulfur_features(self) -> None:
        service = ChemistryService()
        if not service.is_rdkit_available():
            self.skipTest("RDKit unavailable in current environment.")

        summary = service.build_chemistry_summary("c1ccsc1")

        self.assertTrue(summary.structural_features["sulfur_present"])
        self.assertTrue(summary.structural_features["thiophene_like_present"])
        self.assertTrue(any("thiophene" in item.lower() for item in summary.reactive_metabolite_risks or []))

    def test_detects_carboxylic_acid_features(self) -> None:
        service = ChemistryService()
        if not service.is_rdkit_available():
            self.skipTest("RDKit unavailable in current environment.")

        summary = service.build_chemistry_summary("CC(=O)O")

        self.assertTrue(summary.structural_features["carboxylic_acid_present"])
        self.assertTrue(any("acyl glucuronidation" in item.lower() for item in summary.phase2_liabilities or []))

    def test_soft_spot_hints_include_tertiary_amine_pathway(self) -> None:
        service = ChemistryService()
        if not service.is_rdkit_available():
            self.skipTest("RDKit unavailable in current environment.")

        summary = service.build_chemistry_summary("CCN(CC)CC")

        labels = [hint["label"].lower() for hint in summary.soft_spot_hints or []]
        self.assertTrue(any("n-dealkylation" in label for label in labels))

    def test_soft_spot_hints_include_phenol_phase2_pathway(self) -> None:
        service = ChemistryService()
        if not service.is_rdkit_available():
            self.skipTest("RDKit unavailable in current environment.")

        summary = service.build_chemistry_summary("c1ccccc1O")

        labels = [hint["label"].lower() for hint in summary.soft_spot_hints or []]
        self.assertTrue(any("glucuronidation" in label or "sulfation" in label for label in labels))

    def test_tertiary_amine_triggers_cyp_preference_hint(self) -> None:
        service = ChemistryService()
        summary = service.build_chemistry_summary("CCN(CC)CC")

        labels = [hint["label"].lower() for hint in summary.cyp_preference_hints or []]
        assay_implications = [hint["assay_implication"].lower() for hint in summary.cyp_preference_hints or []]
        self.assertTrue(any("oxidative amine" in label or "broad cyp" in label for label in labels))
        self.assertTrue(any("cyp phenotyping" in implication for implication in assay_implications))

    def test_phenol_triggers_conjugation_competition_hint(self) -> None:
        service = ChemistryService()
        summary = service.build_chemistry_summary("c1ccccc1O")

        labels = [hint["label"].lower() for hint in summary.cyp_preference_hints or []]
        self.assertTrue(any("conjugation may compete" in label for label in labels))

    def test_ester_triggers_plasma_stability_assay_priority(self) -> None:
        service = ChemistryService()
        summary = service.build_chemistry_summary("CC(=O)OC")
        assay_priorities = service.infer_assay_priorities(summary.structural_features or {}, species="Human", focus="PK")

        assay_names = [item["assay_name"].lower() for item in assay_priorities]
        self.assertIn("plasma stability", assay_names)

    def test_thiophene_triggers_gsh_related_assay_suggestion(self) -> None:
        service = ChemistryService()
        summary = service.build_chemistry_summary("c1ccsc1")
        assay_priorities = service.infer_assay_priorities(summary.structural_features or {}, species="Rat", focus="MetID")

        assay_names = [item["assay_name"].lower() for item in assay_priorities]
        self.assertIn("gsh trapping consideration", assay_names)

    def test_rat_species_interpretation_emphasizes_preclinical_coverage(self) -> None:
        service = ChemistryService()
        interpretation = service.infer_species_chemistry_interpretation(
            {"aromatic_ring_count": 1, "tertiary_amine_present": True},
            "Rat",
        )

        self.assertEqual(interpretation["species_label"], "Rat")
        self.assertTrue(any("rat liver microsomes" in item.lower() for item in interpretation["preferred_contexts"]))
        self.assertTrue(any("bile" in item.lower() or "urine" in item.lower() for item in interpretation["preferred_contexts"]))

    def test_human_species_interpretation_emphasizes_translation_and_ddi(self) -> None:
        service = ChemistryService()
        interpretation = service.infer_species_chemistry_interpretation(
            {"aromatic_ring_count": 2, "tertiary_amine_present": True},
            "Human",
        )

        self.assertEqual(interpretation["species_label"], "Human")
        self.assertTrue(any("human liver microsomes" in item.lower() for item in interpretation["preferred_contexts"]))
        self.assertTrue(any("translation" in item.lower() or "human-specific" in item.lower() for item in interpretation["extrapolation_cautions"]))

    def test_unknown_species_interpretation_remains_neutral(self) -> None:
        service = ChemistryService()
        interpretation = service.infer_species_chemistry_interpretation({}, "")

        self.assertEqual(interpretation["species_label"], "Unknown")
        self.assertIn("neutral", interpretation["interpretation_summary"].lower())

    def test_metid_rat_oxidation_liabilities_prioritize_microsomes_hepatocytes_and_hrms(self) -> None:
        service = ChemistryService()
        assay_priorities = service.infer_assay_priorities(
            {"aromatic_ring_count": 1, "tertiary_amine_present": True},
            species="Rat",
            focus="MetID",
        )

        assay_names = [item["assay_name"].lower() for item in assay_priorities]
        self.assertIn("rat liver microsomes", assay_names)
        self.assertIn("rat hepatocytes", assay_names)
        self.assertIn("high-resolution ms metabolite profiling", assay_names)

    def test_human_ddi_prioritizes_cyp_phenotyping(self) -> None:
        service = ChemistryService()
        assay_priorities = service.infer_assay_priorities(
            {"aromatic_ring_count": 1, "tertiary_amine_present": True},
            species="Human",
            focus="DDI",
        )

        cyp_assays = [item for item in assay_priorities if item["assay_name"] == "CYP phenotyping"]
        self.assertTrue(cyp_assays)
        self.assertEqual(cyp_assays[0]["priority"], "high")

    def test_pathway_priorities_rank_oxidation_and_conjugation(self) -> None:
        service = ChemistryService()
        pathway_priorities = service.infer_pathway_priorities(
            {
                "aromatic_ring_count": 1,
                "tertiary_amine_present": True,
                "phenol_present": True,
            },
            species="Rat",
            focus="MetID",
        )

        pathways = [item["pathway"] for item in pathway_priorities]
        self.assertIn("Oxidative metabolism including aromatic hydroxylation", pathways)
        self.assertIn("N-dealkylation", pathways)
        self.assertIn("Conjugation including glucuronidation", pathways)

    def test_basic_nitrogen_triggers_transporter_or_efflux_awareness(self) -> None:
        service = ChemistryService()
        summary = service.build_chemistry_summary("CCN(CC)CC")

        labels = [hint["label"].lower() for hint in summary.transporter_hints or []]
        self.assertTrue(any("basic or cationic" in label or "efflux-awareness" in label for label in labels))

    def test_acid_feature_triggers_uptake_and_mixed_clearance_awareness(self) -> None:
        service = ChemistryService()
        summary = service.build_chemistry_summary("CC(=O)O")

        transporter_labels = [hint["label"].lower() for hint in summary.transporter_hints or []]
        route_labels = [hint["route_label"] for hint in summary.clearance_route_hints or []]
        self.assertTrue(any("anionic uptake" in label for label in transporter_labels))
        self.assertIn("conjugative_mixed_clearance", route_labels)

    def test_polar_feature_triggers_limited_passive_permeability_hint(self) -> None:
        service = ChemistryService()
        hints = service.infer_permeability_hints(
            {
                "tpsa": 110.0,
                "hydrogen_bond_donor_count": 2,
                "hydrogen_bond_acceptor_count": 7,
                "anionic_center_hint": True,
            }
        )

        labels = [hint["label"].lower() for hint in hints]
        self.assertTrue(any("passive permeability may be limited" in label for label in labels))

    def test_ester_triggers_hydrolytic_disposition_suggestion(self) -> None:
        service = ChemistryService()
        summary = service.build_chemistry_summary("CC(=O)OC")

        route_labels = [hint["route_label"] for hint in summary.clearance_route_hints or []]
        assay_names = [item["assay_name"].lower() for item in summary.disposition_assay_priorities or []]
        self.assertIn("hydrolytic_clearance_component", route_labels)
        self.assertIn("plasma stability", assay_names)

    def test_rat_metid_disposition_logic_emphasizes_bile_urine_feces(self) -> None:
        service = ChemistryService()
        enriched = service.build_species_chemistry_summary(
            {
                "aromatic_ring_count": 1,
                "tertiary_amine_present": True,
                "basic_nitrogen_present": True,
                "cationic_center_hint": True,
            },
            species="Rat",
            focus="MetID",
        )

        route_notes = [hint["species_context_note"].lower() for hint in enriched["clearance_route_hints"]]
        assay_names = [item["assay_name"].lower() for item in enriched["disposition_assay_priorities"]]
        self.assertTrue(any("rat" in note for note in route_notes))
        self.assertIn("bile/urine/feces recovery context", assay_names)

    def test_human_disposition_logic_keeps_translation_and_transporter_awareness(self) -> None:
        service = ChemistryService()
        enriched = service.build_species_chemistry_summary(
            {
                "aromatic_ring_count": 1,
                "tertiary_amine_present": True,
                "basic_nitrogen_present": True,
                "cationic_center_hint": True,
                "tpsa": 95.0,
            },
            species="Human",
            focus="DDI",
        )

        interpretation = enriched["species_chemistry_interpretation"]
        transporter_hints = enriched["transporter_hints"]
        self.assertTrue(any("translation" in item.lower() for item in interpretation["extrapolation_cautions"]))
        self.assertTrue(transporter_hints)

    def test_permeability_concern_adds_caco2_priority(self) -> None:
        service = ChemistryService()
        assays = service.infer_disposition_assay_priorities(
            {
                "tpsa": 100.0,
                "hydrogen_bond_donor_count": 2,
                "hydrogen_bond_acceptor_count": 7,
                "anionic_center_hint": True,
            },
            species="Human",
            focus="PK",
        )

        assay_names = [item["assay_name"] for item in assays]
        self.assertIn("Caco-2 permeability", assay_names)

    def test_efflux_awareness_adds_mdck_or_mdr1_followup(self) -> None:
        service = ChemistryService()
        assays = service.infer_disposition_assay_priorities(
            {
                "cationic_center_hint": True,
                "tertiary_amine_present": True,
                "aromatic_ring_count": 2,
                "logp_like_hint": "lipophilic",
            },
            species="Human",
            focus="PK",
        )

        assay_names = [item["assay_name"] for item in assays]
        self.assertIn("MDCK or MDR1-aware permeability follow-up", assay_names)

    def test_oxidation_dominant_concern_keeps_hepatocyte_clearance_comparison(self) -> None:
        service = ChemistryService()
        assays = service.infer_disposition_assay_priorities(
            {
                "aromatic_ring_count": 1,
                "tertiary_amine_present": True,
                "cationic_center_hint": True,
            },
            species="Rat",
            focus="MetID",
        )

        assay_names = [item["assay_name"] for item in assays]
        self.assertIn("Hepatocyte clearance comparison", assay_names)

    def test_tertiary_amine_hotspot_links_to_n_dealkylation_and_microsomes(self) -> None:
        service = ChemistryService()
        hotspots = service.build_hotspot_summary(
            features={"tertiary_amine_present": True, "basic_nitrogen_present": True},
            chemistry_summary={"feature_flags": ["tertiary_amine_present"]},
        )

        amine_hotspot = hotspots[0]
        self.assertIn("N-dealkylation", amine_hotspot["linked_pathways"])
        self.assertIn("Liver microsomes", amine_hotspot["linked_assays"])

    def test_phenol_hotspot_links_to_conjugation_assays(self) -> None:
        service = ChemistryService()
        hotspots = service.build_hotspot_summary(
            features={"phenol_present": True},
            chemistry_summary={"feature_flags": ["phenol_present"]},
        )

        labels = [hotspot["hotspot_label"] for hotspot in hotspots]
        self.assertIn("Phenolic or polar conjugation hotspot", labels)
        phenol_hotspot = next(h for h in hotspots if h["hotspot_label"] == "Phenolic or polar conjugation hotspot")
        self.assertIn("S9 or conjugation-aware incubation", phenol_hotspot["linked_assays"])

    def test_ester_hotspot_links_to_plasma_stability(self) -> None:
        service = ChemistryService()
        hotspots = service.build_hotspot_summary(
            features={"ester_present": True},
            chemistry_summary={"feature_flags": ["ester_present"]},
        )

        ester_hotspot = next(h for h in hotspots if h["hotspot_type"] == "hydrolysis_hotspot")
        self.assertIn("Plasma stability", ester_hotspot["linked_assays"])

    def test_sulfur_hotspot_links_to_gsh_awareness(self) -> None:
        service = ChemistryService()
        hotspots = service.build_hotspot_summary(
            features={"sulfur_present": True, "thiophene_like_present": True},
            chemistry_summary={"feature_flags": ["sulfur_present", "thiophene_like_present"]},
        )

        sulfur_hotspot = next(h for h in hotspots if h["hotspot_type"] == "sulfur_reactive_hotspot")
        self.assertIn("GSH trapping consideration", sulfur_hotspot["linked_assays"])

    def test_hotspot_prioritization_uses_evidence_support(self) -> None:
        service = ChemistryService()
        hotspots = [
            {
                "hotspot_label": "Tertiary or secondary amine hotspot",
                "confidence": "high",
                "rationale": "Strong chemistry support.",
                "linked_assays": ["Liver microsomes"],
                "linked_pathways": ["N-dealkylation"],
            }
        ]
        linked_evidence = {
            "Tertiary or secondary amine hotspot": {
                "support_level": "high",
                "record_titles": ["Ibrutinib metabolite identification in rat microsomes"],
            }
        }

        priorities = service.prioritize_hotspots(hotspots, linked_evidence, species="Rat", focus="MetID")

        self.assertEqual(priorities[0]["priority"], "high")
        self.assertEqual(priorities[0]["evidence_support_level"], "high")

    def test_annotate_assay_priorities_adds_traceability(self) -> None:
        service = ChemistryService()
        assays = [{"assay_name": "Rat liver microsomes", "priority": "high", "rationale": "Oxidative liability is plausible."}]
        assay_support_links = {
            "Rat liver microsomes": {
                "support_strength": "high",
                "record_titles": ["Ibrutinib metabolite identification in rat microsomes"],
                "why_prioritized": "Prioritized because oxidative chemistry and rat MetID evidence converge.",
            }
        }
        hotspots = [{"hotspot_label": "Tertiary or secondary amine hotspot", "linked_assays": ["Rat liver microsomes"]}]

        annotated = service.annotate_assay_priorities_with_support(assays, assay_support_links, hotspots)

        self.assertEqual(annotated[0]["support_strength"], "high")
        self.assertIn("Tertiary or secondary amine hotspot", annotated[0]["supporting_hotspots"])
        self.assertTrue(annotated[0]["supporting_evidence_titles"])

    def test_tertiary_amine_hotspot_has_higher_chemistry_confidence_than_vague_transporter_case(self) -> None:
        service = ChemistryService()
        amine_score = service.compute_chemistry_confidence(
            {"tertiary_amine_present": True, "basic_nitrogen_present": True},
            {"hotspot_type": "oxidative_amine_hotspot", "linked_pathways": ["N-dealkylation"], "linked_assays": ["Liver microsomes"]},
        )
        vague_score = service.compute_chemistry_confidence(
            {},
            {"hotspot_type": "general_hotspot", "confidence": "low", "linked_pathways": ["Broad metabolism screen"], "linked_assays": ["Hepatocytes"]},
        )

        self.assertGreater(amine_score, vague_score)
        self.assertEqual(service.classify_chemistry_confidence(amine_score), "high")

    def test_phenol_conjugation_hotspot_has_at_least_medium_chemistry_confidence(self) -> None:
        service = ChemistryService()
        score = service.compute_chemistry_confidence(
            {"phenol_present": True},
            {"hotspot_type": "conjugation_hotspot", "linked_pathways": ["Conjugation including glucuronidation"], "linked_assays": ["S9 or conjugation-aware incubation"]},
        )

        self.assertIn(service.classify_chemistry_confidence(score), {"high", "medium"})

    def test_calibrate_hotspot_confidence_can_reach_high_with_strong_support(self) -> None:
        service = ChemistryService()
        hotspot_priorities = [
            {
                "hotspot_label": "Tertiary or secondary amine hotspot",
                "chemistry_confidence": "high",
                "evidence_confidence": "high",
                "evidence_support_level": "high",
            }
        ]
        linked_evidence = {
            "Tertiary or secondary amine hotspot": {
                "support_level": "high",
                "literature_support_confidence": "high",
                "species_alignment_confidence": "high",
            }
        }

        calibrated = service.calibrate_hotspot_confidence(hotspot_priorities, linked_evidence, species="Rat", focus="MetID")

        self.assertEqual(calibrated[0]["overall_confidence"], "high")

    def test_calibrate_assay_confidence_keeps_transporter_followup_below_high_when_support_is_weak(self) -> None:
        service = ChemistryService()
        assays = [
            {
                "assay_name": "MDCK or MDR1-aware permeability follow-up",
                "priority": "medium",
                "supporting_hotspots": ["General chemistry hotspot"],
            }
        ]
        support_links = {
            "MDCK or MDR1-aware permeability follow-up": {
                "recommendation_confidence": "low",
            }
        }

        calibrated = service.calibrate_assay_confidence(assays, support_links, species="Human", focus="PK")

        self.assertIn(calibrated[0]["recommendation_confidence"], {"medium", "exploratory"})

    def test_build_recommendation_confidence_summary_stratifies_outputs(self) -> None:
        service = ChemistryService()
        summary = service.build_recommendation_confidence_summary(
            hotspot_priorities=[{"hotspot_label": "Amine hotspot", "overall_confidence": "high"}],
            assay_priorities=[{"assay_name": "Rat liver microsomes", "recommendation_confidence": "medium"}],
            pathway_priorities=[{"pathway": "Hydrolysis", "overall_confidence": "exploratory"}],
        )

        self.assertIn("Amine hotspot", summary["high_confidence_priorities"])
        self.assertIn("Rat liver microsomes", summary["medium_confidence_priorities"])
        self.assertIn("Hydrolysis", summary["exploratory_priorities"])


if __name__ == "__main__":
    unittest.main()

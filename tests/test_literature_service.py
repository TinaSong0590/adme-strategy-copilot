from __future__ import annotations

import unittest
from unittest.mock import Mock, patch

from services.literature_service import LiteratureService


class LiteratureServiceTests(unittest.TestCase):
    def test_get_focus_profile_for_metid(self) -> None:
        service = LiteratureService(enable_real_search=False)
        profile = service.get_focus_profile("MetID")

        self.assertEqual(profile["label"], "MetID")
        self.assertIn("metabolite identification", profile["high_priority_phrases"])
        self.assertIn("glucuronidation", profile["high_priority_terms"])

    def test_build_queries_for_metid(self) -> None:
        service = LiteratureService(enable_real_search=False)
        queries = service.build_queries(drug_name="Ibrutinib", smiles="", focus="MetID")

        self.assertEqual(
            queries,
            [
                "Ibrutinib metabolite identification",
                "Ibrutinib metabolism",
                "Ibrutinib biotransformation",
                "Ibrutinib ADME",
            ],
        )

    def test_extract_compound_aliases(self) -> None:
        service = LiteratureService(enable_real_search=False)
        aliases = service.extract_compound_aliases("ABT-199")

        self.assertIn("ABT-199", aliases)
        self.assertIn("abt-199", aliases)
        self.assertIn("ABT199", aliases)
        self.assertIn("abt199", aliases)

    def test_classify_match_type_prefers_exact_match(self) -> None:
        service = LiteratureService(enable_real_search=False)
        aliases = service.extract_compound_aliases("Ibrutinib")

        match_type = service.classify_match_type(
            record={
                "title": "Ibrutinib pharmacokinetics in healthy subjects",
                "summary": "A clinical PK study for ibrutinib.",
            },
            drug_name="Ibrutinib",
            aliases=aliases,
        )

        self.assertEqual(match_type, "exact_name_match")

    def test_classify_match_type_returns_class_level_for_neighbor_compound(self) -> None:
        service = LiteratureService(enable_real_search=False)
        aliases = service.extract_compound_aliases("Ibrutinib")

        match_type = service.classify_match_type(
            record={
                "title": "In vitro metabolism studies of covalent kinase inhibitors",
                "summary": "A class-level ADME comparison across several covalent drugs.",
            },
            drug_name="Ibrutinib",
            aliases=aliases,
        )

        self.assertEqual(match_type, "class_level_match")

    def test_classify_compound_relation_target_exact(self) -> None:
        service = LiteratureService(enable_real_search=False)
        aliases = service.extract_compound_aliases("Ibrutinib")

        relation = service.classify_compound_relation(
            record={
                "title": "Ibrutinib metabolite identification in rat microsomes",
                "summary": "Direct target-compound MetID study.",
            },
            drug_name="Ibrutinib",
            aliases=aliases,
        )

        self.assertEqual(relation, "target_exact")

    def test_classify_compound_relation_target_alias(self) -> None:
        service = LiteratureService(enable_real_search=False)
        aliases = service.extract_compound_aliases("ABT-199")

        relation = service.classify_compound_relation(
            record={
                "title": "ABT199 metabolism in human hepatocytes",
                "summary": "Alias-form target-compound study.",
            },
            drug_name="ABT-199",
            aliases=aliases,
        )

        self.assertEqual(relation, "target_alias")

    def test_classify_compound_relation_neighbor_compound(self) -> None:
        service = LiteratureService(enable_real_search=False)
        aliases = service.extract_compound_aliases("Ibrutinib")

        relation = service.classify_compound_relation(
            record={
                "title": "Remibrutinib metabolite profiling in rat liver microsomes",
                "summary": "Neighbor BTK inhibitor MetID study.",
            },
            drug_name="Ibrutinib",
            aliases=aliases,
        )

        self.assertEqual(relation, "neighbor_compound")

    def test_classify_compound_relation_ambiguous_context(self) -> None:
        service = LiteratureService(enable_real_search=False)
        aliases = service.extract_compound_aliases("Ibrutinib")

        relation = service.classify_compound_relation(
            record={
                "title": "Ibrutinib versus acalabrutinib metabolism in rat microsomes",
                "summary": "Comparison across BTK inhibitors.",
            },
            drug_name="Ibrutinib",
            aliases=aliases,
        )

        self.assertEqual(relation, "ambiguous_compound_context")

    def test_classify_title_target_status_target_exact_in_title(self) -> None:
        service = LiteratureService(enable_real_search=False)
        aliases = service.extract_compound_aliases("Ibrutinib")

        status = service.classify_title_target_status(
            record={
                "title": "Ibrutinib metabolite identification in rat hepatocytes",
                "summary": "Strong MetID study.",
            },
            drug_name="Ibrutinib",
            aliases=aliases,
        )

        self.assertEqual(status, "target_exact_in_title")

    def test_classify_title_target_status_target_alias_in_title(self) -> None:
        service = LiteratureService(enable_real_search=False)
        aliases = service.extract_compound_aliases("ABT-199")

        status = service.classify_title_target_status(
            record={
                "title": "ABT199 metabolism in human liver microsomes",
                "summary": "Alias-form title hit.",
            },
            drug_name="ABT-199",
            aliases=aliases,
        )

        self.assertEqual(status, "target_alias_in_title")

    def test_classify_title_target_status_target_only_in_abstract(self) -> None:
        service = LiteratureService(enable_real_search=False)
        aliases = service.extract_compound_aliases("Ibrutinib")

        status = service.classify_title_target_status(
            record={
                "title": "Metabolite profiling in rat liver microsomes",
                "summary": "Ibrutinib was used as the target compound in this MetID study.",
                "compound_relation": "target_exact",
            },
            drug_name="Ibrutinib",
            aliases=aliases,
        )

        self.assertEqual(status, "target_only_in_abstract_or_summary")

    def test_classify_title_target_status_non_target_title_center(self) -> None:
        service = LiteratureService(enable_real_search=False)
        aliases = service.extract_compound_aliases("Ibrutinib")

        status = service.classify_title_target_status(
            record={
                "title": "Remibrutinib metabolite profiling in rat liver microsomes",
                "summary": "Ibrutinib is mentioned as a comparator.",
                "compound_relation": "neighbor_compound",
            },
            drug_name="Ibrutinib",
            aliases=aliases,
        )

        self.assertEqual(status, "non_target_title_center")

    def test_classify_title_target_status_unclear(self) -> None:
        service = LiteratureService(enable_real_search=False)
        aliases = service.extract_compound_aliases("Ibrutinib")

        status = service.classify_title_target_status(
            record={
                "title": "Preclinical metabolism workflow optimization",
                "summary": "Generic DMPK assay discussion.",
            },
            drug_name="Ibrutinib",
            aliases=aliases,
        )

        self.assertEqual(status, "unclear_title_target_status")

    def test_classify_article_type(self) -> None:
        service = LiteratureService(enable_real_search=False)

        self.assertEqual(
            service.classify_article_type({"title": "A mini-review of kinase inhibitor metabolism", "summary": ""}),
            "review",
        )
        self.assertEqual(
            service.classify_article_type({"title": "Phase II trial of Ibrutinib", "summary": ""}),
            "clinical_study",
        )
        self.assertEqual(
            service.classify_article_type({"title": "Microsome study of Ibrutinib biotransformation", "summary": ""}),
            "preclinical_study",
        )

    def test_apply_exact_match_filter_prefers_exact_over_class_level(self) -> None:
        service = LiteratureService(enable_real_search=False)
        records = [
            {"title": "Class level paper", "match_type": "class_level_match"},
            {"title": "Exact paper", "match_type": "exact_name_match"},
            {"title": "Noise paper", "match_type": "no_clear_match"},
        ]

        filtered = service.apply_exact_match_filter(records=records, drug_name="Ibrutinib", focus="MetID")

        self.assertEqual(filtered[0]["title"], "Exact paper")
        self.assertEqual(filtered[1]["title"], "Class level paper")

    def test_normalize_record_returns_complete_structure(self) -> None:
        service = LiteratureService(enable_real_search=False)

        record = service.normalize_record(
            raw={
                "title": "A Europe PMC title",
                "source": "Europe PMC",
                "pubYear": "2024",
                "abstractText": "Useful ADME abstract.",
                "authorString": "A Author, B Author",
                "journalTitle": "Drug Metabolism Journal",
                "pmid": "123456",
            },
            retrieval_mode="europe_pmc",
            query_used="Ibrutinib metabolism",
        )

        self.assertEqual(record["title"], "A Europe PMC title")
        self.assertEqual(record["source"], "Europe PMC")
        self.assertEqual(record["year"], 2024)
        self.assertEqual(record["summary"], "Useful ADME abstract.")
        self.assertEqual(record["authors"], "A Author, B Author")
        self.assertEqual(record["journal"], "Drug Metabolism Journal")
        self.assertEqual(record["retrieval_mode"], "europe_pmc")
        self.assertEqual(record["query_used"], "Ibrutinib metabolism")
        self.assertEqual(record["match_type"], "no_clear_match")
        self.assertEqual(record["article_type"], "unknown")
        self.assertIn("123456", record["url"])

    def test_compute_focus_relevance_rewards_metid_terms(self) -> None:
        service = LiteratureService(enable_real_search=False)
        record = {
            "title": "Ibrutinib metabolite identification by LC-MS/MS",
            "summary": "Microsome and hepatocyte metabolite profiling study.",
            "article_type": "preclinical_study",
        }

        score = service.compute_focus_relevance(record=record, focus="MetID")

        self.assertGreater(score, 10.0)

    def test_compute_penalty_for_focus_mismatch_penalizes_weak_metid_exact_clinical(self) -> None:
        service = LiteratureService(enable_real_search=False)
        record = {
            "title": "Ibrutinib oral formulation study",
            "summary": "Clinical exposure and administration outcomes.",
            "match_type": "exact_name_match",
            "article_type": "clinical_study",
        }

        penalty = service.compute_penalty_for_focus_mismatch(record=record, focus="MetID")

        self.assertGreaterEqual(penalty, 8.0)

    def test_detect_title_compound_centrality_handles_multi_drug_title(self) -> None:
        service = LiteratureService(enable_real_search=False)
        aliases = service.extract_compound_aliases("Ibrutinib")
        record = {
            "title": "Ibrutinib and acalabrutinib metabolism in rat microsomes",
            "summary": "Comparative MetID paper.",
            "title_target_status": "target_exact_in_title",
        }

        centrality = service.detect_title_compound_centrality(record=record, drug_name="Ibrutinib", aliases=aliases)

        self.assertLess(centrality, 0.9)
        self.assertGreater(centrality, 0.4)

    def test_rerank_records_prefers_exact_original_research_over_review(self) -> None:
        service = LiteratureService(enable_real_search=False)
        records = [
            {
                "title": "Review of kinase inhibitor metabolism",
                "summary": "A broad ADME review across kinase inhibitors.",
                "year": 2025,
                "retrieval_mode": "europe_pmc",
                "query_used": "Ibrutinib metabolism",
            },
            {
                "title": "Ibrutinib metabolism in human liver microsomes",
                "summary": "Original in vitro study describing ibrutinib metabolite formation.",
                "year": 2022,
                "retrieval_mode": "europe_pmc",
                "query_used": "Ibrutinib metabolism",
            },
        ]

        ranked = service.rerank_records(records=records, drug_name="Ibrutinib", focus="MetID", max_results=2)

        self.assertEqual(ranked[0]["match_type"], "exact_name_match")
        self.assertEqual(ranked[0]["article_type"], "preclinical_study")
        self.assertGreater(ranked[0]["final_score"], ranked[1]["final_score"])

    def test_exact_weak_metid_article_does_not_beat_exact_strong_metid_article(self) -> None:
        service = LiteratureService(enable_real_search=False)
        records = [
            {
                "title": "Ibrutinib oral suspension bioavailability study",
                "summary": "Clinical administration and exposure study in healthy volunteers.",
                "year": 2025,
                "retrieval_mode": "europe_pmc",
                "query_used": "Ibrutinib metabolism",
            },
            {
                "title": "Ibrutinib metabolite identification in human hepatocytes by LC-MS/MS",
                "summary": "Metabolite profiling and biotransformation characterization in hepatocyte and microsome systems.",
                "year": 2023,
                "retrieval_mode": "europe_pmc",
                "query_used": "Ibrutinib metabolism",
            },
        ]

        ranked = service.rerank_records(records=records, drug_name="Ibrutinib", focus="MetID", max_results=2)

        self.assertIn("metabolite identification", ranked[0]["title"].lower())
        self.assertGreater(ranked[0]["focus_relevance_score"], ranked[1]["focus_relevance_score"])

    def test_strong_class_level_metid_can_beat_weak_exact_metid(self) -> None:
        service = LiteratureService(enable_real_search=False)
        records = [
            {
                "title": "Ibrutinib oral formulation study",
                "summary": "Clinical administration experience in volunteers.",
                "year": 2025,
                "retrieval_mode": "europe_pmc",
                "query_used": "Ibrutinib metabolism",
            },
            {
                "title": "Metabolite identification workflow for covalent inhibitors using hepatocytes and LC-MS/MS",
                "summary": "Strong metabolite profiling, microsome and biotransformation context for covalent kinase inhibitors.",
                "year": 2024,
                "retrieval_mode": "europe_pmc",
                "query_used": "Ibrutinib metabolism",
            },
        ]

        ranked = service.rerank_records(records=records, drug_name="Ibrutinib", focus="MetID", max_results=2)

        self.assertEqual(ranked[0]["match_type"], "class_level_match")
        self.assertGreater(ranked[0]["final_score"], ranked[1]["final_score"])

    def test_rerank_can_fall_back_to_class_level_when_no_exact_match(self) -> None:
        service = LiteratureService(enable_real_search=False)
        records = [
            {
                "title": "Covalent inhibitor metabolism overview",
                "summary": "Class-level DMPK summary for covalent small molecules.",
                "year": 2024,
                "retrieval_mode": "europe_pmc",
                "query_used": "Ibrutinib metabolism",
            }
        ]

        ranked = service.rerank_records(records=records, drug_name="Ibrutinib", focus="MetID", max_results=1)

        self.assertEqual(ranked[0]["match_type"], "class_level_match")

    def test_focus_profiles_for_pk_ddi_safety(self) -> None:
        service = LiteratureService(enable_real_search=False)

        pk_score = service.compute_focus_relevance(
            {"title": "Ibrutinib pharmacokinetics with AUC and Cmax", "summary": "Exposure and clearance analysis.", "article_type": "clinical_study"},
            "PK",
        )
        ddi_score = service.compute_focus_relevance(
            {"title": "Ibrutinib CYP3A drug-drug interaction study", "summary": "CYP inhibition and transporter risk.", "article_type": "clinical_study"},
            "DDI",
        )
        safety_score = service.compute_focus_relevance(
            {"title": "Reactive metabolite and glutathione conjugate formation of Ibrutinib", "summary": "Bioactivation and toxicity assessment.", "article_type": "preclinical_study"},
            "Safety",
        )

        self.assertGreater(pk_score, 5.0)
        self.assertGreater(ddi_score, 5.0)
        self.assertGreater(safety_score, 5.0)

    def test_explain_relevance_mentions_match_and_type(self) -> None:
        service = LiteratureService(enable_real_search=False)
        record = {
            "title": "Ibrutinib metabolism in rat hepatocytes",
            "summary": "Preclinical metabolite identification work.",
            "year": 2023,
            "match_type": "exact_name_match",
            "article_type": "preclinical_study",
            "focus_relevance_score": 12.0,
            "species_keyword_hits": "rat, rat hepatocyte",
            "matrix_keyword_hits": "hepatocyte, metabolite identification",
            "focus_mismatch_penalty": 0.0,
            "context_mismatch_penalty": 0.0,
        }

        explanation = service.explain_relevance(record=record, drug_name="Ibrutinib", focus="MetID", species="Rat")

        self.assertIn("Exact target-compound match", explanation)
        self.assertIn("preclinical_study", explanation)
        self.assertIn("Strong MetID-specific signals", explanation)
        self.assertIn("aligns with Rat", explanation)

    def test_search_europe_pmc_returns_empty_on_http_failure(self) -> None:
        service = LiteratureService(enable_real_search=True)
        fake_requests = Mock()
        fake_requests.get.side_effect = RuntimeError("timeout")

        with patch("services.literature_service.requests", fake_requests):
            results = service.search_europe_pmc(query="Ibrutinib metabolism", max_results=2)

        self.assertEqual(results, [])

    def test_search_returns_real_results_when_provider_succeeds(self) -> None:
        service = LiteratureService(enable_real_search=True)
        fake_response = Mock()
        fake_response.raise_for_status.return_value = None
        fake_response.json.return_value = {
            "resultList": {
                "result": [
                    {
                        "title": "Ibrutinib metabolism study",
                        "source": "MED",
                        "pubYear": "2022",
                        "abstractText": "Real Europe PMC record.",
                        "authorString": "A Author",
                        "journalTitle": "Clin PK",
                        "pmid": "999999",
                    }
                ]
            }
        }
        fake_requests = Mock()
        fake_requests.get.return_value = fake_response

        with patch("services.literature_service.requests", fake_requests):
            results = service.search(
                query="Ibrutinib metabolism",
                max_results=2,
                drug_name="Ibrutinib",
                focus="MetID",
                species="Rat",
            )

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["retrieval_mode"], "europe_pmc")

    def test_secondary_provider_is_used_when_primary_returns_empty(self) -> None:
        service = LiteratureService(
            enable_real_search=True,
            provider="europe_pmc",
            secondary_provider="pubmed",
            enable_secondary_provider=True,
        )

        with patch.object(LiteratureService, "search_europe_pmc", return_value=[]):
            with patch.object(
                LiteratureService,
                "search_pubmed",
                return_value=[
                    {
                        "title": "Ibrutinib CYP3A interaction study",
                        "source": "PubMed",
                        "year": 2024,
                        "summary": "Drug-drug interaction study.",
                        "authors": "A Author",
                        "journal": "Clin Pharmacol",
                        "url": "https://pubmed.ncbi.nlm.nih.gov/123/",
                        "retrieval_mode": "pubmed",
                        "score": 0.0,
                        "query_used": "Ibrutinib drug-drug interaction",
                        "match_type": "exact_name_match",
                        "article_type": "clinical_study",
                        "relevance_explanation": "Exact clinical DDI hit.",
                    }
                ],
            ):
                result = service.search_compound(drug_name="Ibrutinib", smiles="", focus="DDI", species="Rat", max_results=2)

        self.assertEqual(result.provider_used, "pubmed")
        self.assertEqual(result.records[0].retrieval_mode, "pubmed")

    def test_search_compound_falls_back_to_mock_when_providers_fail(self) -> None:
        service = LiteratureService(
            enable_real_search=True,
            provider="europe_pmc",
            secondary_provider="pubmed",
            enable_secondary_provider=True,
        )

        with patch.object(LiteratureService, "search_europe_pmc", return_value=[]):
            with patch.object(LiteratureService, "search_pubmed", return_value=[]):
                result = service.search_compound(drug_name="Ibrutinib", smiles="", focus="MetID", species="Rat", max_results=2)

        self.assertEqual(result.provider_used, "mock_fallback")
        self.assertTrue(all(record.retrieval_mode == "mock_fallback" for record in result.records))

    def test_get_species_profile_for_human_rat_dog(self) -> None:
        service = LiteratureService(enable_real_search=False)

        human = service.get_species_profile("Human")
        rat = service.get_species_profile("Rat")
        dog = service.get_species_profile("Dog")

        self.assertIn("human liver microsomes", human["phrases"])
        self.assertIn("rlm", rat["aliases"])
        self.assertIn("canine", dog["terms"])

    def test_get_matrix_profile_for_all_focuses(self) -> None:
        service = LiteratureService(enable_real_search=False)

        metid = service.get_matrix_profile("MetID")
        pk = service.get_matrix_profile("PK")
        ddi = service.get_matrix_profile("DDI")
        safety = service.get_matrix_profile("Safety")

        self.assertIn("lc-ms", metid["phrases"])
        self.assertIn("plasma", pk["terms"])
        self.assertIn("interaction study", ddi["phrases"])
        self.assertIn("glutathione conjugate", safety["phrases"])

    def test_compute_species_relevance_rewards_rat_context(self) -> None:
        service = LiteratureService(enable_real_search=False)
        record = {
            "title": "Ibrutinib metabolism in rat liver microsomes and rat hepatocytes",
            "summary": "Rat bile and rat urine metabolite profiling study.",
        }

        score = service.compute_species_relevance(record=record, species="Rat")

        self.assertGreater(score, 8.0)
        self.assertIn("rat", record["species_keyword_hits"])

    def test_compute_matrix_relevance_rewards_metid_context(self) -> None:
        service = LiteratureService(enable_real_search=False)
        record = {
            "title": "Ibrutinib metabolite identification in microsome, hepatocyte, bile, urine, and feces by LC-MS/MS",
            "summary": "Mass spectrometry profiling across plasma and S9 systems.",
        }

        score = service.compute_matrix_relevance(record=record, focus="MetID")

        self.assertGreater(score, 12.0)
        self.assertIn("lc-ms", record["matrix_keyword_hits"])

    def test_exact_metid_with_correct_rat_context_beats_wrong_species_clinical(self) -> None:
        service = LiteratureService(enable_real_search=False)
        records = [
            {
                "title": "Ibrutinib pharmacokinetics in healthy human volunteers",
                "summary": "Clinical study with exposure and tolerability results.",
                "year": 2024,
                "retrieval_mode": "europe_pmc",
                "query_used": "Ibrutinib metabolism",
            },
            {
                "title": "Ibrutinib metabolite identification in rat liver microsomes by LC-MS/MS",
                "summary": "Rat hepatocyte, bile, urine, and feces metabolite profiling study.",
                "year": 2023,
                "retrieval_mode": "europe_pmc",
                "query_used": "Ibrutinib metabolite identification",
            },
        ]

        ranked = service.rerank_records(records=records, drug_name="Ibrutinib", focus="MetID", species="Rat", max_results=2)

        self.assertIn("rat liver microsomes", ranked[0]["title"].lower())
        self.assertGreater(ranked[0]["species_relevance_score"], ranked[1]["species_relevance_score"])
        self.assertGreater(ranked[0]["matrix_relevance_score"], ranked[1]["matrix_relevance_score"])

    def test_target_exact_rat_context_gets_species_specific_exactness_boost(self) -> None:
        service = LiteratureService(enable_real_search=False)
        records = [
            {
                "title": "Ibrutinib metabolite identification in rat liver microsomes by LC-MS/MS",
                "summary": "Rat hepatocyte, bile, and urine metabolite profiling study.",
                "year": 2024,
                "retrieval_mode": "europe_pmc",
                "query_used": "Ibrutinib metabolite identification",
            }
        ]

        ranked = service.rerank_records(records=records, drug_name="Ibrutinib", focus="MetID", species="Rat", max_results=1)

        self.assertEqual(ranked[0]["compound_relation"], "target_exact")
        self.assertGreater(ranked[0]["species_specific_exactness_boost"], 0.0)
        self.assertEqual(ranked[0]["evidence_bucket"], "core_target_evidence")

    def test_title_exact_target_article_beats_abstract_mention_only_article(self) -> None:
        service = LiteratureService(enable_real_search=False)
        records = [
            {
                "title": "Metabolite profiling in rat liver microsomes",
                "summary": "Ibrutinib metabolite identification in rat bile and urine by LC-MS/MS.",
                "year": 2025,
                "retrieval_mode": "europe_pmc",
                "query_used": "Ibrutinib metabolite identification",
            },
            {
                "title": "Ibrutinib metabolite identification in rat liver microsomes",
                "summary": "Direct target-centered MetID study with LC-MS/MS and urine profiling.",
                "year": 2024,
                "retrieval_mode": "europe_pmc",
                "query_used": "Ibrutinib metabolite identification",
            },
        ]

        ranked = service.rerank_records(records=records, drug_name="Ibrutinib", focus="MetID", species="Rat", max_results=2)

        self.assertEqual(ranked[0]["title_target_status"], "target_exact_in_title")
        self.assertGreater(ranked[0]["title_exactness_boost"], ranked[1]["title_exactness_boost"])
        self.assertGreater(ranked[1]["target_mention_only_penalty"], 0.0)

    def test_non_target_title_center_cannot_enter_core_target_evidence(self) -> None:
        service = LiteratureService(enable_real_search=False)
        records = [
            {
                "title": "Remibrutinib metabolite profiling in rat liver microsomes",
                "summary": "Ibrutinib is mentioned only as a comparator in the abstract.",
                "year": 2025,
                "retrieval_mode": "europe_pmc",
                "query_used": "Ibrutinib metabolite identification",
            },
            {
                "title": "Ibrutinib metabolism in rat hepatocytes",
                "summary": "Direct target MetID evidence.",
                "year": 2024,
                "retrieval_mode": "europe_pmc",
                "query_used": "Ibrutinib metabolism",
            },
        ]

        ranked = service.rerank_records(records=records, drug_name="Ibrutinib", focus="MetID", species="Rat", max_results=2)

        neighbor_record = next(record for record in ranked if record["title"].startswith("Remibrutinib"))
        self.assertEqual(neighbor_record["title_target_status"], "non_target_title_center")
        self.assertNotEqual(neighbor_record["evidence_bucket"], "core_target_evidence")

    def test_class_level_strong_context_can_rise_but_not_beat_strong_exact_context(self) -> None:
        service = LiteratureService(enable_real_search=False)
        records = [
            {
                "title": "Ibrutinib metabolite identification in rat hepatocytes by LC-MS/MS",
                "summary": "Exact compound study with rat microsome and bile metabolite characterization.",
                "year": 2024,
                "retrieval_mode": "europe_pmc",
                "query_used": "Ibrutinib metabolite identification",
            },
            {
                "title": "Metabolite profiling workflow for covalent kinase inhibitors in rat hepatocytes and microsomes",
                "summary": "Strong class-level MetID workflow with LC-MS/MS and rat urine context.",
                "year": 2025,
                "retrieval_mode": "europe_pmc",
                "query_used": "Ibrutinib metabolism",
            },
            {
                "title": "Ibrutinib clinical dosing study in patients",
                "summary": "Exact-name clinical article with limited metabolism content.",
                "year": 2025,
                "retrieval_mode": "europe_pmc",
                "query_used": "Ibrutinib metabolism",
            },
        ]

        ranked = service.rerank_records(records=records, drug_name="Ibrutinib", focus="MetID", species="Rat", max_results=3)

        self.assertEqual(ranked[0]["match_type"], "exact_name_match")
        self.assertEqual(ranked[1]["match_type"], "class_level_match")
        self.assertGreater(ranked[1]["final_score"], ranked[2]["final_score"])

    def test_neighbor_compound_strong_metid_does_not_beat_target_exact_strong_context(self) -> None:
        service = LiteratureService(enable_real_search=False)
        records = [
            {
                "title": "Remibrutinib metabolite profiling in rat liver microsomes by LC-MS/MS",
                "summary": "Strong rat microsome and bile MetID context for a neighbor BTK inhibitor.",
                "year": 2025,
                "retrieval_mode": "europe_pmc",
                "query_used": "Ibrutinib metabolism",
            },
            {
                "title": "Ibrutinib metabolite identification in rat hepatocytes by LC-MS/MS",
                "summary": "Target-compound rat microsome and urine metabolite characterization.",
                "year": 2024,
                "retrieval_mode": "europe_pmc",
                "query_used": "Ibrutinib metabolite identification",
            },
        ]

        ranked = service.rerank_records(records=records, drug_name="Ibrutinib", focus="MetID", species="Rat", max_results=2)

        self.assertEqual(ranked[0]["compound_relation"], "target_exact")
        self.assertEqual(ranked[1]["compound_relation"], "neighbor_compound")
        self.assertEqual(ranked[1]["evidence_bucket"], "neighbor_supporting_evidence")
        self.assertGreater(ranked[0]["final_score"], ranked[1]["final_score"])

    def test_explanation_mentions_species_and_matrix_logic(self) -> None:
        service = LiteratureService(enable_real_search=False)
        record = {
            "title": "Ibrutinib pharmacokinetics in human subjects",
            "summary": "Clinical exposure study with limited metabolism discussion.",
            "year": 2024,
            "match_type": "exact_name_match",
            "article_type": "clinical_study",
            "focus_relevance_score": 1.5,
            "focus_mismatch_penalty": 8.0,
            "species_keyword_hits": "none",
            "matrix_keyword_hits": "none",
            "context_mismatch_penalty": 5.0,
        }

        explanation = service.explain_relevance(record=record, drug_name="Ibrutinib", focus="MetID", species="Rat")

        self.assertIn("limited Rat-specific context", explanation)
        self.assertIn("limited matrix/context support", explanation)
        self.assertIn("focus mismatch penalty", explanation)

    def test_split_target_vs_supporting_evidence_keeps_neighbor_as_supporting_when_target_is_sufficient(self) -> None:
        service = LiteratureService(enable_real_search=False)
        split = service.split_target_vs_supporting_evidence(
            records=[
                {
                    "compound_relation": "target_exact",
                    "focus_relevance_score": 10.0,
                    "matrix_relevance_score": 8.0,
                    "title_target_status": "target_exact_in_title",
                    "title_compound_centrality": 0.95,
                },
                {
                    "compound_relation": "target_alias",
                    "focus_relevance_score": 6.0,
                    "matrix_relevance_score": 4.0,
                    "title_target_status": "target_alias_in_title",
                    "title_compound_centrality": 0.85,
                },
                {"compound_relation": "neighbor_compound", "focus_relevance_score": 12.0, "matrix_relevance_score": 10.0},
            ],
            drug_name="Ibrutinib",
        )

        buckets = [record["evidence_bucket"] for record in split["records"]]
        self.assertTrue(split["has_sufficient_target_evidence"])
        self.assertIn("core_target_evidence", buckets)
        self.assertIn("neighbor_supporting_evidence", buckets)

    def test_split_target_vs_supporting_evidence_does_not_promote_neighbor_to_core(self) -> None:
        service = LiteratureService(enable_real_search=False)
        split = service.split_target_vs_supporting_evidence(
            records=[
                {"compound_relation": "neighbor_compound", "focus_relevance_score": 12.0, "matrix_relevance_score": 10.0},
                {"compound_relation": "target_class_level", "focus_relevance_score": 8.0, "matrix_relevance_score": 7.0},
            ],
            drug_name="Ibrutinib",
        )

        buckets = [record["evidence_bucket"] for record in split["records"]]
        self.assertIn("neighbor_supporting_evidence", buckets)
        neighbor_buckets = [
            record["evidence_bucket"]
            for record in split["records"]
            if record["compound_relation"] == "neighbor_compound"
        ]
        self.assertEqual(neighbor_buckets, ["neighbor_supporting_evidence"])

    def test_explanation_mentions_neighbor_supporting_logic(self) -> None:
        service = LiteratureService(enable_real_search=False)
        record = {
            "title": "Remibrutinib metabolite profiling in rat microsomes",
            "summary": "Strong MetID assay context for a neighbor BTK inhibitor.",
            "year": 2025,
            "compound_relation": "neighbor_compound",
            "article_type": "preclinical_study",
            "focus_relevance_score": 10.0,
            "species_keyword_hits": "rat, rat liver microsomes",
            "matrix_keyword_hits": "metabolite profiling, liver microsomes",
            "focus_mismatch_penalty": 0.0,
            "context_mismatch_penalty": 0.0,
            "neighbor_suppression_penalty": 8.0,
        }

        explanation = service.explain_relevance(record=record, drug_name="Ibrutinib", focus="MetID", species="Rat")

        self.assertIn("neighbor compound", explanation.lower())
        self.assertIn("neighbor suppression penalty", explanation)

    def test_explanation_mentions_title_centric_vs_abstract_mention_logic(self) -> None:
        service = LiteratureService(enable_real_search=False)
        record = {
            "title": "Metabolite profiling in rat microsomes",
            "summary": "Ibrutinib is characterized by LC-MS/MS in the abstract.",
            "year": 2025,
            "compound_relation": "target_exact",
            "title_target_status": "target_only_in_abstract_or_summary",
            "evidence_bucket": "supporting_target_evidence",
            "article_type": "preclinical_study",
            "focus_relevance_score": 10.0,
            "matrix_keyword_hits": "metabolite profiling, lc-ms",
            "species_keyword_hits": "rat",
            "title_compound_centrality": 0.25,
            "target_mention_only_penalty": 4.5,
        }

        explanation = service.explain_relevance(record=record, drug_name="Ibrutinib", focus="MetID", species="Rat")

        self.assertIn("abstract or summary", explanation)
        self.assertIn("title centrality", explanation)
        self.assertIn("mention-only penalty", explanation)

    def test_extract_evidence_tags_recognizes_oxidation_and_microsome_context(self) -> None:
        service = LiteratureService(enable_real_search=False)

        tags = service.extract_evidence_tags(
            record={
                "title": "Ibrutinib metabolite identification in rat liver microsomes by LC-MS/MS",
                "summary": "Oxidative metabolism and hepatocyte confirmation were assessed.",
            },
            focus="MetID",
            species="Rat",
        )

        self.assertIn("oxidation", tags)
        self.assertIn("microsome", tags)
        self.assertIn("lc_ms", tags)

    def test_extract_evidence_tags_recognizes_conjugation_support(self) -> None:
        service = LiteratureService(enable_real_search=False)

        tags = service.extract_evidence_tags(
            record={
                "title": "Phenolic glucuronidation in hepatocytes and S9 fractions",
                "summary": "Conjugation pathways were profiled.",
            },
            focus="MetID",
            species="Human",
        )

        self.assertIn("glucuronidation", tags)
        self.assertIn("s9", tags)
        self.assertIn("hepatocyte", tags)

    def test_extract_evidence_tags_recognizes_permeability_and_transporter_context(self) -> None:
        service = LiteratureService(enable_real_search=False)

        tags = service.extract_evidence_tags(
            record={
                "title": "Caco-2 and MDR1 efflux assessment for a basic kinase inhibitor",
                "summary": "Transporter-aware permeability interpretation was emphasized.",
            },
            focus="PK",
            species="Human",
        )

        self.assertIn("permeability", tags)
        self.assertIn("efflux_awareness", tags)
        self.assertIn("transporter_awareness", tags)

    def test_link_records_to_hotspots_supports_oxidation_hotspot(self) -> None:
        service = LiteratureService(enable_real_search=False)
        records = [
            {
                "title": "Ibrutinib metabolite identification in rat liver microsomes by LC-MS/MS",
                "summary": "Oxidative metabolism was characterized in hepatocytes and microsomes.",
                "focus_relevance_score": 8.0,
                "matrix_relevance_score": 6.0,
                "evidence_bucket": "supporting_target_evidence",
            }
        ]
        hotspots = [
            {
                "hotspot_label": "Aromatic oxidation hotspot",
                "linked_evidence_tags": ["oxidation", "aromatic_hydroxylation", "microsome", "hepatocyte", "lc_ms"],
            }
        ]

        linked = service.link_records_to_hotspots(records, hotspots, focus="MetID", species="Rat")

        self.assertEqual(linked["Aromatic oxidation hotspot"]["support_level"], "high")
        self.assertTrue(linked["Aromatic oxidation hotspot"]["record_titles"])

    def test_build_assay_support_links_supports_traceability(self) -> None:
        service = LiteratureService(enable_real_search=False)
        records = [
            {
                "title": "Ibrutinib metabolite identification in rat liver microsomes by LC-MS/MS",
                "summary": "Microsome and hepatocyte MetID workflow.",
                "final_score": 20.0,
                "evidence_bucket": "supporting_target_evidence",
            },
            {
                "title": "Caco-2 and MDR1 efflux assessment for a basic kinase inhibitor",
                "summary": "Transporter-aware permeability interpretation was emphasized.",
                "final_score": 12.0,
                "evidence_bucket": "background_evidence",
            },
        ]
        assays = [
            {"assay_name": "Rat liver microsomes", "rationale": "Oxidative liability is plausible."},
            {"assay_name": "MDCK or MDR1-aware permeability follow-up", "rationale": "Efflux awareness may matter."},
        ]

        links = service.build_assay_support_links(records, assays, focus="MetID", species="Rat")

        self.assertIn("Rat liver microsomes", links)
        self.assertTrue(links["Rat liver microsomes"]["record_titles"])
        self.assertIn("MDCK or MDR1-aware permeability follow-up", links)

    def test_literature_support_confidence_prefers_exact_title_and_species_aligned_evidence(self) -> None:
        service = LiteratureService(enable_real_search=False)
        strong_bundle = [
            {
                "compound_relation": "target_exact",
                "evidence_bucket": "core_target_evidence",
                "title_target_status": "target_exact_in_title",
                "article_type": "preclinical_study",
                "focus_relevance_score": 9.0,
                "species_relevance_score": 6.0,
                "matrix_relevance_score": 7.0,
            }
        ]
        weak_bundle = [
            {
                "compound_relation": "target_class_level",
                "evidence_bucket": "background_evidence",
                "title_target_status": "unclear_title_target_status",
                "article_type": "review",
                "focus_relevance_score": 3.0,
                "species_relevance_score": 0.0,
                "matrix_relevance_score": 1.0,
            }
        ]

        strong_score = service.compute_literature_support_confidence(strong_bundle, focus="MetID", species="Rat")
        weak_score = service.compute_literature_support_confidence(weak_bundle, focus="MetID", species="Rat")

        self.assertGreater(strong_score, weak_score)
        self.assertEqual(service.classify_literature_support_confidence(strong_score), "high")

    def test_modelcompound_like_bundle_naturally_stays_low_or_medium(self) -> None:
        service = LiteratureService(enable_real_search=False)
        bundle = [
            {
                "compound_relation": "neighbor_compound",
                "evidence_bucket": "neighbor_supporting_evidence",
                "title_target_status": "non_target_title_center",
                "article_type": "preclinical_study",
                "focus_relevance_score": 5.0,
                "species_relevance_score": 0.0,
                "matrix_relevance_score": 2.0,
            }
        ]

        score = service.compute_literature_support_confidence(bundle, focus="MetID", species="Rat")
        self.assertIn(service.classify_literature_support_confidence(score), {"low", "medium"})

    def test_species_context_alignment_confidence_increases_with_aligned_bundle(self) -> None:
        service = LiteratureService(enable_real_search=False)
        aligned = [
            {"species_relevance_score": 5.0, "matrix_relevance_score": 6.0, "context_mismatch_penalty": 0.0},
        ]
        weak = [
            {"species_relevance_score": 0.0, "matrix_relevance_score": 1.0, "context_mismatch_penalty": 4.0},
        ]

        self.assertGreater(
            service.compute_species_context_alignment_confidence(aligned, species="Rat", focus="MetID"),
            service.compute_species_context_alignment_confidence(weak, species="Rat", focus="MetID"),
        )


if __name__ == "__main__":
    unittest.main()

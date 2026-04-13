from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from datetime import date
from html import unescape
import re
from typing import Any

try:
    import requests
except ImportError:  # pragma: no cover - public fallback behavior is tested instead.
    requests = None

from utils.models import LiteratureReference, LiteratureSearchResult


DMPK_KEYWORDS = {
    "metabolism",
    "metabolite",
    "pharmacokinetics",
    "adme",
    "microsome",
    "microsomes",
    "hepatocyte",
    "hepatocytes",
    "cyp",
    "clearance",
    "bioavailability",
    "biotransformation",
}

FOCUS_KEYWORDS = {
    "metid": {"metabolite identification", "metabolism", "biotransformation", "metabolic"},
    "pk": {"pharmacokinetics", "clearance", "bioavailability", "exposure", "oral"},
    "ddi": {"drug-drug interaction", "cyp inhibition", "cyp3a", "enzyme induction", "interaction"},
    "safety": {"reactive metabolite", "bioactivation", "toxicity", "safety", "covalent"},
}

FOCUS_PROFILES = {
    "metid": {
        "label": "MetID",
        "high_priority_phrases": [
            "metabolite identification",
            "metabolite profiling",
            "metabolite characterization",
            "oxidative metabolism",
            "mass spectrometry",
            "lc-ms",
            "lc-ms/ms",
        ],
        "high_priority_terms": [
            "metabolite",
            "metabolism",
            "biotransformation",
            "microsome",
            "microsomes",
            "hepatocyte",
            "hepatocytes",
            "glucuronidation",
        ],
        "negative_terms": ["efficacy", "survival", "randomized", "tumor response", "adverse event"],
    },
    "pk": {
        "label": "PK",
        "high_priority_phrases": [
            "pharmacokinetics",
            "half-life",
            "bioavailability",
            "interaction study",
        ],
        "high_priority_terms": [
            "pk",
            "clearance",
            "exposure",
            "auc",
            "cmax",
            "tmax",
            "absorption",
            "distribution",
            "excretion",
        ],
        "negative_terms": ["tumor response", "efficacy"],
    },
    "ddi": {
        "label": "DDI",
        "high_priority_phrases": [
            "drug-drug interaction",
            "cyp inhibition",
            "cyp induction",
            "interaction study",
            "enzyme inhibition",
        ],
        "high_priority_terms": [
            "ddi",
            "cyp3a",
            "transporter",
            "p-gp",
            "interaction",
        ],
        "negative_terms": ["survival", "tumor response"],
    },
    "safety": {
        "label": "Safety",
        "high_priority_phrases": [
            "reactive metabolite",
            "glutathione conjugate",
            "adverse reaction",
            "toxicokinetics",
        ],
        "high_priority_terms": [
            "bioactivation",
            "toxicity",
            "safety",
            "off-target",
            "adverse",
        ],
        "negative_terms": ["efficacy", "response rate"],
    },
}

SPECIES_PROFILES = {
    "human": {
        "label": "Human",
        "terms": ["human", "patient", "clinical"],
        "phrases": ["human liver microsomes", "human hepatocyte", "human plasma", "healthy subjects"],
        "aliases": ["hlm"],
    },
    "rat": {
        "label": "Rat",
        "terms": ["rat"],
        "phrases": ["rat liver microsomes", "rat hepatocyte", "rat plasma", "rat bile", "rat urine", "rat feces"],
        "aliases": ["rlm"],
    },
    "mouse": {
        "label": "Mouse",
        "terms": ["mouse", "mice", "murine"],
        "phrases": ["mouse liver microsomes"],
        "aliases": [],
    },
    "dog": {
        "label": "Dog",
        "terms": ["dog", "canine"],
        "phrases": ["dog hepatocyte", "dog plasma"],
        "aliases": [],
    },
    "monkey": {
        "label": "Monkey",
        "terms": ["monkey", "cynomolgus"],
        "phrases": ["monkey hepatocyte", "monkey plasma"],
        "aliases": [],
    },
    "unknown": {
        "label": "Unknown",
        "terms": [],
        "phrases": [],
        "aliases": [],
    },
}

MATRIX_PROFILES = {
    "metid": {
        "label": "MetID matrix profile",
        "phrases": [
            "liver microsomes",
            "metabolite profiling",
            "metabolite identification",
            "in vitro metabolism",
            "in vivo metabolism",
            "mass spectrometry",
            "lc-ms",
            "lc-ms/ms",
        ],
        "terms": ["microsome", "hepatocyte", "s9", "plasma", "urine", "feces", "bile"],
    },
    "pk": {
        "label": "PK matrix profile",
        "phrases": [
            "pharmacokinetic study",
            "concentration-time",
            "oral administration",
            "intravenous",
            "tissue distribution",
        ],
        "terms": ["plasma", "serum", "whole blood", "exposure", "auc", "cmax"],
    },
    "ddi": {
        "label": "DDI matrix profile",
        "phrases": [
            "cyp phenotyping",
            "interaction study",
            "recombinant enzyme",
        ],
        "terms": ["inhibition", "induction", "transporter", "microsome", "hepatocyte"],
    },
    "safety": {
        "label": "Safety matrix profile",
        "phrases": [
            "reactive metabolite",
            "glutathione conjugate",
            "safety assessment",
            "covalent binding",
        ],
        "terms": ["bioactivation", "toxicity", "metabolite burden", "glutathione"],
    },
}

CLASS_LEVEL_TERMS = {
    "kinase inhibitor",
    "covalent inhibitor",
    "covalent drug",
    "small molecule",
    "btk inhibitor",
    "bruton's tyrosine kinase inhibitor",
}

COMPOUND_SUFFIXES = (
    "metinib",
    "tinib",
    "parib",
    "ciclib",
    "sertib",
    "lisib",
    "nib",
    "mab",
)

GENERIC_REFERENCES = [
    LiteratureReference(
        title="Recommended screening cascade for preclinical ADME triage",
        source="Mock Best Practice Review",
        year=2022,
        summary="Describes a tiered sequence of microsomes, S9, hepatocytes, plasma stability, and CYP phenotyping for early discovery compounds.",
        authors="A. Reviewer et al.",
        journal="Mock Best Practice Review",
    ),
    LiteratureReference(
        title="Using hepatocytes and IVIVE to project human clearance",
        source="Mock Translational PK Review",
        year=2021,
        summary="Summarizes how hepatocyte intrinsic clearance, binding, and blood-to-plasma ratios improve human translation confidence.",
        authors="B. Translational Scientist et al.",
        journal="Mock Translational PK Review",
    ),
    LiteratureReference(
        title="Reactive metabolite alerts in discovery ADME packages",
        source="Mock Safety Assessment Note",
        year=2020,
        summary="Highlights sulfur-, catechol-, aniline-, and electrophile-associated bioactivation flags and trapping experiment design.",
        authors="C. Safety Team et al.",
        journal="Mock Safety Assessment Note",
    ),
]

IBRUTINIB_REFERENCES = [
    LiteratureReference(
        title="Preclinical ADME profile and CYP3A sensitivity of ibrutinib",
        source="Mock PubMed Seed",
        year=2018,
        summary="Reports oxidative metabolism with prominent CYP3A contribution and supports focused DDI phenotyping during lead optimization.",
        authors="D. Discovery ADME et al.",
        journal="Mock PubMed Seed",
    ),
    LiteratureReference(
        title="Metabolite identification strategy for covalent kinase inhibitors",
        source="Mock DMPK Methods",
        year=2020,
        summary="Explains why electrophilic kinase inhibitors benefit from hepatocyte MetID and reactive trapping experiments.",
        authors="E. Bioanalysis Group et al.",
        journal="Mock DMPK Methods",
    ),
    LiteratureReference(
        title="Species translation considerations for orally cleared kinase inhibitors",
        source="Mock Translational ADME Review",
        year=2021,
        summary="Discusses rodent-to-human scaling caveats when oxidative clearance is high and exposure is absorption limited.",
        authors="F. Translational PK Team et al.",
        journal="Mock Translational ADME Review",
    ),
    LiteratureReference(
        title="Best practices for CYP phenotyping in microsomes and hepatocytes",
        source="Mock Bioanalysis Guide",
        year=2019,
        summary="Provides a practical workflow for recombinant CYP panels, inhibitor phenotyping, and metabolite confirmation.",
        authors="G. Enzyme Phenotyping Group et al.",
        journal="Mock Bioanalysis Guide",
    ),
]


@dataclass(slots=True)
class LiteratureService:
    """DMPK-aware literature retrieval with reranking and provider fallback."""

    enable_real_search: bool = True
    provider: str = "europe_pmc"
    europe_pmc_base_url: str = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
    pubmed_esearch_url: str = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    pubmed_esummary_url: str = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
    pubmed_efetch_url: str = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
    enable_secondary_provider: bool = True
    secondary_provider: str = "pubmed"
    timeout: int = 20
    default_max_results: int = 5

    def build_queries(self, drug_name: str, smiles: str, focus: str) -> list[str]:
        focus_key = focus.strip().lower() or "metid"
        query_templates = {
            "metid": [
                "{drug} metabolite identification",
                "{drug} metabolism",
                "{drug} biotransformation",
                "{drug} ADME",
            ],
            "pk": [
                "{drug} pharmacokinetics",
                "{drug} clearance",
                "{drug} bioavailability",
                "{drug} metabolism pharmacokinetics",
            ],
            "ddi": [
                "{drug} drug-drug interaction",
                "{drug} CYP inhibition",
                "{drug} CYP3A",
                "{drug} enzyme induction",
            ],
            "safety": [
                "{drug} reactive metabolite",
                "{drug} bioactivation",
                "{drug} metabolism toxicity",
            ],
        }

        if drug_name.strip():
            templates = query_templates.get(focus_key, query_templates["metid"])
            return self._deduplicate([template.format(drug=drug_name.strip()) for template in templates])

        if smiles.strip():
            queries = [
                "small molecule metabolism ADME",
                "drug metabolite identification LC-MS",
            ]
            if focus_key == "pk":
                queries.append("small molecule pharmacokinetics clearance")
            elif focus_key == "ddi":
                queries.append("small molecule CYP inhibition drug-drug interaction")
            elif focus_key == "safety":
                queries.append("small molecule reactive metabolite bioactivation")
            queries.append("smiles_only")
            return self._deduplicate(queries)

        return ["small molecule metabolism ADME", "drug metabolite identification LC-MS"]

    def extract_compound_aliases(self, drug_name: str) -> list[str]:
        if not drug_name.strip():
            return []

        base = drug_name.strip()
        aliases = {
            base,
            base.lower(),
            base.replace("-", " "),
            base.replace(" ", "-"),
            base.replace(" ", ""),
            base.replace("-", ""),
            base.lower().replace("-", " "),
            base.lower().replace(" ", "-"),
            base.lower().replace(" ", ""),
            base.lower().replace("-", ""),
        }
        return self._deduplicate(sorted(alias for alias in aliases if alias))

    def search(
        self,
        query: str,
        max_results: int = 5,
        drug_name: str = "",
        focus: str = "",
        species: str = "",
    ) -> list[dict[str, Any]]:
        limit = max_results or self.default_max_results
        aliases = self.extract_compound_aliases(drug_name)

        if self.enable_real_search:
            for provider_name in self._provider_sequence():
                try:
                    records = self._search_provider(provider_name=provider_name, query=query, max_results=limit)
                except Exception:
                    records = []
                if records:
                    return self.rerank_records(
                        records=records,
                        drug_name=drug_name,
                        focus=focus,
                        species=species,
                        max_results=limit,
                        aliases=aliases,
                    )

        mock_records = self.search_mock(query=query, max_results=limit)
        return self.rerank_records(
            records=mock_records,
            drug_name=drug_name,
            focus=focus,
            species=species,
            max_results=limit,
            aliases=aliases,
        )

    def search_compound(
        self,
        drug_name: str,
        smiles: str,
        focus: str,
        species: str = "",
        max_results: int = 5,
    ) -> LiteratureSearchResult:
        queries = self.build_queries(drug_name=drug_name, smiles=smiles, focus=focus)
        aliases = self.extract_compound_aliases(drug_name)
        limit = max_results or self.default_max_results

        if self.enable_real_search:
            for provider_name in self._provider_sequence():
                aggregated: list[dict[str, Any]] = []
                for query in queries:
                    try:
                        aggregated.extend(
                            self._search_provider(
                                provider_name=provider_name,
                                query=query,
                                max_results=max(limit * 2, limit),
                            )
                        )
                    except Exception:
                        continue
                reranked = self.rerank_records(
                    records=self._deduplicate_records(aggregated),
                    drug_name=drug_name,
                    focus=focus,
                    species=species,
                    max_results=limit,
                    aliases=aliases,
                )
                if reranked:
                    return self._build_search_result(
                        records=reranked,
                        queries_used=queries,
                        aliases_used=aliases,
                        provider_used=provider_name,
                        focus=focus,
                        species=species,
                    )

        fallback_query = queries[0] if queries else "small molecule metabolism ADME"
        fallback_records = self.rerank_records(
            records=self.search_mock(query=fallback_query, max_results=limit),
            drug_name=drug_name,
            focus=focus,
            species=species,
            max_results=limit,
            aliases=aliases,
        )
        return self._build_search_result(
            records=fallback_records,
            queries_used=queries or [fallback_query],
            aliases_used=aliases,
            provider_used="mock_fallback",
            focus=focus,
            species=species,
        )

    def search_europe_pmc(self, query: str, max_results: int = 5) -> list[dict[str, Any]]:
        if requests is None:
            return []

        params = {
            "query": query,
            "format": "json",
            "pageSize": max_results,
            "resultType": "core",
        }
        try:
            response = requests.get(self.europe_pmc_base_url, params=params, timeout=self.timeout)
            response.raise_for_status()
            payload = response.json()
        except Exception:
            return []

        raw_results = payload.get("resultList", {}).get("result", [])
        return [
            self.normalize_record(raw=raw_record, retrieval_mode="europe_pmc", query_used=query)
            for raw_record in raw_results
        ]

    def search_pubmed(self, query: str, max_results: int = 5) -> list[dict[str, Any]]:
        if requests is None:
            return []

        search_params = {
            "db": "pubmed",
            "term": query,
            "retmode": "json",
            "retmax": max_results,
            "sort": "relevance",
        }
        try:
            search_response = requests.get(self.pubmed_esearch_url, params=search_params, timeout=self.timeout)
            search_response.raise_for_status()
            search_payload = search_response.json()
            pmids = search_payload.get("esearchresult", {}).get("idlist", [])
            if not pmids:
                return []

            summary_params = {
                "db": "pubmed",
                "id": ",".join(pmids),
                "retmode": "json",
            }
            summary_response = requests.get(self.pubmed_esummary_url, params=summary_params, timeout=self.timeout)
            summary_response.raise_for_status()
            summary_payload = summary_response.json()
        except Exception:
            return []

        result_map = summary_payload.get("result", {})
        records: list[dict[str, Any]] = []
        for pmid in pmids:
            raw_record = result_map.get(pmid)
            if raw_record:
                records.append(self.normalize_record(raw=raw_record, retrieval_mode="pubmed", query_used=query))
        return records

    def search_mock(self, query: str, max_results: int = 5) -> list[dict[str, Any]]:
        lowered_query = query.lower()
        references = list(IBRUTINIB_REFERENCES if "ibrutinib" in lowered_query else GENERIC_REFERENCES)

        if "cyp3a" in lowered_query or "drug-drug interaction" in lowered_query or "ddi" in lowered_query:
            references.append(
                LiteratureReference(
                    title="CYP3A victim risk assessment in discovery projects",
                    source="Mock DDI Practice Note",
                    year=2023,
                    summary="Outlines when to escalate CYP3A inhibition, induction, and victim DDI experiments during preclinical ADME packages.",
                    authors="H. Clinical DDI Strategy Group et al.",
                    journal="Mock DDI Practice Note",
                )
            )

        if "reactive metabolite" in lowered_query or "bioactivation" in lowered_query or "toxicity" in lowered_query:
            references.append(
                LiteratureReference(
                    title="Reactive metabolite triage for discovery compounds",
                    source="Mock Safety Signal Review",
                    year=2024,
                    summary="Summarizes trapping experiment choices and bioactivation flag interpretation during early safety assessment.",
                    authors="I. Reactive Metabolite Team et al.",
                    journal="Mock Safety Signal Review",
                )
            )

        if "smiles_only" in lowered_query:
            references.append(
                LiteratureReference(
                    title="Generic ADME search strategy for structure-only inputs",
                    source="Mock Query Design Note",
                    year=2024,
                    summary="Highlights the limitation of structure-only search workflows and recommends manual curation when no recognized drug name is available.",
                    authors="J. Informatics Workflow Team et al.",
                    journal="Mock Query Design Note",
                )
            )

        return [
            self.normalize_record(
                raw={
                    "title": reference.title,
                    "source": reference.source,
                    "year": reference.year,
                    "summary": reference.summary,
                    "authors": reference.authors,
                    "journal": reference.journal,
                    "url": reference.url,
                },
                retrieval_mode="mock_fallback",
                query_used=query,
            )
            for reference in references[:max_results]
        ]

    def normalize_record(
        self,
        raw: dict[str, Any],
        retrieval_mode: str,
        query_used: str = "",
    ) -> dict[str, Any]:
        title = self._clean_text(raw.get("title") or raw.get("display_title") or "Untitled record")
        year = self._parse_year(
            raw.get("year")
            or raw.get("pubYear")
            or raw.get("sortpubdate")
            or raw.get("pubdate")
        )
        summary = self._clean_text(
            raw.get("summary")
            or raw.get("abstractText")
            or raw.get("snippet")
            or "No abstract summary available."
        )
        authors = self._extract_authors(raw)
        journal = self._clean_text(
            raw.get("journal")
            or raw.get("journalTitle")
            or raw.get("fulljournalname")
            or raw.get("source")
            or "Unknown journal"
        )
        source = self._clean_text(
            raw.get("source")
            or ("PubMed" if retrieval_mode == "pubmed" else "Europe PMC" if retrieval_mode == "europe_pmc" else "Mock fallback")
        )
        return {
            "title": title,
            "source": source,
            "year": year,
            "summary": summary,
            "authors": authors,
            "journal": journal,
            "url": self._build_url(raw=raw, retrieval_mode=retrieval_mode),
            "retrieval_mode": retrieval_mode,
            "score": 0.0,
            "base_score": 0.0,
            "focus_relevance_score": 0.0,
            "species_relevance_score": 0.0,
            "matrix_relevance_score": 0.0,
            "focus_mismatch_penalty": 0.0,
            "context_mismatch_penalty": 0.0,
            "title_exactness_boost": 0.0,
            "target_mention_only_penalty": 0.0,
            "title_compound_centrality": 0.0,
            "species_specific_exactness_boost": 0.0,
            "neighbor_suppression_penalty": 0.0,
            "final_score": 0.0,
            "query_used": query_used,
            "match_type": "no_clear_match",
            "compound_relation": "no_clear_compound_relation",
            "title_target_status": "unclear_title_target_status",
            "evidence_bucket": "background_evidence",
            "article_type": "unknown",
            "relevance_explanation": "",
            "focus_keyword_hits": "",
            "species_keyword_hits": "",
            "matrix_keyword_hits": "",
        }

    def extract_evidence_tags(self, record: dict[str, Any], focus: str, species: str) -> list[str]:
        text = f"{record.get('title', '')} {record.get('summary', '')}".lower()
        tags: list[str] = []
        phrase_map = {
            "aromatic_hydroxylation": ["aromatic hydroxylation", "hydroxylation"],
            "n_dealkylation": ["n-dealkylation", "dealkylation"],
            "glucuronidation": ["glucuronidation", "glucuronide"],
            "sulfation": ["sulfation", "sulfate conjugate"],
            "hydrolysis": ["hydrolysis", "hydrolytic"],
            "reactive_metabolite": ["reactive metabolite", "bioactivation", "glutathione conjugate", "covalent binding"],
            "cyp_phenotyping": ["cyp phenotyping", "recombinant enzyme", "selective inhibitor"],
            "metabolite_profiling": ["metabolite profiling", "metabolite identification", "metabolite characterization"],
            "lc_ms": ["lc-ms", "lc-ms/ms", "mass spectrometry"],
            "permeability": ["permeability", "caco-2", "mdck"],
            "efflux_awareness": ["efflux", "mdr1", "p-gp"],
            "transporter_awareness": ["transporter", "uptake transporter", "efflux transporter", "oatp"],
            "bile_urine_feces": ["bile", "urine", "feces"],
            "microsome": ["microsome", "microsomes"],
            "hepatocyte": ["hepatocyte", "hepatocytes"],
            "s9": ["s9"],
            "oxidation": ["oxidation", "oxidative metabolism", "metabolism"],
        }
        for tag, phrases in phrase_map.items():
            if any(self._contains_phrase(text, phrase) for phrase in phrases):
                tags.append(tag)

        species_profile = self.get_species_profile(species)
        if species_profile["species_key"] != "unknown":
            if any(self._contains_phrase(text, phrase) for phrase in species_profile["phrases"]) or any(
                self._contains_phrase(text, term) for term in species_profile["terms"] + species_profile["aliases"]
            ):
                tags.append(f"{species_profile['species_key']}_aligned")

        if (focus or "").strip().lower() == "metid":
            if any(tag in tags for tag in ("lc_ms", "metabolite_profiling", "microsome", "hepatocyte")):
                tags.append("metid_support")
        elif (focus or "").strip().lower() == "ddi":
            if any(tag in tags for tag in ("cyp_phenotyping", "transporter_awareness", "efflux_awareness")):
                tags.append("ddi_support")
        elif (focus or "").strip().lower() == "pk":
            if any(self._contains_phrase(text, phrase) for phrase in ("pharmacokinetics", "clearance", "bioavailability", "exposure")):
                tags.append("pk_support")
        elif (focus or "").strip().lower() == "safety":
            if "reactive_metabolite" in tags:
                tags.append("safety_support")

        return self._deduplicate(tags)

    def score_record_for_hotspot(self, record: dict[str, Any], hotspot: dict[str, Any], focus: str, species: str) -> float:
        record_tags = set(self.extract_evidence_tags(record, focus=focus, species=species))
        hotspot_tags = set(hotspot.get("linked_evidence_tags", []))
        overlap = record_tags & hotspot_tags
        score = float(len(overlap)) * 2.5
        if f"{self.get_species_profile(species)['species_key']}_aligned" in record_tags:
            score += 1.5
        score += min(float(record.get("focus_relevance_score", 0.0)) / 4.0, 2.0)
        score += min(float(record.get("matrix_relevance_score", 0.0)) / 4.0, 1.5)
        if record.get("evidence_bucket") in {"core_target_evidence", "supporting_target_evidence"}:
            score += 1.0
        return round(score, 2)

    def link_records_to_hotspots(
        self,
        records: list[dict[str, Any]],
        hotspots: list[dict[str, Any]],
        focus: str,
        species: str,
    ) -> dict[str, Any]:
        linked: dict[str, Any] = {}
        for hotspot in hotspots:
            label = str(hotspot.get("hotspot_label", "Unspecified hotspot"))
            scored_records: list[tuple[float, dict[str, Any]]] = []
            for record in records:
                record_dict = dict(record)
                record_dict["evidence_tags"] = self.extract_evidence_tags(record_dict, focus=focus, species=species)
                score = self.score_record_for_hotspot(record_dict, hotspot=hotspot, focus=focus, species=species)
                if score > 0:
                    scored_records.append((score, record_dict))
            scored_records.sort(key=lambda item: (item[0], float(item[1].get("final_score", 0.0))), reverse=True)
            top_records = scored_records[:3]
            top_score = top_records[0][0] if top_records else 0.0
            support_level = "high" if top_score >= 8.0 and len(top_records) >= 1 else "medium" if top_score >= 4.0 else "low"
            linked[label] = {
                "support_level": support_level,
                "record_titles": [record["title"] for _, record in top_records],
                "record_bundle": [record for _, record in top_records],
                "record_tags": self._deduplicate(
                    [tag for _, record in top_records for tag in record.get("evidence_tags", [])]
                ),
            }
        return linked

    def compute_literature_support_confidence(
        self,
        linked_records: list[dict[str, Any]],
        focus: str,
        species: str,
    ) -> float:
        if not linked_records:
            return 1.5
        score = 0.0
        for record in linked_records:
            relation = str(record.get("compound_relation", "no_clear_compound_relation"))
            bucket = str(record.get("evidence_bucket", "background_evidence"))
            title_status = str(record.get("title_target_status", "unclear_title_target_status"))
            article_type = str(record.get("article_type", "unknown"))
            focus_score = float(record.get("focus_relevance_score", 0.0))
            species_score = float(record.get("species_relevance_score", 0.0))
            matrix_score = float(record.get("matrix_relevance_score", 0.0))
            score += {
                "target_exact": 3.5,
                "target_alias": 2.8,
                "target_class_level": 1.8,
                "neighbor_compound": 0.8,
                "ambiguous_compound_context": 1.0,
                "no_clear_compound_relation": 0.5,
            }.get(relation, 0.5)
            score += {
                "core_target_evidence": 2.5,
                "supporting_target_evidence": 1.8,
                "neighbor_supporting_evidence": 0.8,
                "background_evidence": 0.3,
            }.get(bucket, 0.3)
            if title_status in {"target_exact_in_title", "target_alias_in_title"}:
                score += 1.5
            score += min(focus_score / 5.0, 2.0)
            score += min(matrix_score / 6.0, 1.5)
            score += min(species_score / 5.0, 1.0) if species.strip() else 0.0
            score += {
                "clinical_study": 1.5,
                "preclinical_study": 1.5,
                "original_research": 1.2,
                "review": 0.8,
                "guideline": 0.8,
                "case_report": 0.4,
                "unknown": 0.0,
            }.get(article_type, 0.0)
        return round(min(score / max(len(linked_records), 1), 10.0), 2)

    @staticmethod
    def classify_literature_support_confidence(score: float) -> str:
        if score >= 6.5:
            return "high"
        if score >= 3.5:
            return "medium"
        return "low"

    def compute_species_context_alignment_confidence(
        self,
        record_bundle: list[dict[str, Any]],
        species: str,
        focus: str,
    ) -> float:
        if not record_bundle:
            return 1.5
        if not species.strip():
            return 4.0
        score = 0.0
        for record in record_bundle:
            score += min(float(record.get("species_relevance_score", 0.0)), 5.0) * 0.8
            score += min(float(record.get("matrix_relevance_score", 0.0)), 6.0) * 0.5
            score -= min(float(record.get("context_mismatch_penalty", 0.0)), 4.0) * 0.5
        if focus.strip().lower() == "metid":
            score += 0.5
        return round(max(min(score / max(len(record_bundle), 1), 10.0), 0.0), 2)

    def summarize_evidence_confidence(
        self,
        linked_evidence: dict[str, Any],
        species: str,
        focus: str,
    ) -> dict[str, Any]:
        summaries: dict[str, Any] = {}
        for label, evidence in linked_evidence.items():
            bundle = list(evidence.get("record_bundle", []))
            literature_score = self.compute_literature_support_confidence(bundle, focus=focus, species=species)
            literature_level = self.classify_literature_support_confidence(literature_score)
            alignment_score = self.compute_species_context_alignment_confidence(bundle, species=species, focus=focus)
            alignment_level = self.classify_literature_support_confidence(alignment_score)
            summaries[label] = {
                "literature_support_score": literature_score,
                "literature_support_confidence": literature_level,
                "species_alignment_score": alignment_score,
                "species_alignment_confidence": alignment_level,
            }
        return summaries

    def build_assay_support_links(
        self,
        records: list[dict[str, Any]],
        assay_priorities: list[dict[str, Any]],
        focus: str,
        species: str,
    ) -> dict[str, Any]:
        assay_links: dict[str, Any] = {}
        for assay in assay_priorities:
            assay_name = str(assay.get("assay_name", "Unspecified assay"))
            assay_text = f"{assay_name} {assay.get('rationale', '')} {assay.get('chemistry_basis', '')} {assay.get('disposition_basis', '')}".lower()
            assay_tags: set[str] = set()
            tag_rules = {
                "microsome": ["microsome", "microsomal"],
                "hepatocyte": ["hepatocyte"],
                "s9": ["s9"],
                "lc_ms": ["mass spectrometry", "hrms", "metabolite profiling"],
                "cyp_phenotyping": ["cyp", "phenotyping"],
                "permeability": ["caco-2", "permeability"],
                "efflux_awareness": ["mdck", "mdr1", "efflux"],
                "transporter_awareness": ["transporter"],
                "hydrolysis": ["plasma stability", "hydrolysis"],
                "bile_urine_feces": ["bile", "urine", "feces"],
            }
            for tag, keys in tag_rules.items():
                if any(keyword in assay_text for keyword in keys):
                    assay_tags.add(tag)

            scored: list[tuple[float, dict[str, Any]]] = []
            for record in records:
                record_dict = dict(record)
                record_tags = set(self.extract_evidence_tags(record_dict, focus=focus, species=species))
                overlap = assay_tags & record_tags
                score = float(len(overlap)) * 2.5
                if record_dict.get("evidence_bucket") in {"core_target_evidence", "supporting_target_evidence"}:
                    score += 1.0
                if score > 0:
                    record_dict["evidence_tags"] = list(record_tags)
                    scored.append((round(score, 2), record_dict))
            scored.sort(key=lambda item: (item[0], float(item[1].get("final_score", 0.0))), reverse=True)
            top_records = scored[:3]
            top_score = top_records[0][0] if top_records else 0.0
            strength = "high" if top_score >= 5.0 else "medium" if top_score >= 2.5 else "low"
            titles = [record["title"] for _, record in top_records]
            assay_links[assay_name] = {
                "support_strength": strength,
                "record_titles": titles,
                "matched_tags": self._deduplicate([tag for _, record in top_records for tag in record.get("evidence_tags", []) if tag in assay_tags]),
                "why_prioritized": (
                    f"Prioritized because {assay.get('rationale', 'the assay is aligned with the current chemistry and focus').rstrip('.')} "
                    f"and the retained literature points toward {', '.join(titles[:2]) or 'limited direct assay-specific evidence'}."
                ),
            }
        return assay_links

    def get_focus_profile(self, focus: str) -> dict[str, Any]:
        focus_key = focus.strip().lower()
        profile = FOCUS_PROFILES.get(focus_key, FOCUS_PROFILES["metid"])
        return {
            "focus_key": focus_key or "metid",
            "label": profile["label"],
            "high_priority_phrases": list(profile["high_priority_phrases"]),
            "high_priority_terms": list(profile["high_priority_terms"]),
            "negative_terms": list(profile["negative_terms"]),
        }

    def get_species_profile(self, species: str) -> dict[str, Any]:
        species_key = species.strip().lower() or "unknown"
        profile = SPECIES_PROFILES.get(species_key, SPECIES_PROFILES["unknown"])
        return {
            "species_key": species_key,
            "label": profile["label"],
            "terms": list(profile["terms"]),
            "phrases": list(profile["phrases"]),
            "aliases": list(profile["aliases"]),
        }

    def get_matrix_profile(self, focus: str) -> dict[str, Any]:
        focus_key = focus.strip().lower() or "metid"
        profile = MATRIX_PROFILES.get(focus_key, MATRIX_PROFILES["metid"])
        return {
            "focus_key": focus_key,
            "label": profile["label"],
            "phrases": list(profile["phrases"]),
            "terms": list(profile["terms"]),
        }

    def classify_match_type(self, record: dict[str, Any], drug_name: str, aliases: list[str]) -> str:
        if not drug_name.strip():
            return "no_clear_match"

        title = str(record.get("title", ""))
        summary = str(record.get("summary", ""))
        title_lower = title.lower()
        summary_lower = summary.lower()
        haystack_lower = f"{title} {summary}".lower()

        if self._contains_phrase(title_lower, drug_name.strip().lower()):
            return "exact_name_match"

        normalized_title = self._normalize_for_alias_matching(title)
        for alias in aliases:
            normalized_alias = self._normalize_for_alias_matching(alias)
            if not normalized_alias or normalized_alias == self._normalize_for_alias_matching(drug_name):
                continue
            if normalized_alias in normalized_title:
                return "alias_match"

        if self._contains_phrase(summary_lower, drug_name.strip().lower()):
            return "class_level_match"

        focus_terms = DMPK_KEYWORDS | CLASS_LEVEL_TERMS
        if any(term in haystack_lower for term in focus_terms):
            if any(class_term in haystack_lower for class_term in CLASS_LEVEL_TERMS):
                return "class_level_match"
            if any(term in haystack_lower for term in {"covalent", "kinase", "btk", "inhibitor"}):
                return "class_level_match"

        return "no_clear_match"

    def classify_article_type(self, record: dict[str, Any]) -> str:
        title = str(record.get("title", "")).lower()
        summary = str(record.get("summary", "")).lower()
        journal = str(record.get("journal", "")).lower()
        text = " ".join([title, summary, journal])

        if self._contains_phrase(text, "case report"):
            return "case_report"
        if any(self._contains_phrase(text, keyword) for keyword in {"guideline", "guidance", "recommendation", "recommendations"}):
            return "guideline"
        if any(self._contains_phrase(text, keyword) for keyword in {"review", "overview", "mini-review"}):
            return "review"
        if any(
            self._contains_phrase(text, keyword)
            for keyword in {"phase i", "phase ii", "phase iii", "randomized", "trial", "healthy subjects", "patients", "volunteers"}
        ):
            return "clinical_study"
        if any(
            self._contains_phrase(text, keyword)
            for keyword in {"mouse", "mice", "rat", "dog", "hepatocyte", "hepatocytes", "microsome", "microsomes", "in vitro", "preclinical"}
        ):
            return "preclinical_study"
        if any(self._contains_phrase(text, keyword) for keyword in {"study", "investigation", "evaluated", "assessment", "analysis"}):
            return "original_research"
        return "unknown"

    def apply_exact_match_filter(self, records: list[dict[str, Any]], drug_name: str, focus: str) -> list[dict[str, Any]]:
        _ = focus
        if not drug_name.strip():
            return records

        exact_or_alias = [
            record
            for record in records
            if record.get("match_type") in {"exact_name_match", "alias_match"}
            or record.get("compound_relation") in {"target_exact", "target_alias"}
        ]
        class_level = [
            record
            for record in records
            if record.get("match_type") == "class_level_match"
            or record.get("compound_relation") == "target_class_level"
        ]
        supporting = [
            record
            for record in records
            if record.get("compound_relation") in {"neighbor_compound", "ambiguous_compound_context", "no_clear_compound_relation"}
            and record not in exact_or_alias
            and record not in class_level
        ]

        if exact_or_alias:
            return exact_or_alias + class_level + supporting
        if class_level:
            return class_level + supporting
        return supporting

    def extract_neighbor_compound_candidates(self, record: dict[str, Any], drug_name: str) -> list[str]:
        if not drug_name.strip():
            return []

        title = str(record.get("title", ""))
        summary = str(record.get("summary", ""))
        text = f"{title} {summary}".lower()
        if not text.strip():
            return []

        suffix_pattern = "|".join(COMPOUND_SUFFIXES)
        candidates = re.findall(rf"\b[a-z][a-z0-9\-]{{3,}}(?:{suffix_pattern})\b", text)
        title_has_target = self._contains_phrase(title.lower(), drug_name.strip().lower())
        if not title_has_target:
            title_candidates = [
                token
                for token in re.findall(r"\b[A-Z][a-z]{5,}\b", title)
                if token.lower()
                not in {
                    "metabolism",
                    "metabolite",
                    "identification",
                    "profiling",
                    "biotransformation",
                    "comparison",
                    "influence",
                    "healthy",
                    "subjects",
                    "clinical",
                    "human",
                    "mouse",
                    "study",
                    "studies",
                    "using",
                    "combined",
                    "liquid",
                    "chromatography",
                    "spectrometry",
                    "lactobacillus",
                    "influenza",
                }
            ]
            candidates.extend(token.lower() for token in title_candidates)
        target_aliases = {
            self._normalize_for_alias_matching(alias)
            for alias in self.extract_compound_aliases(drug_name)
        }
        target_aliases.add(self._normalize_for_alias_matching(drug_name))

        neighbors: list[str] = []
        for candidate in candidates:
            normalized = self._normalize_for_alias_matching(candidate)
            if normalized and normalized not in target_aliases:
                neighbors.append(candidate)
        return self._deduplicate(neighbors)

    def classify_compound_relation(self, record: dict[str, Any], drug_name: str, aliases: list[str]) -> str:
        if not drug_name.strip():
            return "no_clear_compound_relation"

        title = str(record.get("title", ""))
        summary = str(record.get("summary", ""))
        combined = f"{title} {summary}"
        title_lower = title.lower()
        summary_lower = summary.lower()
        combined_lower = combined.lower()
        drug_lower = drug_name.strip().lower()
        neighbor_candidates = self.extract_neighbor_compound_candidates(record=record, drug_name=drug_name)
        title_exact = self._contains_phrase(title_lower, drug_lower)
        summary_exact = self._contains_phrase(summary_lower, drug_lower)

        target_exact = title_exact or summary_exact
        normalized_combined = self._normalize_for_alias_matching(combined)
        target_normalized = self._normalize_for_alias_matching(drug_name)
        alias_match = False
        for alias in aliases:
            normalized_alias = self._normalize_for_alias_matching(alias)
            if not normalized_alias:
                continue
            if alias.strip().lower() == drug_name.strip().lower():
                continue
            if self._contains_phrase(combined_lower, alias.strip().lower()) or normalized_alias in normalized_combined:
                alias_match = True
                break

        if title_exact and neighbor_candidates:
            return "ambiguous_compound_context"
        if title_exact:
            return "target_exact"
        if summary_exact and neighbor_candidates:
            return "ambiguous_compound_context"
        if summary_exact:
            return "target_exact"
        if alias_match:
            return "target_alias"
        if neighbor_candidates:
            return "neighbor_compound"
        if str(record.get("match_type")) == "class_level_match":
            return "target_class_level"
        if self._extract_compound_like_tokens(combined_lower):
            return "ambiguous_compound_context"
        return "no_clear_compound_relation"

    def classify_title_target_status(self, record: dict[str, Any], drug_name: str, aliases: list[str]) -> str:
        if not drug_name.strip():
            return "unclear_title_target_status"

        title = str(record.get("title", ""))
        summary = str(record.get("summary", ""))
        title_lower = title.lower()
        summary_lower = summary.lower()
        drug_lower = drug_name.strip().lower()
        normalized_title = self._normalize_for_alias_matching(title)
        target_normalized = self._normalize_for_alias_matching(drug_name)
        title_compounds = self._extract_compound_like_tokens(title_lower)
        neighbor_in_title = [
            token
            for token in title_compounds
            if self._normalize_for_alias_matching(token) != target_normalized
        ]

        if self._contains_phrase(title_lower, drug_lower):
            return "target_exact_in_title"

        for alias in aliases:
            normalized_alias = self._normalize_for_alias_matching(alias)
            if not normalized_alias or alias.strip().lower() == drug_name.strip().lower():
                continue
            if self._contains_phrase(title_lower, alias.strip().lower()) or normalized_alias in normalized_title:
                return "target_alias_in_title"

        summary_has_target = self._contains_phrase(summary_lower, drug_lower)
        if not summary_has_target:
            for alias in aliases:
                normalized_alias = self._normalize_for_alias_matching(alias)
                if not normalized_alias or alias.strip().lower() == drug_name.strip().lower():
                    continue
                if self._contains_phrase(summary_lower, alias.strip().lower()) or normalized_alias in self._normalize_for_alias_matching(summary):
                    summary_has_target = True
                    break

        if neighbor_in_title:
            return "non_target_title_center"
        if summary_has_target:
            return "target_only_in_abstract_or_summary"

        relation = str(record.get("compound_relation", "no_clear_compound_relation"))
        if relation in {"target_class_level", "ambiguous_compound_context"}:
            return "target_not_in_title_but_compound_context_present"
        return "unclear_title_target_status"

    def detect_title_compound_centrality(self, record: dict[str, Any], drug_name: str, aliases: list[str]) -> float:
        title = str(record.get("title", ""))
        title_lower = title.lower()
        status = str(record.get("title_target_status") or self.classify_title_target_status(record, drug_name, aliases))
        title_tokens = self._extract_compound_like_tokens(title_lower)
        centrality = {
            "target_exact_in_title": 0.9,
            "target_alias_in_title": 0.8,
            "target_only_in_abstract_or_summary": 0.25,
            "target_not_in_title_but_compound_context_present": 0.4,
            "non_target_title_center": 0.1,
            "unclear_title_target_status": 0.2,
        }.get(status, 0.2)

        target_prefix = False
        if status in {"target_exact_in_title", "target_alias_in_title"}:
            first_half = title_lower[: max(len(title_lower) // 2, 1)]
            if self._contains_phrase(first_half, drug_name.strip().lower()):
                target_prefix = True
            else:
                for alias in aliases:
                    if alias.strip().lower() != drug_name.strip().lower() and self._contains_phrase(first_half, alias.strip().lower()):
                        target_prefix = True
                        break
            if target_prefix:
                centrality += 0.08
            if any(keyword in title_lower for keyword in DMPK_KEYWORDS):
                centrality += 0.05

        unique_compounds = {
            self._normalize_for_alias_matching(token)
            for token in title_tokens
            if self._normalize_for_alias_matching(token)
        }
        if len(unique_compounds) >= 2:
            centrality -= 0.15
        return round(min(max(centrality, 0.0), 1.0), 2)

    def compute_title_exactness_boost(self, record: dict[str, Any], drug_name: str, aliases: list[str]) -> float:
        _ = drug_name
        status = str(record.get("title_target_status") or self.classify_title_target_status(record, drug_name, aliases))
        centrality = float(record.get("title_compound_centrality", 0.0)) or self.detect_title_compound_centrality(record, drug_name, aliases)

        if status == "target_exact_in_title":
            return round(8.0 * max(centrality, 0.75), 2)
        if status == "target_alias_in_title":
            return round(6.0 * max(centrality, 0.7), 2)
        if status == "target_not_in_title_but_compound_context_present":
            return round(1.5 * max(centrality, 0.2), 2)
        return 0.0

    def compute_target_mention_only_penalty(self, record: dict[str, Any], drug_name: str, aliases: list[str]) -> float:
        _ = drug_name
        _ = aliases
        status = str(record.get("title_target_status", "unclear_title_target_status"))
        centrality = float(record.get("title_compound_centrality", 0.0))

        if status == "target_only_in_abstract_or_summary":
            return round(4.5 - min(centrality, 0.3), 2)
        if status == "non_target_title_center":
            return round(7.0 - min(centrality, 0.2), 2)
        if status == "unclear_title_target_status":
            return 1.0
        return 0.0

    def explain_relevance(self, record: dict[str, Any], drug_name: str, focus: str, species: str = "") -> str:
        focus_profile = self.get_focus_profile(focus)
        focus_key = str(focus_profile["focus_key"])
        focus_label = str(focus_profile["label"])
        species_profile = self.get_species_profile(species)
        species_label = str(species_profile["label"])
        compound_relation = str(record.get("compound_relation", "no_clear_compound_relation"))
        if compound_relation == "no_clear_compound_relation":
            fallback_match_type = str(record.get("match_type", "no_clear_match"))
            compound_relation = {
                "exact_name_match": "target_exact",
                "alias_match": "target_alias",
                "class_level_match": "target_class_level",
            }.get(fallback_match_type, compound_relation)
        evidence_bucket = str(record.get("evidence_bucket", "background_evidence"))
        article_type = str(record.get("article_type", "unknown"))
        year = int(record.get("year") or 0)
        focus_hits = self._collect_focus_hits(record=record, focus=focus_key)
        focus_relevance = float(record.get("focus_relevance_score", 0.0))
        mismatch_penalty = float(record.get("focus_mismatch_penalty", 0.0))
        context_penalty = float(record.get("context_mismatch_penalty", 0.0))
        title_status = str(record.get("title_target_status", "unclear_title_target_status"))
        title_boost = float(record.get("title_exactness_boost", 0.0))
        mention_penalty = float(record.get("target_mention_only_penalty", 0.0))
        title_centrality = float(record.get("title_compound_centrality", 0.0))
        exactness_boost = float(record.get("species_specific_exactness_boost", 0.0))
        neighbor_penalty = float(record.get("neighbor_suppression_penalty", 0.0))
        species_hits = self._split_hits(str(record.get("species_keyword_hits", "")))
        matrix_hits = self._split_hits(str(record.get("matrix_keyword_hits", "")))
        neighbor_candidates = self.extract_neighbor_compound_candidates(record=record, drug_name=drug_name)

        if compound_relation == "target_exact":
            match_text = "Exact target-compound match"
        elif compound_relation == "target_alias":
            match_text = "Alias-level target-compound match"
        elif compound_relation == "target_class_level":
            match_text = "Class-level target-compound background"
        elif compound_relation == "neighbor_compound":
            neighbor_name = neighbor_candidates[0] if neighbor_candidates else "a neighbor compound"
            match_text = f"Centers on neighbor compound {neighbor_name}"
        elif compound_relation == "ambiguous_compound_context":
            match_text = "Mixed or ambiguous compound context"
        else:
            match_text = "No clear target-compound relation"

        if focus_hits:
            focus_text = f"Strong {focus_label}-specific signals via {', '.join(focus_hits[:2])}"
        else:
            focus_text = f"Limited {focus_label}-specific content"

        if title_status == "target_exact_in_title":
            title_text = "Target drug appears directly in the title"
        elif title_status == "target_alias_in_title":
            title_text = "Target drug alias appears directly in the title"
        elif title_status == "target_only_in_abstract_or_summary":
            title_text = "Target mention appears mainly in abstract or summary"
        elif title_status == "target_not_in_title_but_compound_context_present":
            title_text = "Target-related compound context is present, but the title is not target-centered"
        elif title_status == "non_target_title_center":
            title_text = "Title centers on a non-target compound or object"
        else:
            title_text = "Title target-centrality is unclear"

        if evidence_bucket == "core_target_evidence":
            bucket_text = "retained as core target evidence"
        elif evidence_bucket == "supporting_target_evidence":
            bucket_text = "retained as supporting target evidence"
        elif evidence_bucket == "neighbor_supporting_evidence":
            bucket_text = "retained as supporting neighbor evidence"
        else:
            bucket_text = "retained as background evidence"

        if species_profile["species_key"] == "unknown":
            species_text = "species context neutral"
        elif species_hits:
            species_text = f"species context aligns with {species_label} via {', '.join(species_hits[:2])}"
        elif context_penalty > 0:
            species_text = f"limited {species_label}-specific context relative to the current query"
        else:
            species_text = f"limited {species_label}-specific context"

        if matrix_hits:
            matrix_text = f"matrix/context support via {', '.join(matrix_hits[:2])}"
        elif context_penalty > 0:
            matrix_text = "limited matrix/context support for the requested experimental setup"
        else:
            matrix_text = "limited matrix/context support"

        penalties: list[str] = []
        if mismatch_penalty > 0:
            penalties.append(f"focus mismatch penalty {mismatch_penalty:.1f}")
        if context_penalty > 0:
            penalties.append(f"context mismatch penalty {context_penalty:.1f}")
        if mention_penalty > 0:
            penalties.append(f"mention-only penalty {mention_penalty:.1f}")
        if neighbor_penalty > 0:
            penalties.append(f"neighbor suppression penalty {neighbor_penalty:.1f}")
        if title_boost > 0:
            penalties.append(f"title exactness boost {title_boost:.1f}")
        if exactness_boost > 0:
            penalties.append(f"species-specific exactness boost {exactness_boost:.1f}")
        penalty_text = "; ".join(penalties) if penalties else f"focus relevance score {focus_relevance:.1f}"

        year_text = f"; recent publication year {year}" if year else ""
        return (
            f"{match_text}, {bucket_text}. {title_text} (title centrality {title_centrality:.2f}). "
            f"{focus_text}; {species_text}; {matrix_text}; {penalty_text}; classified as {article_type}.{year_text}"
        )

    def score_record(self, record: dict[str, Any], drug_name: str, focus: str) -> float:
        title = str(record.get("title", "")).lower()
        summary = str(record.get("summary", "")).lower()
        focus_key = focus.strip().lower()
        score = 0.0

        if drug_name.strip():
            drug = drug_name.strip().lower()
            drug_pattern = re.compile(rf"\b{re.escape(drug)}\b")
            if drug_pattern.search(title):
                score += 10.0
            if drug_pattern.search(summary):
                score += 5.0

        for keyword in DMPK_KEYWORDS:
            if keyword in title:
                score += 2.5
            if keyword in summary:
                score += 1.25

        match_weights = {
            "exact_name_match": 20.0,
            "alias_match": 14.0,
            "class_level_match": 4.0,
            "no_clear_match": -10.0,
        }
        article_weights = {
            "original_research": 6.0,
            "clinical_study": 6.0,
            "preclinical_study": 5.0,
            "review": 2.0,
            "guideline": 3.0,
            "case_report": 1.0,
            "unknown": 0.0,
        }
        score += match_weights.get(str(record.get("match_type")), 0.0)
        score += article_weights.get(str(record.get("article_type")), 0.0)

        year = int(record.get("year") or 0)
        current_year = date.today().year
        if year >= current_year - 2:
            score += 2.0
        elif year >= current_year - 5:
            score += 1.0

        if "review" in title or "review" in summary:
            score += 0.5

        return round(score, 2)

    def compute_focus_relevance(self, record: dict[str, Any], focus: str) -> float:
        profile = self.get_focus_profile(focus)
        title = str(record.get("title", "")).lower()
        summary = str(record.get("summary", "")).lower()
        score = 0.0
        hits: list[str] = []

        for phrase in profile["high_priority_phrases"]:
            if self._contains_phrase(title, phrase):
                score += 7.0
                hits.append(phrase)
            elif self._contains_phrase(summary, phrase):
                score += 4.0
                hits.append(phrase)

        for term in profile["high_priority_terms"]:
            if self._contains_phrase(title, term):
                score += 3.0
                hits.append(term)
            elif self._contains_phrase(summary, term):
                score += 1.5
                hits.append(term)

        if profile["focus_key"] == "metid":
            article_type = str(record.get("article_type", "unknown"))
            if article_type == "preclinical_study":
                score += 2.5
            elif article_type == "clinical_study":
                score -= 1.0
        elif profile["focus_key"] == "pk" and str(record.get("article_type", "")) == "clinical_study":
            score += 2.0
        elif profile["focus_key"] == "ddi" and str(record.get("article_type", "")) in {"clinical_study", "guideline"}:
            score += 2.0
        elif profile["focus_key"] == "safety" and str(record.get("article_type", "")) in {"guideline", "case_report", "preclinical_study"}:
            score += 2.0

        record["focus_keyword_hits"] = ", ".join(self._deduplicate(hits)) or "none"
        return round(score, 2)

    def compute_species_relevance(self, record: dict[str, Any], species: str) -> float:
        profile = self.get_species_profile(species)
        if profile["species_key"] == "unknown":
            record["species_keyword_hits"] = "neutral"
            return 0.0

        title = str(record.get("title", "")).lower()
        summary = str(record.get("summary", "")).lower()
        score = 0.0
        hits: list[str] = []

        for phrase in profile["phrases"]:
            if self._contains_phrase(title, phrase):
                score += 5.0
                hits.append(phrase)
            elif self._contains_phrase(summary, phrase):
                score += 3.0
                hits.append(phrase)

        for term in profile["terms"] + profile["aliases"]:
            if self._contains_phrase(title, term):
                score += 2.5
                hits.append(term)
            elif self._contains_phrase(summary, term):
                score += 1.5
                hits.append(term)

        if self._mentions_multiple_species(title, summary):
            score += 1.5
            hits.append("multi-species")

        record["species_keyword_hits"] = ", ".join(self._deduplicate(hits)) or "none"
        return round(score, 2)

    def compute_matrix_relevance(self, record: dict[str, Any], focus: str) -> float:
        profile = self.get_matrix_profile(focus)
        title = str(record.get("title", "")).lower()
        summary = str(record.get("summary", "")).lower()
        score = 0.0
        hits: list[str] = []

        for phrase in profile["phrases"]:
            if self._contains_phrase(title, phrase):
                score += 5.0
                hits.append(phrase)
            elif self._contains_phrase(summary, phrase):
                score += 3.0
                hits.append(phrase)

        for term in profile["terms"]:
            if self._contains_phrase(title, term):
                score += 2.0
                hits.append(term)
            elif self._contains_phrase(summary, term):
                score += 1.0
                hits.append(term)

        record["matrix_keyword_hits"] = ", ".join(self._deduplicate(hits)) or "none"
        return round(score, 2)

    def compute_penalty_for_focus_mismatch(self, record: dict[str, Any], focus: str) -> float:
        profile = self.get_focus_profile(focus)
        text = f"{record.get('title', '')} {record.get('summary', '')}".lower()
        focus_hits = self._collect_focus_hits(record=record, focus=str(profile["focus_key"]))
        penalty = 0.0

        if not focus_hits:
            penalty += 6.0
            if str(record.get("match_type")) == "exact_name_match":
                penalty += 4.0

        for term in profile["negative_terms"]:
            if self._contains_phrase(text, term):
                penalty += 2.0

        if profile["focus_key"] == "metid" and str(record.get("article_type")) == "clinical_study" and not focus_hits:
            penalty += 4.0
        if profile["focus_key"] == "pk" and str(record.get("article_type")) == "preclinical_study" and not focus_hits:
            penalty += 2.0

        return round(penalty, 2)

    def compute_context_mismatch_penalty(self, record: dict[str, Any], species: str, focus: str) -> float:
        species_profile = self.get_species_profile(species)
        matrix_profile = self.get_matrix_profile(focus)
        penalty = 0.0

        species_hits = self._split_hits(str(record.get("species_keyword_hits", "")))
        matrix_hits = self._split_hits(str(record.get("matrix_keyword_hits", "")))
        text = f"{record.get('title', '')} {record.get('summary', '')}".lower()

        if species_profile["species_key"] != "unknown":
            if not species_hits:
                penalty += 3.0
                if self._mentions_non_target_species(text, species_profile["species_key"]):
                    penalty += 2.0

        if not matrix_hits:
            penalty += 3.0
            if str(record.get("match_type")) == "exact_name_match":
                penalty += 1.5

        if matrix_profile["focus_key"] == "metid" and str(record.get("article_type")) == "clinical_study" and len(matrix_hits) < 2:
            penalty += 2.0
        if matrix_profile["focus_key"] == "pk" and str(record.get("article_type")) == "preclinical_study" and len(matrix_hits) < 2:
            penalty += 1.5

        return round(penalty, 2)

    def compute_species_specific_exactness_boost(self, record: dict[str, Any], drug_name: str, species: str) -> float:
        _ = drug_name
        relation = str(record.get("compound_relation", "no_clear_compound_relation"))
        if relation not in {"target_exact", "target_alias"}:
            return 0.0

        species_score = float(record.get("species_relevance_score", 0.0))
        matrix_score = float(record.get("matrix_relevance_score", 0.0))
        focus_score = float(record.get("focus_relevance_score", 0.0))
        boost = 0.0

        if relation == "target_exact":
            boost += 4.0
        else:
            boost += 2.5

        if species.strip() and species_score >= 3.0:
            boost += 3.0
        if focus_score >= 6.0:
            boost += 2.5
        if matrix_score >= 4.0:
            boost += 2.5
        if relation == "target_exact" and species_score >= 5.0 and matrix_score >= 6.0:
            boost += 2.0

        return round(boost, 2)

    def compute_neighbor_suppression_penalty(self, record: dict[str, Any], drug_name: str, species: str) -> float:
        _ = drug_name
        relation = str(record.get("compound_relation", "no_clear_compound_relation"))
        species_score = float(record.get("species_relevance_score", 0.0))
        matrix_score = float(record.get("matrix_relevance_score", 0.0))
        focus_score = float(record.get("focus_relevance_score", 0.0))

        if relation == "neighbor_compound":
            penalty = 10.0
            if species_score >= 3.0:
                penalty -= 1.0
            if matrix_score >= 6.0 and focus_score >= 6.0:
                penalty -= 1.0
            if not species.strip():
                penalty -= 0.5
            return round(max(penalty, 6.0), 2)

        if relation == "ambiguous_compound_context":
            return 4.0
        if relation == "no_clear_compound_relation":
            return 2.5
        return 0.0

    def split_target_vs_supporting_evidence(self, records: list[dict[str, Any]], drug_name: str) -> dict[str, Any]:
        _ = drug_name
        target_specific_count = sum(
            1 for record in records if str(record.get("compound_relation")) in {"target_exact", "target_alias"}
        )
        has_sufficient_target = target_specific_count >= 2

        bucketed_records: list[dict[str, Any]] = []
        for record in records:
            enriched = dict(record)
            relation = str(enriched.get("compound_relation", "no_clear_compound_relation"))
            focus_score = float(enriched.get("focus_relevance_score", 0.0))
            matrix_score = float(enriched.get("matrix_relevance_score", 0.0))
            title_status = str(enriched.get("title_target_status", "unclear_title_target_status"))
            title_centrality = float(enriched.get("title_compound_centrality", 0.0))

            if relation in {"target_exact", "target_alias"}:
                if title_status in {"target_exact_in_title", "target_alias_in_title"} and focus_score >= 4.0 and matrix_score >= 3.0:
                    enriched["evidence_bucket"] = "core_target_evidence"
                elif title_status == "non_target_title_center":
                    enriched["evidence_bucket"] = "background_evidence"
                elif title_status == "target_only_in_abstract_or_summary":
                    enriched["evidence_bucket"] = "supporting_target_evidence"
                elif title_centrality >= 0.55 and focus_score >= 5.0 and matrix_score >= 4.0:
                    enriched["evidence_bucket"] = "supporting_target_evidence"
                else:
                    enriched["evidence_bucket"] = "supporting_target_evidence"
            elif relation == "target_class_level":
                enriched["evidence_bucket"] = "supporting_target_evidence"
            elif relation == "neighbor_compound":
                enriched["evidence_bucket"] = "neighbor_supporting_evidence"
            else:
                enriched["evidence_bucket"] = "background_evidence"

            if not has_sufficient_target and enriched["evidence_bucket"] == "neighbor_supporting_evidence":
                enriched["evidence_bucket"] = "neighbor_supporting_evidence"

            bucketed_records.append(enriched)

        return {
            "records": bucketed_records,
            "target_specific_count": target_specific_count,
            "has_sufficient_target_evidence": has_sufficient_target,
        }

    def rerank_with_title_centrality(
        self,
        records: list[dict[str, Any]],
        drug_name: str,
        focus: str,
        species: str,
        max_results: int,
        aliases: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        _ = focus
        _ = species
        aliases = aliases or self.extract_compound_aliases(drug_name)
        reranked: list[dict[str, Any]] = []
        status_priority = {
            "target_exact_in_title": 6,
            "target_alias_in_title": 5,
            "target_not_in_title_but_compound_context_present": 4,
            "target_only_in_abstract_or_summary": 3,
            "unclear_title_target_status": 2,
            "non_target_title_center": 1,
        }
        for record in records:
            enriched = dict(record)
            enriched["title_target_status"] = self.classify_title_target_status(
                enriched,
                drug_name=drug_name,
                aliases=aliases,
            )
            enriched["title_compound_centrality"] = self.detect_title_compound_centrality(
                enriched,
                drug_name=drug_name,
                aliases=aliases,
            )
            enriched["title_exactness_boost"] = self.compute_title_exactness_boost(
                enriched,
                drug_name=drug_name,
                aliases=aliases,
            )
            enriched["target_mention_only_penalty"] = self.compute_target_mention_only_penalty(
                enriched,
                drug_name=drug_name,
                aliases=aliases,
            )
            enriched["final_score"] = round(
                float(enriched.get("final_score", 0.0))
                + float(enriched["title_exactness_boost"])
                - float(enriched["target_mention_only_penalty"]),
                2,
            )
            enriched["score"] = enriched["final_score"]
            reranked.append(enriched)

        reranked.sort(
            key=lambda item: (
                status_priority.get(str(item.get("title_target_status", "unclear_title_target_status")), 0),
                float(item.get("title_compound_centrality", 0.0)),
                float(item.get("final_score", 0.0)),
                float(item.get("title_exactness_boost", 0.0)),
                -float(item.get("target_mention_only_penalty", 0.0)),
                float(item.get("focus_relevance_score", 0.0)),
                int(item.get("year", 0) or 0),
                item.get("title", ""),
            ),
            reverse=True,
        )
        return reranked[:max_results]

    def rerank_with_target_prioritization(
        self,
        records: list[dict[str, Any]],
        drug_name: str,
        focus: str,
        species: str,
        max_results: int,
        aliases: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        aliases = aliases or self.extract_compound_aliases(drug_name)
        title_ranked = self.rerank_with_title_centrality(
            records=records,
            drug_name=drug_name,
            focus=focus,
            species=species,
            max_results=max_results,
            aliases=aliases,
        )

        prioritized: list[dict[str, Any]] = []
        for record in title_ranked:
            enriched = dict(record)
            enriched["species_specific_exactness_boost"] = self.compute_species_specific_exactness_boost(
                enriched,
                drug_name=drug_name,
                species=species,
            )
            enriched["neighbor_suppression_penalty"] = self.compute_neighbor_suppression_penalty(
                enriched,
                drug_name=drug_name,
                species=species,
            )
            enriched["final_score"] = round(
                float(enriched.get("final_score", 0.0))
                + float(enriched["species_specific_exactness_boost"])
                - float(enriched["neighbor_suppression_penalty"]),
                2,
            )
            enriched["score"] = enriched["final_score"]
            prioritized.append(enriched)

        split = self.split_target_vs_supporting_evidence(records=prioritized, drug_name=drug_name)
        bucketed = list(split["records"])
        bucket_priority = {
            "core_target_evidence": 4,
            "supporting_target_evidence": 3,
            "neighbor_supporting_evidence": 2,
            "background_evidence": 1,
        }
        relation_priority = {
            "target_exact": 6,
            "target_alias": 5,
            "target_class_level": 4,
            "ambiguous_compound_context": 3,
            "neighbor_compound": 2,
            "no_clear_compound_relation": 1,
        }
        bucketed.sort(
            key=lambda item: (
                bucket_priority.get(str(item.get("evidence_bucket", "background_evidence")), 0),
                float(item.get("final_score", 0.0)),
                relation_priority.get(str(item.get("compound_relation", "no_clear_compound_relation")), 0),
                float(item.get("species_specific_exactness_boost", 0.0)),
                -float(item.get("neighbor_suppression_penalty", 0.0)),
                float(item.get("matrix_relevance_score", 0.0)),
                float(item.get("focus_relevance_score", 0.0)),
                int(item.get("year", 0) or 0),
                item.get("title", ""),
            ),
            reverse=True,
        )

        reranked: list[dict[str, Any]] = []
        for record in bucketed[:max_results]:
            enriched = dict(record)
            enriched["relevance_explanation"] = self.explain_relevance(
                enriched,
                drug_name=drug_name,
                focus=focus,
                species=species,
            )
            reranked.append(enriched)
        return reranked

    def rerank_with_focus(
        self,
        records: list[dict[str, Any]],
        drug_name: str,
        focus: str,
        max_results: int,
    ) -> list[dict[str, Any]]:
        reranked: list[dict[str, Any]] = []
        for record in records:
            enriched = dict(record)
            enriched["base_score"] = self.score_record(enriched, drug_name=drug_name, focus=focus)
            enriched["focus_relevance_score"] = self.compute_focus_relevance(enriched, focus=focus)
            enriched["focus_mismatch_penalty"] = self.compute_penalty_for_focus_mismatch(enriched, focus=focus)
            enriched["final_score"] = round(
                float(enriched["base_score"]) + float(enriched["focus_relevance_score"]) - float(enriched["focus_mismatch_penalty"]),
                2,
            )
            enriched["score"] = enriched["final_score"]
            enriched["relevance_explanation"] = self.explain_relevance(enriched, drug_name=drug_name, focus=focus)
            reranked.append(enriched)

        reranked.sort(
            key=lambda item: (
                float(item.get("final_score", 0.0)),
                float(item.get("focus_relevance_score", 0.0)),
                self._match_priority(str(item.get("match_type", "no_clear_match"))),
                int(item.get("year", 0) or 0),
                item.get("title", ""),
            ),
            reverse=True,
        )
        return reranked[:max_results]

    def rerank_with_context(
        self,
        records: list[dict[str, Any]],
        drug_name: str,
        focus: str,
        species: str,
        max_results: int,
    ) -> list[dict[str, Any]]:
        reranked: list[dict[str, Any]] = []
        for record in records:
            enriched = dict(record)
            enriched["species_relevance_score"] = self.compute_species_relevance(enriched, species=species)
            enriched["matrix_relevance_score"] = self.compute_matrix_relevance(enriched, focus=focus)
            enriched["context_mismatch_penalty"] = self.compute_context_mismatch_penalty(
                enriched,
                species=species,
                focus=focus,
            )
            enriched["final_score"] = round(
                float(enriched.get("final_score", 0.0))
                + float(enriched["species_relevance_score"])
                + float(enriched["matrix_relevance_score"])
                - float(enriched["context_mismatch_penalty"]),
                2,
            )
            enriched["score"] = enriched["final_score"]
            enriched["relevance_explanation"] = self.explain_relevance(
                enriched,
                drug_name=drug_name,
                focus=focus,
                species=species,
            )
            reranked.append(enriched)

        reranked.sort(
            key=lambda item: (
                float(item.get("final_score", 0.0)),
                float(item.get("matrix_relevance_score", 0.0)),
                float(item.get("species_relevance_score", 0.0)),
                float(item.get("focus_relevance_score", 0.0)),
                self._match_priority(str(item.get("match_type", "no_clear_match"))),
                int(item.get("year", 0) or 0),
                item.get("title", ""),
            ),
            reverse=True,
        )
        return reranked[:max_results]

    def rerank_records(
        self,
        records: list[dict[str, Any]],
        drug_name: str,
        focus: str,
        species: str = "",
        max_results: int = 5,
        aliases: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        records = self._deduplicate_records(records)
        aliases = aliases or self.extract_compound_aliases(drug_name)
        enriched_records: list[dict[str, Any]] = []
        for record in records:
            enriched = dict(record)
            enriched["match_type"] = self.classify_match_type(enriched, drug_name=drug_name, aliases=aliases)
            enriched["compound_relation"] = self.classify_compound_relation(
                enriched,
                drug_name=drug_name,
                aliases=aliases,
            )
            enriched["article_type"] = self.classify_article_type(enriched)
            enriched_records.append(enriched)

        filtered = self.apply_exact_match_filter(records=enriched_records, drug_name=drug_name, focus=focus)
        focus_ranked = self.rerank_with_focus(records=filtered, drug_name=drug_name, focus=focus, max_results=max_results)
        context_ranked = self.rerank_with_context(
            records=focus_ranked,
            drug_name=drug_name,
            focus=focus,
            species=species,
            max_results=max_results,
        )
        return self.rerank_with_target_prioritization(
            records=context_ranked,
            drug_name=drug_name,
            focus=focus,
            species=species,
            max_results=max_results,
            aliases=aliases,
        )

    def _provider_sequence(self) -> list[str]:
        providers = [self.provider]
        if self.enable_secondary_provider and self.secondary_provider and self.secondary_provider not in providers:
            providers.append(self.secondary_provider)
        return providers

    def _search_provider(self, provider_name: str, query: str, max_results: int) -> list[dict[str, Any]]:
        if provider_name == "europe_pmc":
            return self.search_europe_pmc(query=query, max_results=max_results)
        if provider_name == "pubmed":
            return self.search_pubmed(query=query, max_results=max_results)
        return []

    def _build_search_result(
        self,
        records: list[dict[str, Any]],
        queries_used: list[str],
        aliases_used: list[str],
        provider_used: str,
        focus: str,
        species: str,
    ) -> LiteratureSearchResult:
        references = [LiteratureReference(**record) for record in records]
        retrieval_modes = sorted({reference.retrieval_mode for reference in references}) or ["mock_fallback"]
        reference_dicts = [self._reference_to_dict(reference) for reference in references]
        evidence_tags = Counter(
            tag
            for record in reference_dicts
            for tag in self.extract_evidence_tags(record, focus=focus, species=species)
        )
        return LiteratureSearchResult(
            records=references,
            queries_used=queries_used,
            aliases_used=aliases_used,
            provider_used=provider_used,
            primary_provider=self.provider,
            retrieval_mode_summary=", ".join(retrieval_modes),
            focus_profile_summary=self._format_focus_profile_summary(references),
            focus_keyword_hits_summary=self._summarize_counter(Counter(hit for reference in references for hit in self._split_hits(reference.focus_keyword_hits))),
            focus_relevance_summary=self._format_focus_relevance_summary(references),
            species_profile_summary=self._format_species_profile_summary(references),
            matrix_profile_summary=self._format_matrix_profile_summary(references),
            species_match_summary=self._format_species_relevance_summary(references),
            matrix_relevance_summary=self._format_matrix_relevance_summary(references),
            compound_relation_summary=self._summarize_counter(Counter(reference.compound_relation for reference in references)),
            title_target_status_summary=self._summarize_counter(Counter(reference.title_target_status for reference in references)),
            title_centric_boost_summary=self._format_title_centric_boost_summary(references),
            mention_only_penalty_summary=self._format_mention_only_penalty_summary(references),
            evidence_bucket_summary=self._summarize_counter(Counter(reference.evidence_bucket for reference in references)),
            neighbor_suppression_summary=self._format_neighbor_suppression_summary(references),
            match_distribution_summary=self._summarize_counter(Counter(reference.match_type for reference in references)),
            article_type_summary=self._summarize_counter(Counter(reference.article_type for reference in references)),
            evidence_tag_summary=self._summarize_counter(evidence_tags),
            hotspot_linking_summary="Hotspot linking is generated downstream after chemistry and literature are combined.",
            assay_support_linking_summary="Assay support linking is generated downstream after chemistry and literature are combined.",
            literature_confidence_summary="Cross-source literature confidence is calibrated downstream after chemistry-backed linking is available.",
            evidence_alignment_summary="Species/context evidence alignment is calibrated downstream after chemistry-backed linking is available.",
        )

    def _deduplicate_records(self, records: list[dict[str, Any]]) -> list[dict[str, Any]]:
        deduplicated: dict[tuple[str, int], dict[str, Any]] = {}
        for record in records:
            key = (str(record.get("title", "")).lower(), int(record.get("year", 0) or 0))
            existing = deduplicated.get(key)
            if existing is None or len(str(record.get("summary", ""))) > len(str(existing.get("summary", ""))):
                deduplicated[key] = record
        return list(deduplicated.values())

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
    def _parse_year(value: Any) -> int:
        digits = "".join(character for character in str(value) if character.isdigit())
        if len(digits) >= 4:
            return int(digits[:4])
        return 0

    @staticmethod
    def _clean_text(value: Any) -> str:
        if value is None:
            return ""
        return " ".join(unescape(str(value)).split())

    def _extract_authors(self, raw: dict[str, Any]) -> str:
        if raw.get("authorString"):
            return self._clean_text(raw["authorString"])

        authors = raw.get("authors")
        if isinstance(authors, list):
            names: list[str] = []
            for author in authors:
                if isinstance(author, dict):
                    names.append(self._clean_text(author.get("name")))
                else:
                    names.append(self._clean_text(author))
            cleaned = ", ".join(name for name in names if name)
            return cleaned or "Authors not available."

        if authors:
            return self._clean_text(authors)
        return "Authors not available."

    @staticmethod
    def _build_url(raw: dict[str, Any], retrieval_mode: str) -> str:
        explicit_url = raw.get("url")
        if explicit_url:
            return str(explicit_url)

        if retrieval_mode == "europe_pmc":
            pmid = raw.get("pmid")
            pmcid = raw.get("pmcid")
            doi = raw.get("doi")
            if pmid:
                return f"https://europepmc.org/article/MED/{pmid}"
            if pmcid:
                return f"https://europepmc.org/article/PMC/{pmcid}"
            if doi:
                return f"https://doi.org/{doi}"

        if retrieval_mode == "pubmed":
            uid = raw.get("uid")
            if uid:
                return f"https://pubmed.ncbi.nlm.nih.gov/{uid}/"
        return ""

    @staticmethod
    def _normalize_for_alias_matching(value: str) -> str:
        return re.sub(r"[\s\-]+", "", value.strip().lower())

    @staticmethod
    def _match_priority(match_type: str) -> int:
        priorities = {
            "exact_name_match": 4,
            "alias_match": 3,
            "class_level_match": 2,
            "no_clear_match": 1,
        }
        return priorities.get(match_type, 0)

    def _collect_focus_hits(self, record: dict[str, Any], focus: str) -> list[str]:
        profile = self.get_focus_profile(focus)
        text = f"{record.get('title', '')} {record.get('summary', '')}".lower()
        hits: list[str] = []
        for phrase in profile["high_priority_phrases"]:
            if self._contains_phrase(text, phrase):
                hits.append(phrase)
        for term in profile["high_priority_terms"]:
            if self._contains_phrase(text, term):
                hits.append(term)
        return self._deduplicate(hits)

    @staticmethod
    def _summarize_counter(counter: Counter[str]) -> str:
        if not counter:
            return "none"
        order = [key for key, _ in counter.most_common()]
        return ", ".join(f"{key}={counter[key]}" for key in order)

    @staticmethod
    def _contains_phrase(text: str, phrase: str) -> bool:
        pattern = r"\b" + r"\s+".join(re.escape(token) for token in phrase.split()) + r"\b"
        return bool(re.search(pattern, text))

    @staticmethod
    def _split_hits(hits: str) -> list[str]:
        if not hits or hits in {"none", "neutral"}:
            return []
        return [item.strip() for item in hits.split(",") if item.strip()]

    @staticmethod
    def _extract_compound_like_tokens(text: str) -> list[str]:
        suffix_pattern = "|".join(COMPOUND_SUFFIXES)
        return re.findall(rf"\b[a-z][a-z0-9\-]{{3,}}(?:{suffix_pattern})\b", text)

    @staticmethod
    def _reference_to_dict(reference: LiteratureReference) -> dict[str, Any]:
        return {
            "title": reference.title,
            "source": reference.source,
            "year": reference.year,
            "summary": reference.summary,
            "authors": reference.authors,
            "journal": reference.journal,
            "url": reference.url,
            "retrieval_mode": reference.retrieval_mode,
            "score": reference.score,
            "base_score": reference.base_score,
            "focus_relevance_score": reference.focus_relevance_score,
            "species_relevance_score": reference.species_relevance_score,
            "matrix_relevance_score": reference.matrix_relevance_score,
            "focus_mismatch_penalty": reference.focus_mismatch_penalty,
            "context_mismatch_penalty": reference.context_mismatch_penalty,
            "title_exactness_boost": reference.title_exactness_boost,
            "target_mention_only_penalty": reference.target_mention_only_penalty,
            "title_compound_centrality": reference.title_compound_centrality,
            "species_specific_exactness_boost": reference.species_specific_exactness_boost,
            "neighbor_suppression_penalty": reference.neighbor_suppression_penalty,
            "final_score": reference.final_score,
            "query_used": reference.query_used,
            "match_type": reference.match_type,
            "compound_relation": reference.compound_relation,
            "title_target_status": reference.title_target_status,
            "evidence_bucket": reference.evidence_bucket,
            "article_type": reference.article_type,
            "relevance_explanation": reference.relevance_explanation,
            "focus_keyword_hits": reference.focus_keyword_hits,
            "species_keyword_hits": reference.species_keyword_hits,
            "matrix_keyword_hits": reference.matrix_keyword_hits,
        }

    def _format_focus_profile_summary(self, references: list[LiteratureReference]) -> str:
        if not references:
            return "none"
        sample_hits = Counter(hit for reference in references for hit in self._split_hits(reference.focus_keyword_hits))
        if not sample_hits:
            return "No strong focus-specific keywords detected in the retained set."
        top_hits = ", ".join(keyword for keyword, _ in sample_hits.most_common(4))
        return f"Ranking emphasizes focus-specific keywords such as {top_hits}."

    @staticmethod
    def _format_focus_relevance_summary(references: list[LiteratureReference]) -> str:
        if not references:
            return "none"
        avg_focus = sum(reference.focus_relevance_score for reference in references) / len(references)
        weak_exact = sum(
            1
            for reference in references
            if reference.match_type == "exact_name_match" and reference.focus_relevance_score < 4.0
        )
        return (
            f"Average focus relevance score: {avg_focus:.1f}; "
            f"exact but weak-focus records: {weak_exact}."
        )

    def _format_species_profile_summary(self, references: list[LiteratureReference]) -> str:
        if not references:
            return "none"
        sample_hits = Counter(hit for reference in references for hit in self._split_hits(reference.species_keyword_hits))
        if not sample_hits:
            return "Species-aware reranking is neutral because no explicit species context was detected."
        top_hits = ", ".join(keyword for keyword, _ in sample_hits.most_common(4))
        return f"Ranking boosts records with species context such as {top_hits}."

    @staticmethod
    def _format_matrix_profile_summary(references: list[LiteratureReference]) -> str:
        if not references:
            return "none"
        sample_hits = Counter(hit for reference in references for hit in LiteratureService._split_hits(reference.matrix_keyword_hits))
        if not sample_hits:
            return "Matrix-aware reranking found limited explicit matrix or assay-context signals."
        top_hits = ", ".join(keyword for keyword, _ in sample_hits.most_common(5))
        return f"Ranking emphasizes matrix and experimental-context signals such as {top_hits}."

    @staticmethod
    def _format_species_relevance_summary(references: list[LiteratureReference]) -> str:
        if not references:
            return "none"
        avg_species = sum(reference.species_relevance_score for reference in references) / len(references)
        aligned = sum(1 for reference in references if reference.species_relevance_score >= 3.0)
        mismatched = sum(
            1
            for reference in references
            if reference.species_relevance_score < 1.0 and reference.context_mismatch_penalty >= 3.0
        )
        return (
            f"Average species relevance score: {avg_species:.1f}; "
            f"species-aligned records: {aligned}; context-mismatched records: {mismatched}."
        )

    @staticmethod
    def _format_matrix_relevance_summary(references: list[LiteratureReference]) -> str:
        if not references:
            return "none"
        avg_matrix = sum(reference.matrix_relevance_score for reference in references) / len(references)
        strong_context = sum(1 for reference in references if reference.matrix_relevance_score >= 4.0)
        weak_context = sum(1 for reference in references if reference.matrix_relevance_score < 2.0)
        return (
            f"Average matrix/context relevance score: {avg_matrix:.1f}; "
            f"strong context records: {strong_context}; weak context records: {weak_context}."
        )

    @staticmethod
    def _format_title_centric_boost_summary(references: list[LiteratureReference]) -> str:
        if not references:
            return "none"
        avg_boost = sum(reference.title_exactness_boost for reference in references) / len(references)
        title_centered = sum(
            1
            for reference in references
            if reference.title_target_status in {"target_exact_in_title", "target_alias_in_title"}
        )
        top_title_centered = sum(
            1
            for reference in references[:3]
            if reference.title_target_status in {"target_exact_in_title", "target_alias_in_title"}
        )
        return (
            f"Average title-centric boost: {avg_boost:.1f}; "
            f"title-centered target records: {title_centered}; "
            f"title-centered records in top three: {top_title_centered}."
        )

    @staticmethod
    def _format_mention_only_penalty_summary(references: list[LiteratureReference]) -> str:
        if not references:
            return "none"
        avg_penalty = sum(reference.target_mention_only_penalty for reference in references) / len(references)
        mention_only = sum(1 for reference in references if reference.title_target_status == "target_only_in_abstract_or_summary")
        non_target_titles = sum(1 for reference in references if reference.title_target_status == "non_target_title_center")
        return (
            f"Average mention-only penalty: {avg_penalty:.1f}; "
            f"abstract-mention records: {mention_only}; "
            f"non-target title-centered records: {non_target_titles}."
        )

    @staticmethod
    def _format_neighbor_suppression_summary(references: list[LiteratureReference]) -> str:
        if not references:
            return "none"
        target_core = sum(1 for reference in references if reference.evidence_bucket == "core_target_evidence")
        neighbor_support = sum(1 for reference in references if reference.evidence_bucket == "neighbor_supporting_evidence")
        ambiguous = sum(1 for reference in references if reference.compound_relation == "ambiguous_compound_context")
        avg_penalty = sum(reference.neighbor_suppression_penalty for reference in references) / len(references)
        return (
            f"Core target evidence count: {target_core}; "
            f"neighbor supporting evidence count: {neighbor_support}; "
            f"ambiguous compound-context records: {ambiguous}; "
            f"average neighbor suppression penalty: {avg_penalty:.1f}."
        )

    def _mentions_multiple_species(self, title: str, summary: str) -> bool:
        text = f"{title} {summary}"
        matched_species = 0
        for species_key, profile in SPECIES_PROFILES.items():
            if species_key == "unknown":
                continue
            keywords = list(profile["terms"]) + list(profile["phrases"]) + list(profile["aliases"])
            if any(self._contains_phrase(text, keyword) for keyword in keywords):
                matched_species += 1
        return matched_species >= 2

    def _mentions_non_target_species(self, text: str, target_species_key: str) -> bool:
        for species_key, profile in SPECIES_PROFILES.items():
            if species_key in {"unknown", target_species_key}:
                continue
            keywords = list(profile["terms"]) + list(profile["phrases"]) + list(profile["aliases"])
            if any(self._contains_phrase(text, keyword) for keyword in keywords):
                return True
        return False

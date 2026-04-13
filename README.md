# ADME Strategy Copilot v1.6-stage1

ADME Strategy Copilot is a minimal, runnable, biopharma-focused MVP that generates a preclinical ADME strategy report from a drug name or SMILES input. The current version is intentionally lightweight, demo-friendly, and designed to fit into an OpenClaw / DeerFlow-style agent workflow without modifying existing OpenClaw core code.

## Stage 1 Scope

This repository is now frozen as the Stage 1 prototype for `ADME Strategy Copilot v1.6-stage1`.

Stage 1 currently includes:

- literature intelligence with real-first retrieval plus fallback
- RDKit-enhanced chemistry intelligence with heuristic metabolism and disposition support
- hotspot / evidence linking and confidence-calibrated prioritization
- decision-ready framing sections such as `Executive Decision Summary`, `What to Do Now`, and `Key Uncertainties`
- audience-aware report modes: `scientist`, `executive`, `cro_proposal`, and `regulatory_prep`

Stage 1 intentionally does not include:

- formal statistical certainty or learned predictive models
- full metabolite structure enumeration or reaction-product generation
- frontend / UI layer
- database persistence or user management
- PDF export or workflow management beyond markdown artifact generation

## Who This Is For

- DMPK and ADME scientists who want a structured early-strategy briefing
- project leads who need a shorter decision-oriented summary
- teams preparing CRO assay-package discussions
- teams organizing early conservative evidence and uncertainty summaries

## MVP Scope

This MVP focuses on one artifact: a Markdown `Preclinical ADME Strategy Report`.

Inputs:

- `drug_name` or `smiles`
- `species`
- `focus`

Outputs:

- predicted metabolic pathways
- recommended in vitro studies
- suggested in vivo design
- DDI / clearance / reactive metabolite risks
- initial human translation guidance
- supporting literature and disclaimer

Out of scope for this MVP:

- frontend
- database
- Docker
- authentication
- true raw HRMS processing
- real FDA / EMA integrations

## Environment Notes

This project is designed for the current server layout:

- project root: `/home/knan/adme_strategy_copilot`
- OpenClaw skills root: `/home/knan/.openclaw/workspace/skills`
- OpenClaw env file is reused when present: `/home/knan/.openclaw/.env`

Runtime defaults:

- standard library first
- no mandatory LLM dependency
- no mandatory network dependency
- proxy and API settings can be reused from existing environment variables or `.env` files

## Real Literature Search (v0.2)

The v0.2 literature module now uses a real-first strategy:

- real literature retrieval is attempted first
- Europe PMC is the current supported live provider
- if the live request fails, times out, returns empty data, or `requests` is unavailable, the pipeline automatically falls back to the existing mock references
- network or proxy problems do not break the main ADME report workflow

Configuration is environment-driven and optional:

- `ENABLE_REAL_LITERATURE_SEARCH=true`
- `LITERATURE_PROVIDER=europe_pmc`
- `EUROPE_PMC_BASE_URL=https://www.ebi.ac.uk/europepmc/webservices/rest/search`
- `LITERATURE_TIMEOUT=20`
- `LITERATURE_MAX_RESULTS=5`

Requests inherit the server's existing `HTTP_PROXY` and `HTTPS_PROXY` environment variables automatically. No proxy is hardcoded in the project.

## Literature Retrieval (v0.3)

The v0.3 literature layer keeps the same fallback-safe architecture and improves the retrieval quality:

- a DMPK-aware query builder changes query sets based on `MetID`, `PK`, `DDI`, and `Safety`
- Europe PMC and PubMed results are locally reranked using title, abstract, focus keywords, and publication year
- PubMed E-utilities is now available as an optional provider
- provider routing supports a primary provider, an optional secondary provider, and then mock fallback if both live routes fail
- the report now shows primary provider, provider used, query set used, and retrieval mode summary

Suggested v0.3 environment settings:

- `LITERATURE_PROVIDER=europe_pmc`
- `ENABLE_SECONDARY_LITERATURE_PROVIDER=true`
- `SECONDARY_LITERATURE_PROVIDER=pubmed`
- `PUBMED_ESEARCH_URL=https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi`
- `PUBMED_ESUMMARY_URL=https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi`
- `PUBMED_EFETCH_URL=https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi`

If both live providers fail, the report still completes with `mock_fallback`.

## Literature Quality (v0.4)

The v0.4 retrieval layer adds a second pass that is more compound-aware and less noisy:

- compound exact-match filtering now prefers records with direct target-compound mentions
- lightweight alias handling tolerates case, whitespace, and hyphen variations
- article-type heuristics label results as original research, review, clinical study, preclinical study, guideline, case report, or unknown
- generalized class-level hits and neighbor-compound papers are pushed down unless compound-specific evidence is sparse
- each retained paper now carries a short relevance explanation so the report shows why it ranked near the top

This reduces common noise patterns such as:

- papers about related inhibitors in the same chemical class
- broad ADME or PK reviews with weak target-compound specificity
- mechanistically similar but non-target compounds that only mention the target in passing

## Focus-Aware Reranking (v0.5)

The v0.5 retrieval layer keeps the v0.4 compound filtering logic and adds a second scoring pass tuned to the requested focus.

- each focus now has its own lightweight keyword profile
- ranking is driven by two stages: compound exactness first defines the candidate pool, then focus relevance orders that pool
- `MetID` favors metabolite-identification, biotransformation, microsome, hepatocyte, and LC-MS style evidence
- `PK` favors exposure, clearance, bioavailability, and standard PK parameter terms
- `DDI` favors CYP inhibition, CYP3A, transporter, and interaction-study language
- `Safety` favors reactive metabolite, bioactivation, toxicity, and glutathione-conjugate signals

This matters because DMPK scientists often need different evidence depending on the task:

- a strong exact-name clinical PK paper may be useful for `PK` but weak for `MetID`
- a class-level metabolism paper with rich microsome and metabolite-profiling language can be more useful for `MetID` than an exact-name paper focused on efficacy or dosing logistics
- the report now explains both the compound match quality and the focus-specific ranking logic for each retained paper

## Species- and Matrix-Aware Reranking (v0.6)

The v0.6 retrieval layer keeps the v0.5 focus-aware logic and adds a third reranking pass tuned to species and experimental context.

- `species-aware` scoring now looks for Human, Rat, Mouse, Dog, and Monkey evidence in titles and abstracts
- `matrix-aware` scoring now looks for context such as microsomes, hepatocytes, S9, plasma, bile, urine, feces, LC-MS, and related assay terms
- ranking now follows a practical three-layer idea: compound exactness defines the pool, focus relevance orders that pool, then species and matrix context fine-tune the top evidence
- each retained paper now explains whether it rose because it matched the requested species or because it carried the right experimental matrix context

This matters in real DMPK work because the same exact-name paper can have very different value depending on the question:

- for `MetID`, a rat microsome or rat hepatocyte paper with bile, urine, feces, or LC-MS context is often more actionable than a generic clinical exact-name article
- for `PK`, plasma, serum, exposure, and dosing-route context matters more than broad metabolism language
- for `DDI`, CYP phenotyping, microsomes, hepatocytes, recombinant enzymes, and interaction-study design matter
- for `Safety`, reactive metabolite, glutathione, bioactivation, and covalent binding context matters

This extra pass helps reduce noise from:

- exact-name clinical papers that are weak for the requested experimental setup
- species-mismatched studies when the query clearly targets rat, human, dog, or another species
- broad reviews that mention the compound but do not carry the right assay matrix or bioanalytical context

## Target-Compound Prioritization (v0.7)

The v0.7 retrieval layer keeps the v0.6 context-aware logic and adds a final pass that separates target-compound evidence from neighbor-compound evidence.

- live retrieval results are now classified as `target_exact`, `target_alias`, `target_class_level`, `neighbor_compound`, `ambiguous_compound_context`, or `no_clear_compound_relation`
- target-compound records with strong species and assay-context alignment receive an extra species-specific exactness boost
- neighbor compounds are no longer discarded, but they are explicitly demoted into supporting evidence unless target-compound evidence is genuinely sparse
- the report now groups retained records into `core_target_evidence`, `supporting_target_evidence`, `neighbor_supporting_evidence`, and `background_evidence`

This matters because live DMPK retrieval often surfaces chemically or mechanistically adjacent compounds:

- for BTK inhibitors, papers on remibrutinib, acalabrutinib, or zanubrutinib can look highly relevant for MetID and species context even when they are not actually about ibrutinib
- without neighbor suppression, these papers can outrank weaker but still more decision-relevant target-compound evidence
- in practice, scientists usually want those neighbor papers preserved as supporting background, not mistaken for the core evidence base of the target drug

The v0.7 pass therefore uses a simple but useful rule:

- protect target exact and alias evidence first
- add extra lift when the same paper also matches the requested species and experimental context
- keep neighbor-compound papers available as supporting evidence
- make the target-vs-neighbor distinction explicit in both the ranking explanation and the final report

## Title-Centric Target Detection (v0.8)

The v0.8 retrieval layer keeps the v0.7 target-versus-neighbor logic and adds a title-centric pass that distinguishes articles centered on the target drug from articles that only mention the target in the abstract.

- records are now labeled as `target_exact_in_title`, `target_alias_in_title`, `target_only_in_abstract_or_summary`, `target_not_in_title_but_compound_context_present`, `non_target_title_center`, or `unclear_title_target_status`
- title-exact and title-alias hits receive an explicit boost
- abstract-mention-only records receive a dedicated demotion so they remain supporting rather than masquerading as core target evidence
- title centrality also considers whether the target appears early in the title and whether multiple drug names compete for attention in the same title

This matters because live search often returns papers where the target drug is mentioned only as a comparator, inhibitor control, or side note in the abstract:

- these records can still look highly relevant on focus, species, or matrix context
- but they are usually weaker evidence than papers whose titles are actually centered on the target compound
- title-centered articles are a stronger signal that the whole paper is really about the target drug rather than merely mentioning it

The v0.8 pass therefore adds one more practical rule:

- prefer target-centered titles when ranking core evidence
- preserve abstract-mention records as supporting or background evidence when they still add context
- demote non-target title-centered articles even if they mention the target somewhere downstream

## Chemistry Intelligence Layer (v1.0)

The v1.0 release keeps the full literature-ranking stack and adds an optional RDKit-based chemistry intelligence layer on top of the existing rule-based pipeline.

- RDKit-based SMILES parsing is now supported when RDKit is available in the active Python environment
- the system can now detect lightweight structural features such as aromatic rings, heteroaromatic motifs, amines, phenols, alcohols, sulfur motifs, esters, amides, halogens, and carboxylic acids
- these features feed soft-spot heuristics, Phase I and Phase II liability hints, and reactive-metabolite awareness prompts
- chemistry-derived implications now flow into predicted pathways, potential risks, and in vitro study suggestions

The current chemistry layer is deliberately heuristic rather than fully mechanistic:

- it does not enumerate metabolites
- it does not generate reaction products
- it does not run QSAR, docking, or ML models
- it is designed to behave like a practical medicinal-chemistry and DMPK prototype rather than a full metabolism engine

Fallback behavior remains first-class:

- if no SMILES is provided, the pipeline keeps running and falls back to the existing text-based heuristics
- if the SMILES string is invalid, the pipeline keeps running and records the limitation in the chemistry section
- if RDKit is unavailable, the chemistry layer degrades gracefully and the legacy metabolism and protocol logic still works

## Chemistry Prioritization Layer (v1.1)

The v1.1 release keeps the v1.0 RDKit-based chemistry layer and makes it behave more like a DMPK scientist briefing rather than a raw feature dump.

- substructure-to-CYP preference hints now translate tertiary amines, aromatic motifs, heteroaromatics, sulfur motifs, and hydrolysis-prone esters into conservative "worth checking first" guidance
- species-aware chemistry interpretation now changes the framing for Human, Rat, Mouse, Dog, and Monkey use cases
- chemistry-driven assay prioritization now ranks microsomes, hepatocytes, S9, plasma stability, CYP phenotyping, GSH trapping, and HRMS-style metabolite profiling based on structure, species, and focus
- pathway priorities now help separate which routes should be treated as high-priority verification versus medium-priority background liabilities

This is still a heuristic layer rather than a true isoform predictor:

- CYP hints are intentionally conservative
- the system does not claim exact isoform assignment
- wording is limited to "may be worth checking", "likely worth prioritizing", or other cautious phrasing

The practical goal is to make Rat and Human experiment design feel more naturally linked to chemistry:

- `Rat + MetID` now more naturally emphasizes rat liver microsomes, rat hepatocytes, and bile / urine / feces coverage when the chemistry suggests broad metabolite coverage is useful
- `Human + DDI` now more naturally emphasizes human liver microsomes, human hepatocytes, and CYP phenotyping when oxidative liabilities are present
- hydrolysis-prone chemistry now pushes plasma stability higher
- sulfur or thiophene-linked chemistry now keeps reactive-metabolite awareness and GSH trapping visible without overstating the risk

## Disposition-Aware Chemistry Layer (v1.2)

The v1.2 release keeps the v1.1 metabolism-focused chemistry briefing and expands it into a broader metabolism-plus-disposition interpretation layer.

- substructure-to-transporter hints now add conservative uptake or efflux awareness when basic, acidic, or high-polarity chemistry could matter
- permeability hints now distinguish between limited passive permeability concerns and chemistry that may still permeate but warrants efflux-aware interpretation
- clearance-route hints now frame oxidative, conjugative, hydrolytic, biliary, renal, and transporter-linked route-of-clearance possibilities as empirical follow-up questions rather than conclusions
- disposition-aware assay priorities now add Caco-2, MDCK/MDR1-aware follow-up, transporter-awareness, plasma protein binding, and route-clarification context on top of the existing microsome and hepatocyte priorities

This is still a heuristic layer rather than a transporter or permeability predictor:

- the system does not claim confirmed transporter substrates
- it does not produce a quantitative permeability value
- it does not assign a definitive route of clearance
- all disposition language is intentionally phrased as "may be worth checking", "plausible", or "worth keeping in mind"

The practical effect is that the chemistry layer now extends more naturally from metabolism into disposition:

- metabolism-driven implications still drive soft spots, CYP-oriented hints, and pathway priorities
- disposition-driven implications now add permeability, transporter, and clearance-route context when structure suggests they may matter
- Rat-focused MetID work can now surface bile / urine / feces recovery context more explicitly
- Human-focused work can now keep transporter plus CYP follow-up visible when clearance or exposure interpretation is likely to be mixed

## Evidence-Linked Chemistry Layer (v1.3)

The v1.3 release keeps the v1.2 chemistry and disposition logic and adds a lightweight traceability layer that links structure, literature direction, and assay prioritization.

- structure-to-evidence linking now connects structural hotspots such as amine oxidation, phenolic conjugation, sulfur/reactive motifs, and ester hydrolysis to evidence tags found in the retained literature set
- hotspot-backed prioritization now combines chemistry confidence with evidence availability, so priorities can be described as high, medium, or low support rather than asserted as certainty
- assay recommendation traceability now explains which hotspots and literature directions support a given assay recommendation
- the report now includes an `Evidence-Linked Prioritization` section that summarizes why the top hotspots and assays were prioritized

This is still heuristic linking rather than a formal evidence graph:

- it does not build a knowledge graph database
- it does not claim precise citation grounding
- it does not infer exact experimental conditions from papers
- support is intentionally expressed in layered terms such as `high`, `medium`, or `low` evidence support

The practical goal is to make the final report answer questions that scientists ask during planning:

- why is this pathway considered high-priority
- which structural liabilities support that view
- which retained literature directions reinforce it
- why should a given assay be run first in the current species and focus context

## Confidence-Calibrated Prioritization (v1.4)

The v1.4 release keeps the v1.3 structure-to-evidence linking layer and adds a lightweight confidence calibration layer across chemistry, literature support, and species/context alignment.

- cross-source confidence calibration now combines chemistry clarity, literature support strength, and species/context alignment
- hotspot-backed priorities now distinguish between `priority` and `overall confidence`
- assay recommendations now carry a recommendation-confidence layer rather than assuming every high-priority assay is automatically high-confidence
- pathway priorities now separate "important to check" from "well-supported by current evidence"

This matters because priority does not automatically mean high confidence:

- a chemistry-led oxidative liability may still be only medium-confidence if target-anchored evidence is sparse
- a transporter or permeability follow-up can be useful while still remaining exploratory
- a species-aligned, target-anchored microsome or hepatocyte recommendation can earn higher confidence than a purely structure-led disposition suggestion

The current confidence layer is still heuristic rather than statistical certainty:

- it is not a Bayesian model
- it is not formal uncertainty quantification
- it is not a learned judge model
- confidence is intentionally expressed as `high`, `medium`, or `exploratory` for internal planning discussion rather than numerical certainty

## Decision-Ready Scientist Briefing (v1.5)

The v1.5 release keeps the v1.4 confidence layer and reframes the final report so it reads more like an internal project memo or CRO discussion brief.

- the report now starts with an `Executive Decision Summary` rather than forcing the reader to parse all technical sections first
- recommendations are now organized into `What to Do Now`, `What to Verify Next`, and `Exploratory Follow-up`
- each action is framed with why it should be done now, what it will clarify, and what kind of support currently underpins it
- a structured `Key Uncertainties` section now collects the main open questions instead of scattering them across chemistry, literature, and protocol sections
- a `Suggested Next-Step Plan` now turns priorities into a staged sequence of practical follow-up steps

This makes the output more useful for internal review and CRO communication:

- project teams can quickly see the top few actions instead of re-sorting technical detail by hand
- medium-confidence items stay visible without being confused with immediate first-pass work
- exploratory items remain on the page, but are explicitly framed as conditional follow-up rather than core commitments
- uncertainty is expressed more transparently, especially when the run is limited by no SMILES, weak target-anchored literature, or species translation gaps

The v1.5 framing is still intentionally heuristic:

- it is not a project management engine
- it is not a budgeting or timeline optimizer
- it does not assign formal decision thresholds
- it is meant to support scientist discussion and early planning, not replace experimental judgment

## Multi-Report Modes (v1.6)

The v1.6 release keeps the same underlying analysis pipeline and adds a presentation layer that can reframe the same result for different audiences.

Supported report modes:

- `scientist`: fullest technical view for internal DMPK and ADME discussion
- `executive`: shorter decision memo focused on top priorities, immediate actions, and main uncertainties
- `cro_proposal`: work-package-oriented framing that emphasizes assay priorities, first-pass package design, and optional follow-up
- `regulatory_prep`: more conservative framing that emphasizes evidence boundaries, confidence caveats, and what remains unverified

This mode layer does not change the underlying analysis:

- chemistry, literature, hotspot, evidence-linking, and confidence logic stay the same
- the mode only changes section selection, information density, and audience-facing tone
- `scientist` remains the default mode

Practical differences by mode:

- `scientist` keeps `Chemistry Intelligence`, `Evidence-Linked Prioritization`, `Confidence-Calibrated Prioritization`, and the fuller literature traceability view
- `executive` keeps the decision-ready sections up front and compresses technical detail into a short snapshot
- `cro_proposal` emphasizes `Recommended In Vitro Studies`, assay work-package framing, and suggested first-pass versus optional follow-up packages
- `regulatory_prep` emphasizes `Key Uncertainties`, confidence caveats, evidence strength, and translation caution

If you want to select a mode explicitly, use `--report-mode`:

```bash
python3 /home/knan/adme_strategy_copilot/main.py --report-mode executive
python3 /home/knan/adme_strategy_copilot/main.py --report-mode cro_proposal
python3 /home/knan/adme_strategy_copilot/main.py --report-mode regulatory_prep
```

Generated report files now include the mode suffix to avoid overwriting each other, for example:

- `/home/knan/adme_strategy_copilot/reports/ibrutinib_adme_strategy_scientist.md`
- `/home/knan/adme_strategy_copilot/reports/ibrutinib_adme_strategy_executive.md`
- `/home/knan/adme_strategy_copilot/reports/ibrutinib_adme_strategy_cro_proposal.md`
- `/home/knan/adme_strategy_copilot/reports/ibrutinib_adme_strategy_regulatory_prep.md`

## OpenClaw Skill Integration

`SkillLoader` uses this priority order:

1. `/home/knan/.openclaw/workspace/skills`
2. `/home/knan/adme_strategy_copilot/skills`

It supports both of these shapes:

- single markdown file: `skill_name.md`
- directory skill: `skill_name/SKILL.md`

This lets the project coexist with the current OpenClaw workspace while adding new ADME-specific context files without overwriting existing skills.

## Directory Layout

```text
/home/knan/adme_strategy_copilot/
  app/
  agents/
  services/
  utils/
  prompts/
  skills/
  reports/
  tests/
  main.py
  requirements.txt
  .env.example
  README.md
```

## Agent Design

- `LeadAgent`: orchestrates the workflow, loads skills, and writes the final report
- `LiteratureAgent`: builds DMPK-aware query sets and routes them through provider-aware retrieval with reranking
- `LiteratureAgent`: also tracks alias usage, focus-profile summaries, match quality, and article-type summaries for reporting
- `MetabolismPredictionAgent`: applies heuristic motif rules for metabolism and risk flags
- `ProtocolDesignAgent`: proposes in vitro and in vivo ADME studies tied to the metabolism prediction
- `SynthesisAgent`: normalizes sections into report-ready markdown content
- `ReportGenerator`: saves the final markdown artifact in `reports/`

## Installation

Optional:

```bash
cd /home/knan/adme_strategy_copilot
python3 -m pip install -r requirements.txt
```

The current MVP still runs offline by falling back to mock literature. For live Europe PMC or PubMed retrieval, install `requests`.

## Run

Default demo:

```bash
python3 /home/knan/adme_strategy_copilot/main.py
```

Custom input:

```bash
python3 /home/knan/adme_strategy_copilot/main.py \
  --drug-name "Compound X" \
  --smiles "CCN(CC)C1=CC=CC=C1" \
  --species "Dog" \
  --focus "DDI"
```

## Quick Demo

Fastest Stage 1 demo:

```bash
python3 /home/knan/adme_strategy_copilot/main.py
```

Executive-style demo:

```bash
python3 /home/knan/adme_strategy_copilot/main.py --report-mode executive
```

CRO-oriented demo:

```bash
python3 /home/knan/adme_strategy_copilot/main.py --report-mode cro_proposal
```

Regulatory-prep demo:

```bash
python3 /home/knan/adme_strategy_copilot/main.py --report-mode regulatory_prep
```

## Available Report Modes

- `scientist`
  Default mode. Keeps the fullest technical detail, including chemistry, evidence-linking, confidence, and literature traceability.
- `executive`
  Shorter decision memo focused on top priorities, immediate next step, and main uncertainty.
- `cro_proposal`
  Work-package-oriented framing for assay planning, first-pass package discussion, and follow-up package design.
- `regulatory_prep`
  More conservative framing focused on confidence caveats, evidence boundaries, translation caution, and what remains unverified.

## Recommended Demo Flow

1. Start with `scientist` mode to show the full technical depth of the Stage 1 prototype.
2. Switch to `executive` mode to show how the same analysis is compressed into a project-review memo.
3. Switch to `cro_proposal` mode to show how the same result can be reframed into a suggested assay package.
4. Use `regulatory_prep` mode to highlight confidence caveats, uncertainty framing, and evidence boundaries.
5. If you want to showcase the chemistry layer specifically, rerun with a valid SMILES and compare the output against the no-SMILES fallback path.

## Best Demo Order

1. `scientist`
2. `executive`
3. `cro_proposal`
4. `regulatory_prep`

This order works best because it starts with the richest technical baseline and then shows how the same underlying result can be reframed for progressively different audiences.

## Example Input

- `drug_name = "Ibrutinib"`
- `smiles = ""`
- `species = "Rat"`
- `focus = "MetID"`

## Example Output

Report path:

`/home/knan/adme_strategy_copilot/reports/ibrutinib_adme_strategy_scientist.md`

The report includes:

- input summary
- metabolic pathway hypotheses
- in vitro study recommendations
- in vivo design guidance
- risk statements
- human translation suggestions
- real or fallback literature support
- compound-match and article-type summaries
- disclaimer

See the [`demo/`](/home/knan/adme_strategy_copilot/demo) directory for audience-specific demo walkthroughs.

## Current Limitations

- the current system is heuristic by design and should not be interpreted as formal statistical certainty
- confidence labels are calibrated planning signals, not validated probability estimates
- the chemistry layer does not perform full metabolite enumeration or reaction-network generation
- the project does not yet include a full UI or frontend experience
- literature anchoring can be weaker for synthetic demo compounds or placeholder compound names with limited real-world publication support
- multi-report modes only change framing and section selection; they do not change the underlying analysis

## Testing

```bash
cd /home/knan/adme_strategy_copilot
python3 -m unittest discover -s tests
```

## Roadmap

- plug in real chemistry features via RDKit
- deepen PubMed retrieval and evidence ranking
- add configurable skill routing for more sub-agents
- expose the workflow to an OpenClaw / DeerFlow orchestrator
- persist run metadata and artifact manifests

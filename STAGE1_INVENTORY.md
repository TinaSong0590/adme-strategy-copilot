# Stage 1 Inventory

This document is a concise inventory of the current `ADME Strategy Copilot v1.6-stage1` prototype.

## 1. Code Capabilities

- rule-based ADME strategy report generation from `drug_name` and optional `SMILES`
- OpenClaw skill integration with primary loading from `/home/knan/.openclaw/workspace/skills`
- real-first literature retrieval with Europe PMC and optional PubMed support
- automatic fallback to mock literature when network or provider access is unavailable
- compound-aware literature reranking with:
  - exact-match and title-centric prioritization
  - focus-aware ranking
  - species- and matrix-aware ranking
  - target-versus-neighbor compound handling
- RDKit-backed chemistry intelligence when valid SMILES is available
- heuristic metabolism and disposition interpretation
- hotspot, evidence, and assay traceability
- confidence-calibrated prioritization
- decision-ready report framing
- multi-report rendering modes:
  - `scientist`
  - `executive`
  - `cro_proposal`
  - `regulatory_prep`

## 2. Presentation Materials

- [README.md](/home/knan/adme_strategy_copilot/README.md)
  Primary project guide with Stage 1 scope, report modes, demo flow, and limitations.
- [CHANGELOG.md](/home/knan/adme_strategy_copilot/CHANGELOG.md)
  Milestone-oriented summary from MVP to `v1.6-stage1`.
- [PROJECT_OVERVIEW.md](/home/knan/adme_strategy_copilot/PROJECT_OVERVIEW.md)
  Short project positioning and value statement.
- [DEMO_SCRIPT.md](/home/knan/adme_strategy_copilot/DEMO_SCRIPT.md)
  Suggested 5-minute demo narrative.
- [USE_CASES.md](/home/knan/adme_strategy_copilot/USE_CASES.md)
  Scenario-based explanation of where each report mode fits.

## 3. Demo Files

- [demo_scientist_mode.md](/home/knan/adme_strategy_copilot/demo/demo_scientist_mode.md)
  Full technical walkthrough for scientist audiences.
- [demo_executive_mode.md](/home/knan/adme_strategy_copilot/demo/demo_executive_mode.md)
  Short decision-focused walkthrough for executive audiences.
- [demo_cro_proposal_mode.md](/home/knan/adme_strategy_copilot/demo/demo_cro_proposal_mode.md)
  Work-package-oriented walkthrough for CRO-facing discussions.

## 4. Report Artifacts

Current generated examples include:

- [ibrutinib_adme_strategy_scientist.md](/home/knan/adme_strategy_copilot/reports/ibrutinib_adme_strategy_scientist.md)
- [ibrutinib_adme_strategy_executive.md](/home/knan/adme_strategy_copilot/reports/ibrutinib_adme_strategy_executive.md)
- [ibrutinib_adme_strategy_cro_proposal.md](/home/knan/adme_strategy_copilot/reports/ibrutinib_adme_strategy_cro_proposal.md)
- [ibrutinib_adme_strategy_regulatory_prep.md](/home/knan/adme_strategy_copilot/reports/ibrutinib_adme_strategy_regulatory_prep.md)
- [modelcompound_adme_strategy.md](/home/knan/adme_strategy_copilot/reports/modelcompound_adme_strategy.md)

Legacy pre-mode files are also present:

- [ibrutinib_adme_strategy.md](/home/knan/adme_strategy_copilot/reports/ibrutinib_adme_strategy.md)

## 5. Current Prototype Boundary

- Stage 1 is stable and demo-ready
- the current emphasis is explainable strategy support rather than predictive certainty
- no new analysis capability is being added in this inventory pass
- all report modes share the same underlying analysis and differ only in framing

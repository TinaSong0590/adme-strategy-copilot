# Changelog

## v1.6-stage1

Stage 1 freeze of the ADME Strategy Copilot prototype.

Key milestones captured in this stage:

- `MVP foundation`
  Created the first runnable ADME strategy report generator with OpenClaw skill integration, rule-based fallback behavior, and markdown report output.

- `Literature intelligence`
  Evolved from mock-only retrieval into real-first literature search with Europe PMC, optional PubMed support, reranking, exact-match prioritization, focus-aware ranking, species/matrix-aware ranking, and target-versus-neighbor compound handling.

- `Chemistry intelligence`
  Added RDKit-backed structure parsing, structural feature detection, soft-spot heuristics, Phase I / Phase II liability hints, reactive-metabolite awareness, CYP-oriented chemistry hints, species-aware interpretation, and disposition-aware chemistry support.

- `Hotspot and evidence linking`
  Connected structural hotspots to literature evidence tags, linked hotspots to assays, and added assay recommendation traceability so priorities could be explained with both chemistry and evidence support.

- `Confidence calibration`
  Added cross-source confidence layering to distinguish priority from confidence, separating high-confidence, medium-confidence, and exploratory items.

- `Decision-ready framing`
  Added executive-style sections including `Executive Decision Summary`, `What to Do Now`, `What to Verify Next`, `Exploratory Follow-up`, `Key Uncertainties`, and `Suggested Next-Step Plan`.

- `Multi-report modes`
  Added audience-aware report views for `scientist`, `executive`, `cro_proposal`, and `regulatory_prep`, all built on the same underlying analysis result.

## Notes

- This changelog is intentionally concise and milestone-oriented.
- The repository is currently being treated as the Stage 1 prototype freeze rather than an active feature-expansion branch.

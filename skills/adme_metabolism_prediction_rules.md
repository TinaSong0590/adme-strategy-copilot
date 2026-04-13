---
name: adme_metabolism_prediction_rules
description: Fallback heuristic metabolism rules for the ADME Strategy Copilot MVP.
version: 0.1.0
---

# ADME Metabolism Prediction Rules

## Motif Heuristics

- aromatic ring -> consider aromatic hydroxylation
- tertiary amine -> consider N-dealkylation and CYP-mediated clearance
- phenol or OH -> consider glucuronidation
- sulfur or thiophene -> consider oxidation risk and possible bioactivation
- aniline or catechol-like motif -> raise reactive metabolite concern

## Usage Notes

- This is a planning aid, not a validated metabolism model
- Escalate to hepatocytes, trapping experiments, or real cheminformatics when risk is elevated

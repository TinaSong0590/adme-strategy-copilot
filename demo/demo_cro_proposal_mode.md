# Demo: CRO Proposal Mode

## Best For

- CRO scoping calls
- assay-package planning
- early external work-package discussion

## Suggested Input

- `drug_name="Ibrutinib"`
- `species="Rat"`
- `focus="MetID"`
- optional: use a valid SMILES if you want stronger chemistry-backed assay framing

## Recommended Run

```bash
python3 /home/knan/adme_strategy_copilot/main.py --report-mode cro_proposal
```

## Sections To Highlight

- `Proposed Work Package Framing`
- `First-Pass Experiments`
- `Confirmatory Follow-up`
- `Optional Exploratory Package`
- `Recommended In Vitro Studies`
- `Suggested Next-Step Plan`

## Demo Angle

Use this mode when the conversation is less about technical depth and more about “what work package should we propose first.” It is the clearest view for showing first-pass experiments versus optional follow-up in a CRO-facing style.

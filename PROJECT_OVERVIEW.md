# Project Overview

## One-Line Positioning

ADME Strategy Copilot is a biopharma-focused agent prototype that turns compound-level inputs into decision-ready preclinical ADME strategy reports.

## Core Capabilities

- real-first, fallback-safe literature intelligence
- RDKit-backed chemistry intelligence when SMILES is available
- hotspot, evidence, and assay traceability
- confidence-calibrated prioritization
- decision-ready report framing
- multi-mode reporting for different audiences

## Target Users

- DMPK and ADME scientists
- project leads and portfolio stakeholders
- teams preparing CRO work-package discussions
- teams organizing early regulatory-facing risk and evidence summaries

## Report Modes

- `scientist`
  Full technical view with chemistry, evidence-linking, confidence layering, and literature traceability.
- `executive`
  Shorter decision memo for quickly understanding top priorities, immediate actions, and main risks.
- `cro_proposal`
  Work-package-oriented view for discussing first-pass experiments, confirmatory follow-up, and optional exploratory work.
- `regulatory_prep`
  More conservative framing that emphasizes evidence boundaries, confidence caveats, translation caution, and what remains unverified.

## Why This Project Matters

- it compresses scattered ADME planning signals into a single structured artifact
- it makes early preclinical strategy more explainable by linking chemistry, literature, and assay priorities
- it supports different audiences without changing the underlying analysis
- it is lightweight enough to run as a stable prototype without requiring LLM APIs, a frontend, or a database

## Current Boundaries And Limitations

- the system is heuristic and decision-support-oriented rather than statistically validated
- confidence labels are planning signals, not formal probability estimates
- it does not enumerate full metabolite structures or reaction pathways
- it does not provide a full product UI or workflow platform
- synthetic demo compounds may have weaker target-anchored literature support than real compounds
- report modes change framing only; they do not change the underlying analytical result

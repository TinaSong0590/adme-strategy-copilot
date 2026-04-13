# Executive Decision Summary

Top 3 priorities:
- Start with High-resolution MS metabolite profiling. (confidence: medium). Why it matters: Prioritized because MetID focus benefits from broad metabolite coverage and confident soft-spot readout and the retained literature points toward Harnessing Machine Learning for the Virtual Screening of Natural Compounds as Both EGFR and HER2 Inhibitors in Colorectal Cancer: A Novel Therapeutic Approach.. Evidence basis: literature direction from Harnessing Machine Learning for the Virtual Screening of Natural Compounds as Both EGFR and HER2 Inhibitors in Colorectal Cancer: A Novel Therapeutic Approach.; support strength medium Immediate action: This should clarify whether the leading chemistry-led hypothesis is supported in High-resolution MS metabolite profiling.
Highest-confidence action: Start with High-resolution MS metabolite profiling.
Main uncertainty: Target-anchored literature weakness
Recommended immediate next step: Start with High-resolution MS metabolite profiling.
Decision framing: The current package is most decision-ready around Rat-aligned MetID profiling where chemistry, context, and retained evidence converge best. Immediate work should stay centered on first-pass assays that can clarify the leading clearance and metabolite-coverage hypotheses, while secondary follow-up remains gated by what the first round of data confirms. Tertiary or secondary amine hotspot (literature medium)

Decision-ready take: Decision-ready framing points to start with high-resolution ms metabolite profiling. as the clearest immediate move. Secondary validation should center on no verify-next action was identified. once first-pass data arrive, while keep hepatocyte clearance comparison as exploratory follow-up. remains conditional rather than front-loaded. The main caveat is target-anchored literature weakness, so the current next-step plan is intentionally staged across 2 ordered steps.

## What to Do Now
- Start with High-resolution MS metabolite profiling. (confidence: medium). Prioritized because MetID focus benefits from broad metabolite coverage and confident soft-spot readout and the retained literature points toward Harnessing Machine Learning for the Virtual Screening of Natural Compounds as Both EGFR and HER2 Inhibitors in Colorectal Cancer: A Novel Therapeutic Approach.. This should clarify whether the leading chemistry-led hypothesis is supported in High-resolution MS metabolite profiling. Linked support: literature direction from Harnessing Machine Learning for the Virtual Screening of Natural Compounds as Both EGFR and HER2 Inhibitors in Colorectal Cancer: A Novel Therapeutic Approach.; support strength medium

## What to Verify Next
- No verify next item was generated.

## Exploratory Follow-up
- Keep Hepatocyte clearance comparison as exploratory follow-up. (confidence: exploratory). Prioritized because Microsome and hepatocyte comparison helps decide whether oxidative turnover dominates the overall disposition picture and the retained literature points toward limited direct assay-specific evidence. Escalate if first-pass profiling leaves the mechanism materially unresolved. Linked support: support strength low
- Keep Rat hepatocytes as exploratory follow-up. (confidence: exploratory). Prioritized because Hepatocytes can confirm broader oxidative pathways and soft-spot ranking beyond microsomes and the retained literature points toward limited direct assay-specific evidence. Escalate if first-pass profiling leaves the mechanism materially unresolved. Linked support: structural support from Tertiary or secondary amine hotspot; support strength low
- Keep Rat liver microsomes as exploratory follow-up. (confidence: exploratory). Prioritized because Oxidative liabilities make microsomal turnover and soft-spot coverage worth checking early and the retained literature points toward limited direct assay-specific evidence. Escalate if first-pass profiling leaves the mechanism materially unresolved. Linked support: structural support from Tertiary or secondary amine hotspot; support strength low

## Key Uncertainties
- Target-anchored literature weakness: The retained evidence is only weakly anchored to the exact target compound or remains mostly class-level/background support. Data that would reduce it: Stronger target-specific metabolism or disposition evidence would improve confidence calibration. Confidence impact: This keeps structure-led recommendations from being overstated as high-confidence.
- Species translation uncertainty: Tertiary or secondary amine hotspot (low species/context alignment) Data that would reduce it: Add human-relevant microsome, hepatocyte, or translation-focused follow-up before making stronger human assumptions. Confidence impact: Human-facing implications remain more provisional than the current preclinical recommendation set.
- Transporter involvement uncertainty: Transporter or efflux awareness is currently structure-led and not yet strongly anchored by target-specific evidence. Data that would reduce it: Permeability plus transporter-aware follow-up can separate passive permeability limitations from active transport effects. Confidence impact: Disposition-oriented follow-up stays medium-confidence or exploratory unless exposure data point that way.
- Clearance route ambiguity: More than one plausible clearance route remains in play from the current chemistry and evidence package. Data that would reduce it: Pair hepatocyte or microsome turnover with route-of-recovery or stability data to clarify which component dominates. Confidence impact: Route-specific interpretation remains less certain than the leading first-pass profiling recommendation.

## Suggested Next-Step Plan
1. Start with High-resolution MS metabolite profiling. Purpose: This should clarify whether the leading chemistry-led hypothesis is supported in High-resolution MS metabolite profiling. Confidence: medium Dependency or trigger: Run immediately because it is part of the first-pass package.
2. Keep Hepatocyte clearance comparison as exploratory follow-up. Purpose: Retain this as conditional follow-up rather than part of the immediate package. Confidence: exploratory Dependency or trigger: Escalate if first-pass profiling leaves the mechanism materially unresolved.

# ADME Strategy Report

## Input Summary
- Drug: ModelCompound
- SMILES: CCN(CC)CC
- Species: Rat
- Focus: MetID

## Chemistry Intelligence
- SMILES validity: valid
- RDKit used: yes
- Molecular formula: C6H15N
- Molecular weight: 101.19
- Key structural features: tertiary_amine_present, basic_nitrogen_present, cationic_center_hint
- Pathway priorities:
  - High: N-dealkylation. A tertiary amine creates a strong heuristic basis for oxidative N-dealkylation follow-up. Species context: Rat in vivo metabolite coverage can help clarify pathway relevance. Confidence: medium Confidence rationale: N-dealkylation is medium-confidence because the chemistry-led pathway priority is high and literature support is medium for the current Rat/MetID context.
- Chemistry confidence summary: Chemistry confidence across hotspots: high=1, medium=0, low=0.
- Hotspot confidence summary: Tertiary or secondary amine hotspot (medium overall, chemistry high, evidence medium)
- Recommendation confidence summary: high=0, medium=3, exploratory=9.
- Hotspot summary:
  - Tertiary or secondary amine hotspot: Amine functionality supports oxidative N-dealkylation or related CYP-mediated follow-up. Linked pathways: N-dealkylation, Oxidative metabolism. Linked assays: Liver microsomes, Hepatocytes, CYP phenotyping.
- Hotspot priorities:
  - High: Tertiary or secondary amine hotspot. Chemistry basis: Amine functionality supports oxidative N-dealkylation or related CYP-mediated follow-up. Chemistry confidence: high Evidence support: medium Evidence confidence: medium Overall confidence: medium Confidence rationale: Tertiary or secondary amine hotspot is medium-confidence because chemistry support is high, literature support is medium, and Rat/MetID alignment is low. Supporting records: Harnessing Machine Learning for the Virtual Screening of Natural Compounds as Both EGFR and HER2 Inhibitors in Colorectal Cancer: A Novel Therapeutic Approach.; Exploring the Impact of Developmental Clearance Saturation on Propylene Glycol Exposure in Adults and Term Neonates Using Physiologically Based Pharmacokinetic Modeling.
- Structure-to-assay links:
  - Tertiary or secondary amine hotspot -> Liver microsomes, Hepatocytes, CYP phenotyping. Amine functionality supports oxidative N-dealkylation or related CYP-mediated follow-up.
- CYP preference hints:
  - Oxidative amine liability worth checking early: A tertiary amine can support oxidative metabolism and N-dealkylation in microsomes and hepatocytes. Assay implication: Prioritize microsomes, hepatocytes, and CYP phenotyping. Conservative isoform note: CYP3A-mediated oxidation may be worth checking first in vitro. (confidence: medium)
- Transporter hints:
  - Basic or cationic transporter-awareness hint: Basic nitrogen features can justify uptake or efflux awareness if passive permeability is not dominant. Assay implication: P-gp or broader transporter-aware permeability follow-up may be worth considering if cell permeability is limited. Caution: This is not evidence of a specific transporter substrate assignment. (confidence: medium)
- Permeability hints:
  - No permeability-oriented chemistry hint was generated.
- Clearance-route hints:
  - High: oxidative_metabolic_clearance. Oxidation-prone substructures make metabolic clearance worth prioritizing early in microsomes and hepatocytes. Supporting features: oxidation liabilities and basic/aromatic features Species context: Rat microsomes and hepatocytes can rank this pathway early, but human confirmation is still needed.
  - Medium: renal_or_transporter_contribution_awareness. Polar or ionizable features justify keeping transporter or renal contribution in mind if clearance is not fully explained by metabolism. Supporting features: cationic/anionic or high-polarity disposition cues Species context: Transporter contribution should be interpreted conservatively until empirical data are available.
- Species-aware chemistry interpretation:
  - Summary: Rat interpretation should emphasize preclinical metabolite coverage and sample-matrix richness before extrapolating to human.
  - Preferred contexts: rat liver microsomes, rat hepatocytes, bile/urine/feces profiling
  - Assay biases: Rat liver microsomes and rat hepatocytes are useful for early oxidation and soft-spot screening.; In vivo rat bile, urine, and feces can add practical metabolite-coverage value for MetID work.
  - Extrapolation cautions: Rat metabolism patterns should be checked against human systems before drawing translation conclusions.; Conjugation-heavy chemistry may show species differences that need confirmation outside rat.
- Assay priorities:
  - High: Rat liver microsomes. Oxidative liabilities make microsomal turnover and soft-spot coverage worth checking early. Chemistry basis: oxidation-prone substructures detected Species basis: Rat Recommendation confidence: exploratory Confidence rationale: Rat liver microsomes is exploratory because structural support is present, literature support is low, and the current Rat/MetID context favors this assay.
  - High: Rat hepatocytes. Hepatocytes can confirm broader oxidative pathways and soft-spot ranking beyond microsomes. Chemistry basis: oxidation liabilities with possible competing pathways Species basis: Rat Recommendation confidence: exploratory Confidence rationale: Rat hepatocytes is exploratory because structural support is present, literature support is low, and the current Rat/MetID context favors this assay.
  - High: High-resolution MS metabolite profiling. MetID focus benefits from broad metabolite coverage and confident soft-spot readout. Chemistry basis: MetID focus with chemistry-driven pathway diversity Species basis: Rat Recommendation confidence: medium Confidence rationale: High-resolution MS metabolite profiling is medium because structural support is limited, literature support is medium, and the current Rat/MetID context favors this assay.
  - Medium: CYP phenotyping. Oxidative liabilities and DDI questions make CYP phenotyping worth prioritizing. Chemistry basis: amine or aromatic oxidation liabilities Species basis: Rat Recommendation confidence: exploratory Confidence rationale: CYP phenotyping is exploratory because structural support is present, literature support is low, and the current Rat/MetID context favors this assay.
  - Medium: Rat bile/urine/feces metabolite coverage. Rat MetID work benefits from richer in vivo metabolite coverage matrices. Chemistry basis: MetID focus with likely multiple pathways Species basis: Rat Recommendation confidence: exploratory Confidence rationale: Rat bile/urine/feces metabolite coverage is exploratory because structural support is limited, literature support is low, and the current Rat/MetID context favors this assay.
- Disposition summary:
  - Summary: Transporter awareness may be worth keeping in mind if exposure or clearance is not explained by metabolism alone. Route-of-clearance assignment should remain empirical because oxidative, conjugative, hydrolytic, or transporter-linked components may coexist.
  - Transporter summary: Basic or cationic transporter-awareness hint
  - Permeability summary: No permeability-oriented hint generated.
  - Clearance-route summary: oxidative_metabolic_clearance; renal_or_transporter_contribution_awareness
- Disposition assay priorities:
  - Medium: MDCK or MDR1-aware permeability follow-up. Basic or lipophilic chemistry justifies efflux-aware interpretation if apparent permeability is not straightforward. Chemistry basis: basic or aromatic transporter-awareness cues Disposition basis: efflux/transporter awareness Species basis: Rat Recommendation confidence: exploratory Confidence rationale: MDCK or MDR1-aware permeability follow-up is exploratory because structural support is limited, literature support is low, and the current Rat/MetID context favors this assay.
  - Medium: Transporter screening awareness. Transporter involvement may be worth checking if metabolism alone does not explain clearance or exposure behavior. Chemistry basis: cationic or anionic disposition cues Disposition basis: uptake/efflux awareness Species basis: Rat Recommendation confidence: exploratory Confidence rationale: Transporter screening awareness is exploratory because structural support is limited, literature support is low, and the current Rat/MetID context favors this assay.
  - High: Hepatocyte clearance comparison. Microsome and hepatocyte comparison helps decide whether oxidative turnover dominates the overall disposition picture. Chemistry basis: oxidation liabilities Disposition basis: metabolic-clearance route clarification Species basis: Rat Recommendation confidence: exploratory Confidence rationale: Hepatocyte clearance comparison is exploratory because structural support is limited, literature support is low, and the current Rat/MetID context favors this assay.
  - Medium: Plasma protein binding. Binding and distribution context can help interpret whether route-of-clearance uncertainty is metabolic, transporter-related, or mixed. Chemistry basis: ionizable or polar disposition cues Disposition basis: route-of-clearance interpretation Species basis: Rat Recommendation confidence: exploratory Confidence rationale: Plasma protein binding is exploratory because structural support is limited, literature support is low, and the current Rat/MetID context favors this assay.
  - Medium: Bile/urine/feces recovery context. Rat MetID work often benefits from route-of-clearance context beyond plasma alone. Chemistry basis: mixed metabolism/disposition liabilities Disposition basis: excretion-route clarification Species basis: Rat Recommendation confidence: exploratory Confidence rationale: Bile/urine/feces recovery context is exploratory because structural support is limited, literature support is low, and the current Rat/MetID context favors this assay.
- Soft spot hints:
  - Potential N-dealkylation soft spot: A tertiary amine often increases susceptibility to CYP-mediated N-dealkylation. (confidence: high; pathway: phase1)
- Phase I liabilities: CYP-mediated N-dealkylation is likely because a tertiary amine is present.
- Phase II liabilities: No specific Phase II liability hint generated.
- Reactive metabolite awareness: No specific reactive metabolite alert generated.
- Chemistry-derived risk notes: Disposition interpretation should retain transporter awareness if exposure or clearance is not fully explained by metabolism.; Rat MetID interpretation should emphasize bile, urine, and feces coverage before human extrapolation.
- Chemistry-derived protocol implications: Prioritize microsome incubation, hepatocyte confirmation, and CYP phenotyping because oxidative amine liability is plausible.; Add disposition-aware permeability and transporter follow-up if exposure or clearance is not explained by metabolism alone.
- Chemistry limitations: No major chemistry-layer limitation detected for this run.
- Chemistry summary: RDKit detected key structural flags: tertiary_amine_present, basic_nitrogen_present, cationic_center_hint. Primary soft-spot hints include potential n-dealkylation soft spot.

## Evidence-Linked Prioritization
- Structure-to-evidence summary: Tertiary or secondary amine hotspot (high, evidence medium)
- Assay traceability summary: Rat liver microsomes (low support); Rat hepatocytes (low support); High-resolution MS metabolite profiling (medium support); CYP phenotyping (low support)
- Evidence tag summary: oxidation=3, lc_ms=1, rat_aligned=1, metid_support=1
- Literature confidence summary: Tertiary or secondary amine hotspot (literature medium)
- Evidence alignment summary: Tertiary or secondary amine hotspot (low species/context alignment)
- Top hotspot-backed priorities:
  - Tertiary or secondary amine hotspot (high priority, evidence medium). Amine functionality supports oxidative N-dealkylation or related CYP-mediated follow-up. Supported by: Harnessing Machine Learning for the Virtual Screening of Natural Compounds as Both EGFR and HER2 Inhibitors in Colorectal Cancer: A Novel Therapeutic Approach.; Exploring the Impact of Developmental Clearance Saturation on Propylene Glycol Exposure in Adults and Term Neonates Using Physiologically Based Pharmacokinetic Modeling.
- Assay recommendation traceability:
  - Rat liver microsomes (high priority; support low). Prioritized because Oxidative liabilities make microsomal turnover and soft-spot coverage worth checking early and the retained literature points toward limited direct assay-specific evidence. Structural support: Tertiary or secondary amine hotspot
  - Rat hepatocytes (high priority; support low). Prioritized because Hepatocytes can confirm broader oxidative pathways and soft-spot ranking beyond microsomes and the retained literature points toward limited direct assay-specific evidence. Structural support: Tertiary or secondary amine hotspot
  - High-resolution MS metabolite profiling (high priority; support medium). Prioritized because MetID focus benefits from broad metabolite coverage and confident soft-spot readout and the retained literature points toward Harnessing Machine Learning for the Virtual Screening of Natural Compounds as Both EGFR and HER2 Inhibitors in Colorectal Cancer: A Novel Therapeutic Approach.. Literature direction: Harnessing Machine Learning for the Virtual Screening of Natural Compounds as Both EGFR and HER2 Inhibitors in Colorectal Cancer: A Novel Therapeutic Approach.
  - CYP phenotyping (medium priority; support low). Prioritized because Oxidative liabilities and DDI questions make CYP phenotyping worth prioritizing and the retained literature points toward limited direct assay-specific evidence. Structural support: Tertiary or secondary amine hotspot
  - Rat bile/urine/feces metabolite coverage (medium priority; support low). Prioritized because Rat MetID work benefits from richer in vivo metabolite coverage matrices and the retained literature points toward limited direct assay-specific evidence.
  - MDCK or MDR1-aware permeability follow-up (medium priority; support low). Prioritized because Basic or lipophilic chemistry justifies efflux-aware interpretation if apparent permeability is not straightforward and the retained literature points toward limited direct assay-specific evidence.

## Confidence-Calibrated Prioritization
- High-confidence priorities: No item currently reaches high-confidence status.
- Medium-confidence priorities: Tertiary or secondary amine hotspot, High-resolution MS metabolite profiling, N-dealkylation
- Exploratory follow-up items: Rat liver microsomes, Rat hepatocytes, CYP phenotyping, Rat bile/urine/feces metabolite coverage, MDCK or MDR1-aware permeability follow-up, Transporter screening awareness, Hepatocyte clearance comparison, Plasma protein binding, Bile/urine/feces recovery context
- Confidence caveats: Confidence levels are heuristic and combine chemistry clarity, literature support, and species/context alignment. Priority does not automatically imply high confidence.
- Cross-source calibration note: Tertiary or secondary amine hotspot (literature medium)
- Species/context alignment note: Tertiary or secondary amine hotspot (low species/context alignment)

## 1. Predicted Metabolic Pathways
- N-dealkylation may occur because a tertiary amine is present.
- High-priority: N-dealkylation. Rationale: A tertiary amine creates a strong heuristic basis for oxidative N-dealkylation follow-up.
- Tertiary amines commonly undergo oxidative dealkylation in microsomes and hepatocytes.
- Rat in vivo metabolite coverage can help clarify pathway relevance.
- Pathway confidence: N-dealkylation is medium-confidence.
- N-dealkylation is medium-confidence because the chemistry-led pathway priority is high and literature support is medium for the current Rat/MetID context.
- Pathway literature direction: Harnessing Machine Learning for the Virtual Screening of Natural Compounds as Both EGFR and HER2 Inhibitors in Colorectal Cancer: A Novel Therapeutic Approach., Exploring the Impact of Developmental Clearance Saturation on Propylene Glycol Exposure in Adults and Term Neonates Using Physiologically Based Pharmacokinetic Modeling..
- Hotspot-backed priority: Tertiary or secondary amine hotspot (high priority, evidence medium).
- Supporting literature direction: Harnessing Machine Learning for the Virtual Screening of Natural Compounds as Both EGFR and HER2 Inhibitors in Colorectal Cancer: A Novel Therapeutic Approach., Exploring the Impact of Developmental Clearance Saturation on Propylene Glycol Exposure in Adults and Term Neonates Using Physiologically Based Pharmacokinetic Modeling..
- Clearance-route context: Oxidation-prone substructures make metabolic clearance worth prioritizing early in microsomes and hepatocytes.
- CYP preference hint: Oxidative amine liability worth checking early. A tertiary amine can support oxidative metabolism and N-dealkylation in microsomes and hepatocytes.
- Assay implication: Prioritize microsomes, hepatocytes, and CYP phenotyping.
- RDKit detected key structural flags: tertiary_amine_present, basic_nitrogen_present, cationic_center_hint. Primary soft-spot hints include potential n-dealkylation soft spot.

## 2. Recommended In Vitro Studies
- Human liver microsomes: measure intrinsic clearance, metabolite soft spots, and time-dependent turnover.
- S9 fraction: capture mixed Phase I and Phase II turnover, especially if glucuronidation is suspected.
- Cryopreserved hepatocytes: profile intact-cell metabolism and compare qualitative metabolites across species.
- Plasma stability: check parent stability and binding-related loss in species-matched plasma.
- CYP phenotyping: use recombinant CYPs or selective inhibitors to map isoform contribution and DDI risk.
- Expand CYP3A-focused inhibition and induction package because a CYP3A liability signal is present.
- Add hepatocyte relay or extended incubation work if rapid turnover obscures metabolite identification.
- Use microsome incubation plus hepatocyte confirmation because amine oxidation and CYP turnover are plausible.
- Retain CYP phenotyping emphasis because structure-based oxidative liability is present.
- High-priority: Rat liver microsomes. Oxidative liabilities make microsomal turnover and soft-spot coverage worth checking early.; oxidation-prone substructures detected; Rat; why prioritized: Prioritized because Oxidative liabilities make microsomal turnover and soft-spot coverage worth checking early and the retained literature points toward limited direct assay-specific evidence.; structural support: Tertiary or secondary amine hotspot; literature support strength: low; recommendation confidence: exploratory; confidence rationale: Rat liver microsomes is exploratory because structural support is present, literature support is low, and the current Rat/MetID context favors this assay..
- High-priority: Rat hepatocytes. Hepatocytes can confirm broader oxidative pathways and soft-spot ranking beyond microsomes.; oxidation liabilities with possible competing pathways; Rat; why prioritized: Prioritized because Hepatocytes can confirm broader oxidative pathways and soft-spot ranking beyond microsomes and the retained literature points toward limited direct assay-specific evidence.; structural support: Tertiary or secondary amine hotspot; literature support strength: low; recommendation confidence: exploratory; confidence rationale: Rat hepatocytes is exploratory because structural support is present, literature support is low, and the current Rat/MetID context favors this assay..
- High-priority: High-resolution MS metabolite profiling. MetID focus benefits from broad metabolite coverage and confident soft-spot readout.; MetID focus with chemistry-driven pathway diversity; Rat; why prioritized: Prioritized because MetID focus benefits from broad metabolite coverage and confident soft-spot readout and the retained literature points toward Harnessing Machine Learning for the Virtual Screening of Natural Compounds as Both EGFR and HER2 Inhibitors in Colorectal Cancer: A Novel Therapeutic Approach..; literature support strength: medium; recommendation confidence: medium; confidence rationale: High-resolution MS metabolite profiling is medium because structural support is limited, literature support is medium, and the current Rat/MetID context favors this assay.; literature direction: Harnessing Machine Learning for the Virtual Screening of Natural Compounds as Both EGFR and HER2 Inhibitors in Colorectal Cancer: A Novel Therapeutic Approach..
- Medium-priority: CYP phenotyping. Oxidative liabilities and DDI questions make CYP phenotyping worth prioritizing.; amine or aromatic oxidation liabilities; Rat; why prioritized: Prioritized because Oxidative liabilities and DDI questions make CYP phenotyping worth prioritizing and the retained literature points toward limited direct assay-specific evidence.; structural support: Tertiary or secondary amine hotspot; literature support strength: low; recommendation confidence: exploratory; confidence rationale: CYP phenotyping is exploratory because structural support is present, literature support is low, and the current Rat/MetID context favors this assay..
- Medium-priority: Rat bile/urine/feces metabolite coverage. Rat MetID work benefits from richer in vivo metabolite coverage matrices.; MetID focus with likely multiple pathways; Rat; why prioritized: Prioritized because Rat MetID work benefits from richer in vivo metabolite coverage matrices and the retained literature points toward limited direct assay-specific evidence.; literature support strength: low; recommendation confidence: exploratory; confidence rationale: Rat bile/urine/feces metabolite coverage is exploratory because structural support is limited, literature support is low, and the current Rat/MetID context favors this assay..
- Medium-priority: MDCK or MDR1-aware permeability follow-up. Basic or lipophilic chemistry justifies efflux-aware interpretation if apparent permeability is not straightforward.; basic or aromatic transporter-awareness cues; efflux/transporter awareness; Rat; why prioritized: Prioritized because Basic or lipophilic chemistry justifies efflux-aware interpretation if apparent permeability is not straightforward and the retained literature points toward limited direct assay-specific evidence.; literature support strength: low; recommendation confidence: exploratory; confidence rationale: MDCK or MDR1-aware permeability follow-up is exploratory because structural support is limited, literature support is low, and the current Rat/MetID context favors this assay..
- Medium-priority: Transporter screening awareness. Transporter involvement may be worth checking if metabolism alone does not explain clearance or exposure behavior.; cationic or anionic disposition cues; uptake/efflux awareness; Rat; why prioritized: Prioritized because Transporter involvement may be worth checking if metabolism alone does not explain clearance or exposure behavior and the retained literature points toward limited direct assay-specific evidence.; literature support strength: low; recommendation confidence: exploratory; confidence rationale: Transporter screening awareness is exploratory because structural support is limited, literature support is low, and the current Rat/MetID context favors this assay..
- High-priority: Hepatocyte clearance comparison. Microsome and hepatocyte comparison helps decide whether oxidative turnover dominates the overall disposition picture.; oxidation liabilities; metabolic-clearance route clarification; Rat; why prioritized: Prioritized because Microsome and hepatocyte comparison helps decide whether oxidative turnover dominates the overall disposition picture and the retained literature points toward limited direct assay-specific evidence.; literature support strength: low; recommendation confidence: exploratory; confidence rationale: Hepatocyte clearance comparison is exploratory because structural support is limited, literature support is low, and the current Rat/MetID context favors this assay..
- Medium-priority: Plasma protein binding. Binding and distribution context can help interpret whether route-of-clearance uncertainty is metabolic, transporter-related, or mixed.; ionizable or polar disposition cues; route-of-clearance interpretation; Rat; why prioritized: Prioritized because Binding and distribution context can help interpret whether route-of-clearance uncertainty is metabolic, transporter-related, or mixed and the retained literature points toward limited direct assay-specific evidence.; literature support strength: low; recommendation confidence: exploratory; confidence rationale: Plasma protein binding is exploratory because structural support is limited, literature support is low, and the current Rat/MetID context favors this assay..
- Medium-priority: Bile/urine/feces recovery context. Rat MetID work often benefits from route-of-clearance context beyond plasma alone.; mixed metabolism/disposition liabilities; excretion-route clarification; Rat; why prioritized: Prioritized because Rat MetID work often benefits from route-of-clearance context beyond plasma alone and the retained literature points toward limited direct assay-specific evidence.; literature support strength: low; recommendation confidence: exploratory; confidence rationale: Bile/urine/feces recovery context is exploratory because structural support is limited, literature support is low, and the current Rat/MetID context favors this assay..
- Prioritize microsome incubation, hepatocyte confirmation, and CYP phenotyping because oxidative amine liability is plausible.
- Add disposition-aware permeability and transporter follow-up if exposure or clearance is not explained by metabolism alone.

## 3. Suggested In Vivo Design
- Rat cassette or single-compound PK study with dense early sampling (for example 0.25, 0.5, 1, 2, 4, 8, 24 h).
- Collect plasma plus optional urine/bile or feces pools when feasible to support clearance route interpretation.
- Include metabolite profiling around Tmax and terminal phase to distinguish formation-limited versus elimination-limited species.
- Consider IV plus PO arms to separate bioavailability limitations from true systemic clearance.
- Rat-focused metabolite coverage: collect bile, urine, and feces when feasible because the chemistry profile supports broader metabolite mapping.

## 4. Potential Risks
- Predicted clearance risk: High.
- Predicted reactive metabolite risk: Moderate.
- CYP3A involvement suspected: assess victim and perpetrator DDI scenarios early.
- High metabolic liability may translate to high clearance risk and limited oral exposure.
- Rat metabolism patterns should be checked against human systems before drawing translation conclusions.
- Conjugation-heavy chemistry may show species differences that need confirmation outside rat.
- Transporter or efflux awareness may be worth checking if exposure or clearance is not fully explained by metabolism alone.
- Route-of-clearance assignment remains heuristic and should be verified with metabolism-plus-disposition follow-up.
- Disposition interpretation should retain transporter awareness if exposure or clearance is not fully explained by metabolism.
- Rat MetID interpretation should emphasize bile, urine, and feces coverage before human extrapolation.
- Potential CYP-mediated N-dealkylation may contribute to DDI sensitivity.
- CYP3A-mediated oxidation may be worth checking first in vitro.
- Disposition interpretation should retain transporter awareness if exposure or clearance is not fully explained by metabolism.
- Rat MetID interpretation should emphasize bile, urine, and feces coverage before human extrapolation.
- High clearance risk: prioritize intrinsic clearance readouts in microsomes and hepatocytes.

## 5. Translation to Human
- Scale microsomal and hepatocyte intrinsic clearance to human hepatic clearance using standard IVIVE assumptions.
- Compare qualitative human versus preclinical metabolites to flag disproportionate human metabolite risk early.
- If systemic clearance appears high in rodent, prioritize hepatocyte and plasma protein binding data before projecting human exposure.
- Rat interpretation should emphasize preclinical metabolite coverage and sample-matrix richness before extrapolating to human.
- Rat metabolism patterns should be checked against human systems before drawing translation conclusions.
- Conjugation-heavy chemistry may show species differences that need confirmation outside rat.
- Human translation should remain cautious until transporter versus metabolic contribution is better separated in relevant in vitro systems.

## 6. Supporting Literature
Focus-aware ranking enabled: yes
Context-aware ranking enabled: yes
Target-compound prioritization enabled: yes
Title-centric target detection enabled: yes
Focus: MetID
Species: Rat
Primary provider: europe_pmc
Provider used: europe_pmc
Query set used: ModelCompound metabolite identification; ModelCompound metabolism; ModelCompound biotransformation; ModelCompound ADME
Retrieval mode summary: europe_pmc
Focus profile summary: Ranking emphasizes focus-specific keywords such as metabolism, lc-ms, lc-ms/ms, metabolite.
Focus relevance summary: Average focus relevance score: 4.1; exact but weak-focus records: 0. Keyword hits: metabolism=3, lc-ms=1, lc-ms/ms=1, metabolite=1. Top literature is partially aligned with MetID.
Species profile summary: Ranking boosts records with species context such as rat, multi-species.
Matrix profile summary: Ranking emphasizes matrix and experimental-context signals such as lc-ms, lc-ms/ms.
Species relevance summary: Average species relevance score: 0.6; species-aligned records: 1; context-mismatched records: 4. Top evidence still contains several non-Rat or species-neutral records.
Matrix/context relevance summary: Average matrix/context relevance score: 1.2; strong context records: 1; weak context records: 4. Top evidence still includes several records with weak MetID matrix context.
Compound relation summary: neighbor_compound=5
Title target status summary: unclear_title_target_status=5 Top evidence shows a mixed level of title target-centrality.
Title-centric boost summary: Average title-centric boost: 0.0; title-centered target records: 0; title-centered records in top three: 0. Title boosts contribute, but they do not dominate the full ranking.
Mention-only penalty summary: Average mention-only penalty: 1.0; abstract-mention records: 0; non-target title-centered records: 0. Mention-only or non-target-title records are actively demoted from the top evidence pool.
Evidence bucket summary: neighbor_supporting_evidence=5
Neighbor suppression summary: Core target evidence count: 0; neighbor supporting evidence count: 5; ambiguous compound-context records: 0; average neighbor suppression penalty: 9.6. Neighbor-compound articles still mix into the top evidence and should be read as supporting only.
Exact/alias/class-level match summary: class_level_match=4, no_clear_match=1
Article type summary: preclinical_study=2, review=2, original_research=1
Literature quality summary: Exact matches: 0; alias matches: 0; class-level matches: 4; target exact: 0; target alias: 0; neighbor compounds: 5; title-centered target records: 0; abstract-mention records: 0; non-target title-centered records: 0; core target evidence: 0; supporting target evidence: 0; neighbor supporting evidence: 5; review articles: 2; clinical studies: 0; preclinical studies: 2. Neighbor-compound evidence still contributes materially as supporting background.

### Neighbor Supporting Evidence
- Harnessing Machine Learning for the Virtual Screening of Natural Compounds as Both EGFR and HER2 Inhibitors in Colorectal Cancer: A Novel Therapeutic Approach.
  Journal: MED
  Year: 2025
  Authors: Oku DNT, Babatunde DD, Nuapia Y, More GK, Chokwe RC.
  Retrieval mode: europe_pmc
  Compound relation: neighbor_compound
  Title target status: unclear_title_target_status
  Evidence bucket: neighbor_supporting_evidence
  Match type: class_level_match
  Article type: preclinical_study
  Base score: 12.25
  Focus relevance score: 10.50
  Species relevance score: 3.00
  Matrix relevance score: 6.00
  Title exactness boost: 0.00
  Mention-only penalty: 1.00
  Title compound centrality: 0.20
  Species-specific exactness boost: 0.00
  Neighbor suppression penalty: 8.00
  Final score: 18.75
  Relevance: Centers on neighbor compound tucatinib, retained as supporting neighbor evidence. Title target-centrality is unclear (title centrality 0.20). Strong MetID-specific signals via lc-ms, lc-ms/ms; species context aligns with Rat via rat, multi-species; matrix/context support via lc-ms, lc-ms/ms; focus mismatch penalty 4.0; mention-only penalty 1.0; neighbor suppression penalty 8.0; classified as preclinical_study.; recent publication year 2025
  URL: https://europepmc.org/article/MED/41358077
  Summary: Colorectal cancer (CRC) is a type of cancer that affects the colon and rectum, with overexpression of epidermal growth factor receptor (EGFR) and human epidermal growth factor receptor 2 (HER2) observed in up to 85% of colorectal cancer cases. Although CRC treatment has progressed with the introduction of targeted drugs, current approaches have primarily focused on a single blockage of EGFR or HER2 to combat colon cancer. However, monotherapies that target either the EGFR or HER2 receptor frequently have low efficacy due to mutations in downstream effectors such as Kirsten Rat Sarcoma 2 Viral Oncogene Homologue (KRAS) and the activation of compensatory signaling pathways that support tumor survival and proliferation. Hence, the discovery and development of a therapy with the capability to combat CRC by simultaneously inhibiting both EGFR and HER2 remain avenues for further exploration. This study introduces a novel machine learning (ML)-based stacking ensemble framework for rapidly and accurately identifying dual EGFR and HER2 inhibitors using SMILES notation. A benchmark data set comprising active and inactive compounds against EGFR and HER2 was curated from the ChEMBL database. Based on this data set, 40 baseline models were developed and optimized using a comprehensive set of well-known molecular descriptors and ML algorithms (Figure 1). These models generated probabilistic features integrated via a logistic regression model as a final estimate to construct the final stacking ensemble model. The model was applied to bioactive compounds identified through LC-MS/MS profiling of <i>Ceratonia siliqua</i> extract as well as to a subset of natural products from the LOTUS database for virtual screening. The cytotoxic potential of <i>Ceratonia siliqua</i> was experimentally validated using the MTT assay against HCT116 colorectal cancer cells and noncancerous Vero cells, where the extract exhibited an IC<sub>50</sub> value of 13.32 ± 1.09 μg/mL against HCT116 cells, indicating its significant anticancer potential. Additionally, molecular docking and <i>in silico</i> ADMET studies were conducted on the top three compounds from both the LOTUS database and the predicted candidate from the LC-MS/MS data set identified by the stacking model, alongside four FDA-approved anticancer drugs for comparative analysis. Among these, LTS0131923 demonstrated the highest binding affinity against HER2 (PDB ID: 7MN5), with a binding energy of -11.2 kcal/mol and an inhibition constant of 0.00626 μM, outperforming Tucatinib, a standard CRC treatment. This study reveals the potential of ML-driven approaches to accelerate the discovery of dual-target inhibitors for CRC therapy and highlights <i>Ceratonia siliqua</i> <i>L.</i> as a promising source of bioactive compounds for cancer treatment.
- Single-Walled Carbon Nanotubes Inhibit the Cytochrome P450 Enzyme, CYP3A4.
  Journal: MED
  Year: 2016
  Authors: El-Sayed R, Bhattacharya K, Gu Z, Yang Z, Weber JK, Li H, Leifer K, Zhao Y, Toprak MS, Zhou R, Fadeel B.
  Retrieval mode: europe_pmc
  Compound relation: neighbor_compound
  Title target status: unclear_title_target_status
  Evidence bucket: neighbor_supporting_evidence
  Match type: class_level_match
  Article type: original_research
  Base score: 16.25
  Focus relevance score: 3.00
  Species relevance score: 0.00
  Matrix relevance score: 0.00
  Title exactness boost: 0.00
  Mention-only penalty: 1.00
  Title compound centrality: 0.20
  Species-specific exactness boost: 0.00
  Neighbor suppression penalty: 10.00
  Final score: 2.25
  Relevance: Centers on neighbor compound single, retained as supporting neighbor evidence. Title target-centrality is unclear (title centrality 0.20). Strong MetID-specific signals via metabolite, metabolism; limited Rat-specific context relative to the current query; limited matrix/context support for the requested experimental setup; context mismatch penalty 6.0; mention-only penalty 1.0; neighbor suppression penalty 10.0; classified as original_research.; recent publication year 2016
  URL: https://europepmc.org/article/MED/26899743
  Summary: We report a detailed computational and experimental study of the interaction of single-walled carbon nanotubes (SWCNTs) with the drug-metabolizing cytochrome P450 enzyme, CYP3A4. Dose-dependent inhibition of CYP3A4-mediated conversion of the model compound, testosterone, to its major metabolite, 6β-hydroxy testosterone was noted. Evidence for a direct interaction between SWCNTs and CYP3A4 was also provided. The inhibition of enzyme activity was alleviated when SWCNTs were pre-coated with bovine serum albumin. Furthermore, covalent functionalization of SWCNTs with polyethylene glycol (PEG) chains mitigated the inhibition of CYP3A4 enzymatic activity. Molecular dynamics simulations suggested that inhibition of the catalytic activity of CYP3A4 is mainly due to blocking of the exit channel for substrates/products through a complex binding mechanism. This work suggests that SWCNTs could interfere with metabolism of drugs and other xenobiotics and provides a molecular mechanism for this toxicity. Our study also suggests means to reduce this toxicity, eg., by surface modification.
- Regulation of iron metabolism in ferroptosis: From mechanism research to clinical translation.
  Journal: MED
  Year: 2025
  Authors: Zhang X, Xiang Y, Wang Q, Bai X, Meng D, Wu J, Sun K, Zhang L, Qiang R, Liu W, Zhang X, Qiang J, Liu X, Yang Y.
  Retrieval mode: europe_pmc
  Compound relation: neighbor_compound
  Title target status: unclear_title_target_status
  Evidence bucket: neighbor_supporting_evidence
  Match type: class_level_match
  Article type: review
  Base score: 12.25
  Focus relevance score: 3.00
  Species relevance score: 0.00
  Matrix relevance score: 0.00
  Title exactness boost: 0.00
  Mention-only penalty: 1.00
  Title compound centrality: 0.20
  Species-specific exactness boost: 0.00
  Neighbor suppression penalty: 10.00
  Final score: -3.75
  Relevance: Centers on neighbor compound regulation, retained as supporting neighbor evidence. Title target-centrality is unclear (title centrality 0.20). Strong MetID-specific signals via metabolism; limited Rat-specific context relative to the current query; limited matrix/context support for the requested experimental setup; context mismatch penalty 8.0; mention-only penalty 1.0; neighbor suppression penalty 10.0; classified as review.; recent publication year 2025
  URL: https://europepmc.org/article/MED/41208920
  Summary: Iron is an essential trace element in the human body, crucial in maintaining normal physiological functions. Recent studies have identified iron ions as a significant factor in initiating the ferroptosis process, a novel mode of programmed cell death characterized by iron overload and lipid peroxide accumulation. The iron metabolism pathway is one of the primary mechanisms regulating ferroptosis, as it maintains iron homeostasis within the cell. Numerous studies have demonstrated that abnormalities in iron metabolism can trigger the Fenton reaction, exacerbating oxidative stress, and leading to cell membrane rupture, cellular dysfunction, and damage to tissue structures. Therefore, regulation of iron metabolism represents a key strategy for ameliorating ferroptosis and offers new insights for treating diseases associated with iron metabolism imbalances. This review first summarizes the mechanisms that regulate iron metabolic pathways in ferroptosis and discusses the connections between the pathogenesis of various diseases and iron metabolism. Next, we introduce natural and synthetic small molecule compounds, hormones, proteins, and new nanomaterials that can affect iron metabolism. Finally, we provide an overview of the challenges faced by iron regulators in clinical translation and a summary and outlook on iron metabolism in ferroptosis, aiming to pave the way for future exploration and optimization of iron metabolism regulation strategies.
- Exploring the Impact of Developmental Clearance Saturation on Propylene Glycol Exposure in Adults and Term Neonates Using Physiologically Based Pharmacokinetic Modeling.
  Journal: MED
  Year: 2025
  Authors: Olafuyi O, Michelet R, Garle M, Allegaert K.
  Retrieval mode: europe_pmc
  Compound relation: neighbor_compound
  Title target status: unclear_title_target_status
  Evidence bucket: neighbor_supporting_evidence
  Match type: no_clear_match
  Article type: preclinical_study
  Base score: 2.00
  Focus relevance score: 4.00
  Species relevance score: 0.00
  Matrix relevance score: 0.00
  Title exactness boost: 0.00
  Mention-only penalty: 1.00
  Title compound centrality: 0.20
  Species-specific exactness boost: 0.00
  Neighbor suppression penalty: 10.00
  Final score: -13.00
  Relevance: Centers on neighbor compound exploring, retained as supporting neighbor evidence. Title target-centrality is unclear (title centrality 0.20). Strong MetID-specific signals via metabolism; limited Rat-specific context relative to the current query; limited matrix/context support for the requested experimental setup; context mismatch penalty 8.0; mention-only penalty 1.0; neighbor suppression penalty 10.0; classified as preclinical_study.; recent publication year 2025
  URL: https://europepmc.org/article/MED/39404076
  Summary: Propylene glycol (PG) is a pharmaceutical excipient which is generally regarded as safe (GRAS), though clinical toxicity has been reported. PG toxicity has been attributed to accumulation due to saturation of the alcohol dehydrogenase (ADH)-mediated clearance pathway. This study aims to explore the impact of the saturation of ADH-mediated PG metabolism on its developmental clearance in adults and neonates and assess the impact of a range of doses on PG clearance saturation and toxicity. Physiologically based pharmacokinetic (PBPK) models for PG in adults and term neonates were developed using maximum velocity (V<sub>max</sub>) and Michaelis-Menten's constant (K<sub>m</sub>) of ADH-mediated metabolism determined in vitro in human liver cytosol, published physicochemical, drug-related and ADH ontogeny parameters. The models were validated and used to determine the impact of dosing regimen on PG clearance saturation and toxicity in adults and neonates. The V<sub>max</sub> and K<sub>m</sub> of PG in human liver cytosol were 1.57 nmol/min/mg protein and 25.1 mM, respectively. The PG PBPK model adequately described PG PK profiles in adults and neonates. The PG dosing regimens associated with saturation and toxicity were dependent on both dose amount and cumulative in standard dosing frequencies. Doses resulting in saturation were higher than those associated with clinically observed toxicity. In individuals without impaired clearance or when PG exposure is through formulations that contain excipients with possible interaction with PG, a total daily dose of 100-200 mg/kg/day in adults and 25-50 mg/kg/day in neonates is unlikely to result in toxic PG levels or PG clearance saturation.
- Ginsenoside Rg1 as a Multifunctional Therapeutic Agent: Pharmacological Properties, Molecular Mechanisms and Clinical Perspectives in Complementary Medicine.
  Journal: MED
  Year: 2026
  Authors: Cortés H, Lima E, Duarte-Peña L, Peña-Corona SI, Almarhoon ZM, Kaverikana R, Mangalpady SS, Shet VB, Manjeshwar N, Sharifi-Rad J, Chen JT, Leyva-Gómez G, Setzer WN, Calina D.
  Retrieval mode: europe_pmc
  Compound relation: neighbor_compound
  Title target status: unclear_title_target_status
  Evidence bucket: neighbor_supporting_evidence
  Match type: class_level_match
  Article type: review
  Base score: 9.75
  Focus relevance score: 0.00
  Species relevance score: 0.00
  Matrix relevance score: 0.00
  Title exactness boost: 0.00
  Mention-only penalty: 1.00
  Title compound centrality: 0.20
  Species-specific exactness boost: 0.00
  Neighbor suppression penalty: 10.00
  Final score: -15.25
  Relevance: Centers on neighbor compound ginsenoside, retained as supporting neighbor evidence. Title target-centrality is unclear (title centrality 0.20). Limited MetID-specific content; limited Rat-specific context relative to the current query; limited matrix/context support for the requested experimental setup; focus mismatch penalty 6.0; context mismatch penalty 8.0; mention-only penalty 1.0; neighbor suppression penalty 10.0; classified as review.; recent publication year 2026
  URL: https://europepmc.org/article/MED/41648642
  Summary: Ginsenoside Rg1 (GRg1), a major bioactive component of <i>Panax ginseng</i>, exhibits potent antioxidant, anti-inflammatory, and neuroprotective properties, positioning it as a promising therapeutic agent in neurodegenerative and metabolic disorders. This review critically examines the current literature on GRg1, emphasizing its molecular mechanisms, pharmacological pathways, and clinical translation in complementary medicine. GRg1 demonstrates protective effects in conditions such as Alzheimer's disease (AD), Parkinson's disease (PD), ischemic stroke, cardiovascular dysfunction, diabetes, and aging, acting primarily through the nuclear factor kappa B (NF-κB), mitogen-activated protein kinase (MAPK), Wnt/β-catenin, and peroxisome proliferator-activated receptor gamma/heme oxygenase-1 (PPARγ/HO-1) signaling pathways. Evidence from in vitro, in vivo, and clinical studies indicates that GRg1 enhances cellular resilience, reduces oxidative damage, and regulates apoptosis. Despite its broad therapeutic potential, low bioavailability remains a major limitation, warranting the development of advanced delivery systems such as nanoparticles and liposomes. Overall, this review provides a comprehensive assessment of GRg1's pharmacological actions and highlights its growing relevance as a multifunctional therapeutic agent in complementary and integrative medicine.

## 7. Disclaimer
This report is an MVP-generated preclinical planning aid that uses heuristic metabolism rules, template-driven protocol logic, and a real-first literature retrieval pipeline with automatic fallback. It is not a substitute for medicinal chemistry judgment, wet-lab data, or formal regulatory advice.

Skill context loaded from: adme_human_translation_rules (openclaw:/home/knan/.openclaw/workspace/skills/adme_human_translation_rules.md), adme_metabolism_prediction_rules (openclaw:/home/knan/.openclaw/workspace/skills/adme_metabolism_prediction_rules.md), adme_preclinical_design (openclaw:/home/knan/.openclaw/workspace/skills/adme_preclinical_design.md).

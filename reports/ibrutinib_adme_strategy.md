# Executive Decision Summary

Top 3 priorities:
- No top priority was generated.
Highest-confidence action: No immediate high-confidence action identified.
Main uncertainty: No-SMILES limitation
Recommended immediate next step: Start with a first-pass metabolism screen to reduce the largest uncertainty.
Decision framing: The current package is most decision-ready around Rat-aligned MetID profiling where chemistry, context, and retained evidence converge best. Immediate work should stay centered on first-pass assays that can clarify the leading clearance and metabolite-coverage hypotheses, while secondary follow-up remains gated by what the first round of data confirms. Literature confidence remained low because no SMILES-backed hotspots were available for cross-source calibration.

Decision-ready take: Decision-ready framing points to no immediate do-now action was identified. as the clearest immediate move. Secondary validation should center on no verify-next action was identified. once first-pass data arrive, while no exploratory follow-up is currently emphasized. remains conditional rather than front-loaded. The main caveat is no-smiles limitation, so the current next-step plan is intentionally staged across 0 ordered steps.

## What to Do Now
- No do now item was generated.

## What to Verify Next
- No verify next item was generated.

## Exploratory Follow-up
- No exploratory follow-up item was generated.

## Key Uncertainties
- No-SMILES limitation: The chemistry layer is operating without structure-resolved feature detection, so pathway and assay prioritization remain more template-led. Data that would reduce it: Provide a valid SMILES so structure-driven hotspot and liability logic can anchor the next recommendation cycle. Confidence impact: This keeps several recommendations closer to medium or exploratory confidence.
- Target-anchored literature weakness: The retained evidence is only weakly anchored to the exact target compound or remains mostly class-level/background support. Data that would reduce it: Stronger target-specific metabolism or disposition evidence would improve confidence calibration. Confidence impact: This keeps structure-led recommendations from being overstated as high-confidence.
- Species translation uncertainty: Evidence alignment remained neutral because hotspot-level cross-source linking was not available. Data that would reduce it: Add human-relevant microsome, hepatocyte, or translation-focused follow-up before making stronger human assumptions. Confidence impact: Human-facing implications remain more provisional than the current preclinical recommendation set.

## Suggested Next-Step Plan
1. No next-step plan was generated.

# ADME Strategy Report

## Input Summary
- Drug: Ibrutinib
- SMILES: N/A
- Species: Rat
- Focus: MetID

## Chemistry Intelligence
- SMILES validity: not valid or not provided
- RDKit used: no
- Molecular formula: N/A
- Molecular weight: N/A
- Key structural features: No RDKit-derived structural flags available.
- Pathway priorities:
  - No chemistry-driven pathway prioritization was generated.
- Chemistry confidence summary: No hotspot chemistry confidence summary was generated.
- Hotspot confidence summary: No hotspot confidence summary was generated.
- Recommendation confidence summary: high=0, medium=0, exploratory=0.
- Hotspot summary:
  - No SMILES-backed hotspot summary was generated.
- Hotspot priorities:
  - No hotspot-backed prioritization was generated.
- Structure-to-assay links:
  - No structure-to-assay links were generated.
- CYP preference hints:
  - No additional CYP-oriented chemistry hint was generated.
- Transporter hints:
  - No transporter-oriented chemistry hint was generated.
- Permeability hints:
  - No permeability-oriented chemistry hint was generated.
- Clearance-route hints:
  - No disposition-oriented clearance-route hint was generated.
- Species-aware chemistry interpretation:
  - Summary: Rat interpretation should emphasize preclinical metabolite coverage and sample-matrix richness before extrapolating to human.
  - Preferred contexts: rat liver microsomes, rat hepatocytes, bile/urine/feces profiling
  - Assay biases: Rat liver microsomes and rat hepatocytes are useful for early oxidation and soft-spot screening.; In vivo rat bile, urine, and feces can add practical metabolite-coverage value for MetID work.
  - Extrapolation cautions: Rat metabolism patterns should be checked against human systems before drawing translation conclusions.; Conjugation-heavy chemistry may show species differences that need confirmation outside rat.
- Assay priorities:
  - No chemistry-driven assay prioritization was generated.
- Disposition summary:
  - Summary: No additional disposition-oriented chemistry interpretation was generated.
  - Transporter summary: No transporter-oriented hint generated.
  - Permeability summary: No permeability-oriented hint generated.
  - Clearance-route summary: No disposition-oriented clearance-route hint generated.
- Disposition assay priorities:
  - No additional disposition assay priority was generated.
- Soft spot hints:
  - No structure-driven soft-spot hints were generated.
- Phase I liabilities: No specific Phase I liability hint generated.
- Phase II liabilities: No specific Phase II liability hint generated.
- Reactive metabolite awareness: No specific reactive metabolite alert generated.
- Chemistry-derived risk notes: No additional chemistry-derived risk note generated.
- Chemistry-derived protocol implications: No additional chemistry-driven protocol implication beyond the base ADME template.
- Chemistry limitations: No SMILES provided; RDKit-based structure analysis was skipped.; Chemistry agent continued in fallback mode because no SMILES was supplied.
- Chemistry summary: No SMILES was provided, so the chemistry intelligence layer fell back to text-only heuristics.

## Evidence-Linked Prioritization
- Structure-to-evidence summary: No hotspot linking was generated because no SMILES-backed hotspot summary was available.
- Assay traceability summary: No assay support linking was generated because no chemistry-backed assay priorities were available.
- Evidence tag summary: metabolite_profiling=3, microsome=3, oxidation=3, metid_support=3, lc_ms=2, rat_aligned=2, n_dealkylation=1, hydrolysis=1, glucuronidation=1, bile_urine_feces=1, reactive_metabolite=1
- Literature confidence summary: Literature confidence remained low because no SMILES-backed hotspots were available for cross-source calibration.
- Evidence alignment summary: Evidence alignment remained neutral because hotspot-level cross-source linking was not available.
- Top hotspot-backed priorities:
  - No hotspot-backed priority was generated.
- Assay recommendation traceability:
  - No assay traceability entry was generated.

## Confidence-Calibrated Prioritization
- High-confidence priorities: No item currently reaches high-confidence status.
- Medium-confidence priorities: No medium-confidence priority was generated.
- Exploratory follow-up items: No exploratory item was generated.
- Confidence caveats: Confidence calibration was limited because hotspot-backed evidence linking was unavailable.
- Cross-source calibration note: Literature confidence remained low because no SMILES-backed hotspots were available for cross-source calibration.
- Species/context alignment note: Evidence alignment remained neutral because hotspot-level cross-source linking was not available.

## 1. Predicted Metabolic Pathways
- Aromatic hydroxylation is plausible due to aromatic ring features.
- N-dealkylation may occur because a tertiary amine is present.
- Aromatic motifs often increase the likelihood of Phase I ring oxidation.
- Tertiary amines commonly undergo oxidative dealkylation in microsomes and hepatocytes.
- Ibrutinib often shows oxidative metabolism and CYP3A sensitivity in preclinical ADME discussions.
- No SMILES was provided, so the chemistry intelligence layer fell back to text-only heuristics.

## 2. Recommended In Vitro Studies
- Human liver microsomes: measure intrinsic clearance, metabolite soft spots, and time-dependent turnover.
- S9 fraction: capture mixed Phase I and Phase II turnover, especially if glucuronidation is suspected.
- Cryopreserved hepatocytes: profile intact-cell metabolism and compare qualitative metabolites across species.
- Plasma stability: check parent stability and binding-related loss in species-matched plasma.
- CYP phenotyping: use recombinant CYPs or selective inhibitors to map isoform contribution and DDI risk.
- Expand CYP3A-focused inhibition and induction package because a CYP3A liability signal is present.
- Add hepatocyte relay or extended incubation work if rapid turnover obscures metabolite identification.
- Run glutathione or cyanide trapping in microsomes/S9 to screen for reactive intermediates.

## 3. Suggested In Vivo Design
- Rat cassette or single-compound PK study with dense early sampling (for example 0.25, 0.5, 1, 2, 4, 8, 24 h).
- Collect plasma plus optional urine/bile or feces pools when feasible to support clearance route interpretation.
- Include metabolite profiling around Tmax and terminal phase to distinguish formation-limited versus elimination-limited species.
- Consider IV plus PO arms to separate bioavailability limitations from true systemic clearance.
- Rat-focused metabolite coverage: collect bile, urine, and feces when feasible because the chemistry profile supports broader metabolite mapping.

## 4. Potential Risks
- Predicted clearance risk: High.
- Predicted reactive metabolite risk: Elevated.
- CYP3A involvement suspected: assess victim and perpetrator DDI scenarios early.
- High metabolic liability may translate to high clearance risk and limited oral exposure.
- Reactive metabolite concern: add trapping experiments and targeted bioactivation review.
- Rat metabolism patterns should be checked against human systems before drawing translation conclusions.
- Conjugation-heavy chemistry may show species differences that need confirmation outside rat.
- Potential CYP-mediated N-dealkylation may contribute to DDI sensitivity.
- Michael acceptor liability may warrant reactive metabolite awareness.
- Known or suspected CYP3A contribution suggests DDI focus during phenotyping.
- High clearance risk: prioritize intrinsic clearance readouts in microsomes and hepatocytes.

## 5. Translation to Human
- Scale microsomal and hepatocyte intrinsic clearance to human hepatic clearance using standard IVIVE assumptions.
- Compare qualitative human versus preclinical metabolites to flag disproportionate human metabolite risk early.
- If systemic clearance appears high in rodent, prioritize hepatocyte and plasma protein binding data before projecting human exposure.
- Rat interpretation should emphasize preclinical metabolite coverage and sample-matrix richness before extrapolating to human.
- Rat metabolism patterns should be checked against human systems before drawing translation conclusions.
- Conjugation-heavy chemistry may show species differences that need confirmation outside rat.

## 6. Supporting Literature
Focus-aware ranking enabled: yes
Context-aware ranking enabled: yes
Target-compound prioritization enabled: yes
Title-centric target detection enabled: yes
Focus: MetID
Species: Rat
Primary provider: europe_pmc
Provider used: europe_pmc
Query set used: Ibrutinib metabolite identification; Ibrutinib metabolism; Ibrutinib biotransformation; Ibrutinib ADME
Retrieval mode summary: europe_pmc
Focus profile summary: Ranking emphasizes focus-specific keywords such as metabolite, metabolism, biotransformation, microsomes.
Focus relevance summary: Average focus relevance score: 10.9; exact but weak-focus records: 2. Keyword hits: metabolite=4, metabolism=3, biotransformation=3, microsomes=3, metabolite profiling=2, mass spectrometry=2, metabolite identification=1. Top literature still contains several exact-name but weak-MetID articles.
Species profile summary: Ranking boosts records with species context such as rat, multi-species, rat liver microsomes, rat bile.
Matrix profile summary: Ranking emphasizes matrix and experimental-context signals such as liver microsomes, in vitro metabolism, metabolite profiling, mass spectrometry, plasma.
Species relevance summary: Average species relevance score: 2.6; species-aligned records: 2; context-mismatched records: 3. Top evidence still contains several non-Rat or species-neutral records.
Matrix/context relevance summary: Average matrix/context relevance score: 9.0; strong context records: 3; weak context records: 2. Top evidence still includes several records with weak MetID matrix context.
Compound relation summary: target_exact=2, ambiguous_compound_context=2, neighbor_compound=1
Title target status summary: target_exact_in_title=2, target_only_in_abstract_or_summary=2, non_target_title_center=1 Top evidence is mostly title-centered on the target compound.
Title-centric boost summary: Average title-centric boost: 3.1; title-centered target records: 2; title-centered records in top three: 2. Title-exact or title-alias boosts materially shape the top evidence.
Mention-only penalty summary: Average mention-only penalty: 3.1; abstract-mention records: 2; non-target title-centered records: 1. Mention-only or non-target-title records are actively demoted from the top evidence pool.
Evidence bucket summary: supporting_target_evidence=2, background_evidence=2, neighbor_supporting_evidence=1
Neighbor suppression summary: Core target evidence count: 0; neighbor supporting evidence count: 1; ambiguous compound-context records: 2; average neighbor suppression penalty: 3.2. Top evidence is clearly target-compound led.
Exact/alias/class-level match summary: class_level_match=3, exact_name_match=2
Article type summary: clinical_study=2, preclinical_study=2, unknown=1
Literature quality summary: Exact matches: 2; alias matches: 0; class-level matches: 3; target exact: 2; target alias: 0; neighbor compounds: 1; title-centered target records: 2; abstract-mention records: 2; non-target title-centered records: 1; core target evidence: 0; supporting target evidence: 2; neighbor supporting evidence: 1; review articles: 0; clinical studies: 2; preclinical studies: 2. Results are dominated by class-level matches.

### Supporting Target Evidence
- Lactobacillus gasseri prevents ibrutinib-associated atrial fibrillation through butyrate.
  Journal: MED
  Year: 2025
  Authors: Shi L, Duan Y, Fang N, Zhang N, Yan S, Wang K, Hou T, Wang Z, Jiang X, Gao Q, Zhang S, Li Y, Zhang Y, Gong Y.
  Retrieval mode: europe_pmc
  Compound relation: target_exact
  Title target status: target_exact_in_title
  Evidence bucket: supporting_target_evidence
  Match type: exact_name_match
  Article type: unknown
  Base score: 38.25
  Focus relevance score: 1.50
  Species relevance score: 0.00
  Matrix relevance score: 0.00
  Title exactness boost: 7.84
  Mention-only penalty: 0.00
  Title compound centrality: 0.98
  Species-specific exactness boost: 4.00
  Neighbor suppression penalty: 0.00
  Final score: 42.09
  Relevance: Exact target-compound match, retained as supporting target evidence. Target drug appears directly in the title (title centrality 0.98). Strong MetID-specific signals via metabolite; limited Rat-specific context relative to the current query; limited matrix/context support for the requested experimental setup; focus mismatch penalty 2.0; context mismatch penalty 7.5; title exactness boost 7.8; species-specific exactness boost 4.0; classified as unknown.; recent publication year 2025
  URL: https://europepmc.org/article/MED/39821305
  Summary: <h4>Background</h4>Ibrutinib, a widely used anti-cancer drug, is known to significantly increase the susceptibility to atrial fibrillation (AF). While it is recognized that drugs can reshape the gut microbiota, influencing both therapeutic effectiveness and adverse events, the role of gut microbiota in ibrutinib-induced AF remains largely unexplored.<h4>Method</h4>Utilizing 16S rRNA gene sequencing, faecal microbiota transplantation, metabonomics, electrophysiological examination, and molecular biology methodologies, we sought to validate the hypothesis that gut microbiota dysbiosis promotes ibrutinib-associated AF and to elucidate the underlying mechanisms.<h4>Result</h4>We found that ibrutinib administration pre-disposes rats to AF. Interestingly, ibrutinib-associated microbial transplantation conferred increased susceptibility to AF in rats. Notably, ibrutinib induced a significantly decrease in the abundance of Lactobacillus gasseri (L. gasseri), and oral supplementation of L. gasseri or its metabolite, butyrate (BA), effectively prevented rats from ibrutinib-induced AF. Mechanistically, BA inhibits the generation of reactive oxygen species, thereby ameliorating atrial structural remodelling. Furthermore, we demonstrated that ibrutinib inhibited the growth of L. gasseri by disrupting the intestinal barrier integrity.<h4>Conclusion</h4>Collectively, our findings provide compelling experimental evidence supporting the potential efficacy of targeting gut microbes in preventing ibrutinib-associated AF, opening new avenues for therapeutic interventions.
- Influence of CYP2D6, CYP3A, and ABCG2 Genetic Polymorphisms on Ibrutinib Disposition in Chinese Healthy Subjects.
  Journal: MED
  Year: 2025
  Authors: Fu K, Wang Y, Duan L, Zhang Z, Qian J, Chen X, Liang Y, Lu C, Zhao D.
  Retrieval mode: europe_pmc
  Compound relation: target_exact
  Title target status: target_exact_in_title
  Evidence bucket: supporting_target_evidence
  Match type: exact_name_match
  Article type: clinical_study
  Base score: 49.25
  Focus relevance score: -1.00
  Species relevance score: 0.00
  Matrix relevance score: 1.00
  Title exactness boost: 7.60
  Mention-only penalty: 0.00
  Title compound centrality: 0.95
  Species-specific exactness boost: 4.00
  Neighbor suppression penalty: 0.00
  Final score: 37.85
  Relevance: Exact target-compound match, retained as supporting target evidence. Target drug appears directly in the title (title centrality 0.95). Limited MetID-specific content; limited Rat-specific context relative to the current query; matrix/context support via plasma; focus mismatch penalty 16.0; context mismatch penalty 7.0; title exactness boost 7.6; species-specific exactness boost 4.0; classified as clinical_study.; recent publication year 2025
  URL: https://europepmc.org/article/MED/41304862
  Summary: <b>Objectives</b>: This study aimed to elucidate the determinants of interindividual variability in the pharmacokinetics of ibrutinib among healthy Chinese subjects, focusing on the influence of demographic characteristics, dietary conditions, and genetic polymorphisms on CYP enzymes and ABC transporters. <b>Methods</b>: Thirty-two participants were randomly assigned to either a fasting (n = 16) or fed (n = 16) group, each receiving a single 140 mg oral dose of ibrutinib. Plasma concentrations were quantified using a validated UPLC-MS/MS method. Genetic polymorphisms in CYP3A4, CYP3A5, CYP2D6, and ABCG2 were identified by Sanger sequencing. Pharmacokinetic parameters, including apparent clearance (CL/F), maximum plasma concentration (Cmax), area under the plasma concentration-time curve (AUC0-t), and time to maximum concentration (Tmax), were estimated by non-compartmental analysis and statistically evaluated for associations with demographic, dietary, and genetic variables. <b>Results</b>: Food intake significantly affected ibrutinib pharmacokinetics, with postprandial administration resulting in reduced CL/F and increased Cmax and AUC0-t (<i>p</i> < 0.01). Gender differences were also observed, as females exhibited higher CL/F, lower Cmax, and AUC0-t than males (<i>p</i> < 0.05). The CYP2D6 c.100C>T polymorphism significantly decreased CL/F and increased exposure in fasting and male subjects (<i>p</i> < 0.05), but this effect was absent under fed conditions. Conversely, the ABCG2 c.421C>A variant was associated with increased CL/F and decreased AUC0-t (<i>p</i> < 0.05), while other genotypes exerted negligible effects. <b>Conclusions</b>: Ibrutinib pharmacokinetics are significantly modulated by dietary status, gender, and genetic polymorphisms, particularly CYP2D6 c.100C>T and ABCG2 c.421C>A. These findings underscore the importance of integrating pharmacogenetic and physiological factors into individualized dosing strategies to optimize therapeutic efficacy and minimize adverse effects.

### Neighbor Supporting Evidence
- Metabolite profiling of remibrutinib in rat and human liver microsomes using liquid chromatography combined with benchtop orbitrap high-resolution mass spectrometry.
  Journal: MED
  Year: 2023
  Authors: Lai X, Liu J, Li W, Qiao M, Qiu M, Lu L.
  Retrieval mode: europe_pmc
  Compound relation: neighbor_compound
  Title target status: non_target_title_center
  Evidence bucket: neighbor_supporting_evidence
  Match type: class_level_match
  Article type: preclinical_study
  Base score: 23.75
  Focus relevance score: 25.50
  Species relevance score: 7.00
  Matrix relevance score: 18.00
  Title exactness boost: 0.00
  Mention-only penalty: 6.90
  Title compound centrality: 0.10
  Species-specific exactness boost: 0.00
  Neighbor suppression penalty: 8.00
  Final score: 59.35
  Relevance: Centers on neighbor compound remibrutinib, retained as supporting neighbor evidence. Title centers on a non-target compound or object (title centrality 0.10). Strong MetID-specific signals via metabolite profiling, mass spectrometry; species context aligns with Rat via rat liver microsomes, rat; matrix/context support via liver microsomes, metabolite profiling; mention-only penalty 6.9; neighbor suppression penalty 8.0; classified as preclinical_study.; recent publication year 2023
  URL: https://europepmc.org/article/MED/37651996
  Summary: Remibrutinib is a potent and highly selective covalent Bruton's tyrosine kinase inhibitor that is undergoing clinical development for the treatment of autoimmune diseases. The present study was undertaken to investigate the in vitro metabolism of remibrutinib and to propose its biotransformation pathways. The metabolites were generated by incubating remibrutinib (2 μm) with human and rat liver microsomes at 37°C for 30 min. Ultra-high-performance liquid chromatography combined with benchtop orbitrap high-resolution mass spectrometry was used to identify and characterize the metabolites of remibrutinib. Compound Discoverer software was employed to process the acquired data. In rat liver microsomes, a total of 18 metabolites have been identified and characterized among which three (M8, M12 and M13) were identified as the most abundant metabolites. In human liver microsomes, a total of 16 metabolites have been identified, and M8 and M12 were identified as the predominant metabolites. All the metabolites were nicotinamide adenine dinucleotide phosphate dependent. The major metabolic changes were found to be oxygenation, dealkylation, demethylation, epoxidation and hydrolysis. The present study comprehensively reports the in vitro metabolism of remibrutinib mentioning 20 metabolites. These findings will help investigation of remibrutinib disposition and safety evaluation.

### Background Evidence
- Biotransformation of Penindolone, an Influenza A Virus Inhibitor.
  Journal: MED
  Year: 2023
  Authors: Liu S, Zheng K, Jiang Y, Gai S, Li B, Li D, Yang S, Lv Z.
  Retrieval mode: europe_pmc
  Compound relation: ambiguous_compound_context
  Title target status: target_only_in_abstract_or_summary
  Evidence bucket: background_evidence
  Match type: class_level_match
  Article type: clinical_study
  Base score: 24.75
  Focus relevance score: 14.50
  Species relevance score: 6.00
  Matrix relevance score: 15.00
  Title exactness boost: 0.00
  Mention-only penalty: 4.25
  Title compound centrality: 0.25
  Species-specific exactness boost: 0.00
  Neighbor suppression penalty: 4.00
  Final score: 52.00
  Relevance: Mixed or ambiguous compound context, retained as background evidence. Target mention appears mainly in abstract or summary (title centrality 0.25). Strong MetID-specific signals via metabolite identification, mass spectrometry; species context aligns with Rat via rat bile, rat; matrix/context support via liver microsomes, metabolite identification; mention-only penalty 4.2; neighbor suppression penalty 4.0; classified as clinical_study.; recent publication year 2023
  URL: https://europepmc.org/article/MED/36771146
  Summary: Penindolone (PND) is a novel broad-spectrum anti-Influenza A Virus (IAV) agent blocking hemagglutinin-mediated adsorption and membrane fusion. The goal of this work was to reveal the metabolic route of PND in rats. Ultra-high-performance liquid chromatography tandem high-resolution mass spectrometry (UHPLC-HRMS) was used for metabolite identification in rat bile, feces and urine after administration of PND. A total of 25 metabolites, including 9 phase I metabolites and 16 phase II metabolites, were characterized. The metabolic pathways were proposed, and metabolites were visualized via Global Natural Product Social Molecular Networking (GNPS). It was found that 65.24-80.44% of the PND presented in the formation of glucuronide conjugate products in bile, and more than 51% of prototype was excreted through feces. In in vitro metabolism of PND by rat, mouse and human liver microsomes (LMs) system, PND was discovered to be eliminated in LMs to different extents with significant species differences. The effects of chemical inhibitors of isozymes on the metabolism of PND in vitro indicated that CYP2E1/2C9/3A4 and UGT1A1/1A6/1A9 were the metabolic enzymes responsible for PND metabolism. PND metabolism in vivo could be blocked by UGTs inhibitor (ibrutinib) to a certain extent. These findings provided a basis for further research and development of PND.
- In vitro metabolism studies of 5 acrylamide covalent drugs: Comparison with metabolism and disposition in human.
  Journal: MED
  Year: 2026
  Authors: Li R, Shi Q, Zhu M, Cao W, Tao Y, Shen L.
  Retrieval mode: europe_pmc
  Compound relation: ambiguous_compound_context
  Title target status: target_only_in_abstract_or_summary
  Evidence bucket: background_evidence
  Match type: class_level_match
  Article type: preclinical_study
  Base score: 27.25
  Focus relevance score: 14.00
  Species relevance score: 0.00
  Matrix relevance score: 11.00
  Title exactness boost: 0.00
  Mention-only penalty: 4.25
  Title compound centrality: 0.25
  Species-specific exactness boost: 0.00
  Neighbor suppression penalty: 4.00
  Final score: 39.00
  Relevance: Mixed or ambiguous compound context, retained as background evidence. Target mention appears mainly in abstract or summary (title centrality 0.25). Strong MetID-specific signals via metabolite profiling, metabolite; limited Rat-specific context relative to the current query; matrix/context support via liver microsomes, metabolite profiling; context mismatch penalty 5.0; mention-only penalty 4.2; neighbor suppression penalty 4.0; classified as preclinical_study.; recent publication year 2026
  URL: https://europepmc.org/article/MED/41702144
  Summary: Targeted covalent inhibitors, such as acrylamide covalent drugs (ACDs), offer advantages in potency, selectivity, and duration of effect compared with traditional small-molecule inhibitors. However, ACDs undergo unique biotransformation pathways in humans, including CYP-mediated metabolism, protein covalent binding, and nonenzymatic glutathione (GSH) adduction, which make standard in vitro metabolism assays for small molecules unsuitable for characterizing ACDs. This study aimed to develop a specialized panel of in vitro metabolism experiments for characterizing ACDs. The approach included metabolism stability assays in human liver microsomes with or without NADPH, covalent binding to human serum albumin with or without GSH, and metabolite profiling in human liver microsomes with or without GSH. In vitro metabolic data were generated for 5 ACDs, abivertinib, afatinib, osimertinib, ibrutinib, and pyrotinib, and compared with reported human metabolism and disposition data. In general, in vitro biotransformation pathways determined in this study are consistent with major metabolic clearance pathways observed in humans. For example, osimertinib showed the highest nonspecific protein covalent binding, a high oxidation-to-GSH adduct ratio, and moderate NADPH-dependent metabolic rates, supporting protein covalent binding as the major metabolic pathway in humans. In contrast, afatinib exhibited minimal CYP-mediated metabolism after accounting for covalent binding to microsomal proteins, low serum protein binding, and a very low oxidation-to-GSH adduct ratio, consistent with GSH adduction being the predominant biotransformation pathway in humans. The results demonstrate that the newly developed in vitro metabolism workflow enables more accurate predictions of CYP-mediated clearance rates and clarifies the relative contributions of CYP metabolism, nonspecific protein covalent binding, and GSH adduction to overall metabolic clearance in humans. SIGNIFICANT STATEMENT: This study established a novel in vitro metabolism approach for characterizing acrylamide covalent drugs. By comparing in vitro metabolic data for abivertinib, afatinib, osimertinib, ibrutinib, and pyrotinib with reported human metabolism and disposition data, we demonstrated that this method improves the accuracy of predicting CYP-mediated metabolic rates. Furthermore, it provides clearer insights into the relative contributions of CYP metabolism, nonspecific protein covalent binding, and glutathione adduction to the overall metabolic clearance of acrylamide covalent drugs in humans.

## 7. Disclaimer
This report is an MVP-generated preclinical planning aid that uses heuristic metabolism rules, template-driven protocol logic, and a real-first literature retrieval pipeline with automatic fallback. It is not a substitute for medicinal chemistry judgment, wet-lab data, or formal regulatory advice.

Skill context loaded from: adme_human_translation_rules (openclaw:/home/knan/.openclaw/workspace/skills/adme_human_translation_rules.md), adme_metabolism_prediction_rules (openclaw:/home/knan/.openclaw/workspace/skills/adme_metabolism_prediction_rules.md), adme_preclinical_design (openclaw:/home/knan/.openclaw/workspace/skills/adme_preclinical_design.md).

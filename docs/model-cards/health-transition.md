# Model Card: Health Transition

Purpose: evidence-bounded target-trial transition for physical and mental health outcomes.

Estimand: average treatment effect for an advisor-reviewed intervention prior whose outcome_domain is `health`.

Required evidence bounds: `EvidencePrior.review_status = advisor_reviewed`, `effect_validated = true`, citation, risk-of-bias rating, transportability rating, uncertainty, and a source `dataset_reference`.

Required dataset_reference lineage: each result carries the intervention-prior source reference and the run manifest must also carry the produced feature-table reference for `features.intervention_effect_size_priors_v1`.

Outputs: expected effect, 95% uncertainty interval, probability of harm, seed stability, prior sensitivity, E-value hook, exposure-measure disagreement, graph-layer ablation, and subgroup heterogeneity status.

Subgroup status: not estimated unless a validated subgroup-specific prior is provided; the engine withholds subgroup estimates rather than inventing them.

Validation status: public health context can calibrate or validate model behavior, but does not by itself prove causal treatment effects.

Guardrails: Concordia cognition traces and FOS Graph artifacts are qualitative or visual context only and cannot create causal effect sizes.

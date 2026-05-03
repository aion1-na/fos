def target_trial_payload_fixture_only() -> dict[str, object]:
    feature_dataset_reference = {
        "canonical_dataset_name": "features.intervention_effect_size_priors_v1",
        "version": "fixture-0.1",
        "content_hash": "b" * 64,
    }
    return {
        "scenario_id": "job_training_retraining",
        "transition_model_id": "financial_stability",
        "target_population": "young adults",
        "treatment": "job training",
        "comparator": "usual services",
        "outcome_domain": "financial_stability",
        "evidence_prior": {
            "claim_id": "claim_job_training_retraining_financial_security_v1",
            "source_id": "src_job_training_request_status",
            "dataset_reference": {
                "canonical_dataset_name": "intervention_literature.job_training",
                "version": "request-status-v0.1",
                "content_hash": "a" * 64,
            },
            "feature_dataset_reference": feature_dataset_reference,
            "effect_size": 0.1,
            "uncertainty": 0.03,
            "citation": "fixture_only citation",
            "risk_of_bias": "medium",
            "transportability": "medium",
            "review_status": "advisor_reviewed",
            "effect_validated": True,
        },
    }

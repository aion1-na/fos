export const graphStudioInterventionPriors = [
  {
    claimId: "claim_family_support_financial_security_v1",
    scenarioId: "family_support",
    outcomeDomain: "financial_security",
    effectSize: 0,
    ciLow: -0.392,
    ciHigh: 0.392,
    reviewStatus: "draft",
    fixtureOnly: true,
    causalEffectValidated: false,
  },
  {
    claimId: "claim_community_belonging_social_prescribing_employment_v1",
    scenarioId: "community_belonging_social_prescribing",
    outcomeDomain: "employment",
    effectSize: 0.14,
    ciLow: 0.062,
    ciHigh: 0.218,
    reviewStatus: "rejected",
    fixtureOnly: true,
    causalEffectValidated: false,
  },
] as const;

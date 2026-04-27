# Curator Review Workflow

Owner: Evidence Curator

## States

- `draft`: extracted or stubbed claim has not been advisor-reviewed.
- `advisor_reviewed`: claim has passed advisor review and can be used as reviewed prior evidence.
- `rejected`: claim cannot support an intervention prior.

## Required Review Fields

- claim id
- source id
- population
- treatment
- outcome
- estimate
- uncertainty
- risk of bias
- confidence label
- provenance link

Draft and advisor-reviewed claims must remain visually distinguishable in Atlas.

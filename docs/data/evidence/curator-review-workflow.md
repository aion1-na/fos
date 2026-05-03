# Curator Review Workflow

Owner: Evidence Curator

## States

- `draft`: extracted or stubbed claim has not been advisor-reviewed.
- `advisor_reviewed`: claim has passed advisor review and can be used as reviewed prior evidence.
- `rejected`: claim cannot support an intervention prior.
- `superseded`: claim remains auditable but has been replaced by a newer claim or extraction.

## Required Review Fields

- claim id
- source id
- target population
- treatment
- comparator
- outcome
- outcome domain
- effect size estimate
- uncertainty
- risk of bias
- transportability
- review status label
- citation
- source `dataset_reference`
- provenance link

Draft, advisor-reviewed, rejected, and superseded claims must remain visually distinguishable in Atlas and FOS Graph Studio forest-plot views. Graph layout and animation are visual artifacts only; they must not be treated as evidence.

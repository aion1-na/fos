# OSF Pre-Registration Draft Packet

Status: draft for review; not submitted.

## Scenario Definition

Scenario name: Young Adult Flourishing Futures MVP smoke fixture.

The scenario is defined by explicit branch, intervention, validation, and dataset-reference inputs in the platform artifacts. No unversioned data reads are permitted.

## Validation Gates

- Dataset metadata completeness gate.
- Dataset reference resolvability gate.
- Validation-report status gate.
- Brief export gate for draft, research-grade, and decision-grade outputs.

## Seed Policy

All stochastic runs must record seed count, seed values or deterministic seed derivation, and replay manifest. Demo runs may use fixture seeds, but must label outputs as demo-only.

## Dataset Version Policy

Every simulation-facing input must use `dataset_reference = (canonical_dataset_name, version, content_hash)`. Old versions must remain resolvable after a new version is registered. Public outputs must link to the dataset card, provenance manifest, and limitations.

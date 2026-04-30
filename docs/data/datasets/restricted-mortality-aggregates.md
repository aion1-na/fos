# Dataset Card: Restricted Mortality Aggregates

Canonical dataset name: `features.restricted_mortality_aggregates`

Version: `request-status-v0.1`

Access status: request_status_stub

License metadata: NCHS RDC or state vital statistics terms pending; no license is assumed approved.

Codebook mapping: Intended aggregate fields only: geography level, broad demographic fields, cause group, suppressed flag, deaths, and mortality rate.

Quality profile: Small-cell suppression and disclosure review are required before FOS ingestion. Suppressed rows expose neither deaths nor mortality rates.

Provenance manifest: Future restricted source environment metadata and review id; current repository stores request-status metadata only.

Access policy: Restricted-use path. Raw mortality records must not enter FOS. Public CDC WONDER outputs use the public CDC path and are clearly separated.

Limitations: No restricted health data is present. This card documents the aggregate contract and disclosure boundary only.

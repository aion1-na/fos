# Commercial Data Evaluation Checklist

- Confirm vendor license, permitted uses, retention period, and deletion obligations.
- Confirm whether derived features can be used in simulation runs and public briefs.
- Confirm compartment path and access-control owner before ingest.
- Confirm refresh cadence, daily/hourly partition policy, and late-arriving snapshot handling.
- Confirm no credentials, tokens, or vendor extracts are committed to source control.
- Confirm run manifests pin content-addressed snapshot references.

License constraints:
- Lightcast, LinkedIn, and Indeed feeds remain request-status stubs until approved license terms are recorded.
- Commercial feeds must be stored in vendor-specific compartments.
- Public Atlas may display metadata labels only, not restricted feed rows.

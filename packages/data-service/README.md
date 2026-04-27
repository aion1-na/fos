# Data Service

Owner: Data Platform

Test command: `uv run pytest packages/data-service -v`

Definition of done:

- Serves metadata only until source access is approved.
- Never stores credentials in source control.
- Exposes request status, dataset cards, access policy, provenance manifest locations, and dataset references.
- Rejects unversioned dataset reads.

This service is the data workstream boundary for Atlas and platform consumers.

# SOC/O*NET/Census Crosswalk v0.1

Owner: Data Governance

Version: `0.1`

Access status: versioned fixture-only crosswalk for tests; production crosswalk registration requires approved source files

Reversibility: SOC to O*NET is reversible where a fixture row declares `reversible: true`; Census occupation mapping is many-to-one and requires ambiguity metadata.

Policy:

- Preserve original codes.
- Preserve source labels.
- Emit canonical `occupation_code`.
- Record `crosswalk_version` on derived features.
- Do not collapse ambiguous mappings silently.

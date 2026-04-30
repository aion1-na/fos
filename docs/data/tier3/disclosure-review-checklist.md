# Disclosure-Review Checklist

Use before any Tier 3 aggregate result enters FOS.

- Disclosure-review status is `approved`.
- Reviewer identity and review date are recorded.
- Cell suppression has been checked.
- Re-identification risk has been checked.
- Publication path is allowed by the restricted-data terms where possible.
- Aggregate output name appears in the pinned secure analysis manifest.
- No row-level restricted data, raw extract, or restricted URI enters FOS.
- The simulation-facing output receives `dataset_reference = (canonical_dataset_name, version, content_hash)`.

Only aggregate outputs with approved disclosure-review metadata may enter FOS. Outputs that fail any item remain outside FOS.

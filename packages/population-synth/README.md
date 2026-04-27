# Population Synth

Owner: Population Data Engineering

Test command: `uv run pytest packages/population-synth -v`

Definition of done:

- Synthesis is deterministic for identical specs and seeds.
- Snapshots are content-addressed.
- Fidelity reports are emitted with provenance.
- No production data is read without dataset metadata and access approval.

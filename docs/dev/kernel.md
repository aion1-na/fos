# Simulation Kernel

The kernel is deterministic and pack-agnostic. It receives a `Scenario`, `Population`, and `DomainPack`, then emits a `SimulationRun`.

## Runtime Rules

- No pack-specific imports.
- No flourishing, GFS, happiness, or other domain-specific assumptions.
- Every random draw goes through a seeded `numpy.random.Generator`.
- Hot-path transitions operate on vectors, not per-agent Python loops.
- Every tick emits a deterministic hash sequence in the run artifact.

## Tick Loop

The runtime modules implement snapshot, applicability, order, compute, resolve, network, commit, and provenance. Composition conflicts are runtime errors, including multiple `replace` declarations on the same field.

## Artifacts

Run artifacts write Parquet/JSONL plus a manifest. Reload tests assert byte-identical outputs for identical inputs.

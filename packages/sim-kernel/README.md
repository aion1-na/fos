# Simulation Kernel

Owner: Runtime Engineering

Test command: `uv run pytest packages/sim-kernel -v`

Definition of done:

- Runtime remains deterministic.
- Kernel code imports no packs.
- Hot-path transitions stay vectorized.
- Tick hash and artifact serialization tests pass.

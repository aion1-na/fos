# Pack Authoring

A pack supplies domain content behind the `DomainPack` contract. Kernel behavior must not change when adding a pack.

## Required Members

- `id`, `name`, `version`, and `contracts_version`.
- `state_schema`, opaque to the kernel.
- `transition_models`.
- `interventions`.
- `validation_suites`.
- `render_hints`.

## Transition Signature

```python
def vectorized_transition(
    fields: dict[str, np.ndarray],
    rng: np.random.Generator,
    parameters: dict[str, object],
    tick: int,
) -> dict[str, object]:
    ...
```

Transitions declare dependencies, fields written, composition rule, and evidence claims. Flourishing transitions must cite at least one claim from `packs/flourishing/evidence/seed_claims.yml`.

## Lint

Run:

```sh
python3 tools/lint/pack-lint.py
python3 tools/lint/import-lint.py
```

The import seam forbids kernel-side packages from importing `packs/`.

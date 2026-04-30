# FOS Tool Trust Policy

FOS can register external tools without making scientific validity depend on any one engine. Adapters are metadata records until an integration explicitly imports and executes a tool.

## Trust Labels

Allowed adapters may produce visual or analytic artifacts when every input dataset is represented by a `dataset_reference`.

Research-only adapters may support exploratory qualitative interaction, cognition traces, or prototype analysis. Their outputs are not causal effect sizes.

Quarantined adapters are historical or compatibility references. They may be named in manifests for audit continuity, but FOS core must not import them.

Blocked adapters must not execute in FOS workflows.

## Default Registry

The default registry includes:

- `concordia`: research-only qualitative interaction and cognition trace adapter.
- `cosmos_gl`: allowed FOS Graph renderer.
- `sigma_cytoscape`: allowed fallback graph renderer and network-analysis helper.
- `mirofish_reference`: quarantined legacy reference, not imported by FOS core.

Concordia outputs are qualitative interaction/cognition artifacts unless explicitly validated. Concordia must not create causal effect sizes.

FOS Graph outputs are visual or analytic artifacts. Graph layout, animation, or renderer state must not be treated as evidence.

All tool artifacts must retain the dataset references used to produce them. External tools cannot bypass the `dataset_reference = (canonical_dataset_name, version, content_hash)` contract.

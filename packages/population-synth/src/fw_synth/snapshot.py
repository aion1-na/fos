from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pyarrow as pa
import pyarrow.parquet as pq
from fw_contracts import PopulationSnapshot, SpawnSpec

from fw_synth.store import SynthStore


@dataclass(frozen=True)
class SnapshotArtifact:
    snapshot: PopulationSnapshot
    path: str
    manifest: dict[str, Any]


def content_address(
    spec: SpawnSpec,
    data_versions: dict[str, str],
    pack_version: str,
    seed: int,
) -> str:
    payload = {
        "data_versions": data_versions,
        "pack_version": pack_version,
        "seed": seed,
        "spawn_spec": spec.model_dump(mode="json"),
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _table_from_rows(rows: list[dict[str, Any]]) -> pa.Table:
    if not rows:
        return pa.table({})
    keys = sorted(rows[0])
    return pa.table({key: [row[key] for row in rows] for key in keys})


def write_snapshot(
    store: SynthStore,
    spec: SpawnSpec,
    pack_version: str,
    seed: int,
    data_versions: dict[str, str],
    agents: list[dict[str, Any]],
    networks: list[dict[str, Any]],
    institutions: list[dict[str, Any]],
    fidelity: dict[str, Any],
    manifest_metadata: dict[str, Any] | None = None,
) -> SnapshotArtifact:
    snapshot_id = content_address(spec, data_versions, pack_version, seed)
    root = store.path(snapshot_id)
    store.mkdir(root)

    paths = {
        "agents": f"{root}/agents.parquet",
        "networks": f"{root}/networks.parquet",
        "institutions": f"{root}/institutions.parquet",
        "fidelity": f"{root}/fidelity.json",
        "manifest": f"{root}/manifest.json",
    }
    for key in ("agents", "networks", "institutions"):
        with store.open(paths[key], "wb") as handle:
            pq.write_table(_table_from_rows(locals()[key]), handle, compression="zstd")

    with store.open(paths["fidelity"], "wb") as handle:
        handle.write(
            (json.dumps(fidelity, sort_keys=True, separators=(",", ":")) + "\n").encode(
                "utf-8"
            )
        )

    manifest = {
        "snapshot_id": snapshot_id,
        "spawn_spec": spec.model_dump(mode="json"),
        "seed": seed,
        "pack_version": pack_version,
        "data_versions": data_versions,
        "files": {name: Path(path).name for name, path in paths.items() if name != "manifest"},
    }
    if manifest_metadata:
        manifest.update(manifest_metadata)
    with store.open(paths["manifest"], "wb") as handle:
        handle.write(
            (json.dumps(manifest, sort_keys=True, separators=(",", ":")) + "\n").encode(
                "utf-8"
            )
        )

    return SnapshotArtifact(
        snapshot=PopulationSnapshot(id=snapshot_id, population_id=spec.population_id, step=0),
        path=root,
        manifest=manifest,
    )


def read_bytes(store: SynthStore, snapshot_path: str) -> dict[str, bytes]:
    snapshot_root = _snapshot_root(store, snapshot_path)
    manifest_path = f"{snapshot_root}/manifest.json"
    with store.open(manifest_path, "rb") as handle:
        manifest = json.loads(handle.read().decode("utf-8"))
    output = {"manifest.json": json.dumps(manifest, sort_keys=True).encode("utf-8")}
    for filename in manifest["files"].values():
        with store.open(f"{snapshot_root}/{filename}", "rb") as handle:
            output[filename] = handle.read()
    return output


def _snapshot_root(store: SynthStore, snapshot_path: str) -> str:
    root = snapshot_path.rstrip("/")
    if store.fs.exists(f"{root}/manifest.json"):
        return root
    entries = sorted(store.fs.ls(root, detail=False))
    for entry in entries:
        if store.fs.exists(f"{entry}/manifest.json"):
            return entry.rstrip("/")
    raise FileNotFoundError(f"snapshot manifest not found under {snapshot_path}")

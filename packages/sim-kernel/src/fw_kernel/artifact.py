from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pyarrow as pa
import pyarrow.parquet as pq

from fw_kernel.state import state_to_jsonable
from fw_kernel.types import TickRecord


@dataclass(frozen=True)
class RunArtifact:
    manifest_path: Path
    ticks_path: Path
    kpis_path: Path
    manifest: dict[str, Any]


def write_artifact(
    output_dir: Path,
    run_id: str,
    scenario_id: str,
    population_id: str,
    records: list[TickRecord],
) -> RunArtifact:
    output_dir.mkdir(parents=True, exist_ok=True)
    ticks_path = output_dir / "ticks.parquet"
    kpis_path = output_dir / "kpis.jsonl"
    manifest_path = output_dir / "manifest.json"

    table = pa.table(
        {
            "tick": [record.tick for record in records],
            "tick_hash": [record.tick_hash for record in records],
            "state_json": [
                json.dumps(
                    state_to_jsonable(record.state),
                    sort_keys=True,
                    separators=(",", ":"),
                )
                for record in records
            ],
        }
    )
    pq.write_table(table, ticks_path, compression="zstd")

    with kpis_path.open("w", encoding="utf-8") as handle:
        for record in records:
            row = {
                "tick": record.tick,
                "tick_hash": record.tick_hash,
                "kpis": {name: record.kpis[name] for name in sorted(record.kpis)},
            }
            handle.write(json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n")

    manifest = {
        "run_id": run_id,
        "scenario_id": scenario_id,
        "population_id": population_id,
        "tick_count": len(records),
        "tick_hash_sequence": [record.tick_hash for record in records],
        "files": {
            "ticks": ticks_path.name,
            "kpis": kpis_path.name,
        },
    }
    manifest_path.write_text(
        json.dumps(manifest, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
    return RunArtifact(
        manifest_path=manifest_path,
        ticks_path=ticks_path,
        kpis_path=kpis_path,
        manifest=manifest,
    )


def load_artifact(output_dir: Path) -> dict[str, Any]:
    manifest = json.loads((output_dir / "manifest.json").read_text(encoding="utf-8"))
    ticks_bytes = (output_dir / manifest["files"]["ticks"]).read_bytes()
    kpis_bytes = (output_dir / manifest["files"]["kpis"]).read_bytes()
    manifest_bytes = (output_dir / "manifest.json").read_bytes()
    return {
        "manifest": manifest,
        "ticks_bytes": ticks_bytes,
        "kpis_bytes": kpis_bytes,
        "manifest_bytes": manifest_bytes,
    }

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import yaml
from fw_contracts import SpawnSpec

from fw_synth.pipeline import synthesize_snapshot
from fw_synth.snapshot import _snapshot_root
from fw_synth.store import SynthStore
from fw_synth.young_adult import synthesize_young_adult_snapshot


def _load_spec(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise TypeError("spec must be a YAML object")
    return data


def _cmd_synthesize(args: argparse.Namespace) -> int:
    data = _load_spec(Path(args.spec))
    spawn_spec = SpawnSpec.model_validate(data["spawn_spec"])
    if data.get("population_synthesis") == "us_young_adult_calibrated":
        artifact = synthesize_young_adult_snapshot(
            spec=spawn_spec,
            pack_version=str(data["pack_version"]),
            seed=int(data["seed"]),
            output_url=args.out,
            marginal_path=str(data["marginal_path"]),
            demo_mode=bool(data.get("demo_mode", False)),
        )
    else:
        artifact = synthesize_snapshot(
            spec=spawn_spec,
            pack_version=str(data["pack_version"]),
            seed=int(data["seed"]),
            output_url=args.out,
            reference_path=str(data["reference_path"]),
            data_versions={str(k): str(v) for k, v in data["data_versions"].items()},
            thresholds=data.get("thresholds"),
        )
    print(artifact.path)
    return 0


def _cmd_fidelity(args: argparse.Namespace) -> int:
    store = SynthStore(args.snapshot)
    root = _snapshot_root(store, store.base_path)
    with store.open(f"{root}/fidelity.json", "rb") as handle:
        fidelity = json.loads(handle.read().decode("utf-8"))
    statuses = [
        str(metric["status"])
        for metric in fidelity.get("attributes", {}).values()
        if isinstance(metric, dict)
    ]
    if statuses and all(status == "green" for status in statuses):
        status = "green"
    elif any(status == "red" for status in statuses):
        status = "red"
    else:
        status = "amber"
    print(json.dumps({"status": status, "fidelity": fidelity}, sort_keys=True))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(prog="fos_synth")
    subparsers = parser.add_subparsers(dest="command", required=True)

    synthesize = subparsers.add_parser("synthesize")
    synthesize.add_argument("--spec", required=True)
    synthesize.add_argument("--out", required=True)
    synthesize.set_defaults(func=_cmd_synthesize)

    fidelity = subparsers.add_parser("fidelity")
    fidelity.add_argument("--snapshot", required=True)
    fidelity.set_defaults(func=_cmd_fidelity)

    args = parser.parse_args()
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())

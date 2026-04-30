from __future__ import annotations

import json
from pathlib import Path

from fos_data_pipelines.connectors.public_context import (
    ess_connector_config,
    eurostat_connector_config,
    ilo_connector_config,
    oecd_connector_config,
    world_bank_connector_config,
    world_happiness_report_connector_config,
    wvs_connector_config,
)


def parse_world_happiness_report_stub(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def parse_ess_stub(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def parse_wvs_stub(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


__all__ = [
    "ess_connector_config",
    "eurostat_connector_config",
    "ilo_connector_config",
    "oecd_connector_config",
    "parse_ess_stub",
    "parse_world_happiness_report_stub",
    "parse_wvs_stub",
    "world_bank_connector_config",
    "world_happiness_report_connector_config",
    "wvs_connector_config",
]

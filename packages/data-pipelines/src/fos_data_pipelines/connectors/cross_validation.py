from __future__ import annotations

import json
from pathlib import Path


def parse_world_happiness_report_stub(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def parse_ess_stub(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def parse_wvs_stub(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))

from __future__ import annotations

from pathlib import Path


def render_dataset_card(template_path: Path, values: dict[str, str]) -> str:
    rendered = template_path.read_text(encoding="utf-8")
    for key, value in values.items():
        rendered = rendered.replace("{{ " + key + " }}", value)
    return rendered

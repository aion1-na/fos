from __future__ import annotations

import json
from pathlib import Path

from fos_data_pipelines import build_us_young_adult_population_marginals

ROOT = Path(__file__).resolve().parents[1]
MARGINALS = (
    ROOT
    / "packages"
    / "population-synth"
    / "tests"
    / "fixtures"
    / "young_adult_marginals_fixture_only.json"
)


def test_young_adult_population_marginals_feature_has_reference(tmp_path: Path) -> None:
    path, reference = build_us_young_adult_population_marginals(
        MARGINALS,
        tmp_path,
        dataset_version="fixture-only-v0.1",
    )
    payload = json.loads(path.read_text(encoding="utf-8"))

    assert reference.canonical_dataset_name == "features.us_young_adult_population_marginals"
    assert payload["feature_table"] == "features.us_young_adult_population_marginals"
    assert payload["dataset_reference"]["content_hash"] == reference.content_hash
    assert "age_band" in payload["marginals"]
    assert "source_references" in payload

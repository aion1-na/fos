from __future__ import annotations

from pathlib import Path

from fos_data_pipelines import build_fixture_reference


def test_fixture_reference_is_content_addressed(tmp_path: Path) -> None:
    fixture = tmp_path / "sample.csv"
    fixture.write_text("id,value\n1,fixture\n", encoding="utf-8")

    reference = build_fixture_reference(fixture, "fixture.sample", "0.1.0")

    assert reference.as_tuple() == (
        "fixture.sample",
        "0.1.0",
        "622aa93bd19fc2d4d6163edd26631edba5df379574feba07dab62bc822254f17",
    )

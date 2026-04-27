from __future__ import annotations

from dataclasses import dataclass

PANEL_REQUIRED_COLUMNS = (
    "person_id",
    "household_id",
    "wave",
    "country",
    "weights",
    "outcomes",
    "treatments",
    "attrition_metadata",
)


@dataclass(frozen=True, slots=True)
class PanelSchema:
    name: str = "longitudinal_panel_v0"
    person_key: str = "person_id"
    household_key: str = "household_id"
    wave_key: str = "wave"
    country_key: str = "country"
    weight_column: str = "weights"
    outcomes_column: str = "outcomes"
    treatments_column: str = "treatments"
    attrition_column: str = "attrition_metadata"

    def required_columns(self) -> tuple[str, ...]:
        return PANEL_REQUIRED_COLUMNS


def panel_query_keys() -> dict[str, tuple[str, ...]]:
    return {
        "person_level": ("person_id", "wave"),
        "wave_level": ("country", "wave"),
        "household_level": ("household_id", "wave"),
    }

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True, slots=True)
class PanderaColumnSpec:
    name: str
    dtype: str
    nullable: bool = False


@dataclass(frozen=True, slots=True)
class PanderaSchemaSpec:
    name: str
    table_stage: Literal["staged", "harmonized", "feature"]
    columns: tuple[PanderaColumnSpec, ...]

    def required_columns(self) -> set[str]:
        return {column.name for column in self.columns if not column.nullable}


STAGED_TABLE_SCHEMA = PanderaSchemaSpec(
    name="staged_table_schema",
    table_stage="staged",
    columns=(
        PanderaColumnSpec("canonical_dataset_name", "str"),
        PanderaColumnSpec("dataset_version", "str"),
        PanderaColumnSpec("source_row_id", "str"),
        PanderaColumnSpec("source_payload", "object"),
    ),
)

HARMONIZED_TABLE_SCHEMA = PanderaSchemaSpec(
    name="harmonized_table_schema",
    table_stage="harmonized",
    columns=(
        PanderaColumnSpec("canonical_dataset_name", "str"),
        PanderaColumnSpec("dataset_version", "str"),
        PanderaColumnSpec("codebook_mapping_ref", "str"),
        PanderaColumnSpec("quality_profile_ref", "str"),
    ),
)

FEATURE_TABLE_SCHEMA = PanderaSchemaSpec(
    name="feature_table_schema",
    table_stage="feature",
    columns=(
        PanderaColumnSpec("dataset_reference", "str"),
        PanderaColumnSpec("canonical_dataset_name", "str", nullable=True),
        PanderaColumnSpec("feature_name", "str", nullable=True),
    ),
)

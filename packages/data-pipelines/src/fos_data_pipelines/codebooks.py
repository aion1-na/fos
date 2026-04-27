from __future__ import annotations

from pathlib import Path

import yaml
from pydantic import BaseModel, ConfigDict, Field


class CodebookField(BaseModel):
    model_config = ConfigDict(frozen=True)

    source_field: str = Field(min_length=1)
    original_label: str = Field(min_length=1)
    canonical_name: str = Field(min_length=1)
    data_type: str = Field(min_length=1)


class Codebook(BaseModel):
    model_config = ConfigDict(frozen=True)

    version: str = Field(min_length=1)
    canonical_dataset_name: str = Field(min_length=1)
    fields: tuple[CodebookField, ...]

    @property
    def source_to_canonical(self) -> dict[str, str]:
        return {field.source_field: field.canonical_name for field in self.fields}

    @property
    def original_labels(self) -> dict[str, str]:
        return {field.canonical_name: field.original_label for field in self.fields}


def load_codebook(path: Path) -> Codebook:
    content = yaml.safe_load(path.read_text(encoding="utf-8"))
    return Codebook.model_validate(content)

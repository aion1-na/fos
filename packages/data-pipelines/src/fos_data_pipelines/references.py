from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path


@dataclass(frozen=True, slots=True)
class DatasetReference:
    canonical_dataset_name: str
    version: str
    content_hash: str

    def as_tuple(self) -> tuple[str, str, str]:
        return (self.canonical_dataset_name, self.version, self.content_hash)


def build_fixture_reference(path: Path, canonical_dataset_name: str, version: str) -> DatasetReference:
    content = path.read_bytes()
    return DatasetReference(
        canonical_dataset_name=canonical_dataset_name,
        version=version,
        content_hash=sha256(content).hexdigest(),
    )

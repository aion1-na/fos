from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class OccupationCrosswalk:
    version: str
    rows: tuple[dict[str, str], ...]

    def source_codes(self) -> tuple[dict[str, str], ...]:
        return tuple(
            {
                "soc_code": row["soc_code"],
                "onet_soc_code": row["onet_soc_code"],
                "census_occ_code": row["census_occ_code"],
                "source_label": row["source_label"],
                "canonical_occupation_code": row["canonical_occupation_code"],
            }
            for row in self.rows
        )

    def soc_to_onet(self, soc_code: str) -> str | None:
        for row in self.rows:
            if row["soc_code"] == soc_code:
                return row["onet_soc_code"]
        return None

    def onet_to_soc(self, onet_soc_code: str) -> str | None:
        for row in self.rows:
            if row["onet_soc_code"] == onet_soc_code and row["reversible"] == "true":
                return row["soc_code"]
        return None

    def census_to_canonical(self, census_occ_code: str) -> str | None:
        for row in self.rows:
            if row["census_occ_code"] == census_occ_code:
                return row["canonical_occupation_code"]
        return None


def load_crosswalk(path: Path, version: str = "0.1") -> OccupationCrosswalk:
    rows = tuple(csv.DictReader(path.read_text(encoding="utf-8").splitlines()))
    return OccupationCrosswalk(version=version, rows=rows)

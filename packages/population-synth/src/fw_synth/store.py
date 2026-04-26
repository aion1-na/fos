from __future__ import annotations

from pathlib import Path
from typing import BinaryIO

import fsspec


class SynthStore:
    def __init__(self, base_url: str) -> None:
        self.base_url = base_url.rstrip("/")
        self.fs, self.base_path = fsspec.core.url_to_fs(self.base_url)

    def path(self, *parts: str) -> str:
        return "/".join([self.base_path, *[part.strip("/") for part in parts]])

    def mkdir(self, path: str) -> None:
        self.fs.makedirs(path, exist_ok=True)

    def open(self, path: str, mode: str) -> BinaryIO:
        parent = str(Path(path).parent)
        if any(flag in mode for flag in ("w", "a", "+")):
            self.mkdir(parent)
        return self.fs.open(path, mode)

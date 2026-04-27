from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import TypeVar

from fos_data_pipelines.models import ConnectorConfig, RawArtifact
from fos_data_pipelines.raw_zone import RawZone

T = TypeVar("T", bound=Callable[..., object])


def asset(function: T) -> T:
    """Dependency-free stand-in for Dagster's asset decorator.

    The function shape is stable for Sprint 01. Adding Dagster should replace
    only this decorator import, not the connector or raw landing contract.
    """

    setattr(function, "__fos_asset__", True)
    return function


@asset
def land_raw_fixture(source_path: Path, config: ConnectorConfig, raw_zone: RawZone) -> RawArtifact:
    return raw_zone.land_file(source_path, config).artifact

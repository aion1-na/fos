from __future__ import annotations

from fos_data_service.app import health, list_datasets


def test_health_is_metadata_only() -> None:
    assert health() == {"status": "ok", "service": "data-service"}


def test_dataset_listing_uses_request_status_stubs() -> None:
    datasets = list_datasets()["datasets"]
    assert datasets
    assert all(dataset["access_status"] == "request_status_stub" for dataset in datasets)

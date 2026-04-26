from fos_api.main import health


def test_health() -> None:
    assert health() == {"status": "ok", "version": "0.1.0", "packs": []}

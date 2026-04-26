from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_openapi_schema_and_client_are_generated() -> None:
    schema_path = ROOT / "packages" / "contracts" / "dist" / "api" / "openapi.json"
    client_js = ROOT / "packages" / "contracts" / "dist" / "api" / "client.js"
    client_dts = ROOT / "packages" / "contracts" / "dist" / "api" / "client.d.ts"

    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    assert schema["openapi"].startswith("3.")
    assert "/health" in schema["paths"]
    assert "/runs/{run_id}/brief" in schema["paths"]
    assert "/scenarios/{scenario_id}/invalidation-preview" in schema["paths"]

    js_source = client_js.read_text(encoding="utf-8")
    dts_source = client_dts.read_text(encoding="utf-8")
    assert "API_CLIENT_VERSION = \"0.1.0\"" in js_source
    assert "function getHealth" in js_source
    assert "function postRunsByRunIdBrief" in js_source
    assert "declare function postScenariosByScenarioIdDryRun" in dts_source


def test_contracts_package_publishes_api_client_export() -> None:
    package_json = json.loads(
        (ROOT / "packages" / "contracts" / "package.json").read_text(encoding="utf-8")
    )
    exports = package_json["exports"]
    assert exports["./api"]["types"] == "./dist/api/client.d.ts"
    assert exports["./api"]["import"] == "./dist/api/client.js"
    assert exports["./api/openapi.json"]["default"] == "./dist/api/openapi.json"

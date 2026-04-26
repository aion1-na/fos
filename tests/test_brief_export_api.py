from __future__ import annotations

import json
import subprocess
import sys
import tarfile
import zipfile
from io import BytesIO
from pathlib import Path

import pytest
from fastapi import HTTPException

from fos_api.main import (
    BriefRequest,
    generate_brief,
    get_brief,
    list_brief_versions,
)


def _brief_request() -> BriefRequest:
    return BriefRequest(
        scenario_id="scenario-brief",
        findings=["Finding"],
        assumptions=["Assumption"],
        uncertainty=["Uncertainty"],
        evidence_trail=["income-security-001"],
        validation_status="passed",
        citation_ids=["income-security-001"],
    )


def test_brief_rejects_draft_and_missing_sections() -> None:
    with pytest.raises(HTTPException, match="Draft runs cannot produce briefs"):
        generate_brief("run_draft_001", _brief_request())

    with pytest.raises(HTTPException, match="findings"):
        generate_brief("run_standard_001", _brief_request().model_copy(update={"findings": []}))


def test_brief_exports_all_formats_and_versions() -> None:
    brief = generate_brief("run_standard_001", _brief_request())

    assert brief["version"] >= 1
    versions = list_brief_versions("run_standard_001")["versions"]
    assert any(version["id"] == brief["id"] for version in versions)

    json_export = get_brief("run_standard_001", format="json")
    assert json.loads(json_export.body)["id"] == brief["id"]

    pdf_export = get_brief("run_standard_001", format="pdf")
    assert pdf_export.body.startswith(b"%PDF")

    docx_export = get_brief("run_standard_001", format="docx")
    with zipfile.ZipFile(BytesIO(docx_export.body)) as docx:
        assert "word/document.xml" in docx.namelist()

    bundle_export = get_brief("run_standard_001", format="bundle")
    with tarfile.open(fileobj=BytesIO(bundle_export.body), mode="r:gz") as bundle:
        assert {"brief.json", "brief.sig"} <= set(bundle.getnames())


def test_reproducibility_manifest_reruns_identical_kpi_outputs() -> None:
    brief = generate_brief("run_repro", _brief_request())
    manifest = brief["reproducibility_manifest"]
    script = f"""
import json
from fos_api.main import _simulation_run_artifact
manifest = json.loads({json.dumps(manifest)!r})
artifact = _simulation_run_artifact(manifest["run_id"])
print(json.dumps(artifact["manifest"]["kpi_outputs"], sort_keys=True))
"""
    output = subprocess.check_output([sys.executable, "-c", script], text=True)

    assert json.loads(output) == manifest["kpi_outputs"]


def test_pack_brief_templates_exist_and_docx_opens() -> None:
    template_dir = Path("packs/flourishing/render")

    assert (template_dir / "brief_template.html").exists()
    with zipfile.ZipFile(template_dir / "brief_template.docx") as docx:
        assert "word/document.xml" in docx.namelist()

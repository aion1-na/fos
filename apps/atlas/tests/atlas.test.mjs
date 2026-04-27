import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";

test("atlas has no runtime credential defaults", () => {
  assert.equal(process.env.ATLAS_REAL_CREDENTIAL, undefined);
});

test("atlas dataset directory source exposes required metadata", () => {
  const source = readFileSync(new URL("../lib/datasets.ts", import.meta.url), "utf-8");
  for (const required of [
    "canonicalDatasetName",
    "version",
    "license",
    "contentHash",
    "fetchTimestamp",
    "cardLink",
  ]) {
    assert.match(source, new RegExp(required));
  }
  assert.match(source, /acs_ipums/);
  assert.match(source, /onet/);
  assert.match(source, /bls_oews/);
});

test("atlas ai exposure gallery exposes side-by-side measures and quartiles", () => {
  const page = readFileSync(new URL("../app/ai-exposure/page.tsx", import.meta.url), "utf-8");
  const source = readFileSync(
    new URL("../lib/ai-exposure/measures.ts", import.meta.url),
    "utf-8",
  );
  assert.match(page, /Eloundou/);
  assert.match(page, /Felten/);
  assert.match(page, /Divergence/);
  assert.match(page, /Exposure quartiles/);
  assert.match(source, /disagreementLevel/);
  assert.match(source, /age_18_34/);
  assert.match(source, /geography/);
});

test("atlas gfs view labels wave 1 as cross-sectional research-grade", () => {
  const page = readFileSync(new URL("../app/gfs/page.tsx", import.meta.url), "utf-8");
  const source = readFileSync(new URL("../lib/gfs/wave1.ts", import.meta.url), "utf-8");
  assert.match(source, /cross-sectional and research-grade/);
  assert.match(source, /not prospective forecasting/);
  assert.match(page, /Country comparison/);
  assert.match(page, /Demographic cuts/);
  assert.match(page, /weighted mean/);
});

test("atlas backtest viewer exposes gate and slices", () => {
  const page = readFileSync(new URL("../app/backtests/page.tsx", import.meta.url), "utf-8");
  const source = readFileSync(new URL("../lib/backtests/anchors.ts", import.meta.url), "utf-8");
  assert.match(page, /Backtest anchors/);
  assert.match(page, /Geography and demographic slices/);
  assert.match(source, /china_shock_backtest_v0\.1/);
  assert.match(source, /fail-closed/);
  assert.match(source, /robotExposure/);
});

test("atlas evidence viewer traces claim to provenance", () => {
  const page = readFileSync(new URL("../app/evidence/page.tsx", import.meta.url), "utf-8");
  const source = readFileSync(new URL("../lib/evidence/claims.ts", import.meta.url), "utf-8");
  assert.match(page, /Evidence forest plot/);
  assert.match(page, /Risk of bias/);
  assert.match(page, /Confidence/);
  assert.match(source, /advisor_reviewed/);
  assert.match(source, /draft/);
  assert.match(source, /datasetCard/);
  assert.match(source, /provenanceManifest/);
});

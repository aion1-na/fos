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

test("atlas public view excludes gated records and shows transparency fields", () => {
  const page = readFileSync(new URL("../app/public/page.tsx", import.meta.url), "utf-8");
  const source = readFileSync(new URL("../lib/access/public.ts", import.meta.url), "utf-8");
  assert.match(page, /Public transparency subset/);
  assert.match(page, /Tier/);
  assert.match(page, /Limitations/);
  assert.match(page, /Provenance/);
  assert.match(source, /publicAtlasDatasets/);
  assert.match(source, /restricted_data_access/);
  assert.match(source, /license_constrained/);
});

test("atlas admin exposes tier2 dua status outside public view", () => {
  const page = readFileSync(new URL("../app/admin/tier2/page.tsx", import.meta.url), "utf-8");
  const source = readFileSync(new URL("../lib/admin/tier2.ts", import.meta.url), "utf-8");
  const publicSource = readFileSync(new URL("../lib/access/public.ts", import.meta.url), "utf-8");
  assert.match(page, /Tier 2 DUA dashboard/);
  assert.match(page, /Access requests/);
  assert.match(source, /secureCompartment/);
  assert.match(source, /not_approved/);
  assert.doesNotMatch(publicSource, /secureCompartment/);
});

test("atlas search emits citations across cards codebooks and claims", () => {
  const page = readFileSync(new URL("../app/search/page.tsx", import.meta.url), "utf-8");
  const source = readFileSync(new URL("../lib/search/citations.ts", import.meta.url), "utf-8");
  assert.match(page, /Search and citations/);
  assert.match(page, /Sign-off/);
  assert.match(source, /dataset_card/);
  assert.match(source, /codebook/);
  assert.match(source, /evidence_claim/);
  assert.match(source, /searchCitations/);
});

test("atlas completeness dashboard labels tier and status", () => {
  const page = readFileSync(new URL("../app/completeness/page.tsx", import.meta.url), "utf-8");
  const source = readFileSync(new URL("../lib/completeness/tier1.ts", import.meta.url), "utf-8");
  assert.match(page, /Tier 1 completeness dashboard/);
  assert.match(page, /Production-ready/);
  assert.match(source, /tier: "Tier 1"/);
  assert.match(source, /status: "fixture"/);
  assert.match(source, /metadataComplete/);
  assert.match(source, /qualityGate/);
});

test("atlas provenance view answers upstream and downstream lineage", () => {
  const page = readFileSync(new URL("../app/provenance/page.tsx", import.meta.url), "utf-8");
  const source = readFileSync(new URL("../lib/provenance/lineage.ts", import.meta.url), "utf-8");
  assert.match(page, /Provenance lineage/);
  assert.match(page, /What fed this dataset and what consumed it/);
  assert.match(source, /features.community_context/);
  assert.match(source, /fed this dataset/);
  assert.match(source, /consumed by simulation run/);
  assert.match(source, /simulation-run-fdw-smoke/);
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

test("atlas evidence graph exposes react flow traversal and filters", () => {
  const page = readFileSync(new URL("../app/evidence-graph/page.tsx", import.meta.url), "utf-8");
  const source = readFileSync(new URL("../lib/evidence/graph.ts", import.meta.url), "utf-8");
  assert.match(page, /Evidence graph explorer/);
  assert.match(page, /React Flow/);
  assert.match(source, /reactFlowNodes/);
  assert.match(source, /reactFlowEdges/);
  assert.match(source, /construct -> evidence claim/);
  assert.match(source, /evidence claim -> citation/);
  assert.match(source, /citation -> dataset/);
  assert.match(source, /confidenceLabel/);
});

test("atlas international context exposes source and iso3 country identifiers", () => {
  const page = readFileSync(new URL("../app/international/page.tsx", import.meta.url), "utf-8");
  const source = readFileSync(new URL("../lib/international/context.ts", import.meta.url), "utf-8");
  assert.match(page, /International policy context/);
  assert.match(page, /Source country/);
  assert.match(page, /ISO3/);
  assert.match(source, /safety_net_generosity/);
  assert.match(source, /employment_rate/);
  assert.match(source, /atlas.cross_country_policy_dashboard/);
});

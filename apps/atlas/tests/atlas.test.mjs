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

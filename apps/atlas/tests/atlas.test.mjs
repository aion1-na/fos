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

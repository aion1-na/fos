import assert from "node:assert/strict";
import test from "node:test";

test("atlas has no runtime credential defaults", () => {
  assert.equal(process.env.ATLAS_REAL_CREDENTIAL, undefined);
});

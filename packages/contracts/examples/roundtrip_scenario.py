from __future__ import annotations

import json
import subprocess
from pathlib import Path

from fw_contracts import Scenario

ROOT = Path(__file__).resolve().parents[3]

scenario = Scenario(
    id="toy-scenario",
    domain_pack_id="toy-pack",
    name="Toy Scenario",
    stage_status={"frame": "ready"},
)

script = """
  import fs from "node:fs";
  import { parseScenario } from "./packages/contracts/dist/ts/index.js";
  const parsed = parseScenario(JSON.parse(fs.readFileSync(0, "utf8")));
  process.stdout.write(JSON.stringify(parsed));
"""

result = subprocess.run(
    ["node", "--input-type=module", "-e", script],
    cwd=ROOT,
    check=True,
    capture_output=True,
    input=scenario.model_dump_json(),
    text=True,
)

reloaded = Scenario.model_validate(json.loads(result.stdout))
assert reloaded == scenario
print(reloaded.model_dump_json())

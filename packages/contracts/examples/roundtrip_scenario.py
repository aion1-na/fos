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
  import { parseScenario } from "./packages/contracts/dist/ts/index.js";
  const parsed = parseScenario(JSON.parse(process.argv[1]));
  process.stdout.write(JSON.stringify(parsed));
"""

result = subprocess.run(
    ["node", "--input-type=module", "-e", script, scenario.model_dump_json()],
    cwd=ROOT,
    check=True,
    capture_output=True,
    text=True,
)

reloaded = Scenario.model_validate(json.loads(result.stdout))
assert reloaded == scenario
print(reloaded.model_dump_json())

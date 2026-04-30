#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from fw_contracts.models import CONTRACTS_VERSION
from fw_contracts.schema_export import EXPORTED_MODELS, SCHEMA_VERSION, write_schemas

ROOT = Path(__file__).resolve().parents[2]
CONTRACTS_DIR = ROOT / "packages" / "contracts"
SCHEMA_DIR = CONTRACTS_DIR / "schemas" / SCHEMA_VERSION
TS_DIR = CONTRACTS_DIR / "dist" / "ts"


EXPORTED_NAMES = set(EXPORTED_MODELS)


def schema_type(schema: dict[str, Any]) -> str:
    if "$ref" in schema:
        ref_name = schema["$ref"].split("/")[-1]
        return ref_name if ref_name in EXPORTED_NAMES else "unknown"
    if "anyOf" in schema:
        variants = [schema_type(item) for item in schema["anyOf"]]
        return " | ".join(dict.fromkeys(variants))
    if "const" in schema:
        return json.dumps(schema["const"])
    if "enum" in schema:
        return " | ".join(json.dumps(item) for item in schema["enum"])

    schema_kind = schema.get("type")
    if isinstance(schema_kind, list):
        return " | ".join(schema_type({"type": item}) for item in schema_kind)
    if schema_kind == "string":
        return "string"
    if schema_kind in {"integer", "number"}:
        return "number"
    if schema_kind == "boolean":
        return "boolean"
    if schema_kind == "array":
        item_type = schema_type(schema.get("items", {}))
        if " | " in item_type:
            item_type = f"({item_type})"
        return f"{item_type}[]"
    if schema_kind == "object":
        additional = schema.get("additionalProperties")
        if isinstance(additional, dict):
            return f"Record<string, {schema_type(additional)}>"
        return "Record<string, unknown>"
    return "unknown"


def interface_for(name: str, schema: dict[str, Any]) -> str:
    if name == "AgentState":
        return "\n".join(
            [
                "export interface AgentState<TState = unknown> {",
                "  agent_id: string;",
                "  metadata?: Record<string, unknown>;",
                "  state: TState;",
                "  step: number;",
                "}",
            ]
        )
    if name == "PopulationSnapshot":
        return "\n".join(
            [
                "export interface PopulationSnapshot<TState = unknown> {",
                "  agents?: AgentState<TState>[];",
                "  created_at?: string | unknown;",
                "  id: string;",
                "  population_id: string;",
                "  step: number;",
                "}",
            ]
        )

    properties: dict[str, Any] = schema.get("properties", {})
    required = set(schema.get("required", []))
    lines = [f"export interface {name} {{"]
    for field_name, field_schema in properties.items():
        optional = "" if field_name in required else "?"
        lines.append(f"  {field_name}{optional}: {schema_type(field_schema)};")
    lines.append("}")
    return "\n".join(lines)


def parser_for(name: str, schema: dict[str, Any]) -> str:
    required = sorted(schema.get("required", []))
    if name == "DatasetReference":
        return f"""export function parse{name}(input) {{
  const value = cloneObject(input, "{name}");
  requireFields(value, {json.dumps(required)}, "{name}");
  if (!/^[a-z0-9_][a-z0-9_.-]*$/.test(value.canonical_dataset_name)) {{
    throw new TypeError("{name}.canonical_dataset_name is invalid");
  }}
  if (!/^[a-f0-9]{{64}}$/.test(value.content_hash)) {{
    throw new TypeError("{name}.content_hash is invalid");
  }}
  return value;
}}"""
    if name == "ToolArtifactReference":
        return f"""export function parse{name}(input) {{
  const value = cloneObject(input, "{name}");
  requireFields(value, {json.dumps(required)}, "{name}");
  if (!/^[a-f0-9]{{64}}$/.test(value.content_hash)) {{
    throw new TypeError("{name}.content_hash is invalid");
  }}
  if (!Array.isArray(value.dataset_references) || value.dataset_references.length === 0) {{
    throw new TypeError("{name}.dataset_references must be nonempty");
  }}
  value.dataset_references = value.dataset_references.map(parseDatasetReference);
  return value;
}}"""
    if name == "RunDataManifest":
        return f"""export function parse{name}(input) {{
  const value = cloneObject(input, "{name}");
  requireFields(value, {json.dumps(required)}, "{name}");
  if (Array.isArray(value.dataset_references)) {{
    value.dataset_references = value.dataset_references.map(parseDatasetReference);
  }}
  for (const field of ["tool_artifacts", "graph_artifacts", "qualitative_artifacts"]) {{
    if (Array.isArray(value[field])) {{
      value[field] = value[field].map(parseToolArtifactReference);
    }}
  }}
  return value;
}}"""
    return f"""export function parse{name}(input) {{
  const value = cloneObject(input, "{name}");
  requireFields(value, {json.dumps(required)}, "{name}");
  return value;
}}"""


def write_ts(schema_map: dict[str, dict[str, Any]]) -> None:
    TS_DIR.mkdir(parents=True, exist_ok=True)
    names = list(schema_map)
    dts_parts = [
        'export declare const CONTRACTS_VERSION = "0.1.0";',
    ]
    js_parts = [
        f"export const CONTRACTS_VERSION = {json.dumps(CONTRACTS_VERSION)};",
        """
function cloneObject(input, modelName) {
  if (input === null || typeof input !== "object" || Array.isArray(input)) {
    throw new TypeError(`${modelName} must be an object`);
  }
  return JSON.parse(JSON.stringify(input));
}

function requireFields(value, fields, modelName) {
  for (const field of fields) {
    if (!(field in value)) {
      throw new TypeError(`${modelName}.${field} is required`);
    }
  }
}
""".strip(),
    ]

    for name in names:
        dts_parts.append(interface_for(name, schema_map[name]))
        if name == "AgentState":
            dts_parts.append(
                "export declare function parseAgentState<TState = unknown>(input: unknown): AgentState<TState>;"
            )
        elif name == "PopulationSnapshot":
            dts_parts.append(
                "export declare function parsePopulationSnapshot<TState = unknown>(input: unknown): PopulationSnapshot<TState>;"
            )
        else:
            dts_parts.append(
                f"export declare function parse{name}(input: unknown): {name};"
            )
        js_parts.append(parser_for(name, schema_map[name]))

    (TS_DIR / "index.d.ts").write_text("\n\n".join(dts_parts) + "\n", encoding="utf-8")
    (TS_DIR / "index.js").write_text("\n\n".join(js_parts) + "\n", encoding="utf-8")


def main() -> None:
    write_schemas(SCHEMA_DIR)
    schema_map = {
        name: json.loads(
            (SCHEMA_DIR / f"{name}.schema.json").read_text(encoding="utf-8")
        )
        for name in EXPORTED_MODELS
    }
    write_ts(schema_map)


if __name__ == "__main__":
    main()

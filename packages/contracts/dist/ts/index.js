export const CONTRACTS_VERSION = "0.1.0";

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

export function parseDatasetReference(input) {
  const value = cloneObject(input, "DatasetReference");
  requireFields(value, ["canonical_dataset_name", "content_hash", "version"], "DatasetReference");
  return value;
}

export function parseDomainPack(input) {
  const value = cloneObject(input, "DomainPack");
  requireFields(value, ["id", "name", "state_schema", "version"], "DomainPack");
  return value;
}

export function parseScenario(input) {
  const value = cloneObject(input, "Scenario");
  requireFields(value, ["domain_pack_id", "id", "name"], "Scenario");
  return value;
}

export function parseAgentState(input) {
  const value = cloneObject(input, "AgentState");
  requireFields(value, ["agent_id", "state", "step"], "AgentState");
  return value;
}

export function parsePopulation(input) {
  const value = cloneObject(input, "Population");
  requireFields(value, ["id", "scenario_id", "size"], "Population");
  return value;
}

export function parsePopulationSnapshot(input) {
  const value = cloneObject(input, "PopulationSnapshot");
  requireFields(value, ["id", "population_id", "step"], "PopulationSnapshot");
  return value;
}

export function parseSpawnSpec(input) {
  const value = cloneObject(input, "SpawnSpec");
  requireFields(value, ["count", "population_id"], "SpawnSpec");
  return value;
}

export function parseSimulationRun(input) {
  const value = cloneObject(input, "SimulationRun");
  requireFields(value, ["id", "population_id", "scenario_id", "status"], "SimulationRun");
  return value;
}

export function parseEvidenceClaim(input) {
  const value = cloneObject(input, "EvidenceClaim");
  requireFields(value, ["id", "statement"], "EvidenceClaim");
  return value;
}

export function parseValidationReport(input) {
  const value = cloneObject(input, "ValidationReport");
  requireFields(value, ["id", "simulation_run_id", "status", "suite_id"], "ValidationReport");
  return value;
}

export function parseOntologyRef(input) {
  const value = cloneObject(input, "OntologyRef");
  requireFields(value, ["id"], "OntologyRef");
  return value;
}

export function parseTransitionModel(input) {
  const value = cloneObject(input, "TransitionModel");
  requireFields(value, ["entrypoint", "id", "version"], "TransitionModel");
  return value;
}

export function parseIntervention(input) {
  const value = cloneObject(input, "Intervention");
  requireFields(value, ["id", "label"], "Intervention");
  return value;
}

export function parseValidationSuite(input) {
  const value = cloneObject(input, "ValidationSuite");
  requireFields(value, ["id"], "ValidationSuite");
  return value;
}

export function parseRenderHints(input) {
  const value = cloneObject(input, "RenderHints");
  requireFields(value, [], "RenderHints");
  return value;
}

export function parseBranchSpec(input) {
  const value = cloneObject(input, "BranchSpec");
  requireFields(value, ["id", "label"], "BranchSpec");
  return value;
}

export function parseShockSpec(input) {
  const value = cloneObject(input, "ShockSpec");
  requireFields(value, ["at_step", "id", "label"], "ShockSpec");
  return value;
}

export function parseFidelityReport(input) {
  const value = cloneObject(input, "FidelityReport");
  requireFields(value, ["level"], "FidelityReport");
  return value;
}

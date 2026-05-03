export declare const CONTRACTS_VERSION = "0.1.0";

export interface DatasetReference {
  canonical_dataset_name: string;
  content_hash: string;
  version: string;
}

export declare function parseDatasetReference(input: unknown): DatasetReference;

export interface DomainPack {
  contracts_version?: "0.1.0";
  id: string;
  name: string;
  ontology?: OntologyRef[];
  render_hints?: RenderHints;
  state_schema: Record<string, unknown>;
  transition_models?: TransitionModel[];
  validation_suites?: ValidationSuite[];
  version: string;
}

export declare function parseDomainPack(input: unknown): DomainPack;

export interface Scenario {
  branches?: BranchSpec[];
  domain_pack_id: string;
  id: string;
  interventions?: Intervention[];
  name: string;
  ontology?: OntologyRef[];
  parameters?: Record<string, unknown>;
  shocks?: ShockSpec[];
  stage_status?: Record<string, "empty" | "pending" | "ready" | "running" | "complete" | "error">;
}

export declare function parseScenario(input: unknown): Scenario;

export interface AgentState<TState = unknown> {
  agent_id: string;
  metadata?: Record<string, unknown>;
  state: TState;
  step: number;
}

export declare function parseAgentState<TState = unknown>(input: unknown): AgentState<TState>;

export interface Population {
  agent_ids?: string[];
  id: string;
  metadata?: Record<string, unknown>;
  scenario_id: string;
  size: number;
}

export declare function parsePopulation(input: unknown): Population;

export interface PopulationSnapshot<TState = unknown> {
  agents?: AgentState<TState>[];
  created_at?: string | unknown;
  id: string;
  population_id: string;
  step: number;
}

export declare function parsePopulationSnapshot<TState = unknown>(input: unknown): PopulationSnapshot<TState>;

export interface SpawnSpec {
  count: number;
  metadata?: Record<string, unknown>;
  population_id: string;
  state_seed?: Record<string, unknown>;
}

export declare function parseSpawnSpec(input: unknown): SpawnSpec;

export interface RunDataManifest {
  adapter_versions?: Record<string, string>;
  branch_id?: string | unknown;
  dataset_references?: DatasetReference[];
  graph_artifacts?: ToolArtifactReference[];
  manifest_hash?: string | unknown;
  parent_branch_id?: string | unknown;
  population_id: string;
  qualitative_artifacts?: ToolArtifactReference[];
  run_id: string;
  scenario_id: string;
  tool_artifacts?: ToolArtifactReference[];
  touched_components?: ("population_synthesis" | "transition_models" | "validation" | "adapter_artifacts")[];
}

export declare function parseRunDataManifest(input: unknown): RunDataManifest;

export interface ToolArtifactReference {
  adapter_id: string;
  artifact_id: string;
  artifact_type: "tool" | "graph" | "qualitative";
  content_hash: string;
  dataset_references: DatasetReference[];
  notes?: string;
  uri: string;
  validated_for_causal_effects?: boolean;
}

export declare function parseToolArtifactReference(input: unknown): ToolArtifactReference;

export interface SimulationRun {
  completed_at?: string | unknown;
  fidelity?: FidelityReport | unknown;
  id: string;
  outputs?: Record<string, unknown>;
  population_id: string;
  scenario_id: string;
  started_at?: string | unknown;
  status: "queued" | "running" | "succeeded" | "failed" | "cancelled";
}

export declare function parseSimulationRun(input: unknown): SimulationRun;

export interface EvidenceClaim {
  citation: string;
  comparator: string;
  confidence?: number | unknown;
  dataset_reference: DatasetReference;
  effect_size: number;
  id: string;
  metadata?: Record<string, unknown>;
  outcome_domain: string;
  review_status: "draft" | "advisor_reviewed" | "rejected" | "superseded";
  risk_of_bias: "low" | "medium" | "high";
  scenario_id: string;
  source_id: string;
  source_uri?: string | unknown;
  statement: string;
  target_population: string;
  transition_model_id: string;
  transportability: "low" | "medium" | "high";
  treatment: string;
  uncertainty: number;
}

export declare function parseEvidenceClaim(input: unknown): EvidenceClaim;

export interface ValidationReport {
  claims?: EvidenceClaim[];
  errors?: string[];
  id: string;
  metrics?: Record<string, unknown>;
  simulation_run_id: string;
  status: "passed" | "failed" | "warning";
  suite_id: string;
}

export declare function parseValidationReport(input: unknown): ValidationReport;

export interface OntologyRef {
  id: string;
  uri?: string | unknown;
  version?: string | unknown;
}

export declare function parseOntologyRef(input: unknown): OntologyRef;

export interface TransitionModel {
  entrypoint: string;
  id: string;
  parameters_schema?: Record<string, unknown>;
  version: string;
}

export declare function parseTransitionModel(input: unknown): TransitionModel;

export interface Intervention {
  ends_at_step?: number | unknown;
  id: string;
  label: string;
  parameters?: Record<string, unknown>;
  starts_at_step?: number | unknown;
}

export declare function parseIntervention(input: unknown): Intervention;

export interface ValidationSuite {
  checks?: string[];
  id: string;
  parameters?: Record<string, unknown>;
}

export declare function parseValidationSuite(input: unknown): ValidationSuite;

export interface RenderHints {
  encodings?: Record<string, unknown>;
  preferred_views?: string[];
}

export declare function parseRenderHints(input: unknown): RenderHints;

export interface BranchSpec {
  id: string;
  label: string;
  parameters?: Record<string, unknown>;
  parent_id?: string | unknown;
}

export declare function parseBranchSpec(input: unknown): BranchSpec;

export interface ShockSpec {
  at_step: number;
  id: string;
  label: string;
  parameters?: Record<string, unknown>;
}

export declare function parseShockSpec(input: unknown): ShockSpec;

export interface FidelityReport {
  level: "low" | "medium" | "high";
  metrics?: Record<string, unknown>;
  notes?: string[];
}

export declare function parseFidelityReport(input: unknown): FidelityReport;

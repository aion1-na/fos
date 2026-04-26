import hashlib
import json
from os import getenv
from typing import Literal

from fastapi import FastAPI, HTTPException, WebSocket
from pydantic import BaseModel, Field

from fos_api import __version__

app = FastAPI(title="FOS API")


class SpawnSpecRequest(BaseModel):
    population_id: str = "pop_young_adult_5000"
    count: int = Field(default=5000, ge=1, le=50000)
    pack_id: str = "flourishing"
    seed: int = 88


class CohortFilter(BaseModel):
    population_id: str
    field: str
    operator: Literal[">=", "<=", "="]
    value: str | int | float | bool


class CohortRequest(BaseModel):
    population_id: str
    filters: list[CohortFilter] = Field(default_factory=list)


class RunSpecRequest(BaseModel):
    branch: str = "baseline"
    seeds: int = Field(default=30, ge=1, le=500)
    horizon_months: int = Field(default=120, ge=1, le=600)
    agent_count: int = Field(default=5000, ge=1, le=100000)
    runtime_tier: Literal["draft", "standard", "audit"] = "standard"
    evidence_mode: Literal["fixture-only", "pack-default"] = "pack-default"
    validation_gates: bool = True
    draft: bool = False
    kpis: list[str] = Field(default_factory=lambda: ["happiness", "health", "meaning"])
    shocks: list[str] = Field(default_factory=list)


class ProposedEditRequest(BaseModel):
    field: str
    value: str | int | float | bool | list[str]


POPULATIONS: dict[str, dict[str, object]] = {}
COHORTS: dict[str, dict[str, object]] = {}
STREAM_FRAMES: dict[str, list[dict[str, object]]] = {}


@app.get("/health")
def health() -> dict[str, object]:
    return {
        "status": "ok",
        "version": getenv("FOS_VERSION", __version__),
        "packs": [],
    }


def _stable_digest(payload: object) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _invalidated_artifacts(scenario_id: str, edit: ProposedEditRequest) -> list[dict[str, str]]:
    return [
        {
            "id": f"population_snapshot:{scenario_id}:latest",
            "stage": "Population",
            "reason": f"{edit.field} changes the target population or its content-address.",
            "regenerationCost": "45s synth + 12MB artifact",
        },
        {
            "id": f"simulation_run:{scenario_id}:latest",
            "stage": "Execute",
            "reason": "Run outputs depend on saved configuration, branch, seeds, shocks, and horizon.",
            "regenerationCost": "2m 10s runtime + 34MB artifact",
        },
        {
            "id": f"validation_report:{scenario_id}:latest",
            "stage": "Validate",
            "reason": "Validation metrics depend on the run artifact sequence.",
            "regenerationCost": "35s validation",
        },
        {
            "id": f"brief:{scenario_id}:published_candidate",
            "stage": "Brief",
            "reason": "Published findings cannot point at stale validation artifacts.",
            "regenerationCost": "Manual review required",
        },
    ]


def _stream_frames(simulation_id: str) -> list[dict[str, object]]:
    frames = STREAM_FRAMES.get(simulation_id)
    if frames is not None:
        return frames
    frames = []
    for tick in range(12):
        frames.extend(
            [
                {
                    "offset": len(frames),
                    "type": "agent_update_count",
                    "tick": tick,
                    "count": 500 + tick * 37,
                },
                {
                    "offset": len(frames) + 1,
                    "type": "event_log_entry",
                    "tick": tick,
                    "message": f"Committed tick {tick}",
                },
                {
                    "offset": len(frames) + 2,
                    "type": "kpi_tick",
                    "tick": tick,
                    "kpis": {
                        "happiness": round(0.55 + tick * 0.004, 4),
                        "health": round(0.61 + tick * 0.002, 4),
                        "meaning": round(0.58 + tick * 0.003, 4),
                    },
                },
            ]
        )
    frames.append(
        {
            "offset": len(frames),
            "type": "event_log_entry",
            "tick": 12,
            "message": "Run complete",
        }
    )
    STREAM_FRAMES[simulation_id] = frames
    return frames


def _agent(index: int, population_id: str) -> dict[str, object]:
    institutions = ["Employer", "Healthcare", "School", "Civic", "Training"]
    employment = ["student", "employed", "caregiver", "retired"]
    return {
        "id": f"{population_id}-{index:05d}",
        "institutionId": institutions[index % len(institutions)].lower(),
        "fields": {
            "age": 18 + index % 55,
            "income_percentile": round(((index * 37) % 100) / 100, 2),
            "employment_status": employment[index % len(employment)],
            "network_degree": 2 + index % 18,
            "institution_membership": institutions[index % len(institutions)],
        },
    }


def _population_from_spec(spec: SpawnSpecRequest) -> dict[str, object]:
    agents = [_agent(index, spec.population_id) for index in range(spec.count)]
    return {
        "id": spec.population_id,
        "pack_id": spec.pack_id,
        "count": spec.count,
        "seed": spec.seed,
        "agents": agents,
        "composition": {
            "attributes": [
                {"key": "age", "kind": "continuous", "ks": 0.018, "status": "green"},
                {"key": "employment_status", "kind": "categorical", "ks": 0.041, "status": "amber"},
                {"key": "income_percentile", "kind": "continuous", "ks": 0.033, "status": "green"},
            ]
        },
    }


@app.post("/populations")
def create_population(spec: SpawnSpecRequest) -> dict[str, object]:
    population = _population_from_spec(spec)
    POPULATIONS[spec.population_id] = population
    return {
        "id": population["id"],
        "count": population["count"],
        "pack_id": population["pack_id"],
    }


@app.get("/populations/{population_id}/composition")
def get_population_composition(population_id: str) -> dict[str, object]:
    population = POPULATIONS.get(population_id)
    if population is None:
        population = _population_from_spec(SpawnSpecRequest(population_id=population_id))
        POPULATIONS[population_id] = population
    return {
        "id": population_id,
        "count": population["count"],
        "composition": population["composition"],
    }


@app.get("/populations/{population_id}/agents/{agent_id}")
def get_agent(population_id: str, agent_id: str) -> dict[str, object]:
    population = POPULATIONS.get(population_id)
    if population is None:
        raise HTTPException(status_code=404, detail="population not found")
    for agent in population["agents"]:
        if isinstance(agent, dict) and agent.get("id") == agent_id:
            return agent
    raise HTTPException(status_code=404, detail="agent not found")


def _matches(agent: dict[str, object], cohort_filter: CohortFilter) -> bool:
    fields = agent.get("fields")
    if not isinstance(fields, dict):
        return False
    value = fields.get(cohort_filter.field)
    if isinstance(value, int | float) and isinstance(cohort_filter.value, int | float):
        if cohort_filter.operator == ">=":
            return value >= cohort_filter.value
        if cohort_filter.operator == "<=":
            return value <= cohort_filter.value
    return value == cohort_filter.value


@app.post("/cohorts")
def create_cohort(request: CohortRequest) -> dict[str, object]:
    population = POPULATIONS.get(request.population_id)
    if population is None:
        population = _population_from_spec(SpawnSpecRequest(population_id=request.population_id))
        POPULATIONS[request.population_id] = population
    agent_ids = [
        str(agent["id"])
        for agent in population["agents"]
        if isinstance(agent, dict) and all(_matches(agent, cohort_filter) for cohort_filter in request.filters)
    ]
    payload = {
        "target_population": request.population_id,
        "filters": [cohort_filter.model_dump(mode="json") for cohort_filter in request.filters],
        "agent_ids": sorted(agent_ids),
    }
    cohort = {
        "id": f"cohort_{_stable_digest(payload)[:24]}",
        **payload,
    }
    COHORTS[str(cohort["id"])] = cohort
    return cohort


@app.get("/cohorts")
def list_cohorts() -> dict[str, object]:
    return {"cohorts": list(COHORTS.values())}


@app.post("/scenarios/{scenario_id}/dry-run")
def dry_run_scenario(scenario_id: str, request: RunSpecRequest) -> dict[str, object]:
    errors: list[str] = []
    if request.draft:
        if request.agent_count != 500:
            errors.append("draft runs must use 500 agents")
        if request.horizon_months != 12:
            errors.append("draft runs must use a 12-month horizon")
        if request.seeds != 5:
            errors.append("draft runs must use 5 seeds")
        if request.evidence_mode != "fixture-only":
            errors.append("draft runs must use fixture-only evidence")
        if request.validation_gates:
            errors.append("draft runs must disable validation gates")
    estimate_seconds = 18 if request.draft else max(30, request.seeds * request.horizon_months // 12)
    return {
        "scenario_id": scenario_id,
        "valid": not errors,
        "errors": errors,
        "artifact_count": 2 if request.draft else 5,
        "estimate_seconds": estimate_seconds,
    }


@app.post("/scenarios/{scenario_id}/invalidation-preview")
def invalidation_preview(scenario_id: str, request: ProposedEditRequest) -> dict[str, object]:
    return {
        "scenario_id": scenario_id,
        "invalidated_artifacts": _invalidated_artifacts(scenario_id, request),
    }


@app.websocket("/simulations/{simulation_id}/stream")
async def simulation_stream(websocket: WebSocket, simulation_id: str) -> None:
    await websocket.accept()
    raw_offset = websocket.query_params.get("offset", "0")
    try:
        offset = max(0, int(raw_offset))
    except ValueError:
        offset = 0
    for frame in _stream_frames(simulation_id)[offset:]:
        await websocket.send_json(frame)
    await websocket.close()


def main() -> None:
    import uvicorn

    uvicorn.run("fos_api.main:app", host="0.0.0.0", port=8000, reload=True)

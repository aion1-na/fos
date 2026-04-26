import hashlib
import json
from os import getenv
from typing import Literal

from fastapi import FastAPI, HTTPException
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


POPULATIONS: dict[str, dict[str, object]] = {}
COHORTS: dict[str, dict[str, object]] = {}


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


def main() -> None:
    import uvicorn

    uvicorn.run("fos_api.main:app", host="0.0.0.0", port=8000, reload=True)

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import numpy as np
from fw_contracts import (
    CONTRACTS_VERSION,
    DomainPack,
    Intervention,
    OntologyRef,
    RenderHints,
    SpawnSpec,
    TransitionModel,
    ValidationSuite,
    assert_contracts_version,
)
from pydantic import BaseModel, Field

PACK_ID = "toy-sir"
PACK_VERSION = "0.1.0"
DEFAULT_BETA = 0.28
DEFAULT_RECOVERY_DAYS = 10

SirStatus = Literal["S", "I", "R"]


class ToySirState(BaseModel):
    status: SirStatus
    days_since_infection: int = Field(ge=0)
    age: int = Field(ge=0)


@dataclass(frozen=True)
class ToySirAgent:
    agent_id: str
    state: ToySirState


VACCINATION_INTERVENTION = Intervention(
    id="vaccination",
    label="Vaccination",
    parameters={
        "eligible_age_min": 18,
        "target_status": "S",
        "result_status": "R",
    },
)


def _state_schema() -> dict[str, object]:
    return {
        "type": "object",
        "additionalProperties": False,
        "required": ["status", "days_since_infection", "age"],
        "properties": {
            "status": {"enum": ["S", "I", "R"]},
            "days_since_infection": {"type": "integer", "minimum": 0},
            "age": {"type": "integer", "minimum": 0},
        },
    }


def _pack() -> DomainPack:
    pack = DomainPack(
        id=PACK_ID,
        name="Toy SIR",
        version=PACK_VERSION,
        contracts_version=CONTRACTS_VERSION,
        state_schema=_state_schema(),
        ontology=[
            OntologyRef(id="susceptible"),
            OntologyRef(id="infectious"),
            OntologyRef(id="recovered"),
            OntologyRef(id=VACCINATION_INTERVENTION.id),
        ],
        transition_models=[
            TransitionModel(
                id="infection",
                version="0.1.0",
                entrypoint="fos_pack_toy_sir.pack.vectorized_infection",
                parameters_schema={
                    "type": "object",
                    "properties": {
                        "beta": {"type": "number", "minimum": 0},
                    },
                },
            ),
            TransitionModel(
                id="recovery",
                version="0.1.0",
                entrypoint="fos_pack_toy_sir.pack.vectorized_recovery",
                parameters_schema={
                    "type": "object",
                    "properties": {
                        "recovery_days": {"type": "integer", "minimum": 1},
                    },
                },
            ),
        ],
        validation_suites=[
            ValidationSuite(
                id="sir-curve-mse",
                checks=["prevalence_curve_mse"],
                parameters={
                    "agent_count": 1000,
                    "ticks": 100,
                    "mse_threshold": 0.05,
                    "beta": DEFAULT_BETA,
                    "recovery_days": DEFAULT_RECOVERY_DAYS,
                },
            )
        ],
        render_hints=RenderHints(
            preferred_views=["compartment_curve", "agent_grid"],
            encodings={
                "color_ramp": {
                    "S": "#2f80ed",
                    "I": "#d64545",
                    "R": "#27ae60",
                },
                "glyphs": {
                    "S": "circle",
                    "I": "diamond",
                    "R": "square",
                },
            },
        ),
    )
    assert_contracts_version(pack.contracts_version)
    return pack


PACK = _pack()


def build_pack() -> DomainPack:
    return PACK.model_copy(deep=True)


def spawn_population(spec: SpawnSpec) -> list[ToySirAgent]:
    initial_infected = int(spec.state_seed.get("initial_infected", 10))
    adult_share = float(spec.state_seed.get("adult_share", 0.8))
    if initial_infected < 0 or initial_infected > spec.count:
        raise ValueError("initial_infected must be between 0 and count")
    if adult_share < 0 or adult_share > 1:
        raise ValueError("adult_share must be between 0 and 1")

    adult_cutoff = round(spec.count * adult_share)
    agents: list[ToySirAgent] = []
    for index in range(spec.count):
        state = ToySirState(
            status="I" if index < initial_infected else "S",
            days_since_infection=1 if index < initial_infected else 0,
            age=35 if index < adult_cutoff else 12,
        )
        agents.append(ToySirAgent(agent_id=f"{spec.population_id}-{index}", state=state))
    return agents


def spawn_population_state(spec: SpawnSpec) -> dict[str, list[int] | list[str]]:
    agents = spawn_population(spec)
    return {
        "status": [agent.state.status for agent in agents],
        "days_since_infection": [
            agent.state.days_since_infection for agent in agents
        ],
        "age": [agent.state.age for agent in agents],
    }


def apply_vaccination(
    agents: list[ToySirAgent],
    intervention: Intervention = VACCINATION_INTERVENTION,
) -> list[ToySirAgent]:
    eligible_age = int(intervention.parameters.get("eligible_age_min", 18))
    vaccinated: list[ToySirAgent] = []
    for agent in agents:
        if agent.state.status == "S" and agent.state.age >= eligible_age:
            vaccinated.append(
                ToySirAgent(
                    agent_id=agent.agent_id,
                    state=ToySirState(
                        status="R",
                        days_since_infection=0,
                        age=agent.state.age,
                    ),
                )
            )
        else:
            vaccinated.append(agent)
    return vaccinated


def apply_infection(
    agents: list[ToySirAgent],
    beta: float = DEFAULT_BETA,
) -> list[ToySirAgent]:
    total = len(agents)
    if total == 0:
        return []
    infectious = sum(1 for agent in agents if agent.state.status == "I")
    susceptible_indexes = [
        index for index, agent in enumerate(agents) if agent.state.status == "S"
    ]
    new_infections = round(len(susceptible_indexes) * beta * infectious / total)
    infection_mask = [False] * total
    for index in susceptible_indexes[:new_infections]:
        infection_mask[index] = True

    next_agents: list[ToySirAgent] = []
    for index, agent in enumerate(agents):
        if infection_mask[index]:
            next_agents.append(
                ToySirAgent(
                    agent_id=agent.agent_id,
                    state=ToySirState(
                        status="I",
                        days_since_infection=1,
                        age=agent.state.age,
                    ),
                )
            )
        else:
            next_agents.append(agent)
    return next_agents


def vectorized_infection(
    fields: dict[str, np.ndarray],
    rng: np.random.Generator,
    parameters: dict[str, object],
    tick: int,
) -> dict[str, object]:
    del rng, tick
    beta = float(parameters.get("beta", DEFAULT_BETA))
    status = fields["status"]
    total = status.shape[0]
    if total == 0:
        return {"mode": "replace", "fields": {}, "masks": {}, "kpis": {"prevalence": 0.0}}

    infectious = status == "I"
    susceptible = status == "S"
    infection_probability = beta * float(np.count_nonzero(infectious)) / total
    susceptible_rank = np.cumsum(susceptible) - 1
    infection_count = int(round(float(np.count_nonzero(susceptible)) * infection_probability))
    infection_mask = susceptible & (susceptible_rank < infection_count)

    next_status = status.copy()
    next_days = fields["days_since_infection"].copy()
    next_status[infection_mask] = "I"
    next_days[infection_mask] = 1
    next_prevalence = float(np.count_nonzero(next_status == "I") / total)
    return {
        "mode": "replace",
        "fields": {
            "status": next_status,
            "days_since_infection": next_days,
        },
        "masks": {
            "status": infection_mask,
            "days_since_infection": infection_mask,
        },
        "kpis": {
            "new_cases": float(np.count_nonzero(infection_mask)),
            "prevalence": next_prevalence,
        },
    }


def vectorized_recovery(
    fields: dict[str, np.ndarray],
    rng: np.random.Generator,
    parameters: dict[str, object],
    tick: int,
) -> dict[str, object]:
    del rng, tick
    recovery_days = int(parameters.get("recovery_days", DEFAULT_RECOVERY_DAYS))
    status = fields["status"]
    days = fields["days_since_infection"]
    infectious = status == "I"
    incremented_days = days.copy()
    incremented_days[infectious] = incremented_days[infectious] + 1
    recovery_mask = infectious & (incremented_days >= recovery_days)
    stay_infectious_mask = infectious & ~recovery_mask

    next_status = status.copy()
    next_days = days.copy()
    next_status[recovery_mask] = "R"
    next_days[recovery_mask] = 0
    next_days[stay_infectious_mask] = incremented_days[stay_infectious_mask]
    days_mask = recovery_mask | stay_infectious_mask
    total = status.shape[0]
    prevalence_value = 0.0 if total == 0 else float(np.count_nonzero(next_status == "I") / total)
    return {
        "mode": "replace",
        "fields": {
            "status": next_status,
            "days_since_infection": next_days,
        },
        "masks": {
            "status": recovery_mask,
            "days_since_infection": days_mask,
        },
        "kpis": {
            "recoveries": float(np.count_nonzero(recovery_mask)),
            "prevalence": prevalence_value,
        },
    }


def apply_recovery(
    agents: list[ToySirAgent],
    recovery_days: int = DEFAULT_RECOVERY_DAYS,
) -> list[ToySirAgent]:
    next_agents: list[ToySirAgent] = []
    for agent in agents:
        if agent.state.status != "I":
            next_agents.append(agent)
            continue
        days = agent.state.days_since_infection + 1
        if days >= recovery_days:
            state = ToySirState(status="R", days_since_infection=0, age=agent.state.age)
        else:
            state = ToySirState(
                status="I",
                days_since_infection=days,
                age=agent.state.age,
            )
        next_agents.append(ToySirAgent(agent_id=agent.agent_id, state=state))
    return next_agents


def prevalence(agents: list[ToySirAgent]) -> float:
    if not agents:
        return 0.0
    return sum(1 for agent in agents if agent.state.status == "I") / len(agents)


def simulate(
    spec: SpawnSpec,
    ticks: int,
    beta: float = DEFAULT_BETA,
    recovery_days: int = DEFAULT_RECOVERY_DAYS,
) -> list[float]:
    agents = spawn_population(spec)
    curve = [prevalence(agents)]
    for _ in range(ticks):
        agents = apply_infection(agents, beta=beta)
        agents = apply_recovery(agents, recovery_days=recovery_days)
        curve.append(prevalence(agents))
    return curve


def analytical_sir_curve(
    population_size: int,
    initial_infected: int,
    ticks: int,
    beta: float = DEFAULT_BETA,
    recovery_days: int = DEFAULT_RECOVERY_DAYS,
) -> list[float]:
    susceptible = float(population_size - initial_infected)
    infectious = float(initial_infected)
    recovered = 0.0
    gamma = 1.0 / recovery_days
    curve = [infectious / population_size]

    for _ in range(ticks):
        new_infections = beta * susceptible * infectious / population_size
        new_recoveries = gamma * infectious
        susceptible = max(0.0, susceptible - new_infections)
        infectious = max(0.0, infectious + new_infections - new_recoveries)
        recovered = min(float(population_size), recovered + new_recoveries)
        total = susceptible + infectious + recovered
        if total:
            susceptible *= population_size / total
            infectious *= population_size / total
            recovered *= population_size / total
        curve.append(infectious / population_size)
    return curve


def mean_squared_error(left: list[float], right: list[float]) -> float:
    if len(left) != len(right):
        raise ValueError("curves must have the same length")
    return sum((a - b) ** 2 for a, b in zip(left, right, strict=True)) / len(left)


def run_validation() -> dict[str, float | bool]:
    agent_count = 1000
    ticks = 100
    initial_infected = 10
    threshold = 0.05
    spec = SpawnSpec(
        population_id="toy-sir-validation",
        count=agent_count,
        state_seed={"initial_infected": initial_infected, "adult_share": 0.8},
    )
    simulated = simulate(spec, ticks=ticks)
    expected = analytical_sir_curve(
        population_size=agent_count,
        initial_infected=initial_infected,
        ticks=ticks,
    )
    mse = mean_squared_error(simulated, expected)
    return {"passed": mse < threshold, "mse": mse, "threshold": threshold}

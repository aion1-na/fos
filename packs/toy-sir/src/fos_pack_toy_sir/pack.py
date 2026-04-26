from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

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
                entrypoint="fos_pack_toy_sir.pack.apply_infection",
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
                entrypoint="fos_pack_toy_sir.pack.apply_recovery",
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
    infected_indexes = set(susceptible_indexes[:new_infections])

    next_agents: list[ToySirAgent] = []
    for index, agent in enumerate(agents):
        if index in infected_indexes:
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

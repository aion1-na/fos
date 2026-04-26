from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class FlourishingState(BaseModel):
    happiness: float = Field(ge=0.0, le=1.0)
    health: float = Field(ge=0.0, le=1.0)
    meaning: float = Field(ge=0.0, le=1.0)
    character: float = Field(ge=0.0, le=1.0)
    relationships: float = Field(ge=0.0, le=1.0)
    financial: float = Field(ge=0.0, le=1.0)
    resilience: float = Field(ge=0.0, le=1.0)
    loneliness_risk: float = Field(ge=0.0, le=1.0)
    childhood_household_income: float = Field(ge=0.0, le=1.0)
    childhood_parent_education: float = Field(ge=0.0, le=1.0)
    childhood_neighborhood_safety: float = Field(ge=0.0, le=1.0)
    childhood_health_access: float = Field(ge=0.0, le=1.0)
    childhood_food_security: float = Field(ge=0.0, le=1.0)
    childhood_housing_stability: float = Field(ge=0.0, le=1.0)
    childhood_school_quality: float = Field(ge=0.0, le=1.0)
    childhood_caregiver_support: float = Field(ge=0.0, le=1.0)
    childhood_adverse_events: int = Field(ge=0, le=12)
    childhood_social_trust: float = Field(ge=0.0, le=1.0)
    childhood_mobility_count: int = Field(ge=0, le=20)
    childhood_rurality: float = Field(ge=0.0, le=1.0)
    age: int = Field(ge=0, le=120)
    education_years: int = Field(ge=0, le=30)
    employment_status: Literal["student", "employed", "unemployed", "caregiver", "retired"]
    income_percentile: float = Field(ge=0.0, le=1.0)
    debt_burden: float = Field(ge=0.0, le=1.0)
    savings_buffer_months: float = Field(ge=0.0, le=120.0)
    housing_stability: float = Field(ge=0.0, le=1.0)
    food_security: float = Field(ge=0.0, le=1.0)
    commute_minutes: float = Field(ge=0.0, le=360.0)
    work_hours: float = Field(ge=0.0, le=100.0)
    care_hours: float = Field(ge=0.0, le=100.0)
    sleep_hours: float = Field(ge=0.0, le=24.0)
    exercise_minutes: float = Field(ge=0.0, le=1440.0)
    preventive_care_access: float = Field(ge=0.0, le=1.0)
    chronic_condition_count: int = Field(ge=0, le=20)
    stress_load: float = Field(ge=0.0, le=1.0)
    perceived_safety: float = Field(ge=0.0, le=1.0)
    civic_trust: float = Field(ge=0.0, le=1.0)
    neighborhood_cohesion: float = Field(ge=0.0, le=1.0)
    digital_access: float = Field(ge=0.0, le=1.0)
    schedule_volatility: float = Field(ge=0.0, le=1.0)
    autonomy_at_work: float = Field(ge=0.0, le=1.0)
    skill_match: float = Field(ge=0.0, le=1.0)
    job_security: float = Field(ge=0.0, le=1.0)
    benefits_access: float = Field(ge=0.0, le=1.0)
    social_contact_frequency: float = Field(ge=0.0, le=1.0)
    trusted_friend_count: int = Field(ge=0, le=100)
    household_size: int = Field(ge=1, le=20)
    caregiving_support: float = Field(ge=0.0, le=1.0)
    partner_support: float = Field(ge=0.0, le=1.0)
    family_contact: float = Field(ge=0.0, le=1.0)
    community_participation: float = Field(ge=0.0, le=1.0)
    religious_service_frequency: float = Field(ge=0.0, le=1.0)
    volunteering_hours: float = Field(ge=0.0, le=80.0)
    purpose_clarity: float = Field(ge=0.0, le=1.0)
    values_alignment: float = Field(ge=0.0, le=1.0)
    learning_hours: float = Field(ge=0.0, le=80.0)
    creative_hours: float = Field(ge=0.0, le=80.0)
    nature_access: float = Field(ge=0.0, le=1.0)
    mentor_access: float = Field(ge=0.0, le=1.0)
    institution_school: bool
    institution_employer: bool
    institution_healthcare: bool
    institution_bank: bool
    institution_housing_program: bool
    institution_childcare: bool
    institution_transport: bool
    institution_religious: bool
    institution_civic: bool
    institution_training: bool


STATE_FIELD_COUNT = len(FlourishingState.model_fields)


def state_schema() -> dict[str, object]:
    return FlourishingState.model_json_schema()

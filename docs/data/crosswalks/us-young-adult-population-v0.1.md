# Crosswalk: US Young Adult Population v0.1

Feature table: `features.us_young_adult_population_marginals`

Population scope: United States young adults ages 18-29.

| Construct | Canonical field | Primary source | Notes |
| --- | --- | --- | --- |
| Age | `age_band`, `age` | ACS PUMS | Generator samples integer ages within calibrated 18-20, 21-24, and 25-29 bands. |
| Education | `education`, `education_years` | CPS | Mapped to less-than-high-school, high-school, some-college, and bachelor-plus bins. |
| Employment | `employment_status`, `work_hours` | CPS | Simulation states use student, employed, unemployed, and caregiver categories. |
| Household | `household_type`, `household_size` | ACS PUMS | Household type calibrates alone, family, and roommate/shared contexts. |
| Income | `income_band`, `income_percentile` | CPS | Income bands calibrate household/family income and map to percentile ranges. |
| Geography | `geography`, `childhood_rurality` | ACS PUMS | Region/rural categories are calibration dimensions; rurality is derived from the rural category. |
| Occupation | `occupation_group` | ACS PUMS plus SOC/O*NET crosswalk | Occupation group is preserved on agent exports for downstream exposure joins. |
| Flourishing current context | pack state fields | GFS | Non-sensitive GFS distributions fill current context where available. |
| Childhood predictors | `childhood_*` pack state fields | GFS or documented prior | Missing childhood distributions must be marked imputed in the snapshot manifest. |

The calibration output `features.synthetic_population_calibration_diagnostics` reports max absolute standardized difference, KL divergence, marginal coverage, and per-dimension target/observed shares. MiroFish narrative artifacts are not accepted as causal effect-size inputs for this crosswalk.

import type { PopulationInspectorData } from "@/lib/population/types";

const STATUSES = ["student", "employed", "caregiver", "retired"];
const INSTITUTIONS = [
  { id: "employer", label: "Employer" },
  { id: "healthcare", label: "Healthcare" },
  { id: "school", label: "School" },
  { id: "civic", label: "Civic" },
  { id: "training", label: "Training" },
];

function continuousBins(seed: number): Array<{ label: string; value: number }> {
  return Array.from({ length: 10 }, (_, index) => ({
    label: `${index * 10}-${index * 10 + 9}`,
    value: 18 + ((index * 17 + seed) % 48),
  }));
}

export function buildPopulationFixture(count = 5000): PopulationInspectorData {
  const agents = Array.from({ length: count }, (_, index) => {
    const institution = INSTITUTIONS[index % INSTITUTIONS.length];
    const age = 18 + (index % 55);
    const income_percentile = Number((((index * 37) % 100) / 100).toFixed(2));
    const employment_status = STATUSES[index % STATUSES.length];
    return {
      id: `agent-${index.toString().padStart(5, "0")}`,
      institutionId: institution.id,
      fields: {
        age,
        income_percentile,
        employment_status,
        household_size: 1 + (index % 5),
        network_degree: 2 + (index % 18),
        institution_membership: institution.label,
        source_wave: "synthetic-gfs-heldout",
      },
    };
  });
  return {
    id: "pop_young_adult_5000",
    name: "Young adult synthetic population",
    packId: "flourishing",
    count,
    createdAt: "2026-04-26T00:00:00Z",
    renderHints: {
      colorBy: "institution_membership",
      institutionField: "institution_membership",
      fields: [
        { key: "age", label: "Age", kind: "continuous", tab: "composition", domain: [18, 72] },
        {
          key: "employment_status",
          label: "Employment status",
          kind: "categorical",
          tab: "composition",
        },
        {
          key: "network_degree",
          label: "Network degree",
          kind: "continuous",
          tab: "networks",
          domain: [0, 20],
        },
        {
          key: "institution_membership",
          label: "Institution membership",
          kind: "categorical",
          tab: "institutions",
        },
        {
          key: "income_percentile",
          label: "Income percentile",
          kind: "continuous",
          tab: "fidelity",
          domain: [0, 1],
        },
        { key: "source_wave", label: "Source wave", kind: "categorical", tab: "provenance" },
      ],
    },
    distributions: [
      {
        key: "age",
        label: "Age",
        kind: "continuous",
        tab: "composition",
        bins: continuousBins(3),
        ks: 0.018,
        status: "green",
      },
      {
        key: "employment_status",
        label: "Employment status",
        kind: "categorical",
        tab: "composition",
        bins: STATUSES.map((label, index) => ({ label, value: 20 + index * 5 })),
        ks: 0.041,
        status: "amber",
      },
      {
        key: "network_degree",
        label: "Network degree",
        kind: "continuous",
        tab: "networks",
        bins: continuousBins(11),
        ks: 0.024,
        status: "green",
      },
      {
        key: "institution_membership",
        label: "Institution membership",
        kind: "categorical",
        tab: "institutions",
        bins: INSTITUTIONS.map((institution) => ({ label: institution.label, value: count / 5 })),
        ks: 0.012,
        status: "green",
      },
      {
        key: "income_percentile",
        label: "Income percentile",
        kind: "continuous",
        tab: "fidelity",
        bins: continuousBins(19),
        ks: 0.033,
        status: "green",
      },
      {
        key: "source_wave",
        label: "Source wave",
        kind: "categorical",
        tab: "provenance",
        bins: [{ label: "synthetic-gfs-heldout", value: count }],
        ks: 0,
        status: "green",
      },
    ],
    networks: [
      { id: "household", label: "Household", density: 0.022, meanDegree: 2.4, status: "green" },
      { id: "support", label: "Support", density: 0.014, meanDegree: 7.6, status: "green" },
      { id: "institution", label: "Institution", density: 0.031, meanDegree: 9.8, status: "amber" },
    ],
    institutions: INSTITUTIONS.map((institution) => ({
      ...institution,
      members: count / INSTITUTIONS.length,
    })),
    provenance: [
      { label: "SpawnSpec", value: "fixtures/young_adult_spec.yml" },
      { label: "Pack", value: "flourishing@0.1.0" },
      { label: "Seed", value: "88" },
      { label: "Snapshot", value: "sha256:7d9c8c0f" },
    ],
    agents,
  };
}

export const populationFixture = buildPopulationFixture();

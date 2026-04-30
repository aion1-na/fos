export interface Tier1DatasetStatus {
  canonicalDatasetName: string;
  label: string;
  tier: "Tier 1";
  status: "fixture" | "request_status_stub" | "approved_production";
  productionReady: boolean;
  metadataComplete: boolean;
  qualityGate: "not_run" | "passing_fixture" | "blocked";
  sourceClass: "fixture_only" | "real_data_registration_gated";
  cardLink: string;
}

export const tier1Datasets: Tier1DatasetStatus[] = [
  {
    canonicalDatasetName: "acs-ipums",
    label: "ACS/IPUMS",
    tier: "Tier 1",
    status: "fixture",
    productionReady: false,
    metadataComplete: true,
    qualityGate: "passing_fixture",
    sourceClass: "fixture_only",
    cardLink: "/docs/data/datasets/acs-ipums",
  },
  {
    canonicalDatasetName: "onet",
    label: "O*NET",
    tier: "Tier 1",
    status: "fixture",
    productionReady: false,
    metadataComplete: true,
    qualityGate: "passing_fixture",
    sourceClass: "fixture_only",
    cardLink: "/docs/data/datasets/onet",
  },
  {
    canonicalDatasetName: "bls-oews",
    label: "BLS OEWS",
    tier: "Tier 1",
    status: "fixture",
    productionReady: false,
    metadataComplete: true,
    qualityGate: "passing_fixture",
    sourceClass: "fixture_only",
    cardLink: "/docs/data/datasets/bls-oews",
  },
  {
    canonicalDatasetName: "gfs-wave1",
    label: "GFS Wave 1",
    tier: "Tier 1",
    status: "request_status_stub",
    productionReady: false,
    metadataComplete: true,
    qualityGate: "blocked",
    sourceClass: "real_data_registration_gated",
    cardLink: "/docs/data/datasets/gfs-wave1",
  },
  {
    canonicalDatasetName: "gfs-wave2",
    label: "GFS Wave 2",
    tier: "Tier 1",
    status: "request_status_stub",
    productionReady: false,
    metadataComplete: true,
    qualityGate: "blocked",
    sourceClass: "real_data_registration_gated",
    cardLink: "/docs/data/datasets/gfs-wave2",
  },
  {
    canonicalDatasetName: "community-pathways",
    label: "Community pathways",
    tier: "Tier 1",
    status: "fixture",
    productionReady: false,
    metadataComplete: true,
    qualityGate: "passing_fixture",
    sourceClass: "fixture_only",
    cardLink: "/docs/data/datasets/community-pathways",
  },
];

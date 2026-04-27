export interface AtlasDataset {
  canonicalDatasetName: string;
  label: string;
  version: string;
  license: string;
  contentHash: string;
  fetchTimestamp: string;
  cardLink: string;
}

export const datasets: AtlasDataset[] = [
  {
    canonicalDatasetName: "acs_ipums",
    label: "ACS/IPUMS fixture",
    version: "fixture-0.1",
    license: "request-status stub; production terms pending",
    contentHash: "fixture-hash-computed-in-tests",
    fetchTimestamp: "fixture-only",
    cardLink: "/docs/data/datasets/acs-ipums",
  },
  {
    canonicalDatasetName: "onet",
    label: "O*NET fixture",
    version: "fixture-0.1",
    license: "public endpoint smoke tests require explicit approval",
    contentHash: "fixture-hash-computed-in-tests",
    fetchTimestamp: "fixture-only",
    cardLink: "/docs/data/datasets/onet",
  },
  {
    canonicalDatasetName: "bls_oews",
    label: "BLS OEWS fixture",
    version: "fixture-0.1",
    license: "public endpoint smoke tests require explicit approval",
    contentHash: "fixture-hash-computed-in-tests",
    fetchTimestamp: "fixture-only",
    cardLink: "/docs/data/datasets/bls-oews",
  },
];

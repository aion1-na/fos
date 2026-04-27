export interface BacktestSlice {
  geography: string;
  demographicGroup: string;
  chinaShock: number;
  mortalityRate: number;
  robotExposure: number;
}

export const validationGate = {
  id: "china_shock_backtest_v0.1",
  mode: "fail-closed",
  requiredReferences: [
    "features.adh_china_shock_panel",
    "raw_archive_hash",
    "connector_version",
    "source_citation",
    "stata_variable_label_manifest",
  ],
} as const;

export const backtestSlices: BacktestSlice[] = [
  {
    geography: "01001",
    demographicGroup: "45_54",
    chinaShock: 1.2,
    mortalityRate: 412.0,
    robotExposure: 0.12,
  },
  {
    geography: "01001",
    demographicGroup: "45_54",
    chinaShock: 2.4,
    mortalityRate: 438.0,
    robotExposure: 0.29,
  },
];

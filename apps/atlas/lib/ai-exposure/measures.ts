export interface ExposureMeasureRow {
  occupationCode: string;
  occupationTitle: string;
  eloundou: number;
  felten: number;
  divergence: number;
  disagreementLevel: "low" | "medium" | "high";
}

export interface ExposureQuartileRow {
  demographicGroup: string;
  geography: string;
  quartile: number;
  workerCount: number;
}

export const exposureMeasures: ExposureMeasureRow[] = [
  {
    occupationCode: "15-1252",
    occupationTitle: "Software Developers",
    eloundou: 0.82,
    felten: 0.77,
    divergence: 0.05,
    disagreementLevel: "low",
  },
  {
    occupationCode: "29-1141",
    occupationTitle: "Registered Nurses",
    eloundou: 0.41,
    felten: 0.36,
    divergence: 0.05,
    disagreementLevel: "low",
  },
  {
    occupationCode: "43-4051",
    occupationTitle: "Customer Service Representatives",
    eloundou: 0.63,
    felten: 0.70,
    divergence: 0.07,
    disagreementLevel: "low",
  },
];

export const exposureQuartiles: ExposureQuartileRow[] = [
  { demographicGroup: "age_18_34", geography: "US", quartile: 4, workerCount: 120 },
  { demographicGroup: "age_35_54", geography: "US", quartile: 4, workerCount: 180 },
  { demographicGroup: "age_18_34", geography: "US", quartile: 2, workerCount: 90 },
  { demographicGroup: "age_35_54", geography: "US", quartile: 2, workerCount: 210 },
  { demographicGroup: "age_18_34", geography: "US", quartile: 3, workerCount: 160 },
  { demographicGroup: "age_35_54", geography: "US", quartile: 3, workerCount: 140 },
];

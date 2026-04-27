export interface DomainDistribution {
  domain: string;
  us: number;
  jp: number;
}

export interface DemographicCut {
  country: string;
  demographicGroup: string;
  happiness: number;
  health: number;
  meaning: number;
}

export const gfsMeasurementLabel =
  "GFS Wave 1 is cross-sectional and research-grade; it is not prospective forecasting.";

export const domainDistributions: DomainDistribution[] = [
  { domain: "happiness", us: 6.6, jp: 5.45 },
  { domain: "health", us: 7.6, jp: 6.55 },
  { domain: "meaning", us: 6.4, jp: 6.9 },
  { domain: "character", us: 7.6, jp: 7.55 },
  { domain: "relationships", us: 6.6, jp: 6.45 },
  { domain: "financial", us: 5.4, jp: 6.55 },
];

export const demographicCuts: DemographicCut[] = [
  { country: "US", demographicGroup: "18_34", happiness: 7.0, health: 8.0, meaning: 6.0 },
  { country: "US", demographicGroup: "35_54", happiness: 6.0, health: 7.0, meaning: 7.0 },
  { country: "JP", demographicGroup: "18_34", happiness: 5.0, health: 7.0, meaning: 6.0 },
  { country: "JP", demographicGroup: "35_54", happiness: 6.0, health: 6.0, meaning: 8.0 },
];

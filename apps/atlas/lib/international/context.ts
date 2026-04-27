export interface PolicyContextRow {
  source: string;
  sourceCountryCode: string;
  countryIso3: string;
  indicator: string;
  value: number;
}

export const policyContextRows: PolicyContextRow[] = [
  {
    source: "OECD",
    sourceCountryCode: "USA",
    countryIso3: "USA",
    indicator: "safety_net_generosity",
    value: 0.62,
  },
  {
    source: "OECD",
    sourceCountryCode: "JPN",
    countryIso3: "JPN",
    indicator: "safety_net_generosity",
    value: 0.55,
  },
  {
    source: "WorldBank",
    sourceCountryCode: "US",
    countryIso3: "USA",
    indicator: "gdp_per_capita",
    value: 63528,
  },
  {
    source: "ILO",
    sourceCountryCode: "USA",
    countryIso3: "USA",
    indicator: "employment_rate",
    value: 0.71,
  },
];

export const dashboardViewName = "atlas.cross_country_policy_dashboard";

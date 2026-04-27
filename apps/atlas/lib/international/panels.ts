export interface CrossCountryPanel {
  canonicalDatasetName: string;
  label: string;
  country: "USA" | "GBR" | "DEU" | "AUS" | "EUR";
  coverage: string;
  accessStatus: "request_status_stub" | "approved";
  licenseStatus: "not_approved" | "approved";
  weightColumn: string;
  samplingDesign: string;
  comparableConstructs: string[];
}

export const crossCountryPanels: CrossCountryPanel[] = [
  {
    canonicalDatasetName: "psid_us",
    label: "PSID",
    country: "USA",
    coverage: "US",
    accessStatus: "request_status_stub",
    licenseStatus: "not_approved",
    weightColumn: "family_weight",
    samplingDesign: "US longitudinal household sample",
    comparableConstructs: ["employment", "education", "income", "family", "health", "wellbeing"],
  },
  {
    canonicalDatasetName: "understanding_society_uk",
    label: "Understanding Society",
    country: "GBR",
    coverage: "UK",
    accessStatus: "request_status_stub",
    licenseStatus: "not_approved",
    weightColumn: "indinui_xw",
    samplingDesign: "UK longitudinal household sample",
    comparableConstructs: ["employment", "education", "income", "family", "health", "wellbeing"],
  },
  {
    canonicalDatasetName: "soep_germany",
    label: "SOEP",
    country: "DEU",
    coverage: "Germany",
    accessStatus: "request_status_stub",
    licenseStatus: "not_approved",
    weightColumn: "phrf",
    samplingDesign: "German longitudinal household sample",
    comparableConstructs: ["employment", "education", "income", "family", "health", "wellbeing"],
  },
  {
    canonicalDatasetName: "hilda_australia",
    label: "HILDA",
    country: "AUS",
    coverage: "Australia",
    accessStatus: "request_status_stub",
    licenseStatus: "not_approved",
    weightColumn: "hhwte",
    samplingDesign: "Australian longitudinal household sample",
    comparableConstructs: ["employment", "education", "income", "family", "health", "wellbeing"],
  },
  {
    canonicalDatasetName: "share_eu_age50",
    label: "SHARE",
    country: "EUR",
    coverage: "EU age-50+",
    accessStatus: "request_status_stub",
    licenseStatus: "not_approved",
    weightColumn: "dw_w",
    samplingDesign: "multi-country age-50+ panel",
    comparableConstructs: ["employment", "education", "income", "family", "health", "wellbeing"],
  },
];

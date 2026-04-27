export interface PanelAvailability {
  canonicalDatasetName: string;
  label: string;
  accessStatus: "request_status_stub" | "approved";
  licenseStatus: "not_approved" | "approved";
  registrationRequired: boolean;
  constructs: string[];
  qualityProfile: string;
}

export const usPanelAvailability: PanelAvailability[] = [
  {
    canonicalDatasetName: "hrs",
    label: "HRS",
    accessStatus: "request_status_stub",
    licenseStatus: "not_approved",
    registrationRequired: true,
    constructs: ["employment_status", "income", "health", "depression_wellbeing", "household", "demographics"],
    qualityProfile: "pending_access",
  },
  {
    canonicalDatasetName: "midus",
    label: "MIDUS",
    accessStatus: "request_status_stub",
    licenseStatus: "not_approved",
    registrationRequired: true,
    constructs: ["employment_status", "income", "health", "depression_wellbeing", "household", "demographics"],
    qualityProfile: "pending_access",
  },
  {
    canonicalDatasetName: "nlsy79",
    label: "NLSY79",
    accessStatus: "request_status_stub",
    licenseStatus: "not_approved",
    registrationRequired: true,
    constructs: ["employment_status", "income", "health", "depression_wellbeing", "household", "demographics"],
    qualityProfile: "pending_access",
  },
  {
    canonicalDatasetName: "nlsy97",
    label: "NLSY97",
    accessStatus: "request_status_stub",
    licenseStatus: "not_approved",
    registrationRequired: true,
    constructs: ["employment_status", "income", "health", "depression_wellbeing", "household", "demographics"],
    qualityProfile: "pending_access",
  },
  {
    canonicalDatasetName: "psid",
    label: "PSID",
    accessStatus: "request_status_stub",
    licenseStatus: "not_approved",
    registrationRequired: true,
    constructs: ["employment_status", "income", "health", "depression_wellbeing", "household", "demographics"],
    qualityProfile: "pending_access",
  },
];

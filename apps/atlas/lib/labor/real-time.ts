export interface RealTimeLaborFeed {
  canonicalDatasetName: string;
  label: string;
  licenseCompartment: string;
  partitionGrain: "daily" | "hourly";
  signalFamily: "job_postings" | "hiring_velocity";
  accessStatus: "request_status_stub" | "approved";
  licenseStatus: "not_approved" | "approved";
  labelText: "deployment signal";
}

export const realTimeLaborFeeds: RealTimeLaborFeed[] = [
  {
    canonicalDatasetName: "lightcast_job_postings",
    label: "Lightcast job postings",
    licenseCompartment: "commercial/lightcast",
    partitionGrain: "daily",
    signalFamily: "job_postings",
    accessStatus: "request_status_stub",
    licenseStatus: "not_approved",
    labelText: "deployment signal",
  },
  {
    canonicalDatasetName: "linkedin_hiring_signals",
    label: "LinkedIn hiring signals",
    licenseCompartment: "commercial/linkedin",
    partitionGrain: "daily",
    signalFamily: "hiring_velocity",
    accessStatus: "request_status_stub",
    licenseStatus: "not_approved",
    labelText: "deployment signal",
  },
  {
    canonicalDatasetName: "indeed_job_postings",
    label: "Indeed job postings",
    licenseCompartment: "commercial/indeed",
    partitionGrain: "hourly",
    signalFamily: "job_postings",
    accessStatus: "request_status_stub",
    licenseStatus: "not_approved",
    labelText: "deployment signal",
  },
];

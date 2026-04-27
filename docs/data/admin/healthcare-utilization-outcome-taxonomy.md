# Healthcare Utilization Outcome Taxonomy

This taxonomy maps claims and utilization aggregates to the physical-health domain cautiously. Utilization is not treated as a direct health score or causal health outcome by itself.

| Source outcome | Utilization family | Physical-health mapping | Confidence | Caveat |
| --- | --- | --- | --- | --- |
| emergency_department_visits | acute utilization | physical health stress proxy | cautious | Utilization can reflect access, coding, and care-seeking behavior; interpret as calibration context only |
| inpatient_admissions | severe utilization | physical health burden proxy | cautious | Admissions are not a causal health score and require case-mix context |
| behavioral_health_visits | mental/behavioral utilization | related validation context | exploratory | Use only with explicit construct review and source limitations |

Every mapping must document caveats before it can appear in model calibration or a brief.

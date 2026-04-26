# Risk Register

| Risk | Owner | State | Mitigation |
| --- | --- | --- | --- |
| Kernel/pack seam erosion | Engineering | Active | Import lint and seam canary tests block pack imports and pack-specific strings in kernel code. |
| Non-deterministic runtime output | Engineering | Active | Seeded RNG, deterministic artifact tests, replay-from-manifest regression. |
| Pack evidence overclaiming | Research | Active | Pack lint requires evidence claims; validation gates label exploratory pathways. |
| Accessibility regression | Product Engineering | Active | WCAG 2.1 AA static checks and Cypress axe specs run in CI. |
| Performance regression | Engineering | Active | `tools/perf/agent_step_budget.py` fails CI on per-agent-step budget overruns. |
| Draft output mistaken for publishable result | Product | Active | Brief API and Studio reject draft run export. |
| External contributor onboarding gap | Engineering + Research | Open | `/docs/dev` and `/docs/research` cover setup, authoring, validation, and brief reading. Timed exercises remain required before tag. |
| Premature v0.1.0 tagging | Release | Open | Do not tag until one week of nightly green runs and external acceptance exercises are complete. |

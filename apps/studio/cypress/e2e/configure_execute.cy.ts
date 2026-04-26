// @ts-nocheck

describe("Configure and Execute", () => {
  it("configures a 30-seed run, dry-runs, saves, streams progress, and completes", () => {
    cy.intercept("POST", "/scenarios/scenario-default/dry-run", {
      valid: true,
      errors: [],
      artifact_count: 5,
      estimate_seconds: 300,
    }).as("dryRun");
    cy.intercept("POST", "/scenarios/scenario-default/invalidation-preview", {
      invalidated_artifacts: [
        {
          id: "population_snapshot:scenario-default:latest",
          stage: "Population",
          reason: "Branch changes target population.",
          regenerationCost: "45s synth + 12MB artifact",
        },
        {
          id: "simulation_run:scenario-default:latest",
          stage: "Execute",
          reason: "Run outputs depend on saved configuration.",
          regenerationCost: "2m runtime + 34MB artifact",
        },
      ],
    }).as("invalidationPreview");

    cy.visit("/studio/configure");
    cy.contains("Configure");
    cy.contains("Run Configurator");
    cy.contains("30 seeds");
    cy.contains("Dry-run preview").click();
    cy.wait("@dryRun");
    cy.contains("Dry-run preview passes");
    cy.contains("Save run spec").click();
    cy.contains("Saved run_standard_001");

    cy.get("select").select("Paid leave");
    cy.wait("@invalidationPreview");
    cy.contains("Controlled Re-entry");
    cy.contains("population_snapshot:scenario-default:latest");
    cy.contains("45s synth");
    cy.contains("Regenerate and continue").click();

    cy.visit("/studio/execute");
    cy.contains("Execute");
    cy.contains("Locked configuration");
    cy.contains("Start run").click();
    cy.contains("Status");
    cy.contains("Run complete", { timeout: 3000 });
    cy.contains("Latest happiness");

    cy.visit("/studio/configure");
    cy.contains("Draft mode").click();
    cy.contains("500");
    cy.contains("12 months");
    cy.contains("5");
    cy.visit("/studio/brief");
    cy.contains("Draft runs cannot produce a published brief");
  });
});

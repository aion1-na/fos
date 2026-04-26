// @ts-nocheck

describe("Young Adult Flourishing Futures full walkthrough", () => {
  it("walks all nine stages, re-enters from Validate to Frame, and exports a fresh brief", () => {
    cy.intercept("POST", "/scenarios/scenario-default/invalidation-preview", {
      invalidated_artifacts: [
        { id: "population", stage: "Population", reason: "Frame edit", regenerationCost: "45s synth" },
        { id: "run", stage: "Execute", reason: "Run stale", regenerationCost: "2m runtime" },
        { id: "validation", stage: "Validate", reason: "Validation stale", regenerationCost: "35s validation" },
        { id: "brief", stage: "Brief", reason: "Brief stale", regenerationCost: "manual review" },
      ],
    }).as("invalidation");
    cy.intercept("POST", "/scenarios/scenario-default/dry-run", {
      valid: true,
      errors: [],
      artifact_count: 5,
      estimate_seconds: 300,
    }).as("dryRun");
    cy.intercept("POST", "/runs/run_standard_001/brief", {
      id: "brief_fresh_after_reentry",
      run_id: "run_standard_001",
      version: 2,
      reproducibility_manifest: { run_id: "run_standard_001", kpi_outputs: [] },
    }).as("brief");
    cy.intercept("GET", "/runs/run_standard_001/brief?format=json", "{}").as("briefJson");

    ["frame", "compose", "evidence", "population", "configure", "execute", "validate", "explore", "brief"].forEach(
      (stage) => {
        cy.visit(`/studio/${stage}`);
        cy.contains(new RegExp(stage, "i"));
      },
    );

    cy.visit("/studio/validate");
    cy.contains("Validate");
    cy.visit("/studio/frame");
    cy.visit("/studio/configure");
    cy.get("select").select("Paid leave");
    cy.wait("@invalidation");
    cy.contains("Regenerate and continue").click();
    cy.contains("Dry-run preview").click();
    cy.wait("@dryRun");
    cy.contains("Save run spec").click();
    cy.visit("/studio/execute");
    cy.contains("Start run").click();
    cy.contains("Run complete", { timeout: 3000 });
    cy.visit("/studio/validate");
    cy.contains("E-value");
    cy.visit("/studio/explore");
    cy.contains("Branch Viewer");
    cy.visit("/studio/brief");
    cy.contains("Export brief").click();
    cy.wait("@brief");
    cy.wait("@briefJson");
    cy.contains("Exported json");
  });
});

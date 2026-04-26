// @ts-nocheck

describe("Validate and Explore", () => {
  it("walks validation, overrides an amber gate, explores traces, and saves findings", () => {
    const justification =
      "Amber gate override is acceptable for review because sensitivity notes will be carried into assumptions.";

    cy.intercept("POST", "/runs/run_standard_001/overrides", {
      id: "override_test",
      event: "validation_gate_override_recorded",
      run_id: "run_standard_001",
      gate: "amber",
      justification,
      assumptions: [`Privileged validation override for amber: ${justification}`],
    }).as("recordOverride");
    cy.intercept("POST", "/runs/run_standard_001/findings", (request) => {
      request.reply({
        id: `finding_${request.body.source}`,
        run_id: "run_standard_001",
        ...request.body,
      });
    }).as("saveFinding");

    cy.visit("/studio/validate");
    cy.contains("Validate");
    cy.contains("E-value");
    cy.contains("Seed variance");
    cy.contains("Cited evidence claim id: income-security-001");
    cy.contains("Override amber gate").click();
    cy.contains("Submit override").should("be.disabled");
    cy.get("textarea").type(justification);
    cy.contains("Submit override").click();
    cy.wait("@recordOverride");
    cy.contains("validation_gate_override_recorded");
    cy.contains("Save finding").click();
    cy.wait("@saveFinding");

    cy.visit("/studio/brief");
    cy.contains("Assumptions");
    cy.contains(justification);

    cy.visit("/studio/explore");
    cy.contains("Branch Viewer");
    cy.contains("Causal Trace Overlay");
    cy.contains("Six-Domain Radar");
    cy.contains("Exploratory branch delta finding");
    cy.contains("Save finding").click();
    cy.wait("@saveFinding");
  });
});

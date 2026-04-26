// @ts-nocheck

describe("Brief export", () => {
  it("selects findings, edits assumptions, attaches citations, and exports all formats", () => {
    cy.intercept("POST", "/runs/run_standard_001/brief", {
      id: "brief_run_standard_001_v1",
      run_id: "run_standard_001",
      version: 1,
      reproducibility_manifest: { run_id: "run_standard_001", kpi_outputs: [] },
    }).as("generateBrief");
    cy.intercept("GET", "/runs/run_standard_001/brief?format=pdf", "pdf").as("pdf");
    cy.intercept("GET", "/runs/run_standard_001/brief?format=docx", "docx").as("docx");
    cy.intercept("GET", "/runs/run_standard_001/brief?format=json", "{}").as("json");
    cy.intercept("GET", "/runs/run_standard_001/brief?format=bundle", "bundle").as("bundle");

    cy.visit("/studio/brief");
    cy.contains("Draft run rejected");
    cy.contains("Finding Selection");
    cy.contains("Assumptions");
    cy.contains("Evidence Trail");
    cy.get("textarea").clear().type("Assumptions edited for export with validation override context.");

    ["pdf", "docx", "json", "bundle"].forEach((format) => {
      cy.contains("button", format).click();
      cy.contains("Export brief").click();
      cy.wait("@generateBrief");
      cy.wait(`@${format}`);
      cy.contains(`Exported ${format}`);
    });
  });
});

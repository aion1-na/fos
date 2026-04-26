// @ts-nocheck

describe("Population Inspector", () => {
  it("synthesizes a population, walks all tabs, saves a cohort, and opens an agent", () => {
    cy.intercept("POST", "/populations", {
      id: "pop_young_adult_5000",
      count: 5000,
      pack_id: "flourishing",
    }).as("createPopulation");
    cy.intercept("GET", "/populations/pop_young_adult_5000/composition", {
      id: "pop_young_adult_5000",
      count: 5000,
      composition: { attributes: [] },
    }).as("composition");
    cy.intercept("POST", "/cohorts", {
      id: "cohort_deterministic",
      target_population: "pop_young_adult_5000",
      filters: [],
      agent_ids: ["agent-00000"],
    }).as("saveCohort");
    cy.intercept("GET", "/populations/pop_young_adult_5000/agents/agent-00000", {
      id: "agent-00000",
      fields: { age: 18 },
    }).as("agent");

    cy.visit("/studio/population");
    cy.contains("Population Inspector");
    cy.contains("5,000 agents");
    cy.contains("Synthesize").click();
    cy.wait("@createPopulation");
    cy.contains("Synthesized 5,000 agents");

    ["Composition", "Networks", "Institutions", "Fidelity", "Provenance"].forEach((tab) => {
      cy.contains("button", tab).click();
      cy.contains(tab);
    });

    cy.contains("Save cohort").click();
    cy.wait("@saveCohort");
    cy.contains("Cohort saved as");
    cy.contains("agent-00000").click();
    cy.wait("@agent");
    cy.contains("Agent");
    cy.contains("agent-00000");
  });
});

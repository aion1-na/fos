// @ts-nocheck

import { checkA11y, injectAxe } from "../support/axe";

const stages = [
  "/studio/frame",
  "/studio/compose",
  "/studio/evidence",
  "/studio/population",
  "/studio/configure",
  "/studio/execute",
  "/studio/validate",
  "/studio/explore",
  "/studio/brief",
];

describe("Studio accessibility", () => {
  for (const stage of stages) {
    it(`${stage} has no WCAG 2.1 AA violations`, () => {
      cy.visit(stage);
      injectAxe();
      cy.get('[aria-label="Studio stages"]').should("be.visible");
      cy.get("main").should("be.visible");
      checkA11y();
    });
  }
});

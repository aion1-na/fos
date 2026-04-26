// @ts-nocheck

import axe from "axe-core";

export function injectAxe() {
  cy.window({ log: false }).then((win) => {
    win.eval(axe.source);
  });
}

export function checkA11y() {
  cy.window({ log: false }).then(async (win) => {
    const results = await win.axe.run(win.document);
    expect(results.violations, "WCAG 2.1 AA violations").to.deep.equal([]);
  });
}

import { backtestSlices, validationGate } from "@/lib/backtests/anchors";

export default function BacktestViewerPage() {
  return (
    <main className="atlas-shell">
      <header>
        <p className="eyebrow">Atlas</p>
        <h1>Backtest anchors</h1>
        <p className="lede">
          Known trade and technology shock fixtures used to validate retrodiction before forward AI scenarios are trusted.
        </p>
      </header>

      <section className="dataset-card" aria-label="China shock validation gate">
        <h2>Validation gate</h2>
        <p>
          {validationGate.id} runs in {validationGate.mode} mode.
        </p>
        <ul>
          {validationGate.requiredReferences.map((reference) => (
            <li key={reference}>{reference}</li>
          ))}
        </ul>
      </section>

      <section className="dataset-card" aria-label="Backtest geography and demographic slices">
        <h2>Geography and demographic slices</h2>
        <table>
          <thead>
            <tr>
              <th>Geography</th>
              <th>Demographic</th>
              <th>China shock</th>
              <th>Mortality</th>
              <th>Robot exposure</th>
            </tr>
          </thead>
          <tbody>
            {backtestSlices.map((row, index) => (
              <tr key={`${row.geography}-${index}`}>
                <td>{row.geography}</td>
                <td>{row.demographicGroup}</td>
                <td>{row.chinaShock.toFixed(2)}</td>
                <td>{row.mortalityRate.toFixed(1)}</td>
                <td>{row.robotExposure.toFixed(2)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
    </main>
  );
}

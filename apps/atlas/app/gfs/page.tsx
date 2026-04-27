import { demographicCuts, domainDistributions, gfsMeasurementLabel } from "@/lib/gfs/wave1";

export default function GfsWave1Page() {
  return (
    <main className="atlas-shell">
      <header>
        <p className="eyebrow">Atlas</p>
        <h1>GFS Wave 1 flourishing measurement</h1>
        <p className="lede">{gfsMeasurementLabel}</p>
      </header>

      <section className="dataset-card" aria-label="Per-domain distributions and country comparison">
        <h2>Country comparison</h2>
        <table>
          <thead>
            <tr>
              <th>Domain</th>
              <th>US weighted mean</th>
              <th>JP weighted mean</th>
            </tr>
          </thead>
          <tbody>
            {domainDistributions.map((row) => (
              <tr key={row.domain}>
                <td>{row.domain}</td>
                <td>{row.us.toFixed(2)}</td>
                <td>{row.jp.toFixed(2)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>

      <section className="dataset-card" aria-label="GFS heatmap and demographic cuts">
        <h2>Demographic cuts</h2>
        <table>
          <thead>
            <tr>
              <th>Country</th>
              <th>Group</th>
              <th>Happiness</th>
              <th>Health</th>
              <th>Meaning</th>
            </tr>
          </thead>
          <tbody>
            {demographicCuts.map((row) => (
              <tr key={`${row.country}-${row.demographicGroup}`}>
                <td>{row.country}</td>
                <td>{row.demographicGroup}</td>
                <td>{row.happiness.toFixed(1)}</td>
                <td>{row.health.toFixed(1)}</td>
                <td>{row.meaning.toFixed(1)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
    </main>
  );
}

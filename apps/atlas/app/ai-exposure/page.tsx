import { exposureMeasures, exposureQuartiles } from "@/lib/ai-exposure/measures";

export default function AiExposureGalleryPage() {
  return (
    <main className="atlas-shell">
      <header>
        <p className="eyebrow">Atlas</p>
        <h1>AI exposure gallery</h1>
        <p className="lede">
          Side-by-side fixture measures with disagreement surfaced as uncertainty metadata.
        </p>
      </header>

      <section className="dataset-card" aria-label="Side-by-side exposure measures">
        <h2>Exposure measures</h2>
        <table>
          <thead>
            <tr>
              <th>Occupation</th>
              <th>Eloundou</th>
              <th>Felten</th>
              <th>Divergence</th>
              <th>Uncertainty</th>
            </tr>
          </thead>
          <tbody>
            {exposureMeasures.map((row) => (
              <tr key={row.occupationCode}>
                <td>
                  {row.occupationTitle} ({row.occupationCode})
                </td>
                <td>{row.eloundou.toFixed(2)}</td>
                <td>{row.felten.toFixed(2)}</td>
                <td>{row.divergence.toFixed(2)}</td>
                <td>{row.disagreementLevel}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>

      <section className="dataset-card" aria-label="Exposure quartiles by demographic and geography">
        <h2>Exposure quartiles</h2>
        <table>
          <thead>
            <tr>
              <th>Demographic</th>
              <th>Geography</th>
              <th>Quartile</th>
              <th>Workers</th>
            </tr>
          </thead>
          <tbody>
            {exposureQuartiles.map((row, index) => (
              <tr key={`${row.demographicGroup}-${row.geography}-${index}`}>
                <td>{row.demographicGroup}</td>
                <td>{row.geography}</td>
                <td>Q{row.quartile}</td>
                <td>{row.workerCount}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
    </main>
  );
}

import { tier1Datasets } from "@/lib/completeness/tier1";

export default function CompletenessPage() {
  return (
    <main className="atlas-shell">
      <header>
        <p className="eyebrow">Atlas</p>
        <h1>Tier 1 completeness dashboard</h1>
        <p className="lede">
          Release-candidate readiness for Tier 1 datasets, including metadata completeness and
          production status.
        </p>
      </header>

      <section className="dataset-card" aria-label="Tier 1 dataset completeness">
        <h2>Tier 1 release candidate</h2>
        <table>
          <thead>
            <tr>
              <th>Dataset</th>
              <th>Tier</th>
              <th>Status</th>
              <th>Metadata</th>
              <th>Quality gate</th>
              <th>Production-ready</th>
            </tr>
          </thead>
          <tbody>
            {tier1Datasets.map((dataset) => (
              <tr key={dataset.canonicalDatasetName}>
                <td>{dataset.label}</td>
                <td>{dataset.tier}</td>
                <td>{dataset.status}</td>
                <td>{dataset.metadataComplete ? "complete" : "blocked"}</td>
                <td>{dataset.qualityGate}</td>
                <td>{dataset.productionReady ? "yes" : "no"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
    </main>
  );
}

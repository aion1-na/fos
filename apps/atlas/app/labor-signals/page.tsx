import { realTimeLaborFeeds } from "@/lib/labor/real-time";

export default function LaborSignalsPage() {
  return (
    <main className="atlas-shell">
      <header>
        <p className="eyebrow">Atlas</p>
        <h1>Real-time labor signals</h1>
        <p className="lede">
          Partner-feed deployment signals are labeled separately from predicted exposure measures.
        </p>
      </header>
      <section className="dataset-card" aria-label="Real-time labor feed availability">
        <h2>Deployment signals</h2>
        <table>
          <thead>
            <tr>
              <th>Feed</th>
              <th>Compartment</th>
              <th>Partition</th>
              <th>Signal</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {realTimeLaborFeeds.map((feed) => (
              <tr key={feed.canonicalDatasetName}>
                <td>{feed.label}</td>
                <td>{feed.licenseCompartment}</td>
                <td>{feed.partitionGrain}</td>
                <td>{feed.labelText}</td>
                <td>{feed.licenseStatus}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
    </main>
  );
}

import {
  provenanceEdges,
  provenanceNodes,
  selectedDatasetReference,
} from "@/lib/provenance/lineage";

export default function ProvenancePage() {
  return (
    <main className="atlas-shell">
      <header>
        <p className="eyebrow">Atlas</p>
        <h1>Provenance lineage</h1>
        <p className="lede">
          Upstream and downstream lineage for a content-addressed dataset reference and its
          consuming simulation runs.
        </p>
      </header>

      <section className="dataset-card" aria-label="Selected dataset reference">
        <h2>Dataset reference</h2>
        <dl>
          <dt>Name</dt>
          <dd>{selectedDatasetReference.canonical_dataset_name}</dd>
          <dt>Version</dt>
          <dd>{selectedDatasetReference.version}</dd>
          <dt>Hash</dt>
          <dd className="hash">{selectedDatasetReference.content_hash}</dd>
        </dl>
      </section>

      <section className="dataset-card" aria-label="Lineage graph">
        <h2>What fed this dataset and what consumed it</h2>
        <table>
          <thead>
            <tr>
              <th>Node</th>
              <th>Kind</th>
            </tr>
          </thead>
          <tbody>
            {provenanceNodes.map((node) => (
              <tr key={node.id}>
                <td>{node.label}</td>
                <td>{node.kind}</td>
              </tr>
            ))}
          </tbody>
        </table>
        <table>
          <thead>
            <tr>
              <th>Edge</th>
              <th>Lineage</th>
            </tr>
          </thead>
          <tbody>
            {provenanceEdges.map((edge) => (
              <tr key={edge.id}>
                <td>{edge.id}</td>
                <td>{edge.label}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
    </main>
  );
}

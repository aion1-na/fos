import { graphFilters, reactFlowEdges, reactFlowNodes } from "@/lib/evidence/graph";

export default function EvidenceGraphPage() {
  return (
    <main className="atlas-shell">
      <header>
        <p className="eyebrow">Atlas</p>
        <h1>Evidence graph explorer</h1>
        <p className="lede">
          React Flow graph data for construct-to-claim-to-citation-to-dataset traversal.
        </p>
      </header>

      <section className="dataset-card" aria-label="Evidence graph search filters">
        <h2>Search filters</h2>
        <dl>
          <dt>Construct</dt>
          <dd>{graphFilters.construct.join(", ")}</dd>
          <dt>Claim</dt>
          <dd>{graphFilters.claim.join(", ")}</dd>
          <dt>Source</dt>
          <dd>{graphFilters.source.join(", ")}</dd>
          <dt>Confidence</dt>
          <dd>{graphFilters.confidenceLabel.join(", ")}</dd>
        </dl>
      </section>

      <section className="dataset-card" aria-label="React Flow evidence graph">
        <h2>React Flow nodes and edges</h2>
        <table>
          <thead>
            <tr>
              <th>Node</th>
              <th>Kind</th>
              <th>Label</th>
            </tr>
          </thead>
          <tbody>
            {reactFlowNodes.map((node) => (
              <tr key={node.id}>
                <td>{node.id}</td>
                <td>{node.data.kind}</td>
                <td>{node.data.label}</td>
              </tr>
            ))}
          </tbody>
        </table>
        <table>
          <thead>
            <tr>
              <th>Edge</th>
              <th>Traversal</th>
            </tr>
          </thead>
          <tbody>
            {reactFlowEdges.map((edge) => (
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

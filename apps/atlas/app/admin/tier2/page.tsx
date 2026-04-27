import { tier2AccessRequests } from "@/lib/admin/tier2";

export default function Tier2AdminPage() {
  return (
    <main className="atlas-shell">
      <header>
        <p className="eyebrow">Atlas admin</p>
        <h1>Tier 2 DUA dashboard</h1>
        <p className="lede">
          Admin-only request-status view for pending DUA and license-gated longitudinal sources.
        </p>
      </header>
      <section className="dataset-card" aria-label="Tier 2 access requests">
        <h2>Access requests</h2>
        <table>
          <thead>
            <tr>
              <th>Dataset</th>
              <th>Owner</th>
              <th>Access</th>
              <th>License</th>
              <th>Compartment</th>
              <th>Updated</th>
            </tr>
          </thead>
          <tbody>
            {tier2AccessRequests.map((request) => (
              <tr key={request.canonicalDatasetName}>
                <td>{request.canonicalDatasetName}</td>
                <td>{request.owner}</td>
                <td>{request.accessStatus}</td>
                <td>{request.licenseStatus}</td>
                <td>{request.secureCompartment}</td>
                <td>{request.updatedOn}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
    </main>
  );
}

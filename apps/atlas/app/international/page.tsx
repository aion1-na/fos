import { dashboardViewName, policyContextRows } from "@/lib/international/context";

export default function InternationalContextPage() {
  return (
    <main className="atlas-shell">
      <header>
        <p className="eyebrow">Atlas</p>
        <h1>International policy context</h1>
        <p className="lede">
          Public-table fixture context with source country codes preserved and ISO3 identifiers normalized.
        </p>
      </header>

      <section className="dataset-card" aria-label="Cross-country materialized dashboard view">
        <h2>{dashboardViewName}</h2>
        <table>
          <thead>
            <tr>
              <th>Source</th>
              <th>Source country</th>
              <th>ISO3</th>
              <th>Indicator</th>
              <th>Value</th>
            </tr>
          </thead>
          <tbody>
            {policyContextRows.map((row, index) => (
              <tr key={`${row.source}-${row.indicator}-${index}`}>
                <td>{row.source}</td>
                <td>{row.sourceCountryCode}</td>
                <td>{row.countryIso3}</td>
                <td>{row.indicator}</td>
                <td>{row.value.toLocaleString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
    </main>
  );
}

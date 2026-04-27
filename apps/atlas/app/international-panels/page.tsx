import { crossCountryPanels } from "@/lib/international/panels";

export default function InternationalPanelsPage() {
  return (
    <main className="atlas-shell">
      <header>
        <p className="eyebrow">Atlas</p>
        <h1>Cross-country longitudinal comparison</h1>
        <p className="lede">
          Availability and comparability metadata for US, UK, Germany, Australia, and EU age-50+
          panels.
        </p>
      </header>
      <section className="dataset-card" aria-label="Cross-country panel comparison">
        <h2>Panel comparison</h2>
        <table>
          <thead>
            <tr>
              <th>Panel</th>
              <th>Country</th>
              <th>Coverage</th>
              <th>Weight</th>
              <th>Sampling design</th>
              <th>License</th>
            </tr>
          </thead>
          <tbody>
            {crossCountryPanels.map((panel) => (
              <tr key={panel.canonicalDatasetName}>
                <td>{panel.label}</td>
                <td>{panel.country}</td>
                <td>{panel.coverage}</td>
                <td>{panel.weightColumn}</td>
                <td>{panel.samplingDesign}</td>
                <td>{panel.licenseStatus}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
    </main>
  );
}

import { usPanelAvailability } from "@/lib/panels/us";

export default function PanelsPage() {
  return (
    <main className="atlas-shell">
      <header>
        <p className="eyebrow">Atlas</p>
        <h1>Longitudinal panel availability</h1>
      </header>
      <section className="dataset-grid" aria-label="US panel availability">
        {usPanelAvailability.map((panel) => (
          <article className="dataset-card" key={panel.canonicalDatasetName}>
            <h2>{panel.label}</h2>
            <dl>
              <dt>Access</dt>
              <dd>{panel.accessStatus}</dd>
              <dt>License</dt>
              <dd>{panel.licenseStatus}</dd>
              <dt>Registration</dt>
              <dd>{panel.registrationRequired ? "required" : "not required"}</dd>
              <dt>Constructs</dt>
              <dd>{panel.constructs.join(", ")}</dd>
              <dt>Quality</dt>
              <dd>{panel.qualityProfile}</dd>
            </dl>
          </article>
        ))}
      </section>
    </main>
  );
}

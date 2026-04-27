import { publicAtlasDatasets } from "@/lib/access/public";

export default function PublicAtlasPage() {
  return (
    <main className="atlas-shell">
      <header>
        <p className="eyebrow">Atlas public view</p>
        <h1>Public transparency subset</h1>
        <p className="lede">
          Public dataset metadata only. Gated, restricted, and license-constrained records are
          excluded.
        </p>
      </header>

      <section className="dataset-grid" aria-label="Public Atlas datasets">
        {publicAtlasDatasets.map((dataset) => (
          <article className="dataset-card" key={dataset.canonicalDatasetName}>
            <h2>{dataset.label}</h2>
            <dl>
              <dt>Tier</dt>
              <dd>{dataset.tier}</dd>
              <dt>Status</dt>
              <dd>{dataset.status}</dd>
              <dt>Limitations</dt>
              <dd>{dataset.limitations}</dd>
              <dt>Provenance</dt>
              <dd>{dataset.provenanceLink}</dd>
            </dl>
          </article>
        ))}
      </section>
    </main>
  );
}

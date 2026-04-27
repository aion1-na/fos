import Link from "next/link";

import { datasets } from "@/lib/datasets";

export default function DatasetDirectoryPage() {
  return (
    <main className="atlas-shell">
      <header>
        <p className="eyebrow">Atlas</p>
        <h1>Dataset directory</h1>
      </header>
      <section className="dataset-grid" aria-label="Dataset directory">
        {datasets.map((dataset) => (
          <article className="dataset-card" key={dataset.canonicalDatasetName}>
            <h2>{dataset.label}</h2>
            <dl>
              <dt>Canonical name</dt>
              <dd>{dataset.canonicalDatasetName}</dd>
              <dt>Version</dt>
              <dd>{dataset.version}</dd>
              <dt>License</dt>
              <dd>{dataset.license}</dd>
              <dt>Content hash</dt>
              <dd className="hash">{dataset.contentHash}</dd>
              <dt>Fetch timestamp</dt>
              <dd>{dataset.fetchTimestamp}</dd>
            </dl>
            <Link href={dataset.cardLink}>Dataset card</Link>
          </article>
        ))}
      </section>
    </main>
  );
}

import { searchableCitations } from "@/lib/search/citations";

export default function SearchPage() {
  return (
    <main className="atlas-shell">
      <header>
        <p className="eyebrow">Atlas search</p>
        <h1>Search and citations</h1>
        <p className="lede">
          Citation-ready entries across dataset cards, codebooks, and evidence claims.
        </p>
      </header>

      <section className="dataset-card" aria-label="Search and citation results">
        <h2>Indexed citations</h2>
        <table>
          <thead>
            <tr>
              <th>Kind</th>
              <th>Title</th>
              <th>Citation</th>
              <th>Sign-off</th>
              <th>Provenance</th>
            </tr>
          </thead>
          <tbody>
            {searchableCitations.map((citation) => (
              <tr key={citation.id}>
                <td>{citation.kind}</td>
                <td>{citation.title}</td>
                <td>{citation.citation}</td>
                <td>{citation.signoffStatus}</td>
                <td>{citation.provenanceLink}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
    </main>
  );
}

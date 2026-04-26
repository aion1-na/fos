export function SixDomainRadar({ scores }: { scores: Record<string, number> }) {
  return (
    <section className="run-panel">
      <h2>Six-Domain Radar</h2>
      <div className="radar-list">
        {Object.entries(scores).map(([domain, score]) => (
          <div className="radar-row" key={domain}>
            <span>{domain}</span>
            <span className="radar-track">
              <span style={{ width: `${score * 100}%` }} />
            </span>
            <strong>{score.toFixed(2)}</strong>
          </div>
        ))}
      </div>
    </section>
  );
}

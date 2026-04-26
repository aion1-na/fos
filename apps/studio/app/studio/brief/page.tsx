import { DRAFT_RUN_SPEC } from "@/lib/run/types";

export default function BriefPage() {
  const selectedRun = DRAFT_RUN_SPEC;

  return (
    <main className="workspace">
      <header className="workspace-header">
        <p className="eyebrow">Studio Stage 9</p>
        <h1>Brief</h1>
      </header>
      <section className="placeholder-panel" aria-label="Brief draft guard">
        <h2>Published brief unavailable</h2>
        <p>
          Draft runs cannot produce a published brief. Select a non-draft run with validation gates enabled before
          publishing.
        </p>
        <p>Current run: {selectedRun.id}</p>
      </section>
    </main>
  );
}

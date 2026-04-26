import { StageRail } from "@/components/StageRail";

export default function StudioLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <>
      <a className="skip-link" href="#studio-main">
        Skip to workspace
      </a>
      <div className="studio-shell">
        <StageRail />
        {children}
        <aside className="context-pane" aria-label="Stage context">
          <h2>Context</h2>
          <p>Placeholder pane reserved for stage-specific supporting details.</p>
        </aside>
      </div>
    </>
  );
}

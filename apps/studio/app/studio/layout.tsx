import { StageRail } from "@/components/StageRail";

export default function StudioLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <div className="studio-shell">
      <StageRail />
      {children}
      <aside className="context-pane">
        <h2>Context</h2>
        <p>Placeholder pane reserved for stage-specific supporting details.</p>
      </aside>
    </div>
  );
}

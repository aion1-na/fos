"use client";

export function DraftModeToggle({
  checked,
  onChange,
}: {
  checked: boolean;
  onChange: (checked: boolean) => void;
}) {
  return (
    <label className="draft-toggle">
      <input checked={checked} onChange={(event) => onChange(event.target.checked)} type="checkbox" />
      <span>
        <strong>Draft mode</strong>
        <small>500 agents · 12-month horizon · 5 seeds · fixture-only evidence · no validation gates</small>
      </span>
    </label>
  );
}

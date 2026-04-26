"use client";

import type { AttributeDistribution } from "@/lib/population/types";

function maxValue(distribution: AttributeDistribution): number {
  return Math.max(...distribution.bins.map((bin) => bin.value), 1);
}

export function MarginalDistributionRow({
  distribution,
}: {
  distribution: AttributeDistribution;
}) {
  const max = maxValue(distribution);
  return (
    <div className="distribution-row">
      <div>
        <div className="distribution-title">{distribution.label}</div>
        <div className="distribution-meta">{distribution.kind}</div>
      </div>
      <div className={`mini-chart mini-chart-${distribution.kind}`} aria-label={`${distribution.label} distribution`}>
        {distribution.bins.map((bin) => (
          <span
            className="mini-chart-bar"
            key={bin.label}
            style={{
              height: distribution.kind === "continuous" ? `${Math.max(6, (bin.value / max) * 54)}px` : undefined,
              width: distribution.kind === "categorical" ? `${Math.max(4, (bin.value / max) * 100)}%` : undefined,
            }}
            title={`${bin.label}: ${bin.value}`}
          />
        ))}
      </div>
      <div className="ks-cell">
        <span className="status-badge" data-status={distribution.status}>
          {distribution.status}
        </span>
        <span className="ks-value">KS {distribution.ks.toFixed(3)}</span>
      </div>
    </div>
  );
}

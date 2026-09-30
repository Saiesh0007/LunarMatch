import React from 'react';
import { Badge } from './Badge.jsx';

export function TelemetryRow({ id, inliers, rmse, status }) {
  return (
    <div className="flex items-center justify-between py-3 border-b border-surface-container-high last:border-0 hover:bg-surface-container-low transition-colors px-2 -mx-2 rounded">
      <div className="font-mono text-xs text-primary">{id}</div>
      <div className="font-mono text-xs text-on-surface-variant w-16 text-right">{inliers}</div>
      <div className="font-mono text-xs text-on-surface-variant w-16 text-right">{rmse.toFixed(2)}</div>
      <div className="w-24 text-right">
        {status === 'baseline' && <Badge variant="code" label="NOMINAL" className="border-primary text-primary bg-primary/10" />}
        {status === 'warning' && <Badge variant="code" label="MARGINAL" className="border-secondary text-secondary bg-secondary/10" />}
        {status === 'degraded' && <Badge variant="error" label="DEGRADED" />}
      </div>
    </div>
  );
}

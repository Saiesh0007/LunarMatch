import React from 'react';
import { Badge } from '../../components/ui/Badge.jsx';

export function EngineCapabilityCard({ capability }) {
  return (
    <div className="bg-surface-container-lowest border border-surface-container-high p-4 rounded-xl mb-3 hover:border-outline-variant transition-colors">
      <div className="flex items-start justify-between mb-2">
        <div className="font-headline-sm uppercase text-primary tracking-wide">{capability.title}</div>
        <Badge variant="code" label={capability.version} />
      </div>
      <p className="font-body-sm text-xs text-on-surface-variant mb-3">{capability.description}</p>
      
      <div className="flex gap-2 font-mono text-[10px] text-outline">
        {capability.params.map(param => (
          <span key={param} className="bg-surface-container px-2 py-0.5 rounded border border-surface-container-high">{param}</span>
        ))}
      </div>
    </div>
  );
}

import React from 'react';
import { SectionHeader } from '../../components/ui/SectionHeader.jsx';
import { Icon } from '../../components/ui/Icon.jsx';

export function MissionSpec() {
  return (
    <div className="mb-8">
      <SectionHeader icon="assignment" title="Mission Specification" />
      <div className="grid grid-cols-2 gap-3">
        <div className="bg-surface-container rounded-lg p-3 border border-surface-container-high">
           <div className="flex items-center gap-2 text-outline-variant mb-1">
              <Icon name="explore" size="14px" />
              <span className="font-label-sm uppercase">Reference CRS</span>
           </div>
           <div className="font-mono text-xs text-primary">LUNAR_EQC_2026</div>
        </div>
        <div className="bg-surface-container rounded-lg p-3 border border-surface-container-high">
           <div className="flex items-center gap-2 text-outline-variant mb-1">
              <Icon name="straighten" size="14px" />
              <span className="font-label-sm uppercase">Resolution</span>
           </div>
           <div className="font-mono text-xs text-primary">0.25 M/PX (OHRC)</div>
        </div>
        <div className="bg-surface-container rounded-lg p-3 border border-surface-container-high col-span-2">
           <div className="flex items-center gap-2 text-outline-variant mb-1">
              <Icon name="memory" size="14px" />
              <span className="font-label-sm uppercase">Compute Constraints</span>
           </div>
           <div className="font-mono text-xs text-on-surface-variant flex gap-4">
              <span>RAM: 8GB MAX</span>
              <span>GPU: NONE (CPU SIMD)</span>
           </div>
        </div>
      </div>
    </div>
  );
}

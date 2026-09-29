import React from 'react';
import { SectionHeader } from '../../components/ui/SectionHeader.jsx';
import { Icon } from '../../components/ui/Icon.jsx';
import { TechTag } from '../../components/ui/TechTag.jsx';

export function ArchitectureSummary() {
  return (
    <div className="mb-8">
      <SectionHeader icon="account_tree" title="Pipeline Stages" meta="Module 03" />
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-surface-container-low border border-surface-container-high p-4 rounded-xl">
          <div className="flex justify-between items-center mb-3">
             <span className="font-label-sm text-outline tracking-widest uppercase">Stage 03</span>
             <Icon name="memory" size="16px" className="text-outline-variant" />
          </div>
          <div className="font-headline-sm uppercase tracking-wide mb-4">Phase Congruency</div>
          <TechTag label="RIFT2" className="text-xs" />
        </div>
        <div className="bg-surface-container-low border border-surface-container-high p-4 rounded-xl">
          <div className="flex justify-between items-center mb-3">
             <span className="font-label-sm text-outline tracking-widest uppercase">Stage 05</span>
             <Icon name="join_inner" size="16px" className="text-outline-variant" />
          </div>
          <div className="font-headline-sm uppercase tracking-wide mb-4">Neural Matching</div>
          <TechTag label="SuperGlue Sinkhorn" className="text-xs" />
        </div>
        <div className="bg-surface-container-low border border-surface-container-high p-4 rounded-xl">
          <div className="flex justify-between items-center mb-3">
             <span className="font-label-sm text-outline tracking-widest uppercase">Stage 08</span>
             <Icon name="grid_view" size="16px" className="text-outline-variant" />
          </div>
          <div className="font-headline-sm uppercase tracking-wide mb-4">Spatial Balance</div>
          <TechTag label="Quad-Tree Grid" className="text-xs" />
        </div>
      </div>
    </div>
  );
}

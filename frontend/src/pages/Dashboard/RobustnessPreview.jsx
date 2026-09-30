import React from 'react';
import { SectionHeader } from '../../components/ui/SectionHeader.jsx';
import { Icon } from '../../components/ui/Icon.jsx';

export function RobustnessPreview() {
  return (
    <div className="mb-8">
      <SectionHeader icon="science" title="Robustness Sweep" meta="Module 02" />
      <div className="bg-surface-container rounded-xl p-6 border border-surface-container-high flex items-center justify-between">
        <div className="flex gap-4">
          <div className="bg-surface-container-lowest border border-outline-variant p-3 rounded lg:w-32">
             <Icon name="contrast" size="24px" className="text-outline-variant mb-2" />
             <div className="font-label-lg uppercase tracking-wider mb-1">Illumination</div>
             <div className="font-mono text-xs text-primary">Δ ±42.4°</div>
          </div>
          <div className="bg-surface-container-lowest border border-surface-container-high p-3 rounded lg:w-32 opacity-50">
             <Icon name="zoom_in" size="24px" className="text-outline-variant mb-2" />
             <div className="font-label-lg uppercase tracking-wider mb-1">Scale</div>
             <div className="font-mono text-xs text-outline">1.0x - 2.5x</div>
          </div>
          <div className="bg-surface-container-lowest border border-surface-container-high p-3 rounded lg:w-32 opacity-50">
             <Icon name="360" size="24px" className="text-outline-variant mb-2" />
             <div className="font-label-lg uppercase tracking-wider mb-1">Rotation</div>
             <div className="font-mono text-xs text-outline">0° - 360°</div>
          </div>
        </div>
        <div className="text-right">
          <div className="font-headline-md text-primary mb-1">SWEEP READY</div>
          <div className="font-body-md text-on-surface-variant">Stress test initialized.</div>
        </div>
      </div>
    </div>
  );
}

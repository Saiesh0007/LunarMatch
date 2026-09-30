import React from 'react';
import { SectionHeader } from '../../components/ui/SectionHeader.jsx';
import { Button } from '../../components/ui/Button.jsx';
import { Chip } from '../../components/ui/Chip.jsx';
import { Icon } from '../../components/ui/Icon.jsx';

export function PerturbationSetup({
  selectedParam, setSelectedParam,
  stepsGranularity, setStepsGranularity,
  isSweeping, handleRunSweep
}) {
  const params = [
    { id: 'illumination', icon: 'contrast', label: 'Illumination', range: '±90° Incident' },
    { id: 'scale', icon: 'zoom_in', label: 'Scale Sensitivity', range: '0.25x to 4.0x' },
    { id: 'rotation', icon: '360', label: 'In-Plane Rotation', range: '0° to 360°' }
  ];

  return (
    <div className="flex flex-col gap-6">
      <SectionHeader icon="tune" title="Perturbation Engine" meta="P-01" />

      <div className="flex flex-col gap-3">
        {params.map(p => (
          <div 
            key={p.id}
            onClick={() => setSelectedParam(p.id)}
            className={`border rounded-lg p-3 flex items-center gap-4 cursor-pointer transition-colors ${
              selectedParam === p.id 
                ? 'bg-surface-container-high border-outline-variant text-primary shadow-[0_0_10px_rgba(255,255,255,0.05)]' 
                : 'bg-surface-container-lowest border-surface-container-high hover:bg-surface-container'
            }`}
          >
            <Icon name={p.icon} size="24px" className={selectedParam === p.id ? 'text-primary' : 'text-outline'} />
            <div className="flex-1">
              <div className={`font-label-lg uppercase tracking-wider ${selectedParam === p.id ? 'text-primary' : 'text-on-surface'}`}>{p.label}</div>
              <div className="font-mono text-xs text-outline-variant mt-1">{p.range}</div>
            </div>
            {selectedParam === p.id && <div className="h-2 w-2 rounded-full bg-primary" />}
          </div>
        ))}
      </div>

      <div className="bg-surface-container p-4 rounded-xl border border-surface-container-high mt-2">
        <div className="font-label-sm tracking-widest text-outline uppercase mb-3">Sweep Step Granularity</div>
        <div className="flex bg-surface-container-lowest p-1 rounded-lg border border-surface-container-high">
          {['3', '5', '7'].map(step => (
             <Chip layoutId="sweep-step-group" 
               key={step} 
               label={`${step} Steps`} 
               active={stepsGranularity === step} 
               onClick={() => setStepsGranularity(step)}
             />
          ))}
        </div>
      </div>

      <div className="mt-4">
        <Button 
          variant="primary" 
          className="w-full h-12" 
          onClick={handleRunSweep} 
          loading={isSweeping}
          icon={!isSweeping ? "play_arrow" : undefined}
        >
          {isSweeping ? 'Running Sweep...' : 'Execute Baseline Sweep'}
        </Button>
      </div>
    </div>
  );
}

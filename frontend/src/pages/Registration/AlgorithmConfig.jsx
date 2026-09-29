import React from 'react';
import { Chip } from '../../components/ui/Chip.jsx';
import { SectionHeader } from '../../components/ui/SectionHeader.jsx';

export function AlgorithmConfig({ 
  selectedEngine, setSelectedEngine, 
  selectedModel, setSelectedModel 
}) {
  const engines = [
    { id: 'sift', label: 'SIFT (CPU Baseline)' },
    { id: 'rift2', label: 'RIFT2 (Phase Congruency)' },
    { id: 'superpoint', label: 'SuperPoint (Neural)' },
  ];

  const models = [
    { id: 'homography', label: 'Homography (8-DoF)' },
    { id: 'affine', label: 'Affine (6-DoF)' },
  ];

  return (
    <div className="mt-8 pt-8 border-t border-surface-container-high">
      <SectionHeader icon="settings_applications" title="Pipeline Parameters" />
      
      <div className="grid lg:grid-cols-2 gap-8">
        <div>
          <div className="font-label-sm text-outline tracking-widest uppercase mb-3">Feature Extraction Engine</div>
          <div className="flex bg-surface-container-lowest p-1 rounded-lg border border-surface-container-high relative">
            {engines.map(e => (
              <Chip 
                key={e.id}
                label={e.label} 
                active={selectedEngine === e.id}
                onClick={() => setSelectedEngine(e.id)} 
              />
            ))}
          </div>
        </div>
        
        <div>
          <div className="font-label-sm text-outline tracking-widest uppercase mb-3">Geometric Model</div>
          <div className="flex bg-surface-container-lowest p-1 rounded-lg border border-surface-container-high relative">
            {models.map(m => (
              <Chip 
                key={m.id}
                label={m.label} 
                active={selectedModel === m.id}
                onClick={() => setSelectedModel(m.id)} 
              />
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

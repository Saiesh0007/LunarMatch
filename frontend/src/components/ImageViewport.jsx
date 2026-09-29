import React from 'react';
import { Icon } from './ui/Icon.jsx';

export function ImageViewport({ file, roleId, label }) {
  if (!file) {
    return (
      <div className="h-[400px] bg-surface-container-lowest border border-surface-container-high rounded-xl flex flex-col items-center justify-center text-outline-variant relative">
        <div className="absolute top-4 left-4 font-mono text-[10px] uppercase tracking-wider">{label}</div>
        <Icon name="filter_center_focus" size="48px" className="mb-4 opacity-50" />
        <div className="font-label-md tracking-widest uppercase">No Telemetry Feed</div>
        <div className="font-body-md mt-2 opacity-60">Upload or select a dataset</div>
      </div>
    );
  }

  return (
    <div className="h-[400px] bg-surface-container border border-surface-container-high rounded-xl relative overflow-hidden flex items-center justify-center">
      {/* Mocking the actual image with a grid overlay for the aesthetic */}
      <div className="absolute inset-0 bg-surface-container-lowest"
           style={{ backgroundImage: 'linear-gradient(#2a2a2a 1px, transparent 1px), linear-gradient(90deg, #2a2a2a 1px, transparent 1px)', backgroundSize: '20px 20px' }}>
      </div>
      
      {/* Target Crosshair */}
      <div className="absolute flex items-center justify-center z-10 text-primary opacity-20">
        <Icon name="add" size="120px" />
      </div>

      <div className="absolute top-4 left-4 flex gap-2 z-20">
        <div className="bg-black/80 backdrop-blur border border-surface-container-high px-2 py-1 rounded text-[10px] font-mono text-primary uppercase">{label}</div>
        <div className="bg-black/80 backdrop-blur border border-surface-container-high px-2 py-1 rounded text-[10px] font-mono text-outline-variant">{file.size}</div>
      </div>
      
      <div className="absolute bottom-4 left-4 bg-black/80 backdrop-blur border border-surface-container-high p-2 rounded z-20 font-mono text-[10px] text-outline-variant">
        <div className="flex justify-between w-32 mb-1"><span>FILE:</span><span className="text-on-surface truncate ml-2">{file.name}</span></div>
        <div className="flex justify-between w-32 mb-1"><span>RES:</span><span className="text-on-surface">2048x2048</span></div>
        <div className="flex justify-between w-32"><span>BPP:</span><span className="text-on-surface">16-BIT</span></div>
      </div>
    </div>
  );
}

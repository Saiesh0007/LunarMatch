import React from 'react';
import { Button } from '../../components/ui/Button.jsx';
import { Icon } from '../../components/ui/Icon.jsx';

export function StepHeader({ onSwap, onClear, onLoadSample }) {
  return (
    <div className="flex flex-col md:flex-row md:items-center justify-between mb-6 pb-4 border-b border-surface-container-high gap-4">
      <div>
        <div className="font-label-md text-outline tracking-[0.2em] uppercase mb-1">Mission Configuration</div>
        <h1 className="font-headline-lg text-primary uppercase m-0">Image Registration</h1>
      </div>
      
      <div className="flex flex-wrap items-center gap-3">
        <Button variant="ghost" onClick={onSwap} icon="swap_horiz">Swap Frames</Button>
        <Button variant="ghost" onClick={onClear} icon="delete">Clear</Button>
        <Button variant="ghost" onClick={onLoadSample} icon="file_download">Load Sample</Button>
      </div>
    </div>
  );
}

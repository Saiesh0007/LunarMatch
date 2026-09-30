import React from 'react';
import { Button } from '../../components/ui/Button.jsx';
import { StatusDot } from '../../components/ui/StatusDot.jsx';
import { Icon } from '../../components/ui/Icon.jsx';

export function ActionBar({ isReady, isProcessing, onPreview }) {
  return (
    <div className="mt-8 p-4 border border-surface-container-high bg-surface-container-lowest/90 backdrop-blur-md rounded-xl flex flex-col sm:flex-row items-center justify-between sticky bottom-4 z-20 gap-4 shadow-2xl">
      <div className="flex items-center gap-3 w-full sm:w-auto">
        <StatusDot status={isReady ? 'online' : 'offline'} />
        <div>
          <div className="font-label-sm uppercase tracking-widest text-primary font-bold">
            {isReady ? 'Ready for Alignment' : 'Awaiting Both Frames'}
          </div>
          <div className="font-mono text-[11px] text-outline">
            {isReady ? 'Parameters loaded. Click Run Alignment below.' : 'Please provide both Reference and Target images.'}
          </div>
        </div>
      </div>

      <div className="flex items-center gap-3 w-full sm:w-auto justify-end">
        <Button
          variant="primary"
          disabled={!isReady}
          onClick={onPreview}
          loading={isProcessing}
          icon={!isProcessing ? "play_arrow" : undefined}
          className="w-full sm:w-auto shadow-lg shadow-white/5 font-mono text-xs font-bold"
        >
          {isProcessing ? 'Executing Pipeline...' : 'Run Pipeline Alignment'}
        </Button>
      </div>
    </div>
  );
}

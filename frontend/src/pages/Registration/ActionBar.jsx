import React from 'react';
import { Button } from '../../components/ui/Button.jsx';
import { StatusDot } from '../../components/ui/StatusDot.jsx';

export function ActionBar({ isReady, isProcessing, onPreview }) {
  return (
    <div className="mt-8 p-4 border border-surface-container-high bg-surface-container-lowest rounded-xl flex items-center justify-between sticky bottom-4 z-20">
      <div className="flex items-center gap-4 ml-2">
        <StatusDot status={isReady ? 'online' : 'offline'} />
        <span className="font-label-sm uppercase tracking-widest text-outline">
          {isReady ? 'System Ready to Align' : 'Awaiting Dataset Input'}
        </span>
      </div>
      
      <div className="flex items-center gap-3">
        <Button variant="ghost" disabled={!isReady} onClick={onPreview} loading={isProcessing}>
          Run Preview
        </Button>
        <Button variant="primary" disabled={!isReady} icon="arrow_forward">
          Commit to Dashboard
        </Button>
      </div>
    </div>
  );
}

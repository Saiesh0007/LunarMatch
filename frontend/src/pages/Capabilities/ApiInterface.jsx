import React from 'react';
import { SectionHeader } from '../../components/ui/SectionHeader.jsx';
import { Button } from '../../components/ui/Button.jsx';
import { useApiPing } from './hooks/useApiPing.js';

export function ApiInterface() {
  const { latency, isPinging, pingServer, error } = useApiPing();

  const isOnline = !error && latency != null;

  return (
    <div className="mb-8">
      <SectionHeader icon="settings_ethernet" title="API Interface" />
      <div className="bg-surface-container rounded-xl p-5 border border-surface-container-high shadow-lg">
        <div className="font-label-sm tracking-widest text-outline uppercase mb-2">Socket Address</div>
        <div className="flex gap-2">
          <input
            type="text"
            value="http://127.0.0.1:8000"
            readOnly
            className="flex-1 bg-surface-container-lowest border border-surface-container-high rounded p-2 text-on-surface font-mono text-xs focus:outline-none"
          />
          <Button
            type="button"
            variant="ghost"
            icon="wifi_protected_setup"
            onClick={pingServer}
            loading={isPinging}
            className="font-mono text-xs"
          >
            Ping
          </Button>
        </div>

        {error && (
          <div className="mt-2 font-mono text-xs text-error bg-error-container/20 p-2 rounded border border-error/30">
            Connection Error: {error}
          </div>
        )}

        <div className="flex gap-4 mt-4 text-center">
          <div className="flex-1 bg-surface-container-lowest border border-surface-container-high rounded-lg p-3">
            <div className="font-label-md text-outline tracking-wider uppercase mb-1">Live Latency</div>
            <div className="font-mono text-primary text-xl font-bold">
              {latency != null ? latency : '—'}
              <span className="text-xs text-outline-variant ml-1 font-normal">ms</span>
            </div>
          </div>
          <div className="flex-1 bg-surface-container-lowest border border-surface-container-high rounded-lg p-3">
            <div className="font-label-md text-outline tracking-wider uppercase mb-1">Service Status</div>
            <div className={`font-mono text-xl font-bold ${isOnline ? 'text-green-400' : 'text-error'}`}>
              {isPinging ? 'CHECKING...' : isOnline ? 'ONLINE' : 'OFFLINE'}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

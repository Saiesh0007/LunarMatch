import React from 'react';
import { SectionHeader } from '../../components/ui/SectionHeader.jsx';
import { Button } from '../../components/ui/Button.jsx';
import { useApiPing } from './hooks/useApiPing.js';

export function ApiInterface() {
  const { latency, isPinging, pingServer } = useApiPing();

  return (
    <div className="mb-8">
      <SectionHeader icon="settings_ethernet" title="API Interface" />
      <div className="bg-surface-container rounded-xl p-5 border border-surface-container-high">
        <div className="font-label-sm tracking-widest text-outline uppercase mb-2">Socket Address</div>
        <div className="flex gap-2">
          <input 
            type="text" 
            value="http://10.0.2.2:8000" 
            readOnly 
            className="flex-1 bg-surface-container-lowest border border-surface-container-high rounded p-2 text-on-surface-variant font-mono text-sm focus:outline-none focus:border-outline" 
          />
          <Button variant="ghost" icon="wifi_protected_setup" onClick={pingServer} loading={isPinging}>
            Ping
          </Button>
        </div>
        
        <div className="flex gap-4 mt-4 text-center">
          <div className="flex-1 bg-surface-container-lowest border border-surface-container-high rounded p-3">
             <div className="font-label-md text-outline tracking-wider uppercase mb-1">Latency</div>
             <div className="font-mono text-primary text-xl">{latency}<span className="text-xs text-outline-variant ml-1">ms</span></div>
          </div>
          <div className="flex-1 bg-surface-container-lowest border border-surface-container-high rounded p-3">
             <div className="font-label-md text-outline tracking-wider uppercase mb-1">Max FPS</div>
             <div className="font-mono text-primary text-xl">24</div>
          </div>
        </div>
      </div>
    </div>
  );
}

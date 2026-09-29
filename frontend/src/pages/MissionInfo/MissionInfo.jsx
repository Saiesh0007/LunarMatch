import React from 'react';
import { SectionHeader } from '../../components/ui/SectionHeader.jsx';
import { TelemetryRow } from '../../components/ui/TelemetryRow.jsx';
import { TechTag } from '../../components/ui/TechTag.jsx';

export default function MissionInfo() {
  return (
    <div className="max-w-[1200px] mx-auto pb-12">
      <div className="flex items-center gap-4 mb-8 pb-4 border-b border-surface-container-high">
        <h1 className="font-headline-lg text-primary uppercase tracking-[0.1em] m-0">Mission Telemetry</h1>
        <div className="h-6 w-px bg-surface-container-high" />
        <span className="font-label-md text-outline tracking-widest uppercase">TELEMETRY // LIVE-DATA</span>
      </div>

      <div className="grid lg:grid-cols-2 gap-8">
        <div>
          <SectionHeader icon="satellite_alt" title="Mission Parameters" />
          <div className="bg-surface-container-low border border-surface-container rounded-xl p-6 mb-8 mt-6">
            <h2 className="font-headline-md text-primary mb-4">ISRO CH-2 // LUNAR MATCH</h2>
            <p className="text-on-surface-variant font-body-lg mb-6 leading-relaxed">
              Cross-modal lunar image correspondence and registration engine for the Smart India Hackathon (SIH 2026).
              Powered by deep learned matchers and robust deterministic fallback algorithms.
            </p>
            <div className="flex flex-wrap gap-2">
              <TechTag label="OHRC" type="primary" />
              <TechTag label="TMC-2" type="primary" />
              <TechTag label="IIRS" type="primary" />
              <TechTag label="SUPERGLUE" type="secondary" />
              <TechTag label="RIFT2" type="secondary" />
            </div>
          </div>
        </div>

        <div>
           <SectionHeader icon="radar" title="Engine Telemetry (Last 3 Jobs)" />
           <div className="bg-surface-container border border-surface-container-high rounded-xl overflow-hidden mt-6 p-4 pt-1">
             <div className="flex items-center justify-between text-outline font-label-sm uppercase tracking-wider mb-2 mt-4 px-2">
                 <span>Run ID</span>
                 <div className="flex w-40 justify-between mr-24">
                   <span className="text-right w-16">Inliers</span>
                   <span className="text-right w-16">RMSE</span>
                 </div>
             </div>
             
             <TelemetryRow 
               id="JOB-489"
               inliers={842}
               rmse={1.04}
               status="baseline"
             />
             <TelemetryRow 
               id="JOB-488"
               inliers={610}
               rmse={1.89}
               status="warning"
             />
             <TelemetryRow 
               id="JOB-487"
               inliers={123}
               rmse={4.50}
               status="degraded"
             />
           </div>
        </div>
      </div>
    </div>
  );
}

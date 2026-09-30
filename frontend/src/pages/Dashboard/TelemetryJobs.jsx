import React from 'react';
import { SectionHeader } from '../../components/ui/SectionHeader.jsx';
import { TelemetryRow } from '../../components/ui/TelemetryRow.jsx';

export function TelemetryJobs({ jobs = [] }) {
  return (
    <div>
      <SectionHeader icon="list_alt" title="Recent Telemetry" meta="Module 05" />
      <div className="bg-surface-container rounded-xl p-5 border border-surface-container-high">
        <div className="flex items-center justify-between py-2 border-b border-surface-container-highest mb-2">
          <div className="font-label-sm tracking-widest text-outline uppercase">JOB_ID</div>
          <div className="font-label-sm tracking-widest text-outline uppercase w-16 text-right">INLIERS</div>
          <div className="font-label-sm tracking-widest text-outline uppercase w-16 text-right">RMSE</div>
          <div className="font-label-sm tracking-widest text-outline uppercase w-24 text-right">STATUS</div>
        </div>
        
        <div>
          {jobs.map(job => (
            <TelemetryRow key={job.id} {...job} />
          ))}
          {jobs.length === 0 && (
            <div className="py-6 text-center text-outline-variant font-label-md">NO RECENT JOBS</div>
          )}
        </div>
      </div>
    </div>
  );
}

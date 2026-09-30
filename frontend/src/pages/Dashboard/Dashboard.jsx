import React, { useEffect } from 'react';
import { useDashboardData } from './hooks/useDashboardData.js';
import { MissionBanner } from './MissionBanner.jsx';
import { KpiGrid } from './KpiGrid.jsx';
import { StudioPreview } from './StudioPreview.jsx';
import { RobustnessPreview } from './RobustnessPreview.jsx';
import { ArchitectureSummary } from './ArchitectureSummary.jsx';
import { QuickRunPanel } from './QuickRunPanel.jsx';
import { TelemetryJobs } from './TelemetryJobs.jsx';

export default function Dashboard() {
  const { pipelineStatus, isPipelineLoading } = useDashboardData();

  // Optionally set document title or breadcrumbs if we had a robust layout context
  
  return (
    <div className="max-w-[1600px] mx-auto pb-12">
      <MissionBanner />
      
      {!isPipelineLoading && pipelineStatus && (
        <>
          <KpiGrid data={pipelineStatus.kpis} />
          
          <div className="grid lg:grid-cols-12 gap-8 lg:gap-12">
            <div className="lg:col-span-7">
              <StudioPreview />
              <RobustnessPreview />
              <ArchitectureSummary />
            </div>
            
            <div className="lg:col-span-5 relative">
              <div className="sticky top-24">
                <QuickRunPanel />
                <TelemetryJobs jobs={pipelineStatus.jobs} />
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
}

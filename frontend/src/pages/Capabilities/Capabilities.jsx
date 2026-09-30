import React from 'react';
import { PIPELINE_STAGES } from '../../data/pipelineStages.js';
import { ENGINE_CAPABILITIES } from '../../data/engineCapabilities.js';
import { PipelineStageCard } from './PipelineStageCard.jsx';
import { EngineCapabilityCard } from './EngineCapabilityCard.jsx';
import { ApiInterface } from './ApiInterface.jsx';
import { MissionSpec } from './MissionSpec.jsx';
import { ConsoleStream } from './ConsoleStream.jsx';
import { SectionHeader } from '../../components/ui/SectionHeader.jsx';

export default function Capabilities() {
  return (
    <div className="max-w-[1400px] mx-auto pb-12">
      <div className="flex items-center gap-4 mb-8 pb-4 border-b border-surface-container-high">
        <h1 className="font-headline-lg text-primary uppercase tracking-[0.1em] m-0">Architecture</h1>
        <div className="h-6 w-px bg-surface-container-high" />
        <span className="font-label-md text-outline tracking-widest uppercase">SPEC // SYS-DOC-26166</span>
      </div>

      <div className="grid xl:grid-cols-12 gap-8 xl:gap-12">
        <div className="xl:col-span-7">
          <SectionHeader icon="account_tree" title="Linear Execution Pipeline" />
          
          <div className="mt-6">
            {PIPELINE_STAGES.map((stage, index) => (
              <PipelineStageCard 
                key={stage.id} 
                stage={stage} 
                isLast={index === PIPELINE_STAGES.length - 1} 
              />
            ))}
          </div>
        </div>

        <div className="xl:col-span-5 relative">
          <div className="sticky top-24">
            <ApiInterface />
            <MissionSpec />
            
            <div className="mb-8">
              <SectionHeader icon="memory" title="Compute Engines" />
              <div>
                {ENGINE_CAPABILITIES.map(cap => (
                  <EngineCapabilityCard key={cap.id} capability={cap} />
                ))}
              </div>
            </div>
            
            <SectionHeader icon="terminal" title="Live Boot Stream" />
            <ConsoleStream />
          </div>
        </div>
      </div>
    </div>
  );
}

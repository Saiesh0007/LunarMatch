import React from 'react';
import { useRobustnessLab } from './hooks/useRobustnessLab.js';
import { PerturbationSetup } from './PerturbationSetup.jsx';
import { DegradationChart } from './DegradationChart.jsx';
import { OpticalInspection } from './OpticalInspection.jsx';

export default function RobustnessLab() {
  const {
    selectedParam, setSelectedParam,
    selectedStep, setSelectedStep,
    isSweeping, handleRunSweep,
    stepsGranularity, setStepsGranularity,
    dataSteps
  } = useRobustnessLab();

  return (
    <div className="max-w-[1400px] mx-auto pb-12">
      <div className="flex items-center gap-4 mb-8 pb-4 border-b border-surface-container-high">
        <h1 className="font-headline-lg text-primary uppercase tracking-[0.1em] m-0">Stress Laboratory</h1>
        <div className="h-6 w-px bg-surface-container-high" />
        <span className="font-label-md text-outline tracking-widest uppercase">LAB-EXP // 03-SWEEP</span>
      </div>

      <div className="grid lg:grid-cols-12 gap-6 lg:gap-8 min-h-[600px]">
        <div className="lg:col-span-4 h-full">
          <PerturbationSetup
            selectedParam={selectedParam} setSelectedParam={setSelectedParam}
            stepsGranularity={stepsGranularity} setStepsGranularity={setStepsGranularity}
            isSweeping={isSweeping} handleRunSweep={handleRunSweep}
          />
        </div>
        <div className="lg:col-span-4 h-full">
          <DegradationChart
            dataSteps={dataSteps}
            selectedStep={selectedStep}
            onSelectStep={setSelectedStep}
          />
        </div>
        <div className="lg:col-span-4 h-full">
          <OpticalInspection selectedStep={selectedStep} dataSteps={dataSteps} />
        </div>
      </div>
    </div>
  );
}

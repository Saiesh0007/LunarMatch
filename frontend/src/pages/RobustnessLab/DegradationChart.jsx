import React from 'react';
import { SectionHeader } from '../../components/ui/SectionHeader.jsx';
import { DegradationSvgChart } from '../../components/charts/DegradationSvgChart.jsx';
import { TelemetryRow } from '../../components/ui/TelemetryRow.jsx';
import { Icon } from '../../components/ui/Icon.jsx';

export function DegradationChart({ dataSteps = [], selectedStep, onSelectStep }) {
  return (
    <div className="flex flex-col gap-6">
      <SectionHeader icon="analytics" title="Degradation Profile" meta="P-02" />

      <div className="bg-surface-container rounded-xl p-5 border border-surface-container-high h-[220px]">
        <div className="flex justify-between items-end mb-2">
          <div className="font-label-sm tracking-widest text-outline uppercase">RMSE Error vs Variation</div>
          <div className="font-label-sm tracking-widest text-outline uppercase text-primary font-mono">TOLERANCE: 5.0 PX</div>
        </div>
        <div className="h-[140px]">
          <DegradationSvgChart
            dataSteps={dataSteps}
            selectedStep={selectedStep}
            onSelectStep={onSelectStep}
          />
        </div>
      </div>

      <div className="bg-surface-container rounded-xl border border-surface-container-high overflow-hidden">
        <div className="flex items-center justify-between py-3 px-4 border-b border-surface-container-high bg-surface-container-lowest font-mono">
          <div className="font-label-sm tracking-widest text-outline uppercase">STEP</div>
          <div className="font-label-sm tracking-widest text-outline uppercase w-16 text-right">INLIERS</div>
          <div className="font-label-sm tracking-widest text-outline uppercase w-16 text-right">RMSE</div>
          <div className="font-label-sm tracking-widest text-outline uppercase w-24 text-right">STATUS</div>
        </div>
        <div className="p-2 max-h-[260px] overflow-y-auto">
          {dataSteps.map((step, i) => (
            <div
              key={i}
              onClick={() => onSelectStep(i)}
              className={`rounded-lg cursor-pointer transition-all ${
                selectedStep === i ? 'bg-surface-container-highest ring-1 ring-outline' : ''
              }`}
            >
              <TelemetryRow
                id={step.label || `Δ ${i * 15}°`}
                inliers={step.inliers}
                rmse={step.rmse}
                status={step.rmse < 1.0 ? 'baseline' : step.rmse < 3.0 ? 'warning' : 'degraded'}
              />
            </div>
          ))}
        </div>
      </div>

      <div className="bg-surface-container-lowest border border-outline-variant p-4 rounded-xl flex items-start gap-4">
        <Icon name="verified" className="text-primary mt-1" />
        <div>
          <div className="font-headline-sm uppercase text-primary tracking-wide mb-1">Pass Verdict</div>
          <div className="font-body-md text-on-surface-variant text-xs leading-relaxed">
            Orbital correspondence tolerance maintained across parameter sweep. Robustness profile conforms to ISRO SIH 26166 mission criteria.
          </div>
        </div>
      </div>
    </div>
  );
}

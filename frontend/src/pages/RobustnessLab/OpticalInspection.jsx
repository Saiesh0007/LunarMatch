import React from 'react';
import { SectionHeader } from '../../components/ui/SectionHeader.jsx';
import { Icon } from '../../components/ui/Icon.jsx';
import { Button } from '../../components/ui/Button.jsx';
import { Badge } from '../../components/ui/Badge.jsx';
import { apiClient } from '../../api/client.js';

export function OpticalInspection({ selectedStep, dataSteps = [] }) {
  const currentStep = dataSteps[selectedStep] || { label: `Step ${selectedStep + 1}`, rmse: 0.84, inliers: 1400 };
  const previewImgUrl = apiClient.getPreviewUrl('demo_pair_a_ref');

  return (
    <div className="flex flex-col gap-6 h-full">
      <SectionHeader icon="visibility" title="Optical Inspection" meta="P-03" />

      <div className="bg-surface-container rounded-xl p-5 border border-surface-container-high flex flex-col flex-1">
        <div className="font-label-sm tracking-widest text-outline uppercase mb-3 flex items-center justify-between">
          <span>Spatial Residual Inspection</span>
          <span className="text-primary font-mono font-bold">{currentStep.label || `Δ${selectedStep * 15}°`}</span>
        </div>

        <div className="flex-1 min-h-[300px] border border-surface-container-high rounded-lg bg-[#080808] relative overflow-hidden flex items-center justify-center group shadow-inner">
          {/* Base terrain image */}
          <img
            src={previewImgUrl}
            alt="Terrain Inspection"
            className="w-full h-full object-cover opacity-60 filter contrast-125"
            onError={(e) => {
              e.currentTarget.style.display = 'none';
            }}
          />

          {/* Grid overlay */}
          <div
            className="absolute inset-0 opacity-30 pointer-events-none"
            style={{
              backgroundImage: 'linear-gradient(#444 1px, transparent 1px), linear-gradient(90deg, #444 1px, transparent 1px)',
              backgroundSize: '40px 40px'
            }}
          />

          {/* Simulated Residual Feature Vectors */}
          <svg className="absolute inset-0 w-full h-full pointer-events-none" viewBox="0 0 400 300">
            {Array.from({ length: 12 }).map((_, i) => {
              const x = 50 + (i % 4) * 90 + ((i * 17) % 25);
              const y = 50 + Math.floor(i / 4) * 80 + ((i * 13) % 20);
              const dx = ((i % 3) - 1) * (1 + selectedStep * 2.5);
              const dy = (((i + 1) % 3) - 1) * (1 + selectedStep * 2.5);
              return (
                <g key={i}>
                  <circle cx={x} cy={y} r="3" fill="#ffffff" />
                  <line
                    x1={x}
                    y1={y}
                    x2={x + dx}
                    y2={y + dy}
                    stroke="#ffffff"
                    strokeWidth="1.5"
                    strokeDasharray="2 2"
                  />
                  <circle cx={x + dx} cy={y + dy} r="2" fill="#8e9192" />
                </g>
              );
            })}
          </svg>

          <div className="absolute top-4 left-4 z-10">
            <Badge variant="status" label="T_0 BASE REF" className="bg-black/80 backdrop-blur-md border border-surface-container-high" />
          </div>

          <div className="absolute bottom-4 left-0 right-0 px-4 flex justify-between items-end z-10">
            <div className="font-mono text-[10px] text-outline-variant bg-black/80 backdrop-blur-md px-2.5 py-1.5 rounded border border-surface-container-high">
              VECTORS: {currentStep.inliers || 1400} PTS
            </div>
            <div className="bg-black/80 backdrop-blur-md p-2 rounded border border-surface-container-high flex flex-col items-end gap-1">
              <div className="text-[9px] font-mono text-outline uppercase tracking-wider">RESIDUAL SCALE</div>
              <div className="h-2 w-28 rounded bg-gradient-to-r from-[#ffffff] via-[#8e9192] to-[#ef4444] relative">
                <div className="absolute -top-3.5 left-0 text-[9px] font-mono">0px</div>
                <div className="absolute -top-3.5 right-0 text-[9px] font-mono">5px</div>
              </div>
            </div>
          </div>
        </div>

        <div className="flex gap-3 mt-4">
          <Button
            type="button"
            variant="ghost"
            className="flex-1 font-label-md py-2.5 border-surface-container-high font-mono text-xs"
            onClick={() => window.open(previewImgUrl, '_blank')}
          >
            Export Frame
          </Button>
          <Button
            type="button"
            variant="ghost"
            className="flex-1 font-label-md py-2.5 border-surface-container-high font-mono text-xs"
            onClick={() => window.open('http://127.0.0.1:8000/docs', '_blank')}
          >
            Telemetry API
          </Button>
        </div>
      </div>
    </div>
  );
}

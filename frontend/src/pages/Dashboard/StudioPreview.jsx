import React from 'react';
import { SectionHeader } from '../../components/ui/SectionHeader.jsx';
import { HomographySvgChart } from '../../components/charts/HomographySvgChart.jsx';
import { Icon } from '../../components/ui/Icon.jsx';

export function StudioPreview() {
  return (
    <div className="mb-8">
      <SectionHeader icon="preview" title="Studio Preview" meta="Module 01" />
      
      <div className="bg-surface-container rounded-xl p-6 border border-surface-container-high flex flex-col md:flex-row gap-6">
        <div className="flex-1 flex gap-2 h-48">
          <div className="flex-1 border border-outline-variant bg-surface-container-lowest relative overflow-hidden rounded">
            <div className="absolute top-2 left-2 bg-black/60 px-2 py-1 rounded text-[10px] font-mono text-outline-variant uppercase">Frame A</div>
            <div className="absolute inset-0 flex items-center justify-center text-surface-container-highest">
              <Icon name="satellite_alt" size="48px" />
            </div>
          </div>
          <div className="flex-1 border border-outline-variant bg-surface-container-lowest relative overflow-hidden rounded">
            <div className="absolute top-2 left-2 bg-black/60 px-2 py-1 rounded text-[10px] font-mono text-outline-variant uppercase">Frame B (Warped)</div>
            <div className="absolute inset-0 flex items-center justify-center text-surface-container-highest">
               <Icon name="transform" size="48px" />
            </div>
          </div>
        </div>
        
        <div className="md:w-64 flex flex-col justify-between">
          <div>
            <div className="font-label-md text-outline tracking-widest uppercase mb-2">Homography Convergence</div>
            <div className="h-16 mb-4">
              <HomographySvgChart />
            </div>
          </div>
          
          <div className="bg-surface-container-lowest border border-surface-container-high p-3 rounded text-sm text-on-surface-variant font-mono">
            <div className="flex justify-between mb-1"><span>ITERATIONS:</span><span className="text-primary">250</span></div>
            <div className="flex justify-between mb-1"><span>INLIER RATIO:</span><span className="text-primary">82.4%</span></div>
            <div className="flex justify-between"><span>CONFIDENCE:</span><span className="text-primary">0.999</span></div>
          </div>
        </div>
      </div>
    </div>
  );
}

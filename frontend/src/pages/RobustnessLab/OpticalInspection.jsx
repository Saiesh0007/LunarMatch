import React from 'react';
import { SectionHeader } from '../../components/ui/SectionHeader.jsx';
import { Icon } from '../../components/ui/Icon.jsx';
import { Button } from '../../components/ui/Button.jsx';
import { Badge } from '../../components/ui/Badge.jsx';

export function OpticalInspection({ selectedStep }) {
  // We mirror the visual of vectors over an image using styling
  return (
    <div className="flex flex-col gap-6 h-full">
      <SectionHeader icon="visibility" title="Optical Inspection" meta="P-03" />

      <div className="bg-surface-container rounded-xl p-5 border border-surface-container-high flex flex-col flex-1">
        <div className="font-label-sm tracking-widest text-outline uppercase mb-3">Spatial Residual Heatmap (Step: <span className="text-primary">Δ{selectedStep * 15}°</span>)</div>
        
        <div className="flex-1 min-h-[300px] border border-surface-container-high rounded bg-surface-container-lowest relative overflow-hidden flex items-center justify-center">
          <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyMCIgaGVpZ2h0PSIyMCI+CjxwYXRoIGQ9Ik0wIDIwaDIwdkgyMHoiIGZpbGw9Im5vbmUiIHN0cm9rZT0iIzIyMiIHN0cm9rZS13aWR0aD0iMSIvPgo8L3N2Zz4=')] opacity-50" />
          
          <Icon name="satellite_alt" size="120px" className="text-surface-container-highest" />
          
          <div className="absolute top-4 left-4">
             <Badge variant="status" label="T_0 BASE REF" className="bg-black/80 backdrop-blur-md" />
          </div>
          
          <div className="absolute bottom-4 left-0 right-0 px-4 flex justify-between items-end">
            <div className="font-mono text-[10px] text-outline-variant bg-black/80 px-2 py-1 rounded">MATCHING VECTORS</div>
            <div className="h-2 w-32 rounded bg-gradient-to-r from-[#ffffff] via-[#8e9192] to-[#ffb4ab] border border-outline-variant opacity-80 relative">
               <div className="absolute -top-4 left-0 text-[10px] font-mono">0px</div>
               <div className="absolute -top-4 right-0 text-[10px] font-mono">5px</div>
            </div>
          </div>
        </div>

        <div className="flex gap-4 mt-4">
          <Button variant="ghost" className="flex-1 font-label-md py-2 border-surface-container-high">Export T_MAX Vector</Button>
          <Button variant="ghost" className="flex-1 font-label-md py-2 border-surface-container-high">Raw Inspection Log</Button>
        </div>
      </div>
    </div>
  );
}

import React from 'react';
import { SectionHeader } from '../../components/ui/SectionHeader.jsx';

export function ResultPanel({ result }) {
  if (!result) return null;
  
  const baseUrl = 'http://127.0.0.1:8000';
  const overlayUrl = result.outputs?.overlay_image_url ? `${baseUrl}${result.outputs.overlay_image_url}` : null;
  const matchUrl = result.outputs?.correspondence_image_url ? `${baseUrl}${result.outputs.correspondence_image_url}` : null;
  
  return (
    <div className="mt-12 pt-8 border-t border-surface-container-high animate-in fade-in slide-in-from-bottom-4 duration-500">
      <SectionHeader icon="analytics" title="Registration Output" meta={`RUN: ${result.run_id?.substring(0,8)}`} />
      
      <div className="grid lg:grid-cols-3 gap-6 mt-6">
        <div className="lg:col-span-1 flex flex-col gap-4">
          <div className="bg-surface-container p-5 rounded-xl border border-surface-container-high">
            <div className="font-label-sm uppercase tracking-widest text-outline mb-4">Pipeline Telemetry</div>
            <div className="space-y-3 font-mono text-sm">
              <div className="flex justify-between">
                <span className="text-outline-variant">Status</span>
                <span className={result.status === 'SUCCESS' ? 'text-green-400' : 'text-error'}>{result.status}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-outline-variant">Engine</span>
                <span className="text-on-surface">{result.configuration?.feature_method || 'N/A'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-outline-variant">Inliers</span>
                <span className="text-primary font-bold">{result.metrics?.inlier_count || 0}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-outline-variant">RMSE (px)</span>
                <span className="text-on-surface">{result.metrics?.rmse_px?.toFixed(2) || 'N/A'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-outline-variant">Execution Mode</span>
                <span className="text-on-surface">{result.execution_mode}</span>
              </div>
            </div>
          </div>
          
          {result.failure_reason && (
             <div className="p-4 bg-error-container/20 border border-error/50 rounded-xl">
               <div className="font-label-sm text-error uppercase mb-2">Failure Reason</div>
               <div className="text-sm text-error/90">{result.failure_reason}</div>
             </div>
          )}
        </div>
        
        <div className="lg:col-span-2 flex flex-col gap-6">
          {overlayUrl && (
            <div className="rounded-xl overflow-hidden border border-surface-container-high relative">
              <div className="absolute top-2 left-2 bg-black/80 backdrop-blur text-[10px] font-mono text-primary px-2 py-1 rounded">OVERLAY</div>
              <img src={overlayUrl} alt="Overlay" className="w-full h-auto object-contain bg-black" />
            </div>
          )}
          
          {matchUrl && (
            <div className="rounded-xl overflow-hidden border border-surface-container-high relative">
              <div className="absolute top-2 left-2 bg-black/80 backdrop-blur text-[10px] font-mono text-primary px-2 py-1 rounded">CORRESPONDENCES</div>
              <img src={matchUrl} alt="Matches" className="w-full h-auto object-contain bg-black" />
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

import React, { useState } from 'react';
import { SectionHeader } from '../../components/ui/SectionHeader.jsx';
import { Icon } from '../../components/ui/Icon.jsx';
import { Button } from '../../components/ui/Button.jsx';

export function ResultPanel({ result }) {
  if (!result) return null;

  const baseUrl = window.location.port === '3000' ? '' : 'http://127.0.0.1:8000';
  const outputs = result.outputs || {};

  const [activeTab, setActiveTab] = useState('overlay');

  const views = [
    { id: 'overlay', label: 'Registered Overlay', url: outputs.overlay_image_url ? `${baseUrl}${outputs.overlay_image_url}` : null },
    { id: 'correspondences', label: 'Feature Matches', url: outputs.correspondence_image_url ? `${baseUrl}${outputs.correspondence_image_url}` : null },
    { id: 'difference', label: 'Difference Map', url: outputs.difference_image_url ? `${baseUrl}${outputs.difference_image_url}` : null },
    { id: 'registered', label: 'Warped Image', url: outputs.registered_image_url ? `${baseUrl}${outputs.registered_image_url}` : null },
  ].filter(v => v.url);

  const statusStr = (result.status || '').toUpperCase();
  const isSuccess = statusStr === 'SUCCESS' || statusStr === 'SUCCESSFUL' || statusStr === 'COMPLETED';

  return (
    <div className="mt-12 pt-8 border-t border-surface-container-high">
      <SectionHeader
        icon="analytics"
        title="Registration Output & Diagnostics"
        meta={`ID: ${result.run_id?.substring(0, 18) || 'LIVE'}`}
      />

      {/* Metric Cards Banner */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6">
        <div className="bg-surface-container-lowest border border-surface-container-high p-4 rounded-xl flex flex-col justify-between">
          <span className="font-label-sm text-outline uppercase tracking-wider">Status</span>
          <div className="flex items-center gap-2 mt-2">
            <span className={`w-2.5 h-2.5 rounded-full ${isSuccess ? 'bg-green-500 shadow-[0_0_8px_#22c55e]' : 'bg-red-500 shadow-[0_0_8px_#ef4444]'}`} />
            <span className={`font-mono text-base font-bold ${isSuccess ? 'text-green-400' : 'text-error'}`}>
              {result.status}
            </span>
          </div>
        </div>

        <div className="bg-surface-container-lowest border border-surface-container-high p-4 rounded-xl flex flex-col justify-between">
          <span className="font-label-sm text-outline uppercase tracking-wider">RANSAC Inliers</span>
          <div className="font-mono text-xl font-bold text-primary mt-2">
            {result.metrics?.ransac_inliers ?? result.metrics?.inlier_count ?? 0}
            <span className="text-xs font-normal text-outline-variant ml-1">/ {result.metrics?.candidate_matches || 0}</span>
          </div>
        </div>

        <div className="bg-surface-container-lowest border border-surface-container-high p-4 rounded-xl flex flex-col justify-between">
          <span className="font-label-sm text-outline uppercase tracking-wider">RMSE (Pixel Error)</span>
          <div className="font-mono text-xl font-bold text-on-surface mt-2">
            {result.metrics?.rmse_px != null ? `${result.metrics.rmse_px.toFixed(3)} px` : 'N/A'}
          </div>
        </div>

        <div className="bg-surface-container-lowest border border-surface-container-high p-4 rounded-xl flex flex-col justify-between">
          <span className="font-label-sm text-outline uppercase tracking-wider">Spatial Coverage</span>
          <div className="font-mono text-xl font-bold text-primary mt-2">
            {result.metrics?.spatial_coverage != null ? `${result.metrics.spatial_coverage.toFixed(1)}%` : '100%'}
          </div>
        </div>
      </div>

      <div className="grid lg:grid-cols-3 gap-6 mt-6">
        {/* Left Telemetry Column */}
        <div className="lg:col-span-1 flex flex-col gap-4">
          <div className="bg-surface-container-lowest p-5 rounded-xl border border-surface-container-high shadow-lg">
            <div className="font-label-sm uppercase tracking-widest text-outline mb-4 flex items-center gap-2">
              <Icon name="terminal" size="16px" />
              Pipeline Execution Details
            </div>

            <div className="space-y-3 font-mono text-xs">
              <div className="flex justify-between border-b border-surface-container pb-2">
                <span className="text-outline">Engine</span>
                <span className="text-on-surface uppercase font-semibold">{result.configuration?.feature_method || 'sift'}</span>
              </div>
              <div className="flex justify-between border-b border-surface-container pb-2">
                <span className="text-outline">Geometric Model</span>
                <span className="text-on-surface uppercase font-semibold">{result.configuration?.geometric_model || 'homography'}</span>
              </div>
              <div className="flex justify-between border-b border-surface-container pb-2">
                <span className="text-outline">Keypoints Ref / Mov</span>
                <span className="text-on-surface">{result.metrics?.keypoints_reference || 0} / {result.metrics?.keypoints_moving || 0}</span>
              </div>
              <div className="flex justify-between border-b border-surface-container pb-2">
                <span className="text-outline">Inlier Ratio</span>
                <span className="text-primary font-semibold">{result.metrics?.inlier_ratio != null ? `${result.metrics.inlier_ratio.toFixed(1)}%` : 'N/A'}</span>
              </div>
              <div className="flex justify-between border-b border-surface-container pb-2">
                <span className="text-outline">Runtime</span>
                <span className="text-on-surface">{result.metrics?.runtime_ms ? `${result.metrics.runtime_ms.toFixed(1)} ms` : 'N/A'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-outline">Execution Mode</span>
                <span className="text-primary font-semibold uppercase">{result.execution_mode || 'LIVE'}</span>
              </div>
            </div>
          </div>

          {result.failure_reason && (
            <div className="p-4 bg-error-container/10 border border-error/30 rounded-xl">
              <div className="font-label-sm text-error uppercase mb-1 flex items-center gap-1.5 font-bold">
                <Icon name="warning" size="16px" />
                Failure Reason / Note
              </div>
              <div className="font-mono text-xs text-error/90">{result.failure_reason}</div>
            </div>
          )}

          {result.metrics?.confidence_explanation && (
            <div className="p-4 bg-surface-container-lowest border border-surface-container-high rounded-xl">
              <div className="font-label-sm text-outline uppercase mb-1 flex items-center gap-1.5">
                <Icon name="verified" size="16px" className="text-primary" />
                Quality Assessment
              </div>
              <div className="font-mono text-xs text-on-surface-variant leading-relaxed">
                {result.metrics.confidence_explanation}
              </div>
            </div>
          )}

          {/* Transformation Matrix */}
          {result.transformation_matrix && (
            <div className="p-4 bg-surface-container-lowest border border-surface-container-high rounded-xl font-mono text-[10px]">
              <div className="font-label-sm text-outline uppercase mb-2">Homography / Transform Matrix</div>
              <div className="bg-surface-container p-2 rounded border border-surface-container-high space-y-1">
                {result.transformation_matrix.map((row, rIdx) => (
                  <div key={rIdx} className="flex justify-between text-on-surface">
                    {row.map((val, cIdx) => (
                      <span key={cIdx} className="w-1/3 text-right">
                        {typeof val === 'number' ? val.toFixed(4) : val}
                      </span>
                    ))}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Right Artifact Viewport Column */}
        <div className="lg:col-span-2 flex flex-col gap-4">
          {/* Artifact Tabs */}
          {views.length > 0 && (
            <div className="flex bg-surface-container-lowest border border-surface-container-high p-1 rounded-lg gap-1 overflow-x-auto">
              {views.map(view => (
                <button
                  key={view.id}
                  type="button"
                  onClick={() => setActiveTab(view.id)}
                  className={`px-4 py-2 rounded-md font-mono text-xs uppercase tracking-wider transition-all whitespace-nowrap ${
                    activeTab === view.id
                      ? 'bg-primary text-black font-bold shadow'
                      : 'text-outline hover:text-on-surface hover:bg-surface-container'
                  }`}
                >
                  {view.label}
                </button>
              ))}
            </div>
          )}

          {/* Active Artifact Display */}
          <div className="rounded-xl overflow-hidden border border-surface-container-high bg-[#050505] min-h-[420px] flex items-center justify-center relative shadow-xl">
            {views.find(v => v.id === activeTab)?.url ? (
              <img
                src={views.find(v => v.id === activeTab).url}
                alt={activeTab}
                className="w-full h-auto max-h-[540px] object-contain rounded"
              />
            ) : (
              <div className="text-outline font-mono text-xs p-6 text-center">
                No visual artifact available for this tab.
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

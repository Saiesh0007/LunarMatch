"use client";

import React from "react";
import { LUNAR_METADATA, TIE_POINTS, SPATIAL_GRID_4X4, PRESET_PAIRS } from "../data/lunarData";

interface ExportModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function ExportModal({ isOpen, onClose }: ExportModalProps) {
  if (!isOpen) return null;

  const downloadJson = () => {
    const report = {
      metadata: LUNAR_METADATA,
      timestamp: new Date().toISOString(),
      metrics: PRESET_PAIRS.pair_a.metrics,
      tiePoints: TIE_POINTS,
      spatialGrid: SPATIAL_GRID_4X4
    };
    const blob = new Blob([JSON.stringify(report, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `lunarmatch_flight_telemetry_${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const downloadCsv = () => {
    let csv = "match_id,ref_x,ref_y,mov_x,mov_y,residual_pixels,score,status\n";
    TIE_POINTS.forEach(pt => {
      csv += `${pt.id},${pt.refX},${pt.refY},${pt.movX},${pt.movY},${pt.residual},${pt.score},${pt.inlier ? "refined" : "outlier"}\n`;
    });
    const blob = new Blob([csv], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `lunarmatch_tie_points_${Date.now()}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal-window" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <span style={{ fontWeight: 800, fontSize: "0.95rem", letterSpacing: "0.08em", textTransform: "uppercase" }}>
            EXPORT REGISTRATION REPORT &amp; MANIFEST
          </span>
          <button className="modal-close-btn" onClick={onClose}>&times;</button>
        </div>

        <p style={{ fontSize: "0.78rem", color: "var(--text-secondary)", marginBottom: 16 }}>
          Generates SIH-compliant scientific deliverables for Problem Statement 26166, including JSON flight telemetry, CSV tie-point coordinates with sub-pixel residuals, and geometric homography parameters.
        </p>

        <div style={{ display: "flex", flexDirection: "column", gap: 12, marginBottom: 20 }}>
          <div style={{ background: "var(--surface-elevated)", padding: 12, borderRadius: "var(--radius-sm)", border: "1px solid var(--border)" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 6 }}>
              <strong style={{ fontSize: "0.8rem" }}>JSON Scientific Telemetry Package</strong>
              <span className="tag-badge">.JSON</span>
            </div>
            <p style={{ fontSize: "0.72rem", color: "var(--text-tertiary)", marginBottom: 10 }}>
              Contains complete metric breakdown, runtime profiling, Sinkhorn assignment matrices, and QA acceptance flags.
            </p>
            <button
              className="btn-primary-action"
              style={{ width: "auto", padding: "8px 16px", fontSize: "0.74rem", marginTop: 0 }}
              onClick={downloadJson}
            >
              DOWNLOAD TELEMETRY JSON
            </button>
          </div>

          <div style={{ background: "var(--surface-elevated)", padding: 12, borderRadius: "var(--radius-sm)", border: "1px solid var(--border)" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 6 }}>
              <strong style={{ fontSize: "0.8rem" }}>Tie-Points Coordinates &amp; Residuals</strong>
              <span className="tag-badge">.CSV</span>
            </div>
            <p style={{ fontSize: "0.72rem", color: "var(--text-tertiary)", marginBottom: 10 }}>
              Full table of keypoint pairs (x_ref, y_ref) &harr; (x_mov, y_mov), sub-pixel residuals in pixels, and MAGSAC++ consensus status.
            </p>
            <button
              className="btn-primary-action"
              style={{ width: "auto", padding: "8px 16px", fontSize: "0.74rem", marginTop: 0 }}
              onClick={downloadCsv}
            >
              DOWNLOAD TIE-POINTS CSV
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

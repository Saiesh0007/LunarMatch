"use client";

import React from "react";
import { PIPELINE_STAGES } from "../data/lunarData";

export default function ArchitectureTab() {
  return (
    <div>
      <div className="card-box" style={{ marginBottom: 20 }}>
        <div className="card-header">
          <span className="card-header-title">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <polygon points="12 2 2 7 12 12 22 7 12 2" />
              <polyline points="2 17 12 22 22 17" />
              <polyline points="2 12 12 17 22 12" />
            </svg>
            5-STAGE SCIENTIFIC PIPELINE SPECIFICATION
          </span>
          <span className="tag-badge badge-white">MATHEMATICAL FORMULATIONS</span>
        </div>

        <div className="pipeline-flow-diagram">
          {PIPELINE_STAGES.map(stage => (
            <div key={stage.step} className="flow-stage-card">
              <div style={{ display: "flex", flexDirection: "column", alignItems: "flex-start" }}>
                <span className="flow-badge">STAGE {stage.step}</span>
              </div>

              <div>
                <h4 style={{ fontSize: "0.92rem", marginBottom: 4 }}>{stage.name}</h4>
                <p style={{ fontSize: "0.78rem", color: "var(--text-secondary)", lineHeight: 1.45 }}>
                  {stage.description}
                </p>
              </div>

              <div className="flow-math-col">
                {stage.math}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Hardware & Offline Profile */}
      <div className="card-box">
        <div className="card-header">
          <span className="card-header-title">HARDWARE &amp; OPERATIONAL PROFILE</span>
          <span className="tag-badge badge-subtle">STANDALONE COMPUTE</span>
        </div>

        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: 14 }}>
          <div className="telemetry-tile">
            <span className="tile-label">GPU REQUIREMENT</span>
            <span className="tile-value">NONE (0 GB)</span>
            <span className="tile-desc">Fully CPU-based, optimized with vectorized NumPy &amp; OpenCV</span>
          </div>

          <div className="telemetry-tile">
            <span className="tile-label">MEMORY FOOTPRINT</span>
            <span className="tile-value">&lt; 380 MB</span>
            <span className="tile-desc">Streamlined multi-scale pyramid memory cache</span>
          </div>

          <div className="telemetry-tile">
            <span className="tile-label">NETWORK CONNECTIVITY</span>
            <span className="tile-value">OFFLINE CAPABLE</span>
            <span className="tile-desc">Zero cloud dependencies; runs in isolated orbital command stations</span>
          </div>
        </div>
      </div>
    </div>
  );
}

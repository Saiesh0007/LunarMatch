"use client";

import React from "react";
import { SENSOR_SPECS } from "../data/lunarData";

interface OverviewTabProps {
  onNavigateTab: (tab: string) => void;
}

export default function OverviewTab({ onNavigateTab }: OverviewTabProps) {
  return (
    <div>
      {/* Hero Banner matching mobile HomeScreen */}
      <div className="mission-hero-banner">
        <div className="hero-meta-row">
          <span className="aerospace-tag">ISRO — PROBLEM STATEMENT 26166 &bull; SIH 2026</span>
          <div style={{ display: "flex", gap: "8px" }}>
            <span className="tag-badge">DOMAIN: SPACE TECHNOLOGY</span>
            <span className="tag-badge badge-white">OFFLINE CPU ENGINE</span>
          </div>
        </div>

        <h1 className="hero-title">Multi-Modal Lunar Image Correspondence &amp; Registration Engine</h1>
        <p className="hero-description">
          Aligns heterogeneous Chandrayaan-2 orbital imagery (OHRC, TMC-2, IIRS) against lunar reference data (LRO NAC, SELENE) across extreme Sun illumination shifts, scale differentials, and spatial crater clustering.
        </p>

        <div style={{ display: "flex", gap: "10px", flexWrap: "wrap" }}>
          <button
            className="btn-primary-action"
            style={{ width: "auto", marginTop: 0, padding: "10px 20px" }}
            onClick={() => onNavigateTab("studio")}
          >
            LAUNCH REGISTRATION STUDIO &rarr;
          </button>
          <button
            className="btn-secondary-action"
            style={{ padding: "10px 16px" }}
            onClick={() => onNavigateTab("robustness")}
          >
            EXPLORE ROBUSTNESS LAB
          </button>
        </div>

        <div className="quick-telemetry-row">
          <div className="telemetry-tile">
            <span className="tile-label">RMSE TOLERANCE <span>px</span></span>
            <span className="tile-value">&lt; 0.35</span>
            <span className="tile-desc">Sub-pixel residual accuracy</span>
          </div>
          <div className="telemetry-tile">
            <span className="tile-label">INLIER RATIO <span>%</span></span>
            <span className="tile-value">92.4%</span>
            <span className="tile-desc">Consensus geometric inliers</span>
          </div>
          <div className="telemetry-tile">
            <span className="tile-label">END-TO-END LATENCY <span>ms</span></span>
            <span className="tile-value">~140</span>
            <span className="tile-desc">Fully optimized CPU runtime</span>
          </div>
          <div className="telemetry-tile">
            <span className="tile-label">SENSOR MODALITIES <span>N</span></span>
            <span className="tile-value">5</span>
            <span className="tile-desc">OHRC, TMC-2, IIRS, LRO, SELENE</span>
          </div>
        </div>
      </div>

      {/* Core Capabilities 4-Grid matching mobile layout */}
      <h2 style={{ fontSize: "0.85rem", letterSpacing: "0.12em", textTransform: "uppercase", color: "var(--text-tertiary)", marginBottom: "14px" }}>
        CORE CAPABILITIES
      </h2>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: "16px", marginBottom: "28px" }}>
        <div className="card-box" style={{ cursor: "pointer" }} onClick={() => onNavigateTab("studio")}>
          <div style={{ display: "flex", gap: "14px" }}>
            <div style={{ width: 40, height: 40, background: "var(--surface-elevated)", border: "1px solid var(--border-light)", borderRadius: "var(--radius-sm)", display: "flex", alignItems: "center", justifyContent: "center" }}>
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
                <line x1="3" y1="9" x2="21" y2="9" />
                <line x1="9" y1="21" x2="9" y2="9" />
              </svg>
            </div>
            <div style={{ flex: 1 }}>
              <h3 style={{ fontSize: "0.88rem", marginBottom: 4 }}>IMAGE REGISTRATION</h3>
              <p style={{ fontSize: "0.74rem", color: "var(--text-secondary)", lineHeight: 1.4 }}>
                Select Reference and Moving lunar images, tune multi-scale parameters, and execute registration with instant visual feedback.
              </p>
            </div>
          </div>
        </div>

        <div className="card-box" style={{ cursor: "pointer" }} onClick={() => onNavigateTab("correspondence")}>
          <div style={{ display: "flex", gap: "14px" }}>
            <div style={{ width: 40, height: 40, background: "var(--surface-elevated)", border: "1px solid var(--border-light)", borderRadius: "var(--radius-sm)", display: "flex", alignItems: "center", justifyContent: "center" }}>
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <circle cx="6" cy="6" r="3" />
                <circle cx="18" cy="18" r="3" />
                <line x1="8.5" y1="8.5" x2="15.5" y2="15.5" />
              </svg>
            </div>
            <div style={{ flex: 1 }}>
              <h3 style={{ fontSize: "0.88rem", marginBottom: 4 }}>CORRESPONDENCE VIEWER</h3>
              <p style={{ fontSize: "0.74rem", color: "var(--text-secondary)", lineHeight: 1.4 }}>
                Side-by-side tie points with interactive hover tooltips, showing residual error and Sinkhorn transport confidence.
              </p>
            </div>
          </div>
        </div>

        <div className="card-box" style={{ cursor: "pointer" }} onClick={() => onNavigateTab("robustness")}>
          <div style={{ display: "flex", gap: "14px" }}>
            <div style={{ width: 40, height: 40, background: "var(--surface-elevated)", border: "1px solid var(--border-light)", borderRadius: "var(--radius-sm)", display: "flex", alignItems: "center", justifyContent: "center" }}>
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z" />
              </svg>
            </div>
            <div style={{ flex: 1 }}>
              <h3 style={{ fontSize: "0.88rem", marginBottom: 4 }}>ROBUSTNESS LABORATORY</h3>
              <p style={{ fontSize: "0.74rem", color: "var(--text-secondary)", lineHeight: 1.4 }}>
                Stress-test evaluations across extreme Sun incidence angle shifts (0° to 80°), resolution disparities, and noise.
              </p>
            </div>
          </div>
        </div>

        <div className="card-box" style={{ cursor: "pointer" }} onClick={() => onNavigateTab("architecture")}>
          <div style={{ display: "flex", gap: "14px" }}>
            <div style={{ width: 40, height: 40, background: "var(--surface-elevated)", border: "1px solid var(--border-light)", borderRadius: "var(--radius-sm)", display: "flex", alignItems: "center", justifyContent: "center" }}>
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <polygon points="12 2 2 7 12 12 22 7 12 2" />
                <polyline points="2 17 12 22 22 17" />
                <polyline points="2 12 12 17 22 12" />
              </svg>
            </div>
            <div style={{ flex: 1 }}>
              <h3 style={{ fontSize: "0.88rem", marginBottom: 4 }}>PIPELINE ARCHITECTURE</h3>
              <p style={{ fontSize: "0.74rem", color: "var(--text-secondary)", lineHeight: 1.4 }}>
                Mathematical specifications: Log-Gabor Phase Congruency, Sinkhorn Optimal Transport, MAGSAC++, and Sub-pixel Phase Correlation.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Sensor Specifications Table */}
      <div className="card-box">
        <div className="card-header">
          <span className="card-header-title">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="12" cy="12" r="10" />
              <line x1="2" y1="12" x2="22" y2="12" />
              <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z" />
            </svg>
            SUPPORTED LUNAR OBSERVATION PLATFORMS
          </span>
          <span className="tag-badge badge-subtle">ISRO CHANDRAYAAN-2 &amp; REFERENCE MISSIONS</span>
        </div>

        <div style={{ overflowX: "auto" }}>
          <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "0.76rem", textAlign: "left" }}>
            <thead>
              <tr style={{ borderBottom: "1px solid var(--border)", color: "var(--text-tertiary)", fontFamily: "var(--font-geist-mono)" }}>
                <th style={{ padding: "10px 12px" }}>CODE</th>
                <th style={{ padding: "10px 12px" }}>MISSION</th>
                <th style={{ padding: "10px 12px" }}>SENSOR NAME</th>
                <th style={{ padding: "10px 12px" }}>GROUND RESOLUTION</th>
                <th style={{ padding: "10px 12px" }}>SPECTRAL BAND</th>
                <th style={{ padding: "10px 12px" }}>PIPELINE ROLE</th>
              </tr>
            </thead>
            <tbody style={{ fontFamily: "var(--font-geist-mono)", color: "var(--text-secondary)" }}>
              {SENSOR_SPECS.map(s => (
                <tr key={s.code} style={{ borderBottom: "1px solid var(--border)" }}>
                  <td style={{ padding: "10px 12px", color: "#ffffff", fontWeight: 800 }}>{s.code}</td>
                  <td style={{ padding: "10px 12px" }}>{s.mission}</td>
                  <td style={{ padding: "10px 12px" }}>{s.sensor}</td>
                  <td style={{ padding: "10px 12px" }}>{s.gsd}</td>
                  <td style={{ padding: "10px 12px" }}>{s.spectrum}</td>
                  <td style={{ padding: "10px 12px", color: "#ffffff" }}>{s.role}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

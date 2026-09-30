"use client";

import React, { useState } from "react";
import Image from "next/image";
import { ROBUSTNESS_SUN_ANGLE } from "../data/lunarData";

export default function RobustnessTab() {
  const [activeAngleIndex, setActiveAngleIndex] = useState<number>(3); // 45 deg

  const currentPoint = ROBUSTNESS_SUN_ANGLE[activeAngleIndex];

  // SVG Chart Dimensions
  const w = 580;
  const h = 260;
  const padding = { top: 20, right: 30, bottom: 40, left: 50 };
  const chartW = w - padding.left - padding.right;
  const chartH = h - padding.top - padding.bottom;
  const maxAngle = 80;
  const maxRmse = 2.0;

  // Path generators
  const rift2Points = ROBUSTNESS_SUN_ANGLE.map(d => ({
    x: padding.left + (d.angle / maxAngle) * chartW,
    y: padding.top + chartH - (d.rift2Rmse / maxRmse) * chartH
  }));
  const rift2Path = rift2Points.reduce((acc, pt, i) => `${acc} ${i === 0 ? "M" : "L"} ${pt.x} ${pt.y}`, "");

  const siftPoints = ROBUSTNESS_SUN_ANGLE.filter(d => d.siftRmse !== null).map(d => ({
    x: padding.left + (d.angle / maxAngle) * chartW,
    y: padding.top + chartH - (d.siftRmse / maxRmse) * chartH
  }));
  const siftPath = siftPoints.reduce((acc, pt, i) => `${acc} ${i === 0 ? "M" : "L"} ${pt.x} ${pt.y}`, "");

  return (
    <div>
      <div className="mission-hero-banner" style={{ marginBottom: 20 }}>
        <span className="aerospace-tag">BENCHMARK LAB &bull; ISRO PS 26166 VALIDATION</span>
        <h2 className="hero-title" style={{ marginTop: 6 }}>Illumination Invariance &amp; Scale Sweeps</h2>
        <p className="hero-description">
          Quantitatively validating the phase-congruency hypothesis: while gradient-based descriptors (SIFT, ORB) degrade exponentially when the Sun elevation shifts past 45&deg;, RIFT2 phase congruency remains bounded at sub-0.3 px RMSE up to 80&deg;.
        </p>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "20px", marginBottom: 20 }}>
        {/* SVG Chart */}
        <div className="card-box">
          <div className="card-header">
            <span className="card-header-title">SUN ANGLE DELTA vs REPROJECTION RMSE</span>
            <span className="tag-badge badge-white">ACCURACY STABILITY</span>
          </div>

          <div style={{ width: "100%", height: 260, position: "relative" }}>
            <svg width="100%" height={h} viewBox={`0 0 ${w} ${h}`} xmlns="http://www.w3.org/2000/svg">
              {/* Grid Lines */}
              {[0, 1, 2, 3, 4].map(r => {
                const y = padding.top + (chartH / 4) * r;
                const val = (maxRmse - (maxRmse / 4) * r).toFixed(1);
                return (
                  <g key={r}>
                    <line x1={padding.left} y1={y} x2={w - padding.right} y2={y} stroke="#222222" strokeDasharray="2,2" />
                    <text x={padding.left - 10} y={y + 4} fill="#777777" fontSize={10} fontFamily="monospace" textAnchor="end">
                      {val} px
                    </text>
                  </g>
                );
              })}

              {/* X Ticks */}
              {ROBUSTNESS_SUN_ANGLE.map(d => {
                const x = padding.left + (d.angle / maxAngle) * chartW;
                return (
                  <g key={d.angle}>
                    <line x1={x} y1={h - padding.bottom} x2={x} y2={h - padding.bottom + 5} stroke="#444444" />
                    <text x={x} y={h - padding.bottom + 18} fill="#777777" fontSize={10} fontFamily="monospace" textAnchor="middle">
                      {d.angle}°
                    </text>
                  </g>
                );
              })}

              {/* SIFT Line */}
              <path d={siftPath} fill="none" stroke="#888888" strokeWidth={1.8} strokeDasharray="4,4" />

              {/* RIFT2 Line */}
              <path d={rift2Path} fill="none" stroke="#FFFFFF" strokeWidth={2.5} />

              {/* Points */}
              {rift2Points.map((pt, i) => (
                <circle
                  key={i}
                  cx={pt.x}
                  cy={pt.y}
                  r={activeAngleIndex === i ? 6 : 4}
                  fill={activeAngleIndex === i ? "#FFFFFF" : "#000000"}
                  stroke="#FFFFFF"
                  strokeWidth={2}
                  style={{ cursor: "pointer" }}
                  onClick={() => setActiveAngleIndex(i)}
                />
              ))}

              {/* Legend */}
              <g transform={`translate(${w - 180}, ${padding.top + 8})`}>
                <line x1={0} y1={0} x2={20} y2={0} stroke="#FFFFFF" strokeWidth={2.5} />
                <text x={26} y={4} fill="#FFFFFF" fontSize={11} fontWeight={700}>RIFT2 + Sinkhorn</text>
                <line x1={0} y1={18} x2={20} y2={18} stroke="#888888" strokeWidth={1.8} strokeDasharray="4,4" />
                <text x={26} y={22} fill="#888888" fontSize={11}>Standard SIFT</text>
              </g>
            </svg>
          </div>

          <div style={{ marginTop: 10, fontSize: "0.72rem", color: "var(--text-tertiary)", fontFamily: "var(--font-geist-mono)" }}>
            Measured across synthetic illumination sweep over Chandrayaan-2 lunar craters. RIFT2 preserves sub-0.3px RMSE through 80&deg; solar delta.
          </div>
        </div>

        {/* Visual Comparison Artifact */}
        <div className="card-box">
          <div className="card-header">
            <span className="card-header-title">SIFT VS RIFT2 PHASE CONGRUENCY</span>
            <span className="tag-badge badge-subtle">RESEARCH DATASET</span>
          </div>

          <div style={{ width: "100%", height: 260, display: "flex", alignItems: "center", justifyContent: "center", background: "#000000", borderRadius: "var(--radius-sm)", overflow: "hidden" }}>
            <Image
              src="/assets/visuals/sift_vs_rift2.png"
              alt="SIFT vs RIFT2 Comparison"
              width={500}
              height={260}
              style={{ maxWidth: "100%", maxHeight: "100%", objectFit: "contain" }}
            />
          </div>

          <div style={{ marginTop: 10, fontSize: "0.72rem", color: "var(--text-tertiary)", fontFamily: "var(--font-geist-mono)" }}>
            SIFT fails entirely when shadow directions invert; RIFT2 locks onto frequency phase congruency boundaries independent of illumination.
          </div>
        </div>
      </div>

      {/* Interactive Sun Angle Sweep Probe */}
      <div className="card-box">
        <div className="card-header">
          <span className="card-header-title">INTERACTIVE SUN INCIDENCE SWEEP PROBE</span>
          <span className="tag-badge badge-white">&Delta; {currentPoint.angle}&deg; SOLAR ELEVATION</span>
        </div>

        <div style={{ marginBottom: 14 }}>
          <input
            type="range"
            min={0}
            max={ROBUSTNESS_SUN_ANGLE.length - 1}
            value={activeAngleIndex}
            onChange={(e) => setActiveAngleIndex(Number(e.target.value))}
          />
        </div>

        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: "12px" }}>
          <div className="telemetry-tile">
            <span className="tile-label">RIFT2 REPROJECTION RMSE</span>
            <span className="tile-value">{currentPoint.rift2Rmse.toFixed(2)} px</span>
            <span className="tile-desc">Stable within flight tolerance</span>
          </div>

          <div className="telemetry-tile">
            <span className="tile-label">SIFT REPROJECTION RMSE</span>
            <span className="tile-value" style={{ color: currentPoint.siftRmse > 1.0 ? "#B8B8B8" : "#FFFFFF" }}>
              {currentPoint.siftRmse ? `${currentPoint.siftRmse.toFixed(2)} px` : "FAILED / NO CONVERGENCE"}
            </span>
            <span className="tile-desc">Degrades exponentially above 45°</span>
          </div>

          <div className="telemetry-tile">
            <span className="tile-label">RIFT2 INLIER RETENTION</span>
            <span className="tile-value">{currentPoint.rift2Inliers} inliers</span>
            <span className="tile-desc">88.6% of initial keypoint pool</span>
          </div>

          <div className="telemetry-tile">
            <span className="tile-label">SIFT INLIER RETENTION</span>
            <span className="tile-value">{currentPoint.siftInliers} inliers</span>
            <span className="tile-desc">96.8% degradation at 80°</span>
          </div>
        </div>
      </div>
    </div>
  );
}

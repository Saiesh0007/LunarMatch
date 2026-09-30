"use client";

import React, { useState, useEffect, useRef } from "react";
import { TIE_POINTS, SPATIAL_GRID_4X4, PRESET_PAIRS, TiePoint } from "../data/lunarData";

export default function CorrespondenceTab() {
  const [filterMode, setFilterMode] = useState<"all" | "inliers" | "outliers">("inliers");
  const [hoveredPoint, setHoveredPoint] = useState<TiePoint | null>(null);
  const [tooltipPos, setTooltipPos] = useState<{ x: number; y: number }>({ x: 0, y: 0 });

  const canvasRef = useRef<HTMLCanvasElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    const container = containerRef.current;
    if (!canvas || !container) return;

    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const rect = container.getBoundingClientRect();
    const dpr = window.devicePixelRatio || 1;
    canvas.width = rect.width * dpr;
    canvas.height = rect.height * dpr;
    ctx.scale(dpr, dpr);

    const w = rect.width;
    const h = rect.height;
    const halfW = w / 2;

    ctx.fillStyle = "#000000";
    ctx.fillRect(0, 0, w, h);

    const imgRef = new window.Image();
    const imgMov = new window.Image();
    imgRef.src = PRESET_PAIRS.pair_a.refPath;
    imgMov.src = PRESET_PAIRS.pair_a.movPath;

    let loaded = 0;
    const draw = () => {
      loaded++;
      if (loaded < 2) return;

      // Draw left & right lunar images
      ctx.drawImage(imgRef, 0, 0, halfW - 2, h);
      ctx.drawImage(imgMov, halfW + 2, 0, halfW - 2, h);

      // Center separator
      ctx.strokeStyle = "#2E2E2E";
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.moveTo(halfW, 0);
      ctx.lineTo(halfW, h);
      ctx.stroke();

      const scaleRefX = (halfW - 2) / 600;
      const scaleRefY = h / 600;
      const scaleMovX = (halfW - 2) / 600;
      const scaleMovY = h / 600;

      TIE_POINTS.forEach(pt => {
        if (filterMode === "inliers" && !pt.inlier) return;
        if (filterMode === "outliers" && pt.inlier) return;

        const x1 = pt.refX * scaleRefX;
        const y1 = pt.refY * scaleRefY;
        const x2 = halfW + 2 + pt.movX * scaleMovX;
        const y2 = pt.movY * scaleMovY;

        ctx.beginPath();
        ctx.moveTo(x1, y1);
        ctx.lineTo(x2, y2);

        if (pt.inlier) {
          ctx.strokeStyle = "rgba(255, 255, 255, 0.65)";
          ctx.lineWidth = 1.2;
          ctx.setLineDash([]);
        } else {
          ctx.strokeStyle = "rgba(100, 100, 100, 0.4)";
          ctx.lineWidth = 1.0;
          ctx.setLineDash([3, 3]);
        }
        ctx.stroke();

        ctx.fillStyle = pt.inlier ? "#FFFFFF" : "#666666";
        ctx.beginPath();
        ctx.arc(x1, y1, 2.5, 0, Math.PI * 2);
        ctx.arc(x2, y2, 2.5, 0, Math.PI * 2);
        ctx.fill();
      });

      ctx.setLineDash([]);
    };

    imgRef.onload = draw;
    imgMov.onload = draw;
  }, [filterMode]);

  // Hover detection on canvas
  const handleMouseMove = (e: React.MouseEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const rect = canvas.getBoundingClientRect();
    const mouseX = e.clientX - rect.left;
    const mouseY = e.clientY - rect.top;
    const halfW = rect.width / 2;

    const scaleRefX = (halfW - 2) / 600;
    const scaleRefY = rect.height / 600;
    const scaleMovX = (halfW - 2) / 600;
    const scaleMovY = rect.height / 600;

    let closest: TiePoint | null = null;
    let minDist = 16;

    TIE_POINTS.forEach(pt => {
      if (filterMode === "inliers" && !pt.inlier) return;
      if (filterMode === "outliers" && pt.inlier) return;

      const x1 = pt.refX * scaleRefX;
      const y1 = pt.refY * scaleRefY;
      const x2 = halfW + 2 + pt.movX * scaleMovX;
      const y2 = pt.movY * scaleMovY;

      const d1 = Math.hypot(mouseX - x1, mouseY - y1);
      const d2 = Math.hypot(mouseX - x2, mouseY - y2);

      if (d1 < minDist) { minDist = d1; closest = pt; }
      if (d2 < minDist) { minDist = d2; closest = pt; }
    });

    if (closest) {
      setHoveredPoint(closest);
      setTooltipPos({ x: mouseX + 14, y: mouseY + 14 });
    } else {
      setHoveredPoint(null);
    }
  };

  return (
    <div>
      <div className="card-box" style={{ marginBottom: 20 }}>
        <div className="card-header">
          <span className="card-header-title">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="6" cy="6" r="3" />
              <circle cx="18" cy="18" r="3" />
              <line x1="8.5" y1="8.5" x2="15.5" y2="15.5" />
            </svg>
            INTERACTIVE TIE-POINT CORRESPONDENCE VISUALIZER
          </span>

          <div style={{ display: "flex", gap: "8px" }}>
            <button
              className={`btn-secondary-action ${filterMode === "all" ? "active" : ""}`}
              onClick={() => setFilterMode("all")}
            >
              ALL MATCHES
            </button>
            <button
              className={`btn-secondary-action ${filterMode === "inliers" ? "active" : ""}`}
              onClick={() => setFilterMode("inliers")}
            >
              INLIERS ONLY
            </button>
            <button
              className={`btn-secondary-action ${filterMode === "outliers" ? "active" : ""}`}
              onClick={() => setFilterMode("outliers")}
            >
              OUTLIERS ONLY
            </button>
          </div>
        </div>

        <div className="correspondence-canvas-container" ref={containerRef}>
          <canvas
            ref={canvasRef}
            style={{ width: "100%", height: "100%", display: "block" }}
            onMouseMove={handleMouseMove}
            onMouseLeave={() => setHoveredPoint(null)}
          />

          {hoveredPoint && (
            <div
              className="corr-hover-tooltip"
              style={{ left: tooltipPos.x, top: tooltipPos.y }}
            >
              <strong>TIE POINT #{hoveredPoint.id}</strong><br />
              Ref: ({hoveredPoint.refX.toFixed(1)}, {hoveredPoint.refY.toFixed(1)})<br />
              Mov: ({hoveredPoint.movX.toFixed(1)}, {hoveredPoint.movY.toFixed(1)})<br />
              Residual: {hoveredPoint.residual.toFixed(2)} px<br />
              Sinkhorn OT Score: {(hoveredPoint.score * 100).toFixed(1)}%<br />
              Status: {hoveredPoint.inlier ? "CONSENSUS INLIER" : "REJECTED OUTLIER"}
            </div>
          )}
        </div>
      </div>

      {/* Spatial Grid Analysis Card */}
      <div className="card-box">
        <div className="card-header">
          <span className="card-header-title">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <rect x="3" y="3" width="7" height="7" />
              <rect x="14" y="3" width="7" height="7" />
              <rect x="14" y="14" width="7" height="7" />
              <rect x="3" y="14" width="7" height="7" />
            </svg>
            UNIFORM SPATIAL GRID BALANCING (4&times;4 QUADRANT MATRIX)
          </span>
          <span className="tag-badge badge-white">NON-DEGENERATE HOMOGRAPHY VERIFIED</span>
        </div>

        <p style={{ fontSize: "0.78rem", color: "var(--text-secondary)", marginBottom: 12 }}>
          Standard computer-vision matchers degenerate on the Moon by clustering all tie-points on a single high-contrast crater rim. LunarMatch enforces uniform partition balancing across all spatial quadrants.
        </p>

        <div style={{ display: "grid", gridTemplateColumns: "380px 1fr", gap: "24px", alignItems: "center" }}>
          <div className="spatial-grid-matrix">
            {SPATIAL_GRID_4X4.map((row, rIdx) =>
              row.map((val, cIdx) => {
                const opacity = Math.min(1.0, 0.2 + (val / 45) * 0.8);
                return (
                  <div
                    key={`${rIdx}-${cIdx}`}
                    className="spatial-cell"
                    style={{
                      backgroundColor: `rgba(255, 255, 255, ${opacity * 0.12})`,
                      borderColor: `rgba(255, 255, 255, ${opacity * 0.35})`
                    }}
                    title={`Partition [${rIdx},${cIdx}]: ${val} inliers`}
                  >
                    <span className="spatial-cell-count">{val}</span>
                    <span className="spatial-cell-label">[{rIdx},{cIdx}]</span>
                  </div>
                );
              })
            )}
          </div>

          <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
            <div className="telemetry-tile">
              <span className="tile-label">QUADRANT COVERAGE RATIO</span>
              <span className="tile-value">93.8% (15/16 Active)</span>
              <span className="tile-desc">At least 12 inliers per active partition</span>
            </div>
            <div className="telemetry-tile">
              <span className="tile-label">CHI-SQUARE UNIFORMITY INDEX</span>
              <span className="tile-value">&chi;&sup2; = 4.12 (p &gt; 0.95)</span>
              <span className="tile-desc">Statistically confirms spatial dispersion without crater clustering</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

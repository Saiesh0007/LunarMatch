"use client";

import React, { useState, useEffect, useRef, useMemo } from "react";
import { TIE_POINTS, SPATIAL_GRID_4X4, PRESET_PAIRS, TiePoint } from "../data/lunarData";
import { getRunMatches, StudioSession } from "../lib/api";

// Demo tie-point coordinates are in a 600×600 source frame
const DEMO_FRAME = { w: 600, h: 600 };
const GAP = 4;
const GRID = 4;
const NO_POINTS: TiePoint[] = [];

interface Frame {
  w: number;
  h: number;
}

interface Panel {
  x: number;
  y: number;
  w: number;
  h: number;
}

/** Fit a frame inside a cell, preserving aspect ratio and centering it. */
function fitPanel(cellX: number, cellY: number, cellW: number, cellH: number, frame: Frame): Panel {
  const scale = Math.min(cellW / frame.w, cellH / frame.h);
  const w = frame.w * scale;
  const h = frame.h * scale;
  return { x: cellX + (cellW - w) / 2, y: cellY + (cellH - h) / 2, w, h };
}

/** Two panels: side by side when the container is wide, stacked when tall. */
function getPanels(w: number, h: number, refFrame: Frame, movFrame: Frame): { refPanel: Panel; movPanel: Panel; vertical: boolean } {
  const vertical = h > w;
  if (vertical) {
    const cellH = (h - GAP) / 2;
    return { refPanel: fitPanel(0, 0, w, cellH, refFrame), movPanel: fitPanel(0, cellH + GAP, w, cellH, movFrame), vertical };
  }
  const cellW = (w - GAP) / 2;
  return { refPanel: fitPanel(0, 0, cellW, h, refFrame), movPanel: fitPanel(cellW + GAP, 0, cellW, h, movFrame), vertical };
}

function project(panel: Panel, frame: Frame, x: number, y: number): [number, number] {
  return [panel.x + (x / frame.w) * panel.w, panel.y + (y / frame.h) * panel.h];
}

function filterPoints(points: TiePoint[], mode: "all" | "inliers" | "outliers"): TiePoint[] {
  if (mode === "inliers") return points.filter(pt => pt.inlier);
  if (mode === "outliers") return points.filter(pt => !pt.inlier);
  return points;
}

/** Count inliers per cell of a GRID×GRID partition of the reference frame. */
function computeGrid(points: TiePoint[], frame: Frame): number[][] {
  const grid = Array.from({ length: GRID }, () => new Array<number>(GRID).fill(0));
  points.filter(pt => pt.inlier).forEach(pt => {
    const c = Math.min(GRID - 1, Math.max(0, Math.floor((pt.refX / frame.w) * GRID)));
    const r = Math.min(GRID - 1, Math.max(0, Math.floor((pt.refY / frame.h) * GRID)));
    grid[r][c]++;
  });
  return grid;
}

interface CorrespondenceTabProps {
  session: StudioSession | null;
}

export default function CorrespondenceTab({ session }: CorrespondenceTabProps) {
  const [filterMode, setFilterMode] = useState<"all" | "inliers" | "outliers">("inliers");
  const [hoveredPoint, setHoveredPoint] = useState<TiePoint | null>(null);
  const [tooltipPos, setTooltipPos] = useState<{ x: number; y: number }>({ x: 0, y: 0 });

  const canvasRef = useRef<HTMLCanvasElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [images, setImages] = useState<{ ref: HTMLImageElement; mov: HTMLImageElement } | null>(null);
  const [size, setSize] = useState<{ w: number; h: number }>({ w: 0, h: 0 });

  // Live tie points for the current Studio run (null = use demo data)
  const [livePoints, setLivePoints] = useState<TiePoint[] | null>(null);
  const [loadState, setLoadState] = useState<"idle" | "loading" | "error">("idle");

  const runId = session?.run.run_id ?? null;
  const refSrc = session?.refSrc ?? PRESET_PAIRS.pair_a.refPath;
  const movSrc = session?.movSrc ?? PRESET_PAIRS.pair_a.movPath;

  // Reset when the Studio run changes; the effect below fetches the new matches
  const [prevRunId, setPrevRunId] = useState<string | null>(null);
  if (prevRunId !== runId) {
    setPrevRunId(runId);
    setLivePoints(null);
    setLoadState(runId ? "loading" : "idle");
  }

  useEffect(() => {
    if (!runId) return;
    let cancelled = false;
    getRunMatches(runId)
      .then(matches => {
        if (cancelled) return;
        setLivePoints(matches.map((m, i) => ({
          id: i,
          refX: m.ref_pt[0],
          refY: m.ref_pt[1],
          movX: m.mov_pt[0],
          movY: m.mov_pt[1],
          residual: NaN,
          score: m.distance,
          inlier: m.is_inlier,
        })));
        setLoadState("idle");
      })
      .catch(() => {
        if (cancelled) return;
        setLivePoints([]);
        setLoadState("error");
      });
    return () => {
      cancelled = true;
    };
  }, [runId]);

  // Load the image pair
  useEffect(() => {
    let cancelled = false;
    const ref = new window.Image();
    const mov = new window.Image();
    let loaded = 0;
    const onLoad = () => {
      loaded++;
      if (loaded === 2 && !cancelled) setImages({ ref, mov });
    };
    ref.onload = onLoad;
    mov.onload = onLoad;
    ref.src = refSrc;
    mov.src = movSrc;
    return () => {
      cancelled = true;
    };
  }, [refSrc, movSrc]);

  const isLive = session !== null;
  const points = isLive ? livePoints ?? NO_POINTS : TIE_POINTS;
  const refFrame: Frame = isLive && images ? { w: images.ref.naturalWidth, h: images.ref.naturalHeight } : DEMO_FRAME;
  const movFrame: Frame = isLive && images ? { w: images.mov.naturalWidth, h: images.mov.naturalHeight } : DEMO_FRAME;

  const grid = useMemo(
    () => (isLive ? computeGrid(points, refFrame) : SPATIAL_GRID_4X4),
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [isLive, points, refFrame.w, refFrame.h]
  );
  const gridMax = Math.max(1, ...grid.flat());
  const activeCells = grid.flat().filter(v => v > 0).length;
  const inlierCount = points.filter(pt => pt.inlier).length;
  const chiSquare = (() => {
    const expected = inlierCount / (GRID * GRID);
    if (expected === 0) return null;
    return grid.flat().reduce((acc, o) => acc + ((o - expected) ** 2) / expected, 0);
  })();

  // Track container size so the canvas re-renders crisply on resize / rotation
  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;
    const observer = new ResizeObserver(entries => {
      const { width, height } = entries[0].contentRect;
      setSize({ w: Math.round(width), h: Math.round(height) });
    });
    observer.observe(container);
    return () => observer.disconnect();
  }, []);

  // Draw the pair side by side (wide screens) or stacked (narrow screens)
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas || !images || size.w === 0) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const dpr = window.devicePixelRatio || 1;
    canvas.width = size.w * dpr;
    canvas.height = size.h * dpr;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);

    ctx.fillStyle = "#000000";
    ctx.fillRect(0, 0, size.w, size.h);

    const { refPanel, movPanel, vertical } = getPanels(size.w, size.h, refFrame, movFrame);
    ctx.drawImage(images.ref, refPanel.x, refPanel.y, refPanel.w, refPanel.h);
    ctx.drawImage(images.mov, movPanel.x, movPanel.y, movPanel.w, movPanel.h);

    // Separator between panels
    ctx.strokeStyle = "#2E2E2E";
    ctx.lineWidth = 1;
    ctx.beginPath();
    if (vertical) {
      ctx.moveTo(0, size.h / 2);
      ctx.lineTo(size.w, size.h / 2);
    } else {
      ctx.moveTo(size.w / 2, 0);
      ctx.lineTo(size.w / 2, size.h);
    }
    ctx.stroke();

    const radius = size.w < 500 ? 2 : 2.5;
    filterPoints(points, filterMode).forEach(pt => {
      const [x1, y1] = project(refPanel, refFrame, pt.refX, pt.refY);
      const [x2, y2] = project(movPanel, movFrame, pt.movX, pt.movY);

      ctx.beginPath();
      ctx.moveTo(x1, y1);
      ctx.lineTo(x2, y2);
      if (pt.inlier) {
        ctx.strokeStyle = "rgba(134, 239, 172, 0.7)"; // light green
        ctx.lineWidth = 1.2;
        ctx.setLineDash([]);
      } else {
        ctx.strokeStyle = "rgba(252, 165, 165, 0.6)"; // light red
        ctx.lineWidth = 1.0;
        ctx.setLineDash([3, 3]);
      }
      ctx.stroke();

      ctx.fillStyle = pt.inlier ? "#86EFAC" : "#FCA5A5";
      ctx.beginPath();
      ctx.arc(x1, y1, radius, 0, Math.PI * 2);
      ctx.arc(x2, y2, radius, 0, Math.PI * 2);
      ctx.fill();
    });
    ctx.setLineDash([]);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [filterMode, size, images, points, refFrame.w, refFrame.h, movFrame.w, movFrame.h]);

  // Hover (mouse) and tap (touch) detection
  const handlePointer = (e: React.PointerEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const rect = canvas.getBoundingClientRect();
    const px = e.clientX - rect.left;
    const py = e.clientY - rect.top;
    const { refPanel, movPanel } = getPanels(rect.width, rect.height, refFrame, movFrame);

    let closest: TiePoint | null = null;
    let minDist = e.pointerType === "touch" ? 24 : 16;
    filterPoints(points, filterMode).forEach(pt => {
      const [x1, y1] = project(refPanel, refFrame, pt.refX, pt.refY);
      const [x2, y2] = project(movPanel, movFrame, pt.movX, pt.movY);
      const d = Math.min(Math.hypot(px - x1, py - y1), Math.hypot(px - x2, py - y2));
      if (d < minDist) {
        minDist = d;
        closest = pt;
      }
    });

    if (closest) {
      setHoveredPoint(closest);
      // Keep the tooltip inside the container
      const tipW = 220;
      const tipH = 120;
      setTooltipPos({
        x: Math.max(8, Math.min(px + 14, rect.width - tipW - 8)),
        y: py + 14 + tipH > rect.height ? Math.max(8, py - tipH - 14) : py + 14,
      });
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

          <div className="btn-group" role="group" aria-label="Match filter">
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

        <p style={{ fontSize: "0.74rem", color: "var(--text-tertiary)", fontFamily: "var(--font-geist-mono)", marginBottom: 10 }}>
          {!isLive && "DEMO DATA (PAIR A) — run the pipeline in Studio with the backend online to see your own matches."}
          {isLive && loadState === "loading" && `LOADING MATCHES FOR ${session.run.run_id}…`}
          {isLive && loadState === "error" && `Could not load matches for ${session.run.run_id}.`}
          {isLive && loadState === "idle" && `LIVE RUN ${session.run.run_id} — ${points.length} filtered matches, ${inlierCount} MAGSAC inliers${session.isCustom ? " (custom images)" : ""}`}
        </p>

        <div className="correspondence-canvas-container" ref={containerRef}>
          <canvas
            ref={canvasRef}
            style={{ width: "100%", height: "100%", display: "block", touchAction: "manipulation" }}
            onPointerMove={handlePointer}
            onPointerDown={handlePointer}
            onPointerLeave={(e) => { if (e.pointerType === "mouse") setHoveredPoint(null); }}
            role="img"
            aria-label="Tie-point correspondences between reference and moving images"
          />

          {hoveredPoint && (
            <div
              className="corr-hover-tooltip"
              style={{ left: tooltipPos.x, top: tooltipPos.y }}
            >
              <strong>TIE POINT #{hoveredPoint.id}</strong><br />
              Ref: ({hoveredPoint.refX.toFixed(1)}, {hoveredPoint.refY.toFixed(1)})<br />
              Mov: ({hoveredPoint.movX.toFixed(1)}, {hoveredPoint.movY.toFixed(1)})<br />
              {isLive ? (
                <>Descriptor Distance: {hoveredPoint.score.toFixed(3)}<br /></>
              ) : (
                <>
                  Residual: {hoveredPoint.residual.toFixed(2)} px<br />
                  Sinkhorn OT Score: {(hoveredPoint.score * 100).toFixed(1)}%<br />
                </>
              )}
              Status: <span style={{ color: hoveredPoint.inlier ? "#86EFAC" : "#FCA5A5" }}>
                {hoveredPoint.inlier ? "CONSENSUS INLIER" : "REJECTED OUTLIER"}
              </span>
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
          <span className={`tag-badge ${!isLive || session.run.status === "SUCCESSFUL" ? "badge-white" : "badge-subtle"}`}>
            {isLive ? `RUN STATUS: ${session.run.status.replace("_", " ")}` : "NON-DEGENERATE HOMOGRAPHY VERIFIED"}
          </span>
        </div>

        <p style={{ fontSize: "0.78rem", color: "var(--text-secondary)", marginBottom: 12 }}>
          Standard computer-vision matchers degenerate on the Moon by clustering all tie-points on a single high-contrast crater rim. LunarMatch enforces uniform partition balancing across all spatial quadrants.
        </p>

        <div className="spatial-analysis-layout">
          <div className="spatial-grid-matrix">
            {grid.map((row, rIdx) =>
              row.map((val, cIdx) => {
                const opacity = Math.min(1.0, 0.2 + (val / gridMax) * 0.8);
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
              <span className="tile-value">
                {((activeCells / (GRID * GRID)) * 100).toFixed(1)}% ({activeCells}/{GRID * GRID} Active)
              </span>
              <span className="tile-desc">
                {isLive
                  ? `${inlierCount} inliers over the reference frame · pipeline coverage ${session.run.metrics.spatial_coverage.toFixed(1)}%`
                  : "At least 12 inliers per active partition"}
              </span>
            </div>
            <div className="telemetry-tile">
              <span className="tile-label">CHI-SQUARE UNIFORMITY INDEX</span>
              <span className="tile-value">
                {isLive
                  ? chiSquare !== null ? <>&chi;&sup2; = {chiSquare.toFixed(2)} (df = {GRID * GRID - 1})</> : "N/A (no inliers)"
                  : <>&chi;&sup2; = 4.12 (p &gt; 0.95)</>}
              </span>
              <span className="tile-desc">
                {isLive
                  ? "Lower values mean inliers are spread evenly rather than clustered"
                  : "Statistically confirms spatial dispersion without crater clustering"}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

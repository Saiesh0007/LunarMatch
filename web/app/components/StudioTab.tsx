"use client";

import React, { useState, useEffect, useRef } from "react";
import { PRESET_PAIRS, MetricData } from "../data/lunarData";
import { apiUrl, runPipeline, uploadImage, PipelineRunResponse, StudioSession } from "../lib/api";

const PRESET_IMAGE_IDS: Record<string, { ref: string; mov: string }> = {
  pair_a: { ref: "demo_pair_a_ref", mov: "demo_pair_a_mov" },
  pair_b: { ref: "demo_pair_b_ref", mov: "demo_pair_b_mov" },
};

const SENSOR_OPTIONS = ["OHRC", "TMC-2", "IIRS", "LRO NAC", "SELENE", "Other"];

/** Positive finite number from a text field, or undefined when blank/invalid. */
function parseGsd(value: string): number | undefined {
  const n = Number(value.trim());
  return value.trim() !== "" && Number.isFinite(n) && n > 0 ? n : undefined;
}

const SPARSE_STAGES = ["Phase Congruency", "HOPC Features", "Sinkhorn OT", "MAGSAC++ Consensus", "Sub-Pixel & QA"];
const DENSE_STAGES = ["CFOG Structure Maps", "Scale / Rotation Search", "Template Matching", "MAGSAC++ Consensus", "Sub-Pixel & QA"];
const FALLBACK_STAGES = ["Phase Congruency", "Sparse Matching", "Dense CFOG Fallback", "MAGSAC++ Consensus", "Sub-Pixel & QA"];

/** Which registration path produced a run: the backend reports dense use in its warnings. */
function registrationPath(run: PipelineRunResponse | null, selectedMethod: string): "sparse" | "dense" | "fallback" {
  const dense = run?.warnings.find(w => w.startsWith("Dense structural registration applied"));
  if (dense) return dense.includes("(explicit)") ? "dense" : "fallback";
  if (run) return "sparse";
  return selectedMethod === "dense" ? "dense" : "sparse";
}

function toMetricData(res: PipelineRunResponse): MetricData {
  const m = res.metrics;
  return {
    keypointsRef: m.keypoints_reference,
    keypointsMov: m.keypoints_moving,
    candidateMatches: m.candidate_matches,
    filteredMatches: m.filtered_matches,
    ransacInliers: m.ransac_inliers,
    inlierRatio: m.inlier_ratio / 100,
    rmsePx: m.rmse_px,
    spatialCoverage: m.spatial_coverage / 100,
    spatialCoverageFootprint: m.spatial_coverage_footprint != null ? m.spatial_coverage_footprint / 100 : null,
    mutualInformation: 0,
    ssim: 0,
    runtimeMs: m.runtime_ms,
    status: res.status,
    confidenceExplanation: m.confidence_explanation,
  };
}

interface StudioTabProps {
  isBackendOnline: boolean;
  onSessionChange: (session: StudioSession | null) => void;
}

export default function StudioTab({ isBackendOnline, onSessionChange }: StudioTabProps) {
  const [selectedPairId, setSelectedPairId] = useState<string>("pair_a");
  const [refImageSrc, setRefImageSrc] = useState<string>(PRESET_PAIRS.pair_a.refPath);
  const [movImageSrc, setMovImageSrc] = useState<string>(PRESET_PAIRS.pair_a.movPath);
  const [viewMode, setViewMode] = useState<"split" | "blink" | "checkerboard" | "diff">("split");
  const [splitPercent, setSplitPercent] = useState<number>(50);
  const [isDraggingSplit, setIsDraggingSplit] = useState<boolean>(false);
  const [isProcessing, setIsProcessing] = useState<boolean>(false);
  const [activeStageIndex, setActiveStageIndex] = useState<number>(-1);
  const [blinkShowRef, setBlinkShowRef] = useState<boolean>(true);
  const [zoomScale, setZoomScale] = useState<number>(1.0);
  const [refFile, setRefFile] = useState<File | null>(null);
  const [movFile, setMovFile] = useState<File | null>(null);
  const [originalMovSrc, setOriginalMovSrc] = useState<string>(PRESET_PAIRS.pair_a.movPath);
  const [lastRun, setLastRun] = useState<PipelineRunResponse | null>(null);
  // Results UI only appears once a run has executed for the current images; before that the
  // metrics are the preset's sample values and would contradict what the user is about to run
  const [hasResults, setHasResults] = useState<boolean>(false);

  // Form Controls
  const [featureMethod, setFeatureMethod] = useState<string>("rift2_multiscale");
  const [sinkhornIter, setSinkhornIter] = useState<number>(50);
  const [magsacThreshold, setMagsacThreshold] = useState<number>(2.5);
  const [subpixelEnabled, setSubpixelEnabled] = useState<boolean>(true);
  const [spatialEnabled, setSpatialEnabled] = useState<boolean>(true);
  // Optional image metadata: plain PNG/JPG uploads carry no sensor or resolution information
  const [refSensor, setRefSensor] = useState<string>("");
  const [movSensor, setMovSensor] = useState<string>("");
  const [refGsd, setRefGsd] = useState<string>("");
  const [movGsd, setMovGsd] = useState<string>("");

  // Live Telemetry state
  const [metrics, setMetrics] = useState<MetricData>(PRESET_PAIRS.pair_a.metrics);

  // Logs state
  const [logs, setLogs] = useState<Array<{ time: string; msg: string; type: "info" | "success" }>>([
    {
      time: "00:00:00.000",
      msg: "LUNARMATCH Mission Station Ready. Seed: 26166. Awaiting operator execution.",
      type: "info"
    }
  ]);

  const splitWrapperRef = useRef<HTMLDivElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const logTerminalRef = useRef<HTMLDivElement>(null);
  const telemetryRef = useRef<HTMLDivElement>(null);

  // Bring a section into view; instant for users who prefer reduced motion. The element is looked
  // up two frames later because the results grid only mounts once the run's state has rendered.
  const scrollToSection = (ref: React.RefObject<HTMLDivElement | null>, block: ScrollLogicalPosition) => {
    const reduce = window.matchMedia?.("(prefers-reduced-motion: reduce)").matches;
    requestAnimationFrame(() => requestAnimationFrame(() => {
      ref.current?.scrollIntoView({ behavior: reduce ? "auto" : "smooth", block });
    }));
  };

  // Helper to add log line
  const addLog = (msg: string, type: "info" | "success" = "info") => {
    const now = new Date();
    const timeStr = now.toTimeString().split(" ")[0] + "." + String(now.getMilliseconds()).padStart(3, "0");
    setLogs(prev => [...prev, { time: timeStr, msg, type }]);
  };

  useEffect(() => {
    if (logTerminalRef.current) {
      logTerminalRef.current.scrollTop = logTerminalRef.current.scrollHeight;
    }
  }, [logs]);

  // Handle Preset Selection
  const handleSelectPair = (pairId: string) => {
    setSelectedPairId(pairId);
    const pair = PRESET_PAIRS[pairId];
    if (!pair) return;
    setRefImageSrc(pair.refPath);
    setMovImageSrc(pair.movPath);
    setOriginalMovSrc(pair.movPath);
    setRefFile(null);
    setMovFile(null);
    setLastRun(null);
    setHasResults(false);
    onSessionChange(null);
    setMetrics(pair.metrics);
    addLog(`Selected preset pair: ${pair.name} (${pair.region})`, "info");
  };

  // Custom File Upload Handlers
  const handleCustomUpload = (e: React.ChangeEvent<HTMLInputElement>, isRef: boolean) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (event) => {
      const result = event.target?.result as string;
      if (isRef) {
        setRefImageSrc(result);
        setRefFile(file);
        addLog(`Custom Reference image loaded: ${file.name}`, "info");
      } else {
        setMovImageSrc(result);
        setOriginalMovSrc(result);
        setMovFile(file);
        addLog(`Custom Moving image loaded: ${file.name}`, "info");
      }
      // A custom upload replaces only one side; keep the other side's preset as a file-less source
      if (selectedPairId) {
        if (isRef) setMovFile(null);
        else setRefFile(null);
      }
      setLastRun(null);
      setHasResults(false);
      onSessionChange(null);
      setSelectedPairId("");
    };
    reader.readAsDataURL(file);
  };

  // Split-Screen Drag Logic (pointer events: mouse, touch and pen)
  const handleSplitMove = (clientX: number) => {
    if (!splitWrapperRef.current) return;
    const rect = splitWrapperRef.current.getBoundingClientRect();
    const x = Math.max(0, Math.min(clientX - rect.left, rect.width));
    setSplitPercent((x / rect.width) * 100);
  };

  // Ref (not state) so moves arriving before the next render aren't dropped
  const draggingRef = useRef<boolean>(false);

  const handleSplitPointerDown = (e: React.PointerEvent<HTMLDivElement>) => {
    e.currentTarget.setPointerCapture(e.pointerId);
    draggingRef.current = true;
    setIsDraggingSplit(true);
    handleSplitMove(e.clientX);
  };

  const handleSplitPointerMove = (e: React.PointerEvent<HTMLDivElement>) => {
    if (draggingRef.current) handleSplitMove(e.clientX);
  };

  const handleSplitPointerUp = () => {
    draggingRef.current = false;
    setIsDraggingSplit(false);
  };

  const handleSplitKeyDown = (e: React.KeyboardEvent<HTMLDivElement>) => {
    if (e.key === "ArrowLeft") setSplitPercent(p => Math.max(0, p - 5));
    if (e.key === "ArrowRight") setSplitPercent(p => Math.min(100, p + 5));
  };

  // Blink Mode Timer
  useEffect(() => {
    if (viewMode !== "blink") return;
    const interval = setInterval(() => {
      setBlinkShowRef(prev => !prev);
    }, 500);
    return () => clearInterval(interval);
  }, [viewMode]);

  // Canvas Generation: Checkerboard & Difference Map
  useEffect(() => {
    if (viewMode !== "checkerboard" && viewMode !== "diff") return;
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    canvas.width = 600;
    canvas.height = 600;

    const imgA = new window.Image();
    const imgB = new window.Image();
    // Backend artifacts are cross-origin; request CORS so getImageData doesn't taint the canvas
    imgA.crossOrigin = "anonymous";
    imgB.crossOrigin = "anonymous";
    imgA.src = refImageSrc;
    imgB.src = movImageSrc;

    let loaded = 0;
    const onLoaded = () => {
      loaded++;
      if (loaded < 2) return;

      if (viewMode === "checkerboard") {
        const canA = document.createElement("canvas");
        canA.width = 600; canA.height = 600;
        canA.getContext("2d")?.drawImage(imgA, 0, 0, 600, 600);

        const canB = document.createElement("canvas");
        canB.width = 600; canB.height = 600;
        canB.getContext("2d")?.drawImage(imgB, 0, 0, 600, 600);

        const tiles = 8;
        const tileW = 600 / tiles;
        const tileH = 600 / tiles;

        for (let r = 0; r < tiles; r++) {
          for (let c = 0; c < tiles; c++) {
            const useA = (r + c) % 2 === 0;
            const src = useA ? canA : canB;
            ctx.drawImage(src, c * tileW, r * tileH, tileW, tileH, c * tileW, r * tileH, tileW, tileH);
            ctx.strokeStyle = "rgba(255, 255, 255, 0.2)";
            ctx.strokeRect(c * tileW, r * tileH, tileW, tileH);
          }
        }
      } else if (viewMode === "diff") {
        const canA = document.createElement("canvas");
        canA.width = 600; canA.height = 600;
        const ctxA = canA.getContext("2d");
        ctxA?.drawImage(imgA, 0, 0, 600, 600);
        const dataA = ctxA?.getImageData(0, 0, 600, 600).data;

        const canB = document.createElement("canvas");
        canB.width = 600; canB.height = 600;
        const ctxB = canB.getContext("2d");
        ctxB?.drawImage(imgB, 0, 0, 600, 600);
        const dataB = ctxB?.getImageData(0, 0, 600, 600).data;

        if (dataA && dataB) {
          const diffImg = ctx.createImageData(600, 600);
          const diffData = diffImg.data;
          for (let i = 0; i < dataA.length; i += 4) {
            const diff = Math.abs(dataA[i] - dataB[i]) * 1.5;
            diffData[i] = diff > 30 ? Math.min(255, diff + 40) : diff;
            diffData[i + 1] = diff > 30 ? Math.min(255, diff + 40) : diff;
            diffData[i + 2] = diff > 30 ? Math.min(255, diff + 40) : diff;
            diffData[i + 3] = 255;
          }
          ctx.putImageData(diffImg, 0, 0);
        }
      }
    };

    imgA.onload = onLoaded;
    imgB.onload = onLoaded;
  }, [viewMode, refImageSrc, movImageSrc]);

  // Resolve a Studio image slot to a backend image ID (uploading custom images when needed)
  const resolveImageId = async (isRef: boolean): Promise<string> => {
    const file = isRef ? refFile : movFile;
    if (file) {
      const uploaded = await uploadImage(file, file.name);
      addLog(`Uploaded ${isRef ? "reference" : "moving"} image → ${uploaded.image_id} (${uploaded.width}×${uploaded.height})`, "info");
      return uploaded.image_id;
    }
    const src = isRef ? refImageSrc : originalMovSrc;
    const presetId = Object.keys(PRESET_PAIRS).find(id => (isRef ? PRESET_PAIRS[id].refPath : PRESET_PAIRS[id].movPath) === src);
    if (presetId) return isRef ? PRESET_IMAGE_IDS[presetId].ref : PRESET_IMAGE_IDS[presetId].mov;
    // Fallback: upload whatever the slot currently shows
    const blob = await (await fetch(src)).blob();
    const uploaded = await uploadImage(blob, isRef ? "reference.png" : "moving.png");
    return uploaded.image_id;
  };

  // Execute the real FastAPI registration pipeline
  const executeLivePipeline = async () => {
    setIsProcessing(true);
    setMovImageSrc(originalMovSrc);
    addLog("==================================================", "info");
    addLog("SUBMITTING TO LUNARMATCH FASTAPI PIPELINE (LIVE)...", "info");
    try {
      setActiveStageIndex(0);
      const [refId, movId] = await Promise.all([resolveImageId(true), resolveImageId(false)]);
      const refGsdM = parseGsd(refGsd);
      const movGsdM = parseGsd(movGsd);
      addLog(`Reference: ${refId} | Moving: ${movId} | Method: ${featureMethod}`, "info");
      if (refSensor || movSensor || refGsdM || movGsdM) {
        addLog(`Metadata: REF ${refSensor || "auto"}${refGsdM ? ` @ ${refGsdM} m/px` : ""} | MOV ${movSensor || "auto"}${movGsdM ? ` @ ${movGsdM} m/px` : ""}`, "info");
      }
      setActiveStageIndex(2);
      const res = await runPipeline({
        reference_image_id: refId,
        moving_image_id: movId,
        feature_method: featureMethod,
        ransac_threshold: magsacThreshold,
        subpixel_refinement: subpixelEnabled,
        spatial_balancing: spatialEnabled,
        ...(refSensor ? { reference_sensor: refSensor } : {}),
        ...(movSensor ? { moving_sensor: movSensor } : {}),
        ...(refGsdM ? { reference_gsd_m: refGsdM } : {}),
        ...(movGsdM ? { moving_gsd_m: movGsdM } : {}),
      });
      res.warnings
        .filter(w => w.startsWith("Dense structural registration applied"))
        .forEach(w => addLog(w, "success"));
      res.stages.forEach(stg => {
        addLog(`[${stg.stage_number}] ${stg.name}: ${stg.status}${stg.details ? ` — ${stg.details}` : ""} (${stg.duration_ms.toFixed(1)} ms)`, stg.status === "COMPLETED" ? "success" : "info");
      });
      const live = toMetricData(res);
      setMetrics(live);
      setLastRun(res);
      setHasResults(true);
      onSessionChange({
        run: res,
        refSrc: refImageSrc,
        movSrc: originalMovSrc,
        refImageId: refId,
        movImageId: movId,
        featureMethod,
        isCustom: !selectedPairId,
      });
      if (res.status === "SUCCESSFUL" || res.status === "LOW_CONFIDENCE") {
        if (res.outputs.registered_image_url) setMovImageSrc(apiUrl(res.outputs.registered_image_url));
        addLog(`Run ${res.run_id}: ${res.status}. Inliers = ${live.ransacInliers}, RMSE = ${live.rmsePx ?? "N/A"} px`, "success");
      } else {
        addLog(`Run ${res.run_id}: ${res.status}. ${res.failure_reason ?? live.confidenceExplanation}`, "info");
      }
      setViewMode("split");
    } catch (err) {
      addLog(`Pipeline request failed: ${err instanceof Error ? err.message : String(err)}`, "info");
    } finally {
      addLog("==================================================", "info");
      setActiveStageIndex(-1);
      setIsProcessing(false);
    }
  };

  // Execute Pipeline (live when the backend is reachable, otherwise offline simulation)
  const handleExecutePipeline = async () => {
    if (isProcessing) return;
    scrollToSection(logTerminalRef, "center");
    if (isBackendOnline) {
      await executeLivePipeline();
      scrollToSection(telemetryRef, "start");
      return;
    }
    setIsProcessing(true);
    addLog("==================================================", "info");
    addLog("INITIALIZING LUNARMATCH CORRESPONDENCE PIPELINE...", "info");
    addLog(`Sensor Pair: ${selectedPairId ? selectedPairId.toUpperCase() : "CUSTOM"}`, "info");

    const stages = [
      "Multi-scale Log-Gabor Phase Congruency (RIFT2)",
      "Maximum Moment Keypoint Extraction (HOPC)",
      "SuperGlue-style Sinkhorn Optimal Transport",
      "MAGSAC++ Threshold-Free Homography Consensus",
      "Sub-Pixel Phase Correlation Refinement"
    ];

    for (let i = 0; i < stages.length; i++) {
      setActiveStageIndex(i);
      addLog(`[Stage ${i + 1}/5] Running ${stages[i]}...`, "info");
      await new Promise(r => setTimeout(r, 280));
    }

    setActiveStageIndex(-1);
    const baseMetrics = PRESET_PAIRS[selectedPairId]?.metrics || PRESET_PAIRS.pair_a.metrics;
    setMetrics(baseMetrics);
    setHasResults(true);

    addLog(`Registration Consensus Achieved: Inliers = ${baseMetrics.ransacInliers}, RMSE = ${baseMetrics.rmsePx} px`, "success");
    addLog("Status: ACCEPTED (OPTIMAL). Geometric verification criteria satisfied.", "success");
    addLog("==================================================", "info");
    setIsProcessing(false);
    setViewMode("split");
    scrollToSection(telemetryRef, "start");
  };

  // While a run is in flight, label the stages for the method being run; afterwards, for the path the backend took
  const regPath = registrationPath(isProcessing ? null : lastRun, featureMethod);
  const stageNames = regPath === "dense" ? DENSE_STAGES : regPath === "fallback" ? FALLBACK_STAGES : SPARSE_STAGES;
  // Metric cards describe the run they show: preset (sample) numbers are sparse-pipeline values
  const cardPath = lastRun ? registrationPath(lastRun, featureMethod) : "sparse";

  const isOptimal = lastRun
    ? metrics.status === "SUCCESSFUL"
    : metrics.status === "SUCCESSFUL" || (metrics.rmsePx !== null && metrics.rmsePx < 0.5);

  return (
    <div className="grid-studio">
      {/* Left Column: Configuration Controls */}
      <div className="card-box">
        <div className="card-header">
          <span className="card-header-title">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M12 20h9" />
              <path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z" />
            </svg>
            CONFIGURATION &amp; PAIRS
          </span>
          <span className="tag-badge badge-white">STATION HUD</span>
        </div>

        <label className="param-label" style={{ display: "block", marginBottom: 8 }}>
          OBSERVATION PAIR
        </label>
        <div className="pair-selector-list">
          <div
            className={`pair-card-option ${selectedPairId === "pair_a" ? "selected" : ""}`}
            onClick={() => handleSelectPair("pair_a")}
          >
            <div className="pair-info-left">
              <span className="pair-title">PAIR A: OHRC vs TMC-2</span>
              <span className="pair-sub">Tycho Crater Rim &bull; Sun Angle &Delta; 34.2&deg;</span>
            </div>
            <span className="tag-badge badge-subtle">20&times; SCALE</span>
          </div>

          <div
            className={`pair-card-option ${selectedPairId === "pair_b" ? "selected" : ""}`}
            onClick={() => handleSelectPair("pair_b")}
          >
            <div className="pair-info-left">
              <span className="pair-title">PAIR B: IIRS vs LRO NAC</span>
              <span className="pair-sub">South Pole-Aitken &bull; Sun Angle &Delta; 52.8&deg;</span>
            </div>
            <span className="tag-badge badge-subtle">160&times; SCALE</span>
          </div>
        </div>

        {/* Custom Image Slots */}
        <label className="param-label" style={{ display: "block", marginBottom: 8 }}>
          OR UPLOAD CUSTOM IMAGES
        </label>
        <div className="dropzone-container">
          <div className="upload-slot">
            <input type="file" accept="image/*" onChange={(e) => handleCustomUpload(e, true)} />
            <img src={refImageSrc} className="slot-thumb" alt="Reference Thumbnail" decoding="async" />
            <span className="upload-slot-label">REF (FIXED)</span>
            <span className="upload-slot-hint">Drop or Click</span>
          </div>

          <div className="upload-slot">
            <input type="file" accept="image/*" onChange={(e) => handleCustomUpload(e, false)} />
            <img src={movImageSrc} className="slot-thumb" alt="Moving Thumbnail" decoding="async" />
            <span className="upload-slot-label">MOVING</span>
            <span className="upload-slot-hint">Drop or Click</span>
          </div>
        </div>

        {/* Parameters */}
        <div className="param-group">
          <div className="param-label-row">
            <span className="param-label">DESCRIPTOR PIPELINE</span>
          </div>
          <select className="param-select" value={featureMethod} onChange={(e) => setFeatureMethod(e.target.value)}>
            <option value="rift2_multiscale">RIFT2 Multi-Scale Pyramid (Recommended)</option>
            <option value="rift2">RIFT2 Single-Scale</option>
            <option value="dense">Dense Structural CFOG (Fastest for Cross-Sensor)</option>
            <option value="hopc">HOPC Structural Phase Matching</option>
            <option value="sift">SIFT Baseline (Fails at &Delta; Sun &gt; 45&deg;)</option>
          </select>
        </div>

        <div className="param-group">
          <div className="param-label-row">
            <span className="param-label">IMAGE METADATA (OPTIONAL)</span>
          </div>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8 }}>
            <select className="param-select" aria-label="Reference sensor" value={refSensor} onChange={(e) => setRefSensor(e.target.value)}>
              <option value="">REF sensor: auto</option>
              {SENSOR_OPTIONS.map(s => <option key={s} value={s}>REF: {s}</option>)}
            </select>
            <select className="param-select" aria-label="Moving sensor" value={movSensor} onChange={(e) => setMovSensor(e.target.value)}>
              <option value="">MOV sensor: auto</option>
              {SENSOR_OPTIONS.map(s => <option key={s} value={s}>MOV: {s}</option>)}
            </select>
            <input type="text" inputMode="decimal" className="param-input" aria-label="Reference GSD in metres per pixel"
              placeholder="REF GSD m/px (e.g. 78.32)" value={refGsd} onChange={(e) => setRefGsd(e.target.value)} />
            <input type="text" inputMode="decimal" className="param-input" aria-label="Moving GSD in metres per pixel"
              placeholder="MOV GSD m/px (e.g. 19.6)" value={movGsd} onChange={(e) => setMovGsd(e.target.value)} />
          </div>
          <div className="switch-subtitle" style={{ marginTop: 6 }}>
            Pixel size of the uploaded files (not the instrument&apos;s nominal value if the image was resampled). Narrows the scale search and enables metre-level residuals.
          </div>
        </div>

        <div className="param-group">
          <div className="param-label-row">
            <span className="param-label">SINKHORN OT ITERATIONS</span>
            <span className="param-val-badge">{sinkhornIter}</span>
          </div>
          <input
            type="range"
            min={20}
            max={100}
            step={5}
            value={sinkhornIter}
            onChange={(e) => setSinkhornIter(Number(e.target.value))}
          />
        </div>

        <div className="param-group">
          <div className="param-label-row">
            <span className="param-label">MAGSAC++ INLIER THRESHOLD</span>
            <span className="param-val-badge">{magsacThreshold.toFixed(1)} px</span>
          </div>
          <input
            type="range"
            min={1.0}
            max={5.0}
            step={0.1}
            value={magsacThreshold}
            onChange={(e) => setMagsacThreshold(Number(e.target.value))}
          />
        </div>

        <div className="toggle-switch-row">
          <div>
            <div className="switch-title">Sub-Pixel Phase Refinement</div>
            <div className="switch-subtitle">Local Fourier phase peak interpolation</div>
          </div>
          <label className="switch">
            <input
              type="checkbox"
              checked={subpixelEnabled}
              onChange={(e) => setSubpixelEnabled(e.target.checked)}
            />
            <span className="slider-toggle" />
          </label>
        </div>

        <div className="toggle-switch-row">
          <div>
            <div className="switch-title">Uniform Spatial Grid Balancing</div>
            <div className="switch-subtitle">Distribute inliers across 4x4 quadrants</div>
          </div>
          <label className="switch">
            <input
              type="checkbox"
              checked={spatialEnabled}
              onChange={(e) => setSpatialEnabled(e.target.checked)}
            />
            <span className="slider-toggle" />
          </label>
        </div>

        <button
          className="btn-primary-action"
          disabled={isProcessing}
          onClick={handleExecutePipeline}
        >
          {isProcessing ? (
            <>
              <span className="pulse-dot" /> EXECUTING PIPELINE...
            </>
          ) : (
            <>
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                <polygon points="5 3 19 12 5 21 5 3" />
              </svg>
              {isBackendOnline ? "EXECUTE REGISTRATION ENGINE (LIVE)" : "EXECUTE REGISTRATION ENGINE (SIMULATED)"}
            </>
          )}
        </button>
      </div>

      {/* Right Column: Viewport & Telemetry */}
      <div className="viewer-card">
        {/* Stage Progression HUD */}
        <div className="pipeline-hud-container">
          <div className="stage-step-list">
            {stageNames.map((name, idx) => (
              <div
                key={idx}
                className={`stage-step-item ${activeStageIndex === idx ? "active" : ""} ${activeStageIndex > idx ? "completed" : ""}`}
              >
                <div className="stage-num-tag">STAGE 0{idx + 1}</div>
                <div className="stage-name-text">{name}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Viewport Toolbar */}
        <div className="viewer-top-toolbar">
          <div className="view-mode-buttons">
            <button
              className={`mode-btn ${viewMode === "split" ? "active" : ""}`}
              onClick={() => setViewMode("split")}
            >
              SPLIT SLIDER
            </button>
            <button
              className={`mode-btn ${viewMode === "blink" ? "active" : ""}`}
              onClick={() => setViewMode("blink")}
            >
              OVERLAY BLINK
            </button>
            <button
              className={`mode-btn ${viewMode === "checkerboard" ? "active" : ""}`}
              onClick={() => setViewMode("checkerboard")}
            >
              CHECKERBOARD
            </button>
            <button
              className={`mode-btn ${viewMode === "diff" ? "active" : ""}`}
              onClick={() => setViewMode("diff")}
            >
              DIFFERENCE MAP
            </button>
          </div>

          <div>
            {hasResults && (
              <span className={`tag-badge ${isOptimal ? "badge-white" : "badge-subtle"}`}>
                {isOptimal ? "OPTIMAL (PASS)" : "FAIL-SAFE"}
              </span>
            )}
          </div>
        </div>

        {/* Viewport Display Stage */}
        <div className="viewport-stage">
          <div className="viewport-zoom-layer" style={{ transform: `scale(${zoomScale})` }}>
          {viewMode === "split" ? (
            <div
              className={`split-viewer-wrapper ${isDraggingSplit ? "dragging" : ""}`}
              ref={splitWrapperRef}
              onPointerDown={handleSplitPointerDown}
              onPointerMove={handleSplitPointerMove}
              onPointerUp={handleSplitPointerUp}
              onPointerCancel={handleSplitPointerUp}
            >
              <div className="split-layer">
                <img src={refImageSrc} alt="Reference Lunar Surface" draggable={false} />
              </div>

              <div className="split-layer split-layer-top" style={{ clipPath: `inset(0 0 0 ${splitPercent}%)` }}>
                <img src={movImageSrc} alt="Moving Lunar Surface" draggable={false} />
              </div>

              <div
                className="split-divider-handle"
                style={{ left: `${splitPercent}%` }}
                role="slider"
                tabIndex={0}
                aria-label="Split position"
                aria-valuemin={0}
                aria-valuemax={100}
                aria-valuenow={Math.round(splitPercent)}
                onKeyDown={handleSplitKeyDown}
              >
                <div className="split-handle-badge">&#8596;</div>
              </div>
            </div>
          ) : viewMode === "blink" ? (
            <div className="single-mode-view">
              <img src={blinkShowRef ? refImageSrc : movImageSrc} alt="Blink View" />
            </div>
          ) : (
            <div className="single-mode-view">
              <canvas ref={canvasRef} />
            </div>
          )}
          </div>

          <div className="viewport-hud-tag">
            {viewMode === "split" && "MODE: SPLIT SLIDER (REF ↔ REGISTERED)"}
            {viewMode === "blink" && `MODE: OVERLAY BLINK [${blinkShowRef ? "REFERENCE" : "WARPED MOVING"}]`}
            {viewMode === "checkerboard" && "MODE: CHECKERBOARD MOSAIC"}
            {viewMode === "diff" && "MODE: RESIDUAL DIFFERENCE HEATMAP"}
          </div>

          <div className="viewport-zoom-toolbar">
            <button className="zoom-btn" aria-label="Zoom in" onClick={() => setZoomScale(s => Math.min(2.0, s + 0.2))}>+</button>
            <button className="zoom-btn" aria-label="Zoom out" onClick={() => setZoomScale(s => Math.max(1.0, s - 0.2))}>&minus;</button>
            <button className="zoom-btn" aria-label="Reset zoom" onClick={() => setZoomScale(1.0)}>&#8635;</button>
          </div>
        </div>

        {/* Quantitative Telemetry 8-Grid */}
        {hasResults ? (
        <div className="results-telemetry-grid" ref={telemetryRef} style={{ scrollMarginTop: 16 }}>
          <div className="result-metric-card">
            <div className="metric-title">KEYPOINTS</div>
            {cardPath === "dense" ? (
              <>
                <div className="metric-number">Dense grid</div>
                <div className="metric-sub">Template patches, no keypoints</div>
              </>
            ) : (
              <>
                <div className="metric-number">{metrics.keypointsRef} / {metrics.keypointsMov}</div>
                <div className="metric-sub">{cardPath === "fallback" ? "Sparse stage (unverified)" : "Reference / Moving"}</div>
              </>
            )}
          </div>

          <div className="result-metric-card">
            <div className="metric-title">CANDIDATES</div>
            <div className="metric-number">{metrics.candidateMatches}</div>
            <div className="metric-sub">{cardPath === "sparse" ? "Sinkhorn OT Pairs" : "CFOG Template Matches"}</div>
          </div>

          <div className="result-metric-card">
            <div className="metric-title">RANSAC INLIERS</div>
            <div className="metric-number">{metrics.ransacInliers}</div>
            <div className="metric-sub">Consensus Subset</div>
          </div>

          <div className="result-metric-card">
            <div className="metric-title">INLIER RATIO</div>
            <div className="metric-number">{(metrics.inlierRatio * 100).toFixed(1)}%</div>
            <div className="metric-sub">Consensus / Candidates</div>
          </div>

          <div className="result-metric-card">
            <div className="metric-title">REPROJECTION RMSE</div>
            <div className="metric-number">{metrics.rmsePx !== null ? `${metrics.rmsePx.toFixed(2)} px` : "N/A"}</div>
            <div className="metric-sub">Residual Discrepancy</div>
          </div>

          <div className="result-metric-card">
            <div className="metric-title">SPATIAL COVERAGE</div>
            {metrics.spatialCoverageFootprint != null ? (
              <>
                <div className="metric-number">{(metrics.spatialCoverageFootprint * 100).toFixed(1)}%</div>
                <div className="metric-sub">Of Image Overlap &bull; {(metrics.spatialCoverage * 100).toFixed(0)}% of Full Ref</div>
              </>
            ) : (
              <>
                <div className="metric-number">{(metrics.spatialCoverage * 100).toFixed(1)}%</div>
                <div className="metric-sub">6&times;6 Grid Partition Fill</div>
              </>
            )}
          </div>

          <div className="result-metric-card">
            <div className="metric-title">LATENCY</div>
            <div className="metric-number">{metrics.runtimeMs.toFixed(1)} ms</div>
            <div className="metric-sub">End-to-End CPU Runtime</div>
          </div>

          <div className="result-metric-card">
            <div className="metric-title">DECISION</div>
            <div className="metric-number" style={{ fontSize: "0.95rem" }}>
              {isOptimal ? "ACCEPTED" : "REJECTED"}
            </div>
            <div className="metric-sub">{isOptimal ? "All Criteria Satisfied" : "Quality Gates Not Met"}</div>
          </div>
        </div>
        ) : (
          <div className="result-metric-card" style={{ textAlign: "center" }}>
            <div className="metric-title">RESULTS</div>
            <div className="metric-sub">
              {isProcessing ? "Registration running — metrics appear when it finishes." : "Run the registration engine to see metrics for these images."}
            </div>
          </div>
        )}

        {/* Log Stream Terminal */}
        <div className="log-terminal-box" ref={logTerminalRef}>
          {logs.map((l, i) => (
            <div key={i} className="log-line">
              <span className="log-time">[{l.time}]</span>
              <span className={`log-msg-${l.type}`}>{l.msg}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

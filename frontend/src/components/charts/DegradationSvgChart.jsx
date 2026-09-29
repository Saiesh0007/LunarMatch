import React, { useEffect, useRef } from 'react';
import { gsap } from 'gsap';

export function DegradationSvgChart({ dataSteps = [], selectedStep, onSelectStep }) {
  const pathRef = useRef(null);

  const n = dataSteps.length || 5;
  const paddingX = 40;
  const width = 400;
  const plotWidth = width - paddingX * 2; // 320px
  const height = 180;
  const topY = 25;
  const bottomY = 150;

  // Find min/max RMSE to scale curve
  const rmses = dataSteps.map(d => (typeof d.rmse === 'number' ? d.rmse : 1.0));
  const maxRmse = Math.max(...rmses, 5.0);
  const minRmse = Math.min(...rmses, 0.5);

  const points = dataSteps.map((step, i) => {
    const cx = paddingX + (n > 1 ? (i / (n - 1)) * plotWidth : plotWidth / 2);
    const normalized = maxRmse === minRmse ? 0.5 : (step.rmse - minRmse) / (maxRmse - minRmse);
    // Low RMSE = near bottomY (140), High RMSE = near topY (30)
    const cy = bottomY - normalized * (bottomY - topY);
    return { cx, cy, label: step.label || `Step ${i + 1}`, ...step };
  });

  const pathD = points.length > 0
    ? points.reduce((acc, pt, i) => `${acc} ${i === 0 ? 'M' : 'L'} ${pt.cx},${pt.cy}`, '')
    : '';

  const areaD = points.length > 0
    ? `${pathD} L ${points[points.length - 1].cx},${height} L ${points[0].cx},${height} Z`
    : '';

  useEffect(() => {
    const path = pathRef.current;
    if (path) {
      const length = path.getTotalLength();
      gsap.set(path, { strokeDasharray: length, strokeDashoffset: length });
      gsap.to(path, { strokeDashoffset: 0, duration: 0.8, ease: "power2.out" });
    }
  }, [dataSteps]);

  return (
    <svg viewBox="0 0 400 180" className="w-full h-full preserve-3d">
      <defs>
        <linearGradient id="curveGradient" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#ffffff" stopOpacity="0.35" />
          <stop offset="100%" stopColor="#353535" stopOpacity="0" />
        </linearGradient>
      </defs>

      {/* Background grid lines */}
      <path d="M0,45 L400,45" stroke="#353535" strokeDasharray="4 4" strokeWidth="1" opacity="0.6" />
      <path d="M0,90 L400,90" stroke="#353535" strokeDasharray="4 4" strokeWidth="1" opacity="0.6" />
      <path d="M0,135 L400,135" stroke="#353535" strokeDasharray="4 4" strokeWidth="1" opacity="0.6" />

      {/* Filled Area */}
      {areaD && <path d={areaD} fill="url(#curveGradient)" />}

      {/* Stroke Line */}
      {pathD && (
        <path
          ref={pathRef}
          d={pathD}
          fill="none"
          stroke="#ffffff"
          strokeWidth="2.5"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
      )}

      {/* Anchor points */}
      {points.map((pt, i) => {
        const isActive = selectedStep === i;
        return (
          <g
            key={i}
            onClick={() => onSelectStep && onSelectStep(i)}
            className="cursor-pointer group"
          >
            <circle cx={pt.cx} cy={pt.cy} r="14" fill="transparent" />
            <circle
              cx={pt.cx}
              cy={pt.cy}
              r={isActive ? 6 : 4}
              fill={isActive ? "#ffffff" : "#1b1b1b"}
              stroke="#ffffff"
              strokeWidth="2"
              className="transition-all duration-200"
            />
            <text
              x={pt.cx}
              y="172"
              fill={isActive ? "#ffffff" : "#8e9192"}
              fontSize="9"
              fontFamily="JetBrains Mono"
              textAnchor="middle"
              className="font-mono tracking-tighter select-none"
            >
              {pt.label}
            </text>
          </g>
        );
      })}
    </svg>
  );
}

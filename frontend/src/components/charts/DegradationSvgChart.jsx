import React, { useEffect, useRef } from 'react';
import { gsap } from 'gsap';

export function DegradationSvgChart({ dataSteps, selectedStep, onSelectStep }) {
  const pathRef = useRef(null);

  useEffect(() => {
    const path = pathRef.current;
    if (path) {
      const length = path.getTotalLength();
      gsap.set(path, { strokeDasharray: length, strokeDashoffset: length });
      gsap.to(path, { strokeDashoffset: 0, duration: 1.0, ease: "power2.out" });
    }
  }, []);

  return (
    <svg viewBox="0 0 400 180" className="w-full h-full preserve-3d">
      <defs>
        <linearGradient id="curveGradient" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#ffffff" stopOpacity="0.4" />
          <stop offset="100%" stopColor="#353535" stopOpacity="0" />
        </linearGradient>
      </defs>
      
      {/* Background grid lines */}
      <path d="M0,45 L400,45" stroke="#353535" strokeDasharray="4 4" strokeWidth="1" />
      <path d="M0,90 L400,90" stroke="#353535" strokeDasharray="4 4" strokeWidth="1" />
      <path d="M0,135 L400,135" stroke="#353535" strokeDasharray="4 4" strokeWidth="1" />

      {/* Mock path shape based on the design for 5 points */}
      <path d="M40,20 Q120,40 200,90 T360,160 L360,180 L40,180 Z" fill="url(#curveGradient)" />
      <path 
        ref={pathRef}
        d="M40,20 C120,30 160,80 200,90 S280,150 360,160" 
        fill="none" 
        stroke="#ffffff" 
        strokeWidth="3" 
      />

      {/* Anchor points */}
      {[20, 50, 90, 130, 160].map((cy, i) => {
        const cx = 40 + i * 80;
        const isActive = selectedStep === i;
        return (
          <g key={i} onClick={() => onSelectStep(i)} className="cursor-pointer" style={{ transformOrigin: `${cx}px ${cy}px` }}>
            <circle cx={cx} cy={cy} r="16" fill="transparent" />
            <circle cx={cx} cy={cy} r={isActive ? 6 : 4} fill={isActive ? "#ffffff" : "#1b1b1b"} stroke="#ffffff" strokeWidth="2" className="transition-all duration-300" />
            <text x={cx} y="175" fill={isActive ? "#ffffff" : "#8e9192"} fontSize="10" fontFamily="JetBrains Mono" textAnchor="middle">Δ{i * 15}°</text>
          </g>
        );
      })}
    </svg>
  );
}

import React, { useEffect, useRef } from 'react';
import { gsap } from 'gsap';

export function HomographySvgChart() {
  const pathRef = useRef(null);

  useEffect(() => {
    // Basic drawing animation without DrawSVGPlugin (since it's a paid greensock plugin)
    // We achieve the same effect by animating stroke-dashoffset
    const path = pathRef.current;
    if (path) {
      const length = path.getTotalLength();
      gsap.set(path, { strokeDasharray: length, strokeDashoffset: length });
      gsap.to(path, { strokeDashoffset: 0, duration: 1.5, ease: "power2.out", delay: 0.2 });
    }
  }, []);

  return (
    <svg viewBox="0 0 100 40" className="w-full h-full preserve-3d">
      <defs>
        <linearGradient id="homographyLine" x1="0" y1="0" x2="1" y2="0">
          <stop offset="0%" stopColor="#353535" />
          <stop offset="100%" stopColor="#ffffff" />
        </linearGradient>
      </defs>
      <path 
        ref={pathRef}
        d="M0,35 Q20,35 40,20 T100,5" 
        fill="none" 
        stroke="url(#homographyLine)" 
        strokeWidth="2" 
        vectorEffect="non-scaling-stroke"
      />
      <circle cx="100" cy="5" r="2" fill="#ffffff" />
      <circle cx="0" cy="35" r="2" fill="#353535" />
    </svg>
  );
}

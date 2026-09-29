import React, { useEffect, useRef } from 'react';
import { gsap } from 'gsap';

export function ConsoleStream() {
  const containerRef = useRef(null);

  const logs = [
    "[SYS] LunarMatch Core v2.4 initialized.",
    "[INI] Loading configurations from env...",
    "[MEM] Preallocating OpenCV buffers (2048MB)",
    "[NET] SuperPoint ONNX weights loaded.",
    "[NET] SuperGlue Sinkhorn network active.",
    "[NET] Initializing RIFT2 Phase Congruency C++ extensions...",
    "[SYS] Fast-Math enabled. AVX512 optimizations active.",
    "[API] FastAPI binding to 0.0.0.0:8000",
    "[API] Listening for telemetry..."
  ];

  useEffect(() => {
    const lines = containerRef.current.children;
    
    const ctx = gsap.context(() => {
      gsap.set(lines, { opacity: 0 });
      gsap.to(lines, {
        opacity: 1,
        stagger: 0.15,
        duration: 0.1,
        ease: "none"
      });
    });
    
    return () => ctx.revert();
  }, []);

  return (
    <div className="bg-[#050505] border border-surface-container-high rounded-xl p-4 font-mono text-[10px] leading-relaxed text-outline-variant relative overflow-hidden h-[240px]">
      <div className="absolute top-0 w-full h-4 bg-gradient-to-b from-[#050505] to-transparent z-10" />
      <div className="absolute top-2 right-4 z-20 text-primary animate-pulse">_</div>
      
      <div ref={containerRef} className="pt-2">
        {logs.map((log, i) => (
          <div key={i} className="mb-1">
            <span className="text-surface-container-highest mr-2">{String(i+1).padStart(3, '0')}</span>
            {log.includes('[API]') && <span className="text-secondary mr-2">[API]</span>}
            {log.includes('[SYS]') && <span className="text-primary mr-2">[SYS]</span>}
            {!log.includes('[API]') && !log.includes('[SYS]') && <span className="mr-2">{log.substring(0, 5)}</span>}
            <span className={log.includes('active') || log.includes('Listening') ? 'text-on-surface' : ''}>
              {log.substring(5)}
            </span>
          </div>
        ))}
      </div>
      
      <div className="absolute bottom-0 w-full h-12 bg-gradient-to-t from-[#050505] to-transparent z-10" />
    </div>
  );
}

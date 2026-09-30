import React, { useEffect, useRef } from 'react';
import { gsap } from 'gsap';
import { Badge } from '../../components/ui/Badge.jsx';

export function MissionBanner() {
  const titleRef = useRef(null);
  const descRef = useRef(null);

  useEffect(() => {
    const ctx = gsap.context(() => {
      // Simple stagger entrance for the texts
      gsap.from([titleRef.current, descRef.current], {
        y: 20,
        opacity: 0,
        stagger: 0.1,
        duration: 0.6,
        ease: "power3.out",
        delay: 0.1
      });
    });
    return () => ctx.revert();
  }, []);

  return (
    <div className="border border-surface-container-high bg-surface-container rounded-xl p-6 mb-6 relative overflow-hidden flex items-center justify-between">
      <div className="absolute top-0 right-0 h-full w-1/3 bg-gradient-to-l from-surface-container-highest/20 to-transparent pointer-events-none" />
      
      <div>
        <div className="flex items-center gap-3 mb-2 opacity-0" ref={titleRef}>
          <h1 className="font-headline-lg text-2xl tracking-[0.1em] text-primary uppercase m-0">
            Engine Telemetry
          </h1>
          <Badge variant="status" label="SYS_NOMINAL" />
        </div>
        <p className="font-body-lg text-on-surface-variant max-w-2xl opacity-0" ref={descRef}>
          Cross-modal optical alignment engine initialized. Monitoring subpixel correspondence between orbital reconnaissance imagery and topological basemaps.
        </p>
      </div>

      <div className="hidden lg:flex items-center gap-6 z-10 text-right pr-6">
        <div>
          <div className="font-label-md text-outline tracking-widest uppercase mb-1">Target Mission</div>
          <div className="font-headline-md text-on-surface tracking-wider">CHANDRAYAAN-2</div>
        </div>
        <div className="h-10 w-px bg-surface-container-high" />
        <div>
          <div className="font-label-md text-outline tracking-widest uppercase mb-1">Current Orbit</div>
          <div className="font-headline-md text-on-surface tracking-wider font-mono">100 KM POLAR</div>
        </div>
      </div>
    </div>
  );
}

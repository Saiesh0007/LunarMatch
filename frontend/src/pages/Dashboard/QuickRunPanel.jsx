import React, { useState } from 'react';
import { SectionHeader } from '../../components/ui/SectionHeader.jsx';
import { Button } from '../../components/ui/Button.jsx';
import { Icon } from '../../components/ui/Icon.jsx';

export function QuickRunPanel() {
  const [loading, setLoading] = useState(false);

  const handleRun = () => {
    setLoading(true);
    setTimeout(() => setLoading(false), 2000);
  };

  return (
    <div className="mb-8">
      <SectionHeader icon="rocket_launch" title="Quick Run" meta="Module 04" />
      <div className="bg-surface-container rounded-xl p-5 border border-surface-container-high">
        <div className="mb-6">
          <div className="font-label-sm text-outline tracking-widest uppercase mb-2">Selected Configuration</div>
          <div className="bg-surface-container-lowest border border-outline-variant rounded p-3 text-sm">
             <div className="flex justify-between mb-2 pb-2 border-b border-surface-container-high">
               <span className="text-on-surface-variant font-mono">EXTRACTOR</span>
               <span className="text-primary font-mono uppercase">SuperPoint</span>
             </div>
             <div className="flex justify-between mb-2 pb-2 border-b border-surface-container-high">
               <span className="text-on-surface-variant font-mono">MATCHER</span>
               <span className="text-primary font-mono uppercase">SuperGlue Sinkhorn</span>
             </div>
             <div className="flex justify-between">
               <span className="text-on-surface-variant font-mono">GEOMETRY</span>
               <span className="text-primary font-mono uppercase">Homography / RANSAC</span>
             </div>
          </div>
        </div>

        <Button 
          variant="primary" 
          className="w-full relative overflow-hidden" 
          onClick={handleRun}
          loading={loading}
          disabled={loading}
        >
          {!loading && <span className="relative z-10 flex items-center justify-center gap-2"><Icon name="play_arrow" size="18px" /> EXECUTE PIPELINE</span>}
        </Button>
      </div>
    </div>
  );
}

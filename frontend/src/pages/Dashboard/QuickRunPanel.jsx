import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { SectionHeader } from '../../components/ui/SectionHeader.jsx';
import { Button } from '../../components/ui/Button.jsx';
import { Icon } from '../../components/ui/Icon.jsx';
import { useRegistrationStore } from '../../store/registrationStore.js';
import { apiClient } from '../../api/client.js';

export function QuickRunPanel() {
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const { loadSample, setPipelineResult } = useRegistrationStore();

  const handleQuickRun = async () => {
    setLoading(true);
    loadSample();

    try {
      const config = {
        reference_image_id: 'demo_pair_a_ref',
        moving_image_id: 'demo_pair_a_mov',
        feature_method: 'sift',
        geometric_model: 'homography',
        spatial_balancing: true
      };
      const result = await apiClient.runPipeline(config);
      setPipelineResult(result);
      navigate('/registration');
    } catch (err) {
      console.warn("Quick run pipeline direct fail, navigating with sample loaded:", err);
      navigate('/registration');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="mb-8">
      <SectionHeader icon="rocket_launch" title="Quick Run" meta="Module 04" />
      <div className="bg-surface-container rounded-xl p-5 border border-surface-container-high">
        <div className="mb-6">
          <div className="font-label-sm text-outline tracking-widest uppercase mb-2">Selected Configuration</div>
          <div className="bg-surface-container-lowest border border-outline-variant rounded-lg p-3 text-sm">
            <div className="flex justify-between mb-2 pb-2 border-b border-surface-container-high">
              <span className="text-on-surface-variant font-mono">EXTRACTOR</span>
              <span className="text-primary font-mono uppercase font-semibold">SIFT / RIFT2</span>
            </div>
            <div className="flex justify-between mb-2 pb-2 border-b border-surface-container-high">
              <span className="text-on-surface-variant font-mono">MATCHER</span>
              <span className="text-primary font-mono uppercase font-semibold">BF (L2 / Hamming)</span>
            </div>
            <div className="flex justify-between">
              <span className="text-on-surface-variant font-mono">GEOMETRY</span>
              <span className="text-primary font-mono uppercase font-semibold">Homography / RANSAC</span>
            </div>
          </div>
        </div>

        <Button
          type="button"
          variant="primary"
          className="w-full relative overflow-hidden py-3 font-mono text-xs"
          onClick={handleQuickRun}
          loading={loading}
          disabled={loading}
          icon={!loading ? "play_arrow" : undefined}
        >
          {loading ? 'RUNNING ALIGNMENT...' : 'EXECUTE DEMO PIPELINE'}
        </Button>
      </div>
    </div>
  );
}

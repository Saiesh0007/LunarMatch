import { useRegistrationStore } from '../../../store/registrationStore.js';
import { useState } from 'react';
import { apiClient } from '../../../api/client.js';

export function useRegistration() {
  const store = useRegistrationStore();
  const [isSwapped, setIsSwapped] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);

  const toggleSwap = () => setIsSwapped(!isSwapped);

  const handlePreview = async () => {
    if (!store.referenceFile?.imageId || !store.movingFile?.imageId) {
      alert("Please upload both images first.");
      return;
    }

    setIsProcessing(true);

    // Convert short engine names to API Enums
    // (We fallback to what's defined in the backend: sift | rift2 | hopc | superpoint)
    // SIFT in our UI maps to "sift", "rift2" -> "rift2", "superpoint" -> "sift" (assuming fallback, backend doesn't have superpoint yet without torch)
    // Actually our UI has selectedEngine: 'sift' | 'rift2' | 'superpoint'

    try {
      const config = {
        reference_image_id: store.referenceFile.imageId,
        moving_image_id: store.movingFile.imageId,
        feature_method: store.selectedEngine === 'superpoint' ? 'sift' : store.selectedEngine,
        geometric_model: store.selectedModel === 'homography' ? 'homography' : 'affine',
        simulation_mode: store.selectedEngine === 'superpoint' ? true : false,
        spatial_balancing: true
      };

      const result = await apiClient.runPipeline(config);
      console.log("Pipeline result:", result);
      store.setPipelineResult(result);
      // You could redirect to results page here or show an overlay
      alert(`Pipeline finished successfully! Mode: ${result.execution_mode}, RMSE: ${result.metrics.rmse_px.toFixed(2)}px`);
    } catch (e) {
      console.error(e);
      alert("Pipeline execution failed: " + e.message);
    } finally {
      setIsProcessing(false);
    }
  };

  const isReady = !!(store.referenceFile && store.movingFile);

  return {
    ...store,
    isSwapped,
    toggleSwap,
    isProcessing,
    handlePreview,
    isReady
  };
}

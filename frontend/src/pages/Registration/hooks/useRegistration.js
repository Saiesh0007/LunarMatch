import { useRegistrationStore } from '../../../store/registrationStore.js';
import { useState } from 'react';
import { apiClient } from '../../../api/client.js';

export function useRegistration() {
  const store = useRegistrationStore();
  const [isSwapped, setIsSwapped] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [errorMessage, setErrorMessage] = useState(null);

  const toggleSwap = () => setIsSwapped(!isSwapped);

  const handlePreview = async () => {
    setErrorMessage(null);
    const refFile = isSwapped ? store.movingFile : store.referenceFile;
    const movFile = isSwapped ? store.referenceFile : store.movingFile;

    if (!refFile?.imageId || !movFile?.imageId) {
      setErrorMessage("Please upload or select both Reference (Frame A) and Moving (Frame B) images before executing alignment.");
      return;
    }

    setIsProcessing(true);

    try {
      const config = {
        reference_image_id: refFile.imageId,
        moving_image_id: movFile.imageId,
        feature_method: store.selectedEngine === 'superpoint' ? 'sift' : store.selectedEngine,
        geometric_model: store.selectedModel === 'homography' ? 'homography' : 'affine',
        simulation_mode: store.selectedEngine === 'superpoint',
        spatial_balancing: true
      };

      const result = await apiClient.runPipeline(config);
      store.setPipelineResult(result);

      // Smooth scroll to result
      setTimeout(() => {
        const resultElem = document.getElementById('results-section');
        if (resultElem) {
          resultElem.scrollIntoView({ behavior: 'smooth' });
        }
      }, 100);
    } catch (e) {
      console.error("Pipeline run failed:", e);
      setErrorMessage(e.message || "Pipeline execution failed on backend server.");
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
    isReady,
    errorMessage,
    clearError: () => setErrorMessage(null)
  };
}

import { useRegistrationStore } from '../../../store/registrationStore.js';
import { useState } from 'react';

export function useRegistration() {
  const store = useRegistrationStore();
  const [isSwapped, setIsSwapped] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);

  const toggleSwap = () => setIsSwapped(!isSwapped);

  const handlePreview = () => {
    setIsProcessing(true);
    setTimeout(() => setIsProcessing(false), 2000);
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

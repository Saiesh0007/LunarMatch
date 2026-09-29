import React from 'react';
import { useRegistration } from './hooks/useRegistration.js';
import { StepHeader } from './StepHeader.jsx';
import { InfoBanner } from './InfoBanner.jsx';
import { ImagePanel } from './ImagePanel.jsx';
import { AlgorithmConfig } from './AlgorithmConfig.jsx';
import { ActionBar } from './ActionBar.jsx';

export default function Registration() {
  const { 
    referenceFile, movingFile, 
    selectedEngine, setSelectedEngine,
    selectedModel, setSelectedModel,
    isSwapped, toggleSwap, clearFiles, loadSample,
    isProcessing, handlePreview, isReady
  } = useRegistration();

  return (
    <div className="max-w-[1200px] mx-auto pb-12 relative">
      <StepHeader onSwap={toggleSwap} onClear={clearFiles} onLoadSample={loadSample} />
      <InfoBanner />
      
      <div className="grid xl:grid-cols-2 gap-6 relative">
        <ImagePanel 
          title="Frame A // Fixed" 
          subtitle="Reference Base"
          file={isSwapped ? movingFile : referenceFile}
          roleId="reference"
          orderClass={isSwapped ? "xl:order-2" : "xl:order-1"}
        />
        
        <ImagePanel 
          title="Frame B // Target" 
          subtitle="Moving Image"
          file={isSwapped ? referenceFile : movingFile}
          roleId="moving"
          orderClass={isSwapped ? "xl:order-1" : "xl:order-2"}
        />
      </div>

      <AlgorithmConfig 
        selectedEngine={selectedEngine}
        setSelectedEngine={setSelectedEngine}
        selectedModel={selectedModel}
        setSelectedModel={setSelectedModel}
      />
      
      <ActionBar 
        isReady={isReady} 
        isProcessing={isProcessing} 
        onPreview={handlePreview} 
      />
    </div>
  );
}

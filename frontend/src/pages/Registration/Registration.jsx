import React from 'react';
import { useRegistration } from './hooks/useRegistration.js';
import { StepHeader } from './StepHeader.jsx';
import { InfoBanner } from './InfoBanner.jsx';
import { ImagePanel } from './ImagePanel.jsx';
import { AlgorithmConfig } from './AlgorithmConfig.jsx';
import { ActionBar } from './ActionBar.jsx';
import { ResultPanel } from './ResultPanel.jsx';
import { Icon } from '../../components/ui/Icon.jsx';

export default function Registration() {
  const {
    referenceFile, setReferenceFile,
    movingFile, setMovingFile,
    selectedEngine, setSelectedEngine,
    selectedModel, setSelectedModel,
    isSwapped, toggleSwap, clearFiles, loadSample,
    isProcessing, handlePreview, isReady, pipelineResult,
    errorMessage, clearError
  } = useRegistration();

  return (
    <div className="max-w-[1200px] mx-auto pb-12 relative">
      <StepHeader onSwap={toggleSwap} onClear={clearFiles} onLoadSample={loadSample} />
      <InfoBanner />

      {errorMessage && (
        <div className="mb-6 p-4 bg-error-container/20 border border-error/50 rounded-xl flex items-center justify-between gap-3 text-error">
          <div className="flex items-center gap-3">
            <Icon name="error" size="20px" className="flex-shrink-0" />
            <span className="font-mono text-xs">{errorMessage}</span>
          </div>
          <button
            type="button"
            onClick={clearError}
            className="text-error hover:opacity-80 font-bold px-2"
          >
            ✕
          </button>
        </div>
      )}

      <div className="grid xl:grid-cols-2 gap-6 relative">
        <ImagePanel
          title="Frame A // Fixed"
          subtitle="Reference Base"
          file={isSwapped ? movingFile : referenceFile}
          onUpload={(f) => isSwapped ? setMovingFile(f) : setReferenceFile(f)}
          roleId="reference"
          orderClass={isSwapped ? "xl:order-2" : "xl:order-1"}
        />

        <ImagePanel
          title="Frame B // Target"
          subtitle="Moving Image"
          file={isSwapped ? referenceFile : movingFile}
          onUpload={(f) => isSwapped ? setReferenceFile(f) : setMovingFile(f)}
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

      <div id="results-section">
        <ResultPanel result={pipelineResult} />
      </div>
    </div>
  );
}

import { create } from 'zustand';

export const useRegistrationStore = create((set) => ({
  referenceFile: null,
  movingFile: null,
  selectedEngine: 'sift',
  selectedModel: 'homography',
  pipelineResult: null,

  setReferenceFile: (file) => set({ referenceFile: file }),
  setMovingFile: (file) => set({ movingFile: file }),
  setSelectedEngine: (engine) => set({ selectedEngine: engine }),
  setSelectedModel: (model) => set({ selectedModel: model }),
  setPipelineResult: (result) => set({ pipelineResult: result }),

  clearFiles: () => set({ referenceFile: null, movingFile: null, pipelineResult: null }),
  loadSample: () => set({
    referenceFile: { name: 'Demo Pair A (Ref)', size: 'Auto', imageId: 'demo_pair_a_ref' },
    movingFile: { name: 'Demo Pair A (Mov)', size: 'Auto', imageId: 'demo_pair_a_mov' },
    pipelineResult: null
  })
}));

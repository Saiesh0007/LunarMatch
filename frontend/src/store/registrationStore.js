import { create } from 'zustand';

export const useRegistrationStore = create((set) => ({
  referenceFile: null,
  movingFile: null,
  selectedEngine: 'sift',
  selectedModel: 'homography',
  
  setReferenceFile: (file) => set({ referenceFile: file }),
  setMovingFile: (file) => set({ movingFile: file }),
  setSelectedEngine: (engine) => set({ selectedEngine: engine }),
  setSelectedModel: (model) => set({ selectedModel: model }),
  
  clearFiles: () => set({ referenceFile: null, movingFile: null }),
  loadSample: () => set({ 
    referenceFile: { name: 'ohrc_cal_2026.tif', size: '14.2 MB' },
    movingFile: { name: 'tmc2_raw_2026.tif', size: '18.1 MB' }
  })
}));

export const PIPELINE_STAGES = [
  { id: '01', title: 'Multi-Modal Ingestion', description: 'Orbital CRS alignment and metadata parsing for TMC-2, OHRC, and IIRS modalities.', tags: ['TIFF', 'PDS4', 'RasterIO'], icon: 'satellite_alt' },
  { id: '02', title: 'Radiometric Normalisation', description: 'Contrast enhancement, destriping, and shadow suppression for cross-sensor homogeneity.', tags: ['CLAHE', 'Histogram Matching'], icon: 'contrast' },
  { id: '03', title: 'Phase Congruency', description: 'Illumination-invariant edge extraction via log-Gabor wavelets. (RIFT2 primary)', tags: ['Gabor Bank 4x6', 'Log-Gabor'], icon: 'memory' },
  { id: '04', title: 'Descriptor Modulation', description: 'Feature encoding via pre-trained geometric descriptors or classical spatial pooling.', tags: ['SuperPoint', 'SIFT'], icon: 'hub' },
  { id: '05', title: 'Nearest-Neighbor Matching', description: 'Sinkhorn-driven optimal transport or classical approximate nearest neighbor (FLANN).', tags: ['SuperGlue', 'BF 2-NN'], icon: 'join_inner' },
  { id: '06', title: 'Ambiguity Ratio Filter', description: 'Lowe\'s ratio test to discard topologically ambiguous local maxima matching.', tags: ['Ratio < 0.8'], icon: 'filter_alt' },
  { id: '07', title: 'Geometric Consensus', description: 'Robust model fitting to reject outliers and establish true spatial correspondence.', tags: ['RANSAC', 'MAGSAC++'], icon: 'architecture' },
  { id: '08', title: 'Spatial Grid Balancing', description: 'Quad-tree point redistribution ensuring uniform metric coverage across the lunar terrain.', tags: ['Grid: 10x10', 'Uniformity'], icon: 'grid_view' },
  { id: '09', title: 'Quality Evaluation', description: 'Subpixel RMSE calculation and confidence interval generation over the inlier set.', tags: ['RMSE Calc', 'Telemetry Out'], icon: 'analytics' }
];

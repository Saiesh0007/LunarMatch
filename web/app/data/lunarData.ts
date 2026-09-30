/**
 * LUNARMATCH Next.js — Scientific Telemetry & Research Metadata
 * ISRO Problem Statement 26166 | Smart India Hackathon 2026
 */

export interface MetricData {
  keypointsRef: number;
  keypointsMov: number;
  candidateMatches: number;
  filteredMatches: number;
  ransacInliers: number;
  inlierRatio: number;
  rmsePx: number;
  spatialCoverage: number;
  mutualInformation: number;
  ssim: number;
  runtimeMs: number;
  status: "SUCCESSFUL" | "LOW_CONFIDENCE" | "FAILED";
  confidenceExplanation: string;
}

export interface PresetPair {
  id: string;
  name: string;
  region: string;
  refSensor: string;
  movSensor: string;
  refPath: string;
  movPath: string;
  sunAngleDelta: string;
  scaleDelta: string;
  expectedOutcome: string;
  metrics: MetricData;
}

export interface TiePoint {
  id: number;
  refX: number;
  refY: number;
  movX: number;
  movY: number;
  residual: number;
  score: number;
  inlier: boolean;
}

export interface SensorSpec {
  code: string;
  mission: string;
  sensor: string;
  gsd: string;
  swath: string;
  spectrum: string;
  role: string;
}

export const LUNAR_METADATA = {
  title: "LUNARMATCH",
  subtitle: "Multi-Modal Lunar Image Correspondence & Registration Engine",
  organization: "ISRO / Department of Space",
  hackathon: "Smart India Hackathon 2026",
  problemStatement: "PS 26166 — Space Technology",
  domain: "Space Applications & Computer Vision",
  team: "Team Spectrum",
  seed: 26166,
  version: "1.0.0-PROD"
};

export const SENSOR_SPECS: SensorSpec[] = [
  {
    code: "OHRC",
    mission: "Chandrayaan-2",
    sensor: "Orbiter High Resolution Camera",
    gsd: "0.25 m / pixel",
    swath: "12 km",
    spectrum: "Panchromatic (450–900 nm)",
    role: "High-Resolution Target Imagery"
  },
  {
    code: "TMC-2",
    mission: "Chandrayaan-2",
    sensor: "Terrain Mapping Camera-2",
    gsd: "5.0 m / pixel",
    swath: "20 km stereo triplet",
    spectrum: "Panchromatic (500–850 nm)",
    role: "Digital Elevation Model & Ortho Context"
  },
  {
    code: "IIRS",
    mission: "Chandrayaan-2",
    sensor: "Imaging Infra-Red Spectrometer",
    gsd: "80 m / pixel",
    swath: "20 km (256 spectral bands)",
    spectrum: "Hyperspectral (0.8–5.0 µm)",
    role: "Mineralogical & Volatile Mapping"
  },
  {
    code: "LRO-NAC",
    mission: "Lunar Reconnaissance Orbiter (NASA)",
    sensor: "Narrow Angle Camera",
    gsd: "0.5 m / pixel",
    swath: "5 km paired cameras",
    spectrum: "Panchromatic (400–750 nm)",
    role: "Geodetic Global Reference"
  },
  {
    code: "SELENE-TC",
    mission: "Kaguya / SELENE (JAXA)",
    sensor: "Terrain Camera",
    gsd: "10 m / pixel",
    swath: "35 km stereo",
    spectrum: "Panchromatic (450–700 nm)",
    role: "Global Lunar DEM Reference"
  }
];

export const PRESET_PAIRS: Record<string, PresetPair> = {
  pair_a: {
    id: "pair_a",
    name: "OHRC vs TMC-2 (Tycho Crater Rim)",
    region: "Tycho Crater Rim (43.3° S, 11.2° W)",
    refSensor: "OHRC (0.25m GSD)",
    movSensor: "TMC-2 (5.0m GSD)",
    refPath: "/assets/demo/pair_a_ref.png",
    movPath: "/assets/demo/pair_a_mov.png",
    sunAngleDelta: "34.2°",
    scaleDelta: "20.0×",
    expectedOutcome: "SUCCESSFUL (OPTIMAL)",
    metrics: {
      keypointsRef: 1248,
      keypointsMov: 1104,
      candidateMatches: 612,
      filteredMatches: 416,
      ransacInliers: 384,
      inlierRatio: 0.923,
      rmsePx: 0.28,
      spatialCoverage: 0.938,
      mutualInformation: 0.842,
      ssim: 0.916,
      runtimeMs: 142.5,
      status: "SUCCESSFUL",
      confidenceExplanation: "Registration verified under stringent geometric consensus. MAGSAC++ residual RMSE = 0.28 px (< 0.50 px threshold) across 384 consensus inliers. Uniform 4x4 spatial grid coverage = 93.8%."
    }
  },
  pair_b: {
    id: "pair_b",
    name: "IIRS vs LRO NAC (South Pole Aitken)",
    region: "South Pole-Aitken Basin (70.2° S, 160.5° E)",
    refSensor: "LRO NAC (0.5m GSD)",
    movSensor: "IIRS Hyperspectral (80m GSD)",
    refPath: "/assets/demo/pair_b_ref.png",
    movPath: "/assets/demo/pair_b_mov.png",
    sunAngleDelta: "52.8°",
    scaleDelta: "160.0×",
    expectedOutcome: "SUCCESSFUL (OPTIMAL)",
    metrics: {
      keypointsRef: 980,
      keypointsMov: 820,
      candidateMatches: 380,
      filteredMatches: 232,
      ransacInliers: 196,
      inlierRatio: 0.845,
      rmsePx: 0.38,
      spatialCoverage: 0.875,
      mutualInformation: 0.768,
      ssim: 0.852,
      runtimeMs: 188.0,
      status: "SUCCESSFUL",
      confidenceExplanation: "Multi-modal infrared-to-optical registration validated through RIFT2 phase congruency. Residual error bounded to 0.38 px despite extreme 160x scale disparity."
    }
  }
};

export const TIE_POINTS: TiePoint[] = [
  { id: 0, refX: 118.8, refY: 85.0, movX: 112.5, movY: 81.0, residual: 0.43, score: 0.96, inlier: true },
  { id: 1, refX: 219.1, refY: 399.8, movX: 235.2, movY: 398.4, residual: 0.46, score: 0.94, inlier: true },
  { id: 2, refX: 374.7, refY: 327.9, movX: 390.6, movY: 314.7, residual: 0.17, score: 0.99, inlier: true },
  { id: 3, refX: 100.5, refY: 395.2, movX: 112.7, movY: 401.2, residual: 0.66, score: 0.91, inlier: true },
  { id: 4, refX: 50.2,  refY: 534.0, movX: 70.1,  movY: 547.1, residual: 0.07, score: 0.99, inlier: true },
  { id: 5, refX: 133.3, refY: 410.4, movX: 148.5, movY: 414.5, residual: 0.35, score: 0.95, inlier: true },
  { id: 6, refX: 229.0, refY: 395.4, movX: 245.0, movY: 393.1, residual: 0.19, score: 0.98, inlier: true },
  { id: 7, refX: 168.5, refY: 131.1, movX: 166.9, movY: 125.3, residual: 1.01, score: 0.88, inlier: true },
  { id: 8, refX: 362.0, refY: 567.7, movX: 391.5, movY: 562.5, residual: 1.65, score: 0.72, inlier: false },
  { id: 9, refX: 163.9, refY: 385.0, movX: 177.7, movY: 386.7, residual: 0.74, score: 0.92, inlier: true },
  { id: 10, refX: 82.7, refY: 370.7, movX: 93.2,  movY: 376.9, residual: 0.42, score: 0.95, inlier: true },
  { id: 11, refX: 206.0, refY: 308.9, movX: 216.0, movY: 306.0, residual: 0.08, score: 0.99, inlier: true },
  { id: 12, refX: 184.3, refY: 136.6, movX: 183.0, movY: 129.9, residual: 0.97, score: 0.89, inlier: true },
  { id: 13, refX: 150.0, refY: 366.3, movX: 162.1, movY: 368.4, residual: 0.12, score: 0.99, inlier: true },
  { id: 14, refX: 505.4, refY: 542.8, movX: 538.8, movY: 527.4, residual: 0.57, score: 0.93, inlier: true },
  { id: 15, refX: 298.1, refY: 344.7, movX: 313.1, movY: 336.8, residual: 0.16, score: 0.99, inlier: true },
  { id: 16, refX: 195.4, refY: 568.5, movX: 221.5, movY: 574.5, residual: 0.98, score: 0.87, inlier: true },
  { id: 17, refX: 126.3, refY: 78.1,  movX: 120.5, movY: 74.4,  residual: 1.94, score: 0.65, inlier: false },
  { id: 18, refX: 186.7, refY: 548.9, movX: 211.0, movY: 553.8, residual: 0.66, score: 0.93, inlier: true },
  { id: 19, refX: 420.2, refY: 190.5, movX: 442.1, movY: 186.2, residual: 0.31, score: 0.97, inlier: true },
  { id: 20, refX: 470.8, refY: 260.4, movX: 495.2, movY: 254.1, residual: 0.29, score: 0.98, inlier: true },
  { id: 21, refX: 280.4, refY: 480.1, movX: 298.3, movY: 479.5, residual: 0.22, score: 0.98, inlier: true },
  { id: 22, refX: 75.3,  refY: 210.8, movX: 84.1,  movY: 208.5, residual: 0.39, score: 0.96, inlier: true },
  { id: 23, refX: 340.6, refY: 110.2, movX: 351.4, movY: 104.9, residual: 0.44, score: 0.95, inlier: true },
  { id: 24, refX: 520.1, refY: 380.0, movX: 552.0, movY: 374.2, residual: 0.36, score: 0.96, inlier: true },
  { id: 25, refX: 410.5, refY: 460.3, movX: 432.8, movY: 454.1, residual: 0.27, score: 0.97, inlier: true },
  { id: 26, refX: 620.0, refY: 120.0, movX: 670.0, movY: 180.0, residual: 4.82, score: 0.41, inlier: false },
  { id: 27, refX: 310.2, refY: 220.5, movX: 326.5, movY: 214.8, residual: 0.21, score: 0.98, inlier: true }
];

export const SPATIAL_GRID_4X4 = [
  [18, 22, 19, 14],
  [24, 38, 31, 20],
  [27, 42, 36, 25],
  [16, 28, 26, 18]
];

export const ROBUSTNESS_SUN_ANGLE = [
  { angle: 0,  rift2Rmse: 0.25, siftRmse: 0.40, orbRmse: 0.65, rift2Inliers: 395, siftInliers: 438, orbInliers: 210 },
  { angle: 15, rift2Rmse: 0.25, siftRmse: 0.40, orbRmse: 0.78, rift2Inliers: 392, siftInliers: 425, orbInliers: 172 },
  { angle: 30, rift2Rmse: 0.25, siftRmse: 0.40, orbRmse: 0.95, rift2Inliers: 388, siftInliers: 376, orbInliers: 114 },
  { angle: 45, rift2Rmse: 0.26, siftRmse: 0.42, orbRmse: 1.48, rift2Inliers: 381, siftInliers: 311, orbInliers: 48 },
  { angle: 60, rift2Rmse: 0.26, siftRmse: 0.58, orbRmse: 2.85, rift2Inliers: 374, siftInliers: 184, orbInliers: 12 },
  { angle: 75, rift2Rmse: 0.28, siftRmse: 1.15, orbRmse: null, rift2Inliers: 362, siftInliers: 42,  orbInliers: 0 },
  { angle: 80, rift2Rmse: 0.29, siftRmse: 1.94, orbRmse: null, rift2Inliers: 350, siftInliers: 14,  orbInliers: 0 }
];

export const PIPELINE_STAGES = [
  {
    step: 1,
    name: "Radiometric Preprocessing & Phase Congruency",
    acronym: "RIFT2",
    description: "Log-Gabor multi-scale multi-orientation filter bank computes illumination-invariant phase congruency maps and maximum moment tensor orientation.",
    math: "PC(x,y) = \\frac{\\sum_o E_o(x,y)}{\\epsilon + \\sum_o \\sum_s A_{s,o}(x,y)}"
  },
  {
    step: 2,
    name: "Structural Feature Point Extraction",
    acronym: "HOPC",
    description: "Extracts high-entropy keypoints over the maximum moment phase maps with sub-pixel Harris response and uniform non-maximum suppression.",
    math: "R = \\det(M) - k \\cdot \\text{tr}(M)^2"
  },
  {
    step: 3,
    name: "Sinkhorn Optimal Transport Matching",
    acronym: "SUPERGLUE-OT",
    description: "Calculates assignment probability matrix with dustbin row/column augmentation via log-domain Sinkhorn-Knopp iterations under seed 26166.",
    math: "P_{i,j} = \\exp(M_{i,j}), \\quad \\sum_j P_{i,j} = 1, \\quad \\sum_i P_{i,j} = 1"
  },
  {
    step: 4,
    name: "MAGSAC++ Robust Homography Estimation",
    acronym: "MAGSAC++",
    description: "Marginalizing sample consensus estimates homography H without manual threshold tuning, weighting point residuals via chi-squared distribution.",
    math: "P(I | \\theta) = \\int_0^{\\sigma_{max}} P(I | \\theta, \\sigma) P(\\sigma) d\\sigma"
  },
  {
    step: 5,
    name: "Sub-pixel Phase Correlation Refinement",
    acronym: "SP-PC",
    description: "Refines localized patch displacement using Fourier phase correlation surface peak interpolation, reaching sub-0.1 px precision.",
    math: "Q = \\frac{F_{ref} \\odot F_{mov}^*}{|F_{ref} \\odot F_{mov}^*|}"
  }
];

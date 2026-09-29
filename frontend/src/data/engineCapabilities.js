export const ENGINE_CAPABILITIES = [
  { id: 'sift', title: 'SIFT Classical', version: 'v3.1.2', description: 'Gradient-based rotational invariant features.', params: ['Octaves: 4', 'Contrast: 0.04'] },
  { id: 'rift2', title: 'RIFT2', version: 'v2.0.4', description: 'Phase congruency robust against nonlinear radiation diffs.', params: ['Scales: 4', 'Orient: 6'] },
  { id: 'superpoint', title: 'SuperPoint VGG', version: 'v1.4 (ONNX)', description: 'Self-supervised interest point detection network.', params: ['NMS: 4', 'Conf: 0.015'] },
  { id: 'superglue', title: 'SuperGlue Sinkhorn', version: 'v1.1 (ONNX)', description: 'Graph neural network matcher with attention.', params: ['Sinkhorn Iters: 20'] }
];

# Implementation Audit Notes

## Demo Fixture Resolution and Execution Profile
- **Fixture Identity**: `pair_a_ref.png` and `pair_a_mov.png` in `data/examples/`.
- **Fixture Shape**: Native shape is **640×640** pixels (confirmed via rasterio and OpenCV).
- **Execution Mode**: The pipeline loads and processes the demo pair at its native resolution (640×640) without synthetic upscaling.
- **RIFT2 Direct Routing (F29)**: RIFT2 feature extraction is executed live (`ExecutionMode.LIVE`), computing Kovesi phase congruency with Log-Gabor filters across 4 scales and 6 orientations, producing 216-D orientation histogram descriptors.
- **Vectorized Extraction**: Per-keypoint patch extraction uses batched 3-channel affine warping over local windows combined with flat `np.bincount` histogram accumulation, ensuring runtime remains within the demo pipeline latency budget.

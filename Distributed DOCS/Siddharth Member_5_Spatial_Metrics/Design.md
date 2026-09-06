# LunarMatch — Spatial + Evaluation Engineer Design

## Goal

Spatially balanced correspondences, RMSE, inlier metrics, spatial coverage, benchmarking

## Files Owned

- `src/spatial.py`
- `src/metrics.py`

## Spatial Balancing

Start with a grid-based method:

```text
candidate matches
→ assign to grid cells
→ rank by quality
→ retain strong matches across cells
→ calculate coverage
```

Interface:

```python
spatially_balance(
    matches,
    image_shape,
    grid=(4,4)
)
```

## Metrics

Implement real calculations for:
- candidate match count
- filtered match count
- inlier count
- inlier ratio
- spatial coverage
- RMSE/reprojection error where mathematically valid
- runtime

## Important

Define every metric clearly in code/documentation. Do not compare values produced under incompatible definitions.

## Visual Priority

```text
Registered result
>
Correspondence visualization
>
Metrics
>
Pipeline status
>
Configuration
```

## Demo Requirement

A panel member should understand the result without reading source code.

## Failure Requirement

The system should explain when a registration is unreliable.

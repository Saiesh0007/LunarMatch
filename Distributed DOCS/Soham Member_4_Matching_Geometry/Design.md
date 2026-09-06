# LunarMatch — Matching + Geometry Engineer Design

## Goal

Descriptor matching, filtering, RANSAC, transformation estimation, image registration

## Files Owned

- `src/matching.py`
- `src/geometry.py`
- registration/warping helper if needed

## Matching Interface

```python
match_features(
    desc_ref,
    desc_mov,
    method="bf"
)
```

## Filtering

Implement k-nearest-neighbour matching and ratio filtering.

## Geometry Interface

```python
estimate_transform(
    points_ref,
    points_mov,
    model="homography"
)
```

Return:
- transformation matrix
- inlier mask
- inlier count
- inlier ratio

## Registration

```python
warp_image(
    moving,
    transformation,
    reference_shape
)
```

## Safety

Reject unstable transformations and insufficient correspondences.

## Advanced

RANSAC improvements and learned matching can be explored after the baseline works.

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

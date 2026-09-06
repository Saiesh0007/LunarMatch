# LunarMatch — src modules

## Module Interfaces

Every module in `src/` exposes a consistent interface so extractors, matchers, and estimators are interchangeable.

```
extract(image) → keypoints, descriptors
match(descriptors_a, descriptors_b) → candidate_matches
estimate(points_a, points_b) → transformation, inlier_mask
register(reference, moving, transformation) → registered_image
evaluate(matches, inliers, transformation) → metrics
```

## Rules

- Never hard-code feature extraction into matching — keep them as separate replaceable components.
- Record all parameters used in a run (preprocessing config, feature method, matcher, ratio threshold, RANSAC threshold, spatial-balancing settings) for reproducibility.
- Distinguish match types at every stage: candidate → filtered → geometrically verified inlier → spatially selected correspondence.
- Preprocessing chain must be configurable, not hard-coded.
- RANSAC must record: model type, threshold, inlier count, inlier ratio, transformation matrix.
- Spatial balancing: divide image into grid, assign matches to cells, rank by quality, keep strong matches per cell, calculate coverage.
- Fail safely — return a low-confidence result instead of an untrustworthy registration when correspondence quality is insufficient.

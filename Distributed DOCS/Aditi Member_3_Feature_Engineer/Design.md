# LunarMatch — Feature Extraction Engineer Design

## Goal

SIFT baseline, RIFT experimental integration, feature/keypoint visualization, extractor interface

## Files Owned

- `src/features.py`

## Interface

```python
extract_features(
    image,
    method="sift"
) -> {
    "keypoints": keypoints,
    "descriptors": descriptors
}
```

## MVP

Implement SIFT reliably.

## Advanced

Add RIFT behind the same interface if time permits.

## Visualization

Provide a helper or serializable result that allows the UI to display keypoints.

## Requirements

The extractor should handle:
- low-texture images
- empty descriptor output
- different image sizes
- reproducible configuration

## Do Not Own

Do not implement matching or RANSAC inside the feature module.

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

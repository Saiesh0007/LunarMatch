# LunarMatch — Design Specification

## 1. Design Goal

Create a technically credible, demonstrable prototype for SIH 2026 PS 26166 without overclaiming research results.

The design prioritizes:

1. a working end-to-end registration pipeline
2. visible correspondence points
3. registered output
4. quantitative metrics
5. spatially balanced matching
6. a clear path to RIFT / learned matching / sub-pixel refinement

## 2. User Flow

```text
Open application
      │
      ▼
Select reference image
      │
      ▼
Select moving image
      │
      ▼
Select sensor labels
      │
      ▼
Configure method
      │
      ▼
Run LunarMatch
      │
      ├── preprocessing
      ├── feature extraction
      ├── matching
      ├── geometric verification
      ├── spatial balancing
      └── registration
      │
      ▼
View results
      │
      ├── keypoint visualization
      ├── correspondence visualization
      ├── registered overlay
      ├── metrics
      └── confidence / failure reason
```

## 3. UI Layout

### Header

```text
LUNARMATCH
Multi-Modal Lunar Image Correspondence & Registration

SIH 2026 • PS 26166
```

### Input Panel

```text
Reference Image       Moving Image
[ Upload ]             [ Upload ]

Reference sensor      Moving sensor
[ OHRC ▼ ]             [ IIRS ▼ ]

[ Run LunarMatch ]
```

### Configuration

```text
Feature method:
○ SIFT
○ RIFT
○ Learned (if available)

Preprocessing:
☑ Normalize
☑ Contrast enhancement
☑ Denoise

Spatial balancing:
☑ Enabled

Geometric model:
○ Affine
○ Homography
```

Advanced controls should be hidden by default to keep the demo simple.

## 4. Results Dashboard

### Pipeline Status

```text
✓ Input validation
✓ Preprocessing
✓ Feature extraction
✓ Feature matching
✓ Geometric verification
✓ Spatial balancing
✓ Registration
```

### Metrics

Display at minimum:

- Keypoints — reference
- Keypoints — moving
- Candidate matches
- Good matches
- RANSAC inliers
- Inlier ratio
- RMSE / reprojection error where calculable
- Spatial coverage
- Registration confidence

Do not fabricate a metric. If it cannot be calculated reliably, show `N/A`.

## 5. Visual Outputs

### A. Keypoints

Show reference and moving images with detected points.

### B. Correspondence View

Show selected correspondences as lines between the two images.

Use two states if useful:

```text
Before spatial balancing
After spatial balancing
```

This makes the spatial-coverage contribution visible.

### C. Registration Overlay

Show:
- reference
- registered moving image
- alpha overlay
- optional difference image

### D. Error Visualization

Where valid ground-truth or proxy error is available, visualize residuals.

## 6. Design for Demonstration

The demo should be deterministic.

Recommended sequence:

1. load a known-good pair
2. show preprocessing
3. run baseline
4. show correspondences
5. show RANSAC inliers
6. show spatially balanced points
7. show registered result
8. show metrics
9. optionally run a robustness case

Do not make the panel wait for large model downloads during the main demo.

## 7. Visual Hierarchy

The most important result is the registered product.

Priority:

```text
1. Registered image
2. Correspondence visualization
3. Metrics
4. Pipeline status
5. Configuration
6. Debug details
```

## 8. Failure State Design

If registration fails:

```text
REGISTRATION NOT RELIABLE

Reason:
Insufficient geometrically consistent correspondences.

Detected:
Keypoints: 84
Valid matches: 7
RANSAC inliers: 3

Suggested action:
• Try another image pair
• Enable stronger preprocessing
• Use RIFT / learned matching
```

This is preferable to displaying a visually plausible but incorrect registration.

## 9. Accessibility and Readability

- Use large labels for the four primary metrics.
- Avoid dense text during the live demo.
- Use consistent terminology: reference, moving, keypoint, match, inlier, registered image.
- Keep technical logs available in an expandable section.

## 10. Engineering UX Principles

- Every run gets a unique run configuration in memory/log output.
- Parameters should be visible enough to reproduce a result.
- The UI should never imply that a prototype component is scientifically validated when it is only experimental.
- "Sub-pixel" should only appear as a completed result after an actual sub-pixel method and validation have been implemented.

## 11. Suggested Demo Screens

### Screen 1 — Problem / Input
Two lunar images and sensor labels.

### Screen 2 — Correspondence
Raw/filtered/inlier matches.

### Screen 3 — Registration
Before/after overlay.

### Screen 4 — Evaluation
RMSE, inlier count, inlier ratio and spatial coverage.

### Screen 5 — Robustness
Controlled scale, rotation and illumination tests.

## 12. MVP Design Rule

A smaller working interface is preferred over a larger interface containing unimplemented controls.

If RIFT or LightGlue is not ready, the UI should not pretend that selecting the option executes those methods.

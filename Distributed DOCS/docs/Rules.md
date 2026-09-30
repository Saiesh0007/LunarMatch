# LunarMatch — Development Rules

## Rule 1 — Never Overclaim

The system must never claim an algorithm or capability that has not been implemented and tested.

Examples:
- Do not claim "RIFT implemented" until RIFT actually runs.
- Do not claim "sub-pixel accuracy" without a validated sub-pixel refinement and measurement.
- Do not claim "sun-angle invariant" based only on one successful image.
- Do not claim cross-modal robustness without testing cross-modal pairs.

Use precise wording:
- "designed to be robust"
- "prototype evaluation"
- "baseline"
- "experimental"
- "planned"

when the evidence does not support a stronger claim.

## Rule 2 — Working Software Before Fancy Software

Priority order:

```text
Working algorithm
>
Correct metrics
>
Reliable visualization
>
Advanced model
>
Fancy UI
```

A stable SIFT/RANSAC prototype is preferable to a broken learned pipeline.

## Rule 3 — Every Result Must Be Reproducible

Record:
- input pair
- preprocessing configuration
- feature method
- matcher
- ratio threshold
- geometric model
- RANSAC threshold
- spatial-balancing settings
- resulting metrics

## Rule 4 — Never Fake Metrics

Do not hard-code:
- RMSE
- inlier count
- inlier ratio
- spatial coverage
- confidence
- keypoint count
- match count

All displayed metrics must come from the current or recorded experiment.

## Rule 5 — Distinguish Match Types

The software should distinguish:

```text
candidate matches
      ↓
filtered matches
      ↓
geometrically verified inliers
      ↓
spatially selected correspondences
```

Do not call every descriptor match a reliable correspondence.

## Rule 6 — Spatial Coverage Matters

The PS explicitly calls for uniform spatial distribution.

Do not optimize only for the number of matches.

A smaller set of strong, well-distributed correspondences can be more useful than a large cluster from one region.

## Rule 7 — RANSAC Is a Verification Stage

RANSAC should be used to reject geometrically inconsistent matches.

Always record:
- model type
- threshold
- number of iterations if configurable
- inlier count
- inlier ratio

## Rule 8 — Preserve Image Integrity

Never silently overwrite original imagery.

Use:

```text
data/raw/
data/processed/
outputs/
```

and preserve:
- original dimensions
- scale factors
- metadata where possible

## Rule 9 — Separate Reference and Moving Images

Terminology:

**Reference / fixed:** target coordinate system.

**Moving / source:** image that gets transformed.

Never reverse these labels in the UI.

## Rule 10 — Keep Algorithms Modular

Feature extraction must not be hard-coded into matching.

Use replaceable components:

```text
Extractor
Matcher
GeometricEstimator
SpatialSelector
Registrar
Metrics
```

This makes it possible to compare SIFT, RIFT and learned approaches.

## Rule 11 — Avoid Unnecessary Dependencies

For the emergency prototype, prefer:
- Python
- OpenCV
- NumPy
- Streamlit

Add dependencies only when they solve a real requirement.

## Rule 12 — No Internet Dependency During the Main Demo

The primary demo should work from locally available images and installed models/libraries.

Do not depend on:
- live downloads
- external APIs
- remote model downloads
- unstable network access

unless a tested offline fallback exists.

## Rule 13 — Always Maintain a Known-Good Demo Pair

Keep at least one pair that:
- has sufficient overlap
- reliably produces correspondences
- produces stable registration
- has tested metrics

The known-good pair is the emergency fallback for the presentation.

## Rule 14 — Maintain a Backup Demo

Have:
1. primary image pair
2. secondary image pair
3. prerecorded screenshots/video if permitted

The backup must never replace a live demo when live execution is possible, but it protects against environmental failure.

## Rule 15 — Fail Safely

If correspondence quality is insufficient:

```text
Do not register blindly.
Do not invent a result.
Report failure.
```

The UI should explain:
- insufficient keypoints
- insufficient matches
- low inlier ratio
- poor spatial coverage
- unstable transformation

## Rule 16 — Use the Simplest Valid Transformation

Do not use a homography merely because it is available.

Choose the model appropriate to the test case and document it.

For the prototype:
- affine or homography may be used for suitable image pairs
- more complex lunar/geometric modeling is a later phase

## Rule 17 — Evaluation Definitions Must Be Explicit

Before reporting RMSE, define what points and coordinates it uses.

Do not compare two RMSE values if they were calculated using different definitions without explaining the difference.

## Rule 18 — Controlled Experiments Must Be Labeled

If an image is synthetically modified:

```text
Synthetic brightness +30%
Synthetic scale 1.5x
Synthetic rotation 30°
```

Do not present it as naturally acquired Chandrayaan imagery.

## Rule 19 — Separate Research Roadmap From Current Implementation

The PPT contains advanced concepts such as:
- RIFT
- SuperPoint
- LightGlue / SuperGlue
- RANSAC++
- sub-pixel refinement

The codebase must clearly identify whether each is:

```text
IMPLEMENTED
EXPERIMENTAL
PLANNED
```

## Rule 20 — Optimize for the Panel

The live demonstration should make the technical value obvious within minutes.

Show:

```text
Input
→ Correspondence
→ Geometric verification
→ Spatial distribution
→ Registration
→ Metrics
```

Avoid spending most of the demo on code or UI navigation.

## Rule 21 — Explain the Contribution Correctly

Do not say:

> "We created SIFT."

Say:

> "We are integrating robust correspondence, geometric verification, spatial balancing and high-precision registration into a unified pipeline targeted at the multimodal lunar-imaging problem."

## Rule 22 — Keep the MVP Small

The MVP does not need:
- authentication
- database
- cloud infrastructure
- mobile application
- chatbot
- unrelated AI features

Only add a component if it improves the PS demonstration.

## Rule 23 — Version Everything Before the Demo

Before presentation:
- freeze dependencies
- test the main command
- test the primary pair
- test the backup pair
- save known results
- make a copy of the repository

## Rule 24 — No Last-Minute Algorithm Swaps

Once the main demo works reliably, do not replace the baseline with an untested algorithm immediately before presentation.

Advanced algorithms can be shown as optional modules only after they pass the same test protocol.

## Rule 25 — Evidence Beats Claims

For every major claim, prefer:

```text
Claim
+
Method
+
Measured result
+
Visualization
```

Example:

> "Spatial balancing improves correspondence coverage."

Then show the before/after match distribution and actual coverage values.

## Rule 26 — Security and Data Hygiene

Do not commit:
- credentials
- API keys
- private tokens
- personal files
- unnecessary large raw datasets

Use `.gitignore` for local data and environment files.

## Rule 27 — Final Presentation Rule

The prototype should answer five panel questions immediately:

1. **Does it work?**
2. **What makes it different?**
3. **How do you handle multimodal/illumination/scale changes?**
4. **How do you know the result is correct?**
5. **What is implemented now versus future research?**

If the prototype can answer these five questions clearly, it is presentation-ready.

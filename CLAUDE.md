# LunarMatch

## Important

- The `Distributed DOCS/` folder in the repo root is obsolete. Ignore it completely. All project context comes from `docs/` only.
- Before building any new feature, adding a module, or making architectural changes, read the relevant files in `docs/` first (Architecture.md, Design.md, Memory.md, Phases.md, Project.md, Rules.md). These are the source of truth for requirements, pipeline design, development rules, and phasing. Do not rely on memory or assumptions — re-read the docs.

## Project

- **Competition:** Smart India Hackathon 2026
- **Problem Statement:** 26166 — Multi-modal, sun-angle and scale invariant image correspondence using Chandrayaan-2 optical images (OHRC, TMC, IIRS)
- **Organization:** ISRO (Department of Space)
- **Team:** Spectrum
- **Category:** Software / Space Technology

## Tech Stack

- Python, OpenCV, NumPy
- scikit-image (optional image processing)
- rasterio / GDAL (when GeoTIFF / geospatial handling is needed)
- Streamlit (demo interface)
- Advanced (optional): RIFT, SuperPoint, LightGlue / SuperGlue

## Commands

```bash
pip install -r requirements.txt    # install dependencies
streamlit run app.py               # launch demo UI
python -m pytest                   # run tests
```

## Repository Structure

```
LunarMatch/
├── app.py                  # Streamlit entry point
├── requirements.txt
├── src/
│   ├── __init__.py
│   ├── io.py               # image input / validation
│   ├── preprocessing.py    # normalization, CLAHE, denoise
│   ├── features.py         # feature extraction (SIFT, RIFT, SuperPoint)
│   ├── matching.py         # descriptor matching (BF, FLANN, LightGlue)
│   ├── geometry.py         # RANSAC, transformation estimation
│   ├── spatial.py          # spatial balancing / grid selection
│   ├── registration.py     # image warping
│   ├── refinement.py       # sub-pixel refinement (advanced)
│   └── metrics.py          # RMSE, inlier count/ratio, spatial coverage
├── data/
│   ├── raw/                # original imagery (gitignored)
│   ├── processed/          # preprocessed imagery (gitignored)
│   └── examples/           # known-good demo pairs (tracked)
├── outputs/                # generated results (gitignored)
├── experiments/            # configs and results
└── docs/                   # specifications (Architecture, Design, Memory, Phases, Project, Rules)
```

## Core Interfaces

Every module exposes a consistent interface so extractors, matchers and estimators are interchangeable.

- `extract(image) → keypoints, descriptors`
- `match(descriptors_a, descriptors_b) → candidate_matches`
- `estimate(points_a, points_b) → transformation, inlier_mask`
- `register(reference, moving, transformation) → registered_image`
- `evaluate(matches, inliers, transformation) → metrics`

## MVP Pipeline

```
Input → preprocessing → SIFT → BF/FLANN → ratio test → RANSAC → affine/homography → warp → metrics
```

Advanced components (RIFT, SuperPoint, LightGlue, sub-pixel refinement) are added only after the baseline is stable.

## Development Rules

### Honesty
- Never overclaim. Label every component as IMPLEMENTED, EXPERIMENTAL, or PLANNED.
- Never fake metrics. All displayed values must come from actual runs.
- Do not present a prototype result as scientifically validated.

### Architecture
- Keep algorithms modular — feature extraction must not be hard-coded into matching.
- Use replaceable components: Extractor, Matcher, GeometricEstimator, SpatialSelector, Registrar, Metrics.
- Distinguish match types: candidate → filtered → geometrically verified inlier → spatially selected correspondence.

### Data Integrity
- Never overwrite original imagery. Use `data/raw/`, `data/processed/`, `outputs/`.
- Preserve original dimensions, scale factors, and metadata.

### Terminology (use consistently)
- **Reference / fixed:** target coordinate system
- **Moving / source:** image that gets transformed
- **Keypoint:** detected salient image location
- **Descriptor:** numerical representation of a local feature
- **Match:** candidate correspondence between two descriptors
- **Inlier:** geometrically consistent match after RANSAC
- **Spatial coverage:** how broadly correspondences cover the image
- **RMSE:** root mean square error (always define what points/coordinates it uses)

### Failure Handling
- Fail safely — report failure instead of registering blindly.
- UI must explain why: insufficient keypoints, low inlier ratio, poor spatial coverage, unstable transformation.

### Demo
- The primary demo must work offline — no live downloads, external APIs, or remote model fetches.
- Keep at least one known-good image pair as emergency fallback (Rule 13).
- Smaller working UI is preferred over larger UI with unimplemented controls.
- Deterministic demo sequence: input → correspondence → verification → spatial distribution → registration → metrics.

### Dependencies
- Prefer Python + OpenCV + NumPy + Streamlit. Add dependencies only when they solve a real requirement.

### Security
- Never commit credentials, API keys, private tokens, or large raw datasets.
- Use `.gitignore` for local data and environment files.

## Evaluation Metrics

| Metric | Description |
|---|---|
| Keypoints | detected feature count per image |
| Candidate matches | initial descriptor correspondences |
| Good matches | retained after ratio filtering |
| Inlier count | geometrically consistent matches |
| Inlier ratio | inliers / selected matches |
| RMSE | defined registration/reprojection error |
| Spatial coverage | distribution of correspondences |
| Runtime | processing time |

All metrics must be calculated from actual runs. Show `N/A` if a metric cannot be reliably computed.

## Current Phase

Phase 0–1: prototype freeze + registration baseline. The immediate goal is a reliable MVP, not a complete production system. The team has cleared the internal PPT round and is preparing a prototype demonstration.

## Workflow

### Big changes (new features, cross-module work, architectural changes)

1. Read this file and the relevant specs in `docs/` (Architecture.md, Design.md, Memory.md, Phases.md, Project.md, Rules.md).
2. Explore the affected code areas.
3. Produce a written implementation plan.
4. Wait for user approval before implementing.

### Small localized fixes (bug fixes, typos, single-file changes)

- Implement directly — no plan needed.

### After implementing

1. Self-review the changes for logic errors, edge cases, and security issues.
2. Run the relevant tests (`python -m pytest`) and summarize what was run and the results. If tests cannot run, explain why.
3. Verify the work against the agreed plan — confirm each planned item was addressed.
4. List any remaining limitations or known gaps.
5. If behavior or architecture changed, update the relevant files in `docs/`.

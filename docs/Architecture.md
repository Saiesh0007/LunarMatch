# LunarMatch — System Architecture

## 1. Purpose

LunarMatch is a modular software pipeline for correspondence and registration of Chandrayaan-2 optical imagery (OHRC, TMC/TMC-2 and IIRS) with other lunar reference imagery such as LRO NAC and SELENE.

The architecture is designed around the SIH 2026 Problem Statement 26166 requirements:

- multimodal correspondence
- illumination / sun-angle variation
- viewpoint variation
- scale and resolution variation
- registered output with corresponding match points
- high-precision / sub-pixel registration target
- spatially distributed correspondences
- quantitative evaluation using RMSE, inlier count, inlier ratio and spatial coverage

## 2. High-Level Architecture

```text
                         ┌─────────────────────────┐
                         │       IMAGE INPUT       │
                         │ OHRC / TMC / IIRS / LRO │
                         └────────────┬────────────┘
                                      │
                                      ▼
                         ┌─────────────────────────┐
                         │  IMAGE VALIDATION &     │
                         │   METADATA HANDLING     │
                         └────────────┬────────────┘
                                      │
                                      ▼
                         ┌─────────────────────────┐
                         │ ILLUMINATION-AWARE      │
                         │ PREPROCESSING           │
                         │ • normalization         │
                         │ • contrast enhancement  │
                         │ • denoising             │
                         └────────────┬────────────┘
                                      │
                                      ▼
                         ┌─────────────────────────┐
                         │ SCALE / RESOLUTION      │
                         │ ALIGNMENT               │
                         └────────────┬────────────┘
                                      │
                         ┌────────────┴────────────┐
                         ▼                         ▼
               ┌──────────────────┐     ┌──────────────────┐
               │ CLASSICAL        │     │ ROBUST / LEARNED │
               │ FEATURES         │     │ FEATURES         │
               │ SIFT (baseline)  │     │ RIFT             │
               │                  │     │ SuperPoint*      │
               └────────┬─────────┘     └────────┬─────────┘
                        │                        │
                        └────────────┬───────────┘
                                     ▼
                         ┌─────────────────────────┐
                         │   FEATURE MATCHING      │
                         │ BF / FLANN / LightGlue* │
                         └────────────┬────────────┘
                                      │
                                      ▼
                         ┌─────────────────────────┐
                         │ MATCH QUALITY FILTERING │
                         │ • ratio test            │
                         │ • descriptor distance   │
                         └────────────┬────────────┘
                                      │
                                      ▼
                         ┌─────────────────────────┐
                         │ GEOMETRIC VERIFICATION  │
                         │ RANSAC / robust model   │
                         └────────────┬────────────┘
                                      │
                                      ▼
                         ┌─────────────────────────┐
                         │ SPATIAL BALANCING       │
                         │ grid / region-aware     │
                         │ match selection         │
                         └────────────┬────────────┘
                                      │
                                      ▼
                         ┌─────────────────────────┐
                         │ TRANSFORMATION ESTIMATE │
                         │ affine / homography     │
                         └────────────┬────────────┘
                                      │
                                      ▼
                         ┌─────────────────────────┐
                         │ SUB-PIXEL REFINEMENT*   │
                         └────────────┬────────────┘
                                      │
                                      ▼
               ┌──────────────────────┴─────────────────────┐
               ▼                                            ▼
     ┌──────────────────────┐                    ┌──────────────────────┐
     │ REGISTERED PRODUCT   │                    │ EVALUATION           │
     │ • aligned image      │                    │ • RMSE               │
     │ • match points       │                    │ • inlier count       │
     │ • overlay            │                    │ • inlier ratio       │
     └──────────────────────┘                    │ • spatial coverage   │
                                                 └──────────────────────┘
```

`*` denotes an advanced/next-stage component. The prototype must not claim a component as implemented until it has been tested.

## 3. Module Responsibilities

### Input and Validation
- Accept raster image formats supported by the prototype.
- Preserve original image dimensions.
- Validate that the pair has usable image content.
- Optionally capture sensor/source labels and metadata.

### Preprocessing
The preprocessing stage reduces appearance differences before feature extraction.

Candidate operations:
1. grayscale conversion where appropriate
2. intensity normalization
3. denoising
4. local contrast enhancement such as CLAHE
5. optional illumination normalization

The exact preprocessing chain should be configurable rather than hard-coded.

### Scale / Resolution Alignment
The system should bring images into a compatible working scale before correspondence search.

Responsibilities:
- estimate or accept scale ratio
- resize the moving image or create image pyramids
- retain the original-to-working scale factor
- avoid unnecessary loss of information

### Feature Extraction
The architecture supports multiple feature extractors.

**Prototype baseline**
- SIFT

**Robust feature module**
- RIFT

**Advanced learned module**
- SuperPoint

The extractor should expose a common interface:

```text
extract(image)
    -> keypoints
    -> descriptors
```

### Feature Matching
The matcher receives descriptors from two images and returns candidate correspondences.

Possible implementations:
- BFMatcher
- FLANN
- LightGlue for the learned pipeline

### Match Filtering
Candidate matches are filtered using descriptor quality and geometric consistency.

Typical baseline:
- k-nearest-neighbour matching
- Lowe-style ratio test

### Geometric Verification
RANSAC rejects geometrically inconsistent correspondences and estimates a transformation model.

The implementation should record:
- total candidate matches
- matches after filtering
- inlier count
- inlier ratio
- transformation matrix
- reprojection error where available

### Spatial Balancing
The PS asks for uniform distribution of match points.

A practical implementation:
1. divide the reference image into a grid
2. assign each candidate match to a grid cell
3. rank matches within each cell
4. keep a controlled number of strong matches per occupied cell
5. run/redo geometric verification using the selected set where appropriate
6. calculate spatial coverage

This prevents a high number of matches from one small region from dominating registration.

### Transformation and Registration
The transformation model is selected according to the image pair and geometry.

For a planar/local prototype:
- affine transformation
- homography

The moving image is warped into the reference image coordinate system.

### Sub-Pixel Refinement
This is an advanced stage aligned with the PS requirement. The prototype should only label it as "implemented" after numerical validation.

Possible refinement strategies include local correlation/optimization around matched locations.

## 4. Data Flow

```text
Reference image ──► preprocess ──► features ──┐
                                               ├─► matching
Moving image ─────► preprocess ──► features ──┘
                                                   │
                                                   ▼
                                             filtering
                                                   │
                                                   ▼
                                               RANSAC
                                                   │
                                                   ▼
                                          spatial balancing
                                                   │
                                                   ▼
                                          transformation
                                                   │
                                                   ▼
                                             registration
                                                   │
                         ┌─────────────────────────┴──────────────┐
                         ▼                                        ▼
                   output image                             evaluation
```

## 5. Design Principles

- **Modular:** detectors, descriptors and matchers can be replaced independently.
- **Reproducible:** all parameters used in a run are recorded.
- **Fail-safe:** weak correspondence must produce a low-confidence result instead of an untrustworthy registration.
- **Measurable:** every successful run produces quantitative metrics.
- **Extensible:** the prototype can evolve from SIFT to RIFT and learned matching without rewriting the whole system.
- **Demo-friendly:** every major stage produces a visual artifact.

## 6. Prototype vs Target Architecture

| Component | MVP | Target |
|---|---|---|
| Input | local raster images | Chandrayaan + reference repositories |
| Preprocessing | normalization + CLAHE/denoise | modality-aware illumination pipeline |
| Feature | SIFT | RIFT + SuperPoint |
| Matching | BF/FLANN | robust/learned matching including LightGlue |
| Verification | RANSAC | robust estimation / RANSAC++ style module |
| Spatial distribution | grid balancing | optimized spatial coverage |
| Registration | affine/homography | high-precision registration |
| Refinement | optional | validated sub-pixel refinement |
| Metrics | RMSE, inliers, ratio, coverage | full benchmark suite |
| UI | Streamlit | scalable research/production interface |

## 7. Failure Handling

A registration result should be rejected or marked low-confidence when:
- too few usable keypoints exist
- too few valid matches remain
- RANSAC cannot find a stable model
- inlier ratio is below the configured threshold
- spatial coverage is inadequate
- reprojection error is excessive

The UI should explain why the result was rejected.

## 8. Deployment

The first prototype is intended to run locally.

Recommended prototype stack:
- Python
- OpenCV
- NumPy
- scikit-image where needed
- rasterio/GDAL where GeoTIFF/geospatial handling is required
- Streamlit for the demonstration interface

Cloud deployment is optional and should not be a prerequisite for the internal prototype.

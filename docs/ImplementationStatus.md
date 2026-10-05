# LunarMatch — Implementation & Verification Status

**Last reviewed:** 2026-10-05, against the code in `backend/`, `web/` and `mobile/`.
"Verified by" names the backend test files (`backend/tests/`) that exercise each
component; "real data" means checked on the Chandrayaan-2 pairs in
[RealData.md](RealData.md). The full backend suite (50 files) passed on
2026-10-05 apart from the wall-clock budget tests, which depend on machine load.

---

## 1. Backend

| Component | Status | Verified by | Notes |
| :--- | :--- | :--- | :--- |
| RIFT2 phase-congruency features (single / multi-scale) | Implemented | `test_rift2.py`, `test_rift2_routing.py`, `test_scale_space.py`, `test_pyramid.py` | Default `feature_method`; 216-D descriptors. |
| SIFT baseline | Implemented | `test_sift.py` | OpenCV SIFT. |
| HOPC structural descriptor, HOPC + RIFT2 fusion | Implemented | `test_hopc.py` | 288-D. |
| SuperPoint extractor | Implemented — needs weights | `test_superpoint_extractor.py`, `test_learned_matchers_pipeline.py` | PyTorch CPU; falls back to RIFT2 without `weights/superpoint_v1.pth`. |
| SuperGlue matcher | Implemented — needs weights | `test_superglue_matcher.py`, `test_superglue.py`, `test_learned_matchers_pipeline.py` | PyTorch CPU, outdoor weights; fallback RIFT2 + BF. A pure-NumPy Sinkhorn matcher in the same module is unit-tested. |
| LightGlue matcher | Implemented — needs weights | `test_lightglue_matcher.py`, `test_learned_matchers_pipeline.py` | PyTorch CPU; fallback RIFT2 + BF. |
| BF / FLANN matching, Lowe's ratio test | Implemented | `test_matching.py` | |
| Hyp-Net descriptor modulation | Implemented | `test_hypnet.py` | |
| SCDF gates | Implemented | `test_scdf_gates.py` | |
| MAGSAC++ / RANSAC, homography / affine | Implemented | `test_magsac.py`, `test_pipeline_api.py` | Matrix stability checks. |
| Dense structural registration (CFOG) | Implemented | `test_dense_structural.py`, `test_pipeline_failure.py`; real data | Explicit or automatic fallback; false-lock guard. |
| Thin-plate-spline correction | Implemented | `test_tps.py` | |
| Sub-pixel refinement | Implemented | `test_subpixel.py` | Phase correlation; NCC peak interpolation for dense runs. |
| Spatial grid balancing | Implemented | `test_spatial_balancing.py` | 6 × 6 default. |
| Chandrayaan-2 PDS4 reader | Implemented | `test_pds_reader.py`, `test_pds_meta_feed.py`; real OHRC / TMC-2 / IIRS products | ISDA labels, memory-mapped `.img` / `.qub`. |
| GeoTIFF reader | Implemented | `test_geotiff_reader.py` | |
| Lunar polar-stereographic reprojection | Implemented | `test_lunar_crs.py` | Pole from scene hemisphere. |
| GSD normalisation | Implemented | `test_resolution.py` | |
| Footprint overlap, SPICE kernels, orbital footprint validation | Implemented | `test_overlap.py`, `test_spice.py`, `test_spice_kernel_build.py`, `test_footprint_validation.py` | Synthesized kernels via SpiceyPy. |
| Illumination check, shadow mask, radiometric normalisation, terrain correction, depth-optical preprocessing | Implemented | `test_illumination.py`, `test_shadow_mask.py`, `test_radiometric_norm.py`, `test_terrain_correction.py`, `test_depth_optical.py` | Terrain correction uses a DEM when `LM_DEM_DIR` is set. |
| Sensor-pair routing | Implemented | `test_router.py`, `test_rift2_routing.py` | |
| Input quality gate | Implemented | `test_input_quality.py` | Fill vs in-footprint gaps; alpha as mask. |
| Status / confidence metrics | Implemented | `test_metrics.py` | [Metrics.md](Metrics.md). |
| Acceptance checklist | Implemented | `test_quality.py` | Resolution- and overlap-aware. |
| Run artifacts, manifest, reports | Implemented | `test_manifest.py`, `test_report_generator.py`, `test_finale_run.py` | |
| Robustness experiments | Implemented | No dedicated API test; exercised from the web and mobile apps | Illumination, scale, rotation, translation. `composite` appears in the request field description but is not implemented (no variation is applied). |
| Seeded simulation mode | Implemented | `test_simulation.py` | [Simulation.md](Simulation.md). |
| REST API, route aliases | Implemented | `test_health.py`, `test_api_aliases.py`, `test_pipeline_api.py`, `test_demo_api.py` | [API.md](API.md). |
| Matcher benchmark | Implemented | `test_matcher_benchmark.py` | `scripts/matcher_benchmark.py`. |
| Documentation visuals | Implemented | `test_visuals.py` | Regenerates `docs/visuals/` when run. |

## 2. Web app (`web/`)

| Feature | Status | Notes |
| :--- | :--- | :--- |
| Studio: upload or preset pair, method, metadata, live run, viewer modes, metric cards, log | Implemented | Dense CFOG option, sensor / GSD inputs, auto-scroll, results only after a run. |
| Correspondences: live matches, inlier / outlier filters, 4 × 4 grid with χ² | Implemented | Uses the latest Studio run; demo data before a run. |
| Robustness: live sweep on the Studio reference image | Implemented | Reference charts are bundled data, labelled as such. |
| Overview, Architecture | Implemented (static content) | Overview tiles and the 5-stage Architecture summary are fixed content. |
| Export | Implemented (sample data) | Exports bundled sample telemetry, not the current run. |
| Offline simulation | Implemented | When the backend is unreachable. |
| Sinkhorn OT iterations slider | Display only | Not sent to the backend. |

## 3. Mobile app (`mobile/`)

| Feature | Status | Notes |
| :--- | :--- | :--- |
| 13 screens: splash, home, upload, configure, processing, results, correspondence, spatial coverage, robustness, architecture, capabilities, about, pipeline details | Implemented | [MobileApp.md](MobileApp.md). |
| Live runs, robustness sweeps, run details, capabilities | Implemented | Via the REST API. |
| Correspondence screen | Illustrative | Line layout generated from match counts, not real coordinates. |
| Dense CFOG option, sensor / GSD input | Not exposed | Backend dense fallback still applies. |
| Offline local demo | Implemented | `LocalDemoSimulator`. |
| Built-in (offline) capability list | Outdated | Still lists the SuperGlue matcher as simulated. |

---

## Engineering commitments
1. Simulated or illustrative output is labelled where it appears.
2. Run metrics come from the run; a rejected run reports RMSE as N/A.
3. Reference image = fixed; moving image = transformed.
4. Every run's parameters, keypoints, matches, decisions and matrices are saved
   in `backend/outputs/run_<id>/`.

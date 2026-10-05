# LunarMatch — REST API

FastAPI backend (`backend/app`). Interactive OpenAPI docs are served at
`http://127.0.0.1:8000/docs` when the server is running.

## Base URL
- Local: `http://127.0.0.1:8000`
- Android emulator: `http://10.0.2.2:8000`
- Physical phone: your PC's LAN address, set on the mobile **About** screen

CORS is open (`*`).

| Method | Path | Purpose |
| :--- | :--- | :--- |
| GET | `/health` | Service status |
| GET | `/api/v1/capabilities` | Capability list |
| POST | `/api/v1/images/upload` | Upload an image |
| GET | `/api/v1/images/demo` | Bundled demo pairs |
| GET | `/api/v1/images/{image_id}/preview` | Image file |
| POST | `/api/v1/pipeline/run` | Run a registration |
| GET | `/api/v1/results/{run_id}` | Full run log |
| GET | `/api/v1/results/{run_id}/artifact/{filename}` | One run artifact |
| GET | `/api/v1/results/{run_id}/report` | Markdown report |
| POST | `/api/v1/experiments/robustness` | Robustness sweep |
| POST | `/api/demo/compare` | Cached SIFT vs RIFT2 comparison |
| GET | `/api/demo/failure-case` | Acceptance checklist of the latest run |

The results endpoints are also available as `/api/runs/{run_id}`,
`/api/runs/{run_id}/artifacts/{key}` and `/api/runs/{run_id}/report`.

---

## 1. Health and capabilities

### `GET /health`
```json
{ "status": "ok", "service": "LunarMatch API", "version": "1.0.0", "mode": "Operational", "cv_available": true }
```

### `GET /api/v1/capabilities`
List of `{name, category, status, notes}` describing each subsystem (RIFT2, HOPC,
MAGSAC++, dense CFOG, PDS4 ingestion, SuperPoint / SuperGlue / LightGlue, …), plus
`pipeline_version` and `build_date`. Every `status` is reported as `"Operational"`;
the `notes` say what each component needs (e.g. learned weights). The mobile
**Engine Capabilities** screen displays this list.

---

## 2. Images

### `POST /api/v1/images/upload`
`multipart/form-data` with `file`. Accepts PNG, JPG, TIFF and BMP (anything
else is stored as `.png` and must decode with OpenCV). RGBA images are accepted;
the alpha channel is treated as a transparency mask. Raw PDS4 `.img` / `.qub` are
not accepted — see [RealData.md](RealData.md). Files are saved in
`backend/data/raw/`.

```json
{
  "image_id": "3b29c91d-…", "filename": "ref_iirs.png",
  "width": 250, "height": 520, "channels": 1, "format": "png",
  "file_size_kb": 95.0, "preview_url": "/api/v1/images/3b29c91d-…/preview"
}
```

### `GET /api/v1/images/demo`
Bundled demo pairs with `pair_id`, `name`, `description`, `reference_image_id`,
`moving_image_id`, sensors, preview URLs and a `provenance_note`. The demo
images (`backend/data/examples/`) are synthetic prototypes, not mission data.

### `GET /api/v1/images/{image_id}/preview`
Streams the image. `image_id` may be an upload ID, a demo ID
(`demo_pair_a_ref`, `demo_pair_a_mov`, `demo_pair_b_ref`, `demo_pair_b_mov`) or a
file path on the server.

---

## 3. Pipeline

### `POST /api/v1/pipeline/run`

Only the two image IDs are required.

| Field | Default | Meaning |
| :--- | :--- | :--- |
| `reference_image_id`, `moving_image_id` | — | Upload ID, demo ID or server file path |
| `feature_method` | `rift2` | `rift2`, `rift2_multiscale`, `sift`, `hopc`, `hopc_rift2_fusion`, `both`, `superpoint`, `superglue` (SIFT keypoints), `dense` |
| `matcher` | `BF` | `BF`, `FLANN`, `superglue`, `lightglue` |
| `ratio_threshold` | 0.75 | Lowe's ratio (0.4–0.95) |
| `geometric_model` | `homography` | `homography` or `affine` |
| `estimator_method` | `magsac` | `magsac` or `ransac` |
| `ransac_threshold` | 3.0 | Inlier threshold in px (0.5–15) |
| `max_features` | 2000 | Keypoint cap (100–10000) |
| `dense_fallback` | `true` | Run dense CFOG when sparse matching does not verify |
| `reference_gsd_m`, `moving_gsd_m` | none | Pixel size (m/px) of each **uploaded file**: scale prior, expected scale for the checklist, metre residuals |
| `reference_sensor`, `moving_sensor` | `OHRC`, `TMC-2` | `OHRC`, `TMC`, `TMC-2`, `IIRS`, `LRO NAC`, `SELENE`, `Other`. Used for routing only when sent explicitly; otherwise sensors come from PDS4 labels or are unknown |
| `reference_pds_label`, `moving_pds_label`, `pds_label_path` | none | PDS4 XML label paths (ISRO ISDA supported). `<image>.xml` next to an image is read automatically |
| `pds_metadata` | none | Metadata dictionary applied to both images |
| `gsd_meters_per_pixel` | none | GSD for metre residuals |
| `solar_elevation_deg`, `solar_azimuth_deg` | none | Sun geometry |
| `use_scdf_gates` | `true` | SCDF match gates |
| `use_tps` | `true` | Thin-plate-spline residual correction |
| `subpixel_refinement` | `true` | Sub-pixel refinement; `subpixel_patch_size` 64, `subpixel_peak_threshold` 0.2 |
| `spatial_balancing` | `true` | Grid balancing; `grid_size` 6, `max_features_per_cell` 5 |
| `preprocessing` | all on | `{normalize, clahe, denoise, clip_limit: 2.0, tile_grid_size: 8}` |
| `simulation_mode`, `is_demo_mode` | `false` | Run the seeded simulator instead of live CV ([Simulation.md](Simulation.md)) |
| `forced_config` | none | Override sensor-routing configuration |
| `lock_to_default` | `false` | Force the fast RIFT2 + BF path |
| `disable_spice`, `fail_safe_override` | `false` | Test switches |

Example (real Chandrayaan-2 pair, dense method):
```json
{
  "reference_image_id": "<upload id of ref_iirs.png>",
  "moving_image_id": "<upload id of mov_tmc2.png>",
  "feature_method": "dense",
  "reference_sensor": "IIRS", "moving_sensor": "TMC-2",
  "reference_gsd_m": 78.32, "moving_gsd_m": 19.6
}
```

Response (abridged):
```json
{
  "run_id": "run_20261004_213650_b04aa5",
  "status": "SUCCESSFUL",
  "execution_mode": "live",
  "stages": [ { "stage_number": 1, "name": "INPUT VALIDATION", "status": "COMPLETED", "duration_ms": 182.0, "details": "…" } ],
  "metrics": {
    "metric_mode": "measured",
    "keypoints_reference": 0, "keypoints_moving": 0,
    "candidate_matches": 100, "filtered_matches": 100, "ransac_inliers": 98,
    "inlier_ratio": 98.0,
    "spatial_coverage": 22.22, "spatial_coverage_before": 22.22,
    "spatial_coverage_footprint": 100.0,
    "rmse_px": 0.706, "runtime_ms": 5468.0,
    "confidence_level": "HIGH", "confidence_score": 0.82,
    "confidence_explanation": "High-confidence registration with strong spatial distribution and tight reprojection error."
  },
  "spatial_stats": { "grid_size": 6, "total_cells": 36, "occupied_cells_before": 8, "occupied_cells_after": 8, "coverage_percentage_before": 22.22, "coverage_percentage_after": 22.22, "coverage_gain_percentage": 0.0 },
  "outputs": {
    "registered_image_url": "/api/v1/results/<run_id>/artifact/registered.png",
    "overlay_image_url": "…/overlay.png", "difference_image_url": "…/difference.png",
    "correspondence_image_url": "…/correspondences.png", "artifacts_dir": "…"
  },
  "warnings": ["Dense structural registration applied (explicit): 98 verified correspondences, scale 0.2613, rotation 2.0 deg"],
  "failure_reason": null,
  "transformation_matrix": [[…], […], […]],
  "configuration": { … }
}
```

- `status`: `SUCCESSFUL`, `LOW_CONFIDENCE`, `NOT_RELIABLE`, `FAILED`; `execution_mode`: `live`, `demo`, `local`.
- `rmse_px` is `null` when the run is `NOT_RELIABLE`.
- `spatial_coverage` counts cells over the whole reference grid;
  `spatial_coverage_footprint` (may be `null`) counts only cells inside the
  moving image's projected footprint.
- When dense registration is used, `warnings` contains
  `"Dense structural registration applied (explicit|sparse_fallback): …"`.
- Each run's `quality_report.json` holds the acceptance checklist
  ([Metrics.md](Metrics.md)); all artifacts are listed in
  [Architecture.md §6](Architecture.md#6-run-artifacts).

---

## 4. Results

- `GET /api/v1/results/{run_id}` — `experiment_log.json` enriched with
  `stages_detail` (one entry per stage from `match_decisions.jsonl`) and
  `matcher_benchmark` (or `null`).
- `GET /api/v1/results/{run_id}/artifact/{filename}` — a PNG or JSON artifact
  (e.g. `registered.png`, `matches_filtered.json`). Paths outside the run folder
  are refused.
- `GET /api/v1/results/{run_id}/report` — Markdown report of the run.

---

## 5. Robustness experiments

### `POST /api/v1/experiments/robustness`
Applies a controlled change to one image in `variation_steps` increments and
registers the original against each variant.

| Field | Default | Meaning |
| :--- | :--- | :--- |
| `base_image_id` | — | Image to perturb |
| `experiment_type` | `illumination` | `illumination` (brightness offset), `scale` (factor = max(0.5, 1 + v/100)), `rotation` (degrees), `translation` (px) |
| `variation_steps` | 5 | 3–10 |
| `min_val`, `max_val` | −50, 50 | Parameter range |
| `feature_method`, `matcher`, `ratio_threshold`, `geometric_model`, `spatial_balancing`, `grid_size` | `sift`, `BF`, 0.75, `homography`, `true`, 6 | Pipeline settings for each step |

Returns `experiment_id`, `points[]` (`variation_value`, `variation_label`,
`inliers`, `inlier_ratio`, `spatial_coverage`, `rmse_px`, `runtime_ms`,
`status`), `summary` and a disclaimer. Results are saved to
`backend/experiments/results/{experiment_id}.json`.

---

## 6. Demo endpoints

- `POST /api/demo/compare` — SIFT vs RIFT2 metrics on the bundled demo pair,
  measured offline by `scripts/compute_and_cache.py` and served from cache.
- `GET /api/demo/failure-case` — the acceptance checklist of the most recent
  run, formatted for a failure-case screen.

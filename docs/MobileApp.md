# LunarMatch — Mobile App

Flutter app in `mobile/` (Android, Windows, web). Requires Flutter 3.41+
(Dart 3.11). State is managed with Provider; charts use `fl_chart`.

```bash
cd mobile
flutter pub get
flutter run -d windows        # or -d chrome, or an Android device
flutter build apk --release
```

**Backend URL:** `http://10.0.2.2:8000` on the Android emulator,
`http://127.0.0.1:8000` on Windows and web. For a physical phone, set your PC's
LAN address (e.g. `http://192.168.x.x:8000`) on the **About** screen.

> Screenshots: the mobile screens are not pictured yet. The machine these docs
> were produced on has Flutter 3.27, which cannot build this app (it needs Dart
> 3.11). Captures can be added as `docs/screenshots/mobile_<screen>.png`.

---

## Screens (13)

| # | Screen | Route | What it does |
| :- | :--- | :--- | :--- |
| 1 | Splash | `/` | Animated intro, then Home. |
| 2 | Home | `/home` | Entry cards for Image Registration, Robustness Laboratory, Pipeline Architecture and Engine Capabilities; backend status with a **CHECK** button. |
| 3 | Select lunar images | `/upload` | Pick a bundled demo pair or upload reference / moving images (`POST /api/v1/images/upload`); **SWAP REFERENCE & MOVING**. |
| 4 | Pipeline configuration | `/configure` | Feature method, matcher, geometric model, spatial grid partitioning, preprocessing (intensity normalization, CLAHE, edge-preserving denoising). |
| 5 | Pipeline execution | `/processing` | Runs the pipeline and shows the ten coarse stages with durations. |
| 6 | Registration result | `/results` | Success / not-reliable banner, image comparison, quantitative metrics, sub-pixel refinement statistics, transformation matrix, Markdown report export. |
| 7 | Correspondence visualization | `/correspondence` | Match-line view and the correspondence filtering pipeline (see note below). |
| 8 | Spatial coverage analysis | `/spatial-coverage` | Grid occupancy before / after balancing from the run's `spatial_stats`. |
| 9 | Robustness laboratory | `/robustness` | Illumination, scale, rotation or translation sweep (`POST /api/v1/experiments/robustness`) with inliers, ratio, coverage, RMSE and status per step. |
| 10 | System architecture | `/architecture` | Pipeline specification: multi-modal ingestion and lunar CRS, radiometric normalisation, RIFT2, Hyp-Net, BF + Lowe ratio + MAGSAC++, SCDF gates, TPS, sub-pixel refinement. |
| 11 | Engine capabilities | `/status` | Capability list from `GET /api/v1/capabilities` (a built-in list when offline). |
| 12 | About | `/about` | Project information, backend URL setting, online / offline switch. |
| 13 | Pipeline details | `/pipeline-details` | Stage timeline from `GET /api/v1/results/{run_id}` (`stages_detail`), matcher comparison when a benchmark is available, link to the full report. |

---

## Configuration options

| Setting | Options sent to the backend |
| :--- | :--- |
| Feature method | `SIFT`, `RIFT2` (default), `SuperPoint`, `superglue` |
| Matcher | `BF`, `FLANN`, `SuperGlue`, `LightGlue` |
| Geometric model | homography or affine |
| Other | Spatial grid partitioning, preprocessing toggles; Lowe ratio is sent at its default 0.75 (no on-screen control) |

- **SuperPoint / SuperGlue / LightGlue** run the PyTorch models on the backend
  when their weights are installed (`backend/scripts/download_weights.py`);
  otherwise the backend falls back to RIFT2. The screen warns that CPU inference
  takes several seconds per pair.
- The feature-method option labelled *Sinkhorn Optimal-Transport Matcher* sends
  `feature_method: superglue`, which in live mode extracts SIFT keypoints and
  matches them with the selected matcher; choose the **SuperGlue** matcher for
  the learned matcher.
- The dense CFOG method and the sensor / GSD fields are not exposed in the app.
  The backend still applies dense registration automatically when sparse
  matching fails (`dense_fallback` defaults to on).

---

## Data shown by each screen

| Screen | Source |
| :--- | :--- |
| Results, Spatial coverage, Pipeline details | The backend run (live) |
| Robustness | The backend sweep; a generated offline result when the backend is unreachable |
| Engine capabilities | `GET /api/v1/capabilities`; a built-in list when offline |
| Correspondence visualization | Uses the run's **match counts** to draw an illustrative layout of inlier / outlier lines — line positions are not the run's actual coordinates. Real match coordinates are in `matches_filtered.json` and the web Correspondences tab. |

---

## Offline mode

When the backend is unreachable (or offline is forced on the About screen),
`LocalDemoSimulator` replays bundled demo results for the demo pairs so the full
flow can be shown without a network. See [Simulation.md](Simulation.md).

# LUNARMATCH
### Multi-Modal Lunar Image Correspondence & Registration Engine

**Smart India Hackathon 2026** | **Problem Statement:** 26166 | **Organization:** ISRO | **Team:** LunarMatch | **Domain:** Space Technology

---

## 1. Executive Summary
**LunarMatch** is an end-to-end, scientifically honest, presentation-ready demonstrable prototype solving multi-modal, cross-sensor correspondence and registration of lunar orbital datasets (such as Chandrayaan-2 OHRC optical imagery, TMC-2 stereo pairs, and IIRS hyperspectral products).

The platform addresses severe lunar imaging challenges:
- Extreme illumination angle differences (multi-temporal shadow shifts).
- Cross-sensor resolution & scale differentials.
- Crater rim feature over-clustering via novel **Uniform Spatial Grid Balancing**.
- Strict scientific integrity: **Zero fabricated metrics**, transparent distinction between **IMPLEMENTED** vs **SIMULATED** models, and fail-safe rejection when alignment is unreliable.

---

## 2. Technology Stack

| Layer | Technologies | Purpose |
| :--- | :--- | :--- |
| **Backend API** | Python 3.11, FastAPI, Pydantic v2, Uvicorn | High-performance asynchronous REST API |
| **Computer Vision** | OpenCV 4.x, NumPy, SciPy, Pillow, scikit-image | SIFT extraction, FLANN/BF matching, RANSAC, spatial balancing, projective warping |
| **Frontend Client** | Flutter 3.41, Dart null safety, Material 3 | Mission-control UI (Android, Windows Desktop, Web) |
| **State Management** | Provider | Reactive MVVM state orchestration |
| **Visualizations** | CustomPainter, fl_chart | Real-time correspondence lines, spatial grid overlays, and degradation curves |
| **Testing** | Pytest, Flutter Test | End-to-end verification of CV algorithms and UI components |

---

## 3. Architecture & Operational Modes

LunarMatch exposes three strictly separated execution modes:

1. **LIVE BASELINE (`metric_mode: MEASURED`)**
   - Actual OpenCV pipeline: Preprocessing (CLAHE + Normalization + Denoising) $\rightarrow$ SIFT Keypoint & 128D Descriptors $\rightarrow$ BFMatcher/FLANN 2-NN $\rightarrow$ Lowe's Ratio Test $\rightarrow$ RANSAC Homography/Affine $\rightarrow$ Spatial Grid Balancing $\rightarrow$ Image Warping $\rightarrow$ Measured RMSE.
2. **DEMO SIMULATION (`metric_mode: SIMULATED`, `seed: 26166`)**
   - Deterministic mathematical simulation for advanced research algorithms (RIFT, SuperPoint).
   - Seed `26166` guarantees identical reproducible presentation outputs.
   - Visibly tagged as `SIMULATED PIPELINE` (never claims unvalidated models ran).
3. **LOCAL FALLBACK (`LOCAL DEMO`)**
   - Zero-network client-side simulator using bundled demo assets (`pair_a_ref.png`, `pair_a_mov.png`).
   - Ensures continuous presentation reliability even if the backend server is disconnected.

---

## 4. Repository Structure
```
c:/sih/
├── backend/
│   ├── app/
│   │   ├── main.py                  # FastAPI application entrypoint
│   │   ├── config.py                # Environment configuration
│   │   ├── api/                     # REST API routers (health, images, pipeline, experiments, results)
│   │   ├── models/                  # Pydantic schemas, requests, responses
│   │   ├── services/                # Pipeline orchestration, image cache, experiment sweeps
│   │   ├── vision/                  # Real OpenCV SIFT, BF/FLANN matching, RANSAC, spatial balancing, RMSE
│   │   ├── simulation/              # Deterministic simulation engine (seed 26166) & crater generator
│   │   └── utils/                   # JSON serializers, logging, OpenCV image helpers
│   ├── data/
│   │   └── examples/                # Bundled demo lunar pairs (Demo Pair A & B)
│   ├── outputs/                     # Persisted run artifacts (JSON & PNG)
│   ├── experiments/                 # Robustness sweep logs
│   ├── tests/                       # 15 Pytest unit & integration tests
│   └── requirements.txt
├── mobile/
│   ├── lib/
│   │   ├── app/                     # App configuration, routes, Space Tech theme
│   │   ├── models/                  # Dart models (image, match, pipeline, metrics, experiment)
│   │   ├── services/                # API service, image picker, local demo simulator
│   │   ├── providers/               # Provider state management
│   │   ├── screens/                 # 12 Screens (Splash, Home, Upload, Config, Processing, Results, etc.)
│   │   ├── widgets/                 # Reusable UI widgets (cards, badges, viewers, grid painters)
│   │   └── utils/                   # Constants, formatters
│   ├── assets/demo/                 # Bundled lunar assets for offline presentation
│   ├── test/                        # Flutter model & widget tests
│   └── pubspec.yaml
├── docs/                            # Comprehensive documentation (Architecture, API, Simulation, etc.)
├── .gitignore
└── README.md
```

---

## 5. Quick Start Instructions

### Prerequisites
- Python 3.10+
- Flutter 3.x+ (Dart 3.x+)

### 1. Run FastAPI Backend
```bash
cd backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
API Documentation will be accessible at: `http://127.0.0.1:8000/docs`.

### 2. Run Flutter Application
```bash
cd mobile

# Run on Windows Desktop
flutter run -d windows

# Or run on Chrome
flutter run -d chrome

# Or build Android APK
flutter build apk --debug
```

---

## 6. Verification & Test Results

### Backend Automated Test Suite (`pytest`)
All 15 test suites passed:
- `test_health.py`: Health check and capabilities matrix verification.
- `test_preprocessing.py`: Intensity normalization, CLAHE enhancement, and denoising.
- `test_sift.py`: SIFT extrema detection and 128D descriptor formation.
- `test_matching.py`: BFMatcher and FLANN 2-NN with Lowe's ratio test filter.
- `test_spatial_balancing.py`: Spatial grid partitioning, cell selection, and coverage ratio.
- `test_metrics.py`: Reprojection RMSE calculation and fail-safe triggers.
- `test_simulation.py`: Deterministic seed reproducibility (Seed 26166).
- `test_pipeline_api.py`: End-to-end API pipeline execution and fail-safe rejection.

### Frontend Automated Test Suite (`flutter test`)
All 4 test suites passed:
- `model_test.dart`: RegistrationMetricsModel deserialization, MatchPairModel coordinate handling, Formatters.
- `widget_test.dart`: Clean app mounting, Splash screen rendering, and Home screen navigation.

---

## 7. Truthful Implementation Status Matrix

| Feature | Status | Verified | Implementation Details |
| :--- | :--- | :---: | :--- |
| **SIFT Feature Extraction** | `IMPLEMENTED` | **YES** | OpenCV SIFT detector and 128D descriptor. |
| **BFMatcher / FLANN** | `IMPLEMENTED` | **YES** | Exhaustive L2 and KD-Tree nearest neighbor matching. |
| **Lowe's Ratio Test** | `IMPLEMENTED` | **YES** | Dual nearest-neighbor ambiguity rejection filter. |
| **RANSAC Homography & Affine**| `IMPLEMENTED` | **YES** | Robust consensus fitting with determinant/stability checks. |
| **Spatial Grid Balancing** | `IMPLEMENTED` | **YES** | Uniform $N \times N$ cell distribution and coverage metrics. |
| **Reprojection RMSE** | `IMPLEMENTED` | **YES** | Measured pixel error over verified inliers (reports N/A if unreliable). |
| **Fail-Safe Mechanism** | `IMPLEMENTED` | **YES** | Declares `REGISTRATION NOT RELIABLE` on ill-conditioned pairs. |
| **Deterministic Simulation**| `IMPLEMENTED` | **YES** | Seed 26166 engine for reproducible demo exploration. |
| **Offline Local Demo** | `IMPLEMENTED` | **YES** | Zero-network fallback using bundled demo assets. |
| **Robustness Lab** | `IMPLEMENTED` | **YES** | Illumination, scale, rotation, translation parameter sweeps. |
| **Multi-scale pyramid on PC map** | `IMPLEMENTED` | **YES** | Phase 1.2, commit `0fc85da`. 3 levels, KD-tree dedup, level filtering. |
| **RIFT2 (Phase Congruency + MIM)** | `IMPLEMENTED` | **YES** | Phase 1.1, commit `2372478`; 216-D illumination-invariant descriptors. |
| **HOPC** | `IMPLEMENTED` | **YES** | Phase 1.3, commit `07afdc0`; dense 288-D PC representation. |
| **MAGSAC++** | `IMPLEMENTED` | **YES** | Phase 1.4, commit `5a79d6a`; OpenCV USAC backend with diagnostics. |
| **Sensor-pair routing** | `IMPLEMENTED` | **YES** | Phase 1.6, commit `c55ecb0`; 8 routing rows plus unknown fallback. |
| **Sub-pixel refinement** | `IMPLEMENTED` | **YES** | Phase 1.5, commit `253699d`; validated bias sweep and safe rejection. |
| **PDS4 / GeoTIFF readers** | `IMPLEMENTED` | **YES** | Phase 2, synthetic fixture coverage; rasterio-backed metadata loading. |
| **Failure detection thresholds** | `IMPLEMENTED` | **YES** | Phase 2 quality checklist with explicit rejection reasons. |
| **IIRS path** | `EXPERIMENTAL` | **NO** | Band-mean fallback implemented; real IIRS validation remains pending. |
| **SuperPoint Deep Features**| `SIMULATED` | **YES** | Deterministic simulation; neural weights planned. |
| **LightGlue Graph Matcher**| `PLANNED` | **NO** | Deep attention correspondence filter scheduled. |
| **RANSAC++ Consensus** | `PLANNED` | **NO** | Non-uniform spatial prior sampling scheduled. |

---

## 8. Non-Negotiable Scientific Principles
1. **Rule A — Zero Fake Scientific Claims:** Never claim sub-pixel accuracy or deep neural matching unless validated. Delineate IMPLEMENTED from SIMULATED.
2. **Rule B — Zero Hard-Coded Metrics:** Every metric is computed directly from computer vision execution or seed 26166 simulation.
3. **Rule C — Consistent Terminology:** Reference Image = Fixed; Moving Image = Transformed.
4. **Rule D — Fail Safely:** When inputs fail reliability criteria, safely report `REGISTRATION NOT RELIABLE` with explicit technical diagnostics.

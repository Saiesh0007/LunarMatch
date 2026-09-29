# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Backend
- **Run server:** `cd backend && uvicorn app.main:app --host 0.0.0.0 --port 8000`
- **Run all tests:** `cd backend && python run_tests_isolated.py`
  *Note: Always use this script instead of raw `pytest` for the full suite to prevent native access violations caused by OpenCV/NumPy under memory pressure.*
- **Run a single test:** `cd backend && pytest tests/test_filename.py -v`
- **Pipeline smoke test:** `cd backend && pytest tests/test_canary.py -v`

### Frontend (Mobile)
- **Install dependencies:** `cd mobile && flutter pub get`
- **Run app:** `cd mobile && flutter run -d windows` (or `-d chrome`)
- **Lint code:** `cd mobile && flutter analyze`
- **Run all tests:** `cd mobile && flutter test`
- **Run a single test:** `cd mobile && flutter test test/test_filename.dart`
- **Build APK release:** `cd mobile && flutter build apk --release`

## Architecture & Structure

LunarMatch is a cross-modal lunar image correspondence and registration engine for the ISRO Smart India Hackathon (SIH 2026).

### Backend (`backend/`)
Python 3.11 with FastAPI, designed as a CPU-capable computer-vision pipeline.
- **`app/main.py`**: FastAPI entrypoint and route orchestration.
- **`app/vision/`**: Domain logic containing feature extraction, matching, and geometry.
  - Core algorithms live here, like `rift2.py` (phase congruency), `superpoint_extractor.py`, `superglue_matcher.py`, and `sift_extractor.py`.
  - `spatial.py` contains grid-based uniform spatial balancing logic.
  - `metrics.py` implements mathematically precise quality scoring (RMSE, spatial coverage, etc.).
- **`app/simulation/`**: Submodules simulating deterministic results for demo scenarios (using fixed seed `26166`) when advanced neural networks cannot act live. Note the distinction between `LIVE` and `SIMULATED` execution modes in the pipeline context.
- **`tests/`**: Over 22 independent Pytest suites.

### Frontend (`mobile/`)
Flutter 3.41 application acting as the mission-control visualizer.
- **State Management:** Connects to the backend via a dedicated API service and manages global state using the `Provider` pattern in `lib/providers/`.
- **Views (`lib/screens/`, `lib/widgets/`)**: 12 custom screens encompassing feature upload, pipeline configuration, and telemetry inspection.
- **Testing (`test/`)**: Widget tests designed to run cleanly under `flutter test`.

## Domain Concepts
- **Reference Image**: The fixed coordinate frame against which registration happens. It is *never transformed*.
- **Moving Image**: The imagery that undergoes geometric transformation/warping to map onto the Reference Image.
- **Pipeline Steps**: Input Normalization -> Denoising -> Feature Extraction (SIFT, RIFT2, etc.) -> Nearest-Neighbor Matching (BFMatcher/FLANN) -> Lowe's Ratio Tests -> RANSAC Geometric Verification (Homography/Affine) -> Spatial Grid Balancing -> Synthesis & Metrics.
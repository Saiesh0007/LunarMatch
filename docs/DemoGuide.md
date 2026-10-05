# LunarMatch — Demonstration Guide

**Target:** Smart India Hackathon 2026 | **Problem Statement:** 26166 | **Organization:** ISRO

Two scripts: the **web demo** (recommended — real Chandrayaan-2 data) and the
**mobile walkthrough**. For talking points and jury questions see
[JuryPresentationGuide.md](JuryPresentationGuide.md).

## Before you start

```bash
cd backend && uvicorn app.main:app --host 0.0.0.0 --port 8000
cd web && npm run dev                      # http://localhost:3000
```

- Check the web header shows `FASTAPI: ONLINE`.
- Have `backend/data/real/pairs/ch2_tmc_iirs_3/ref_iirs.png` and `mov_tmc2.png`
  ready (build them with `python validation/ch2_data.py` if missing).
- Optional, for learned matchers: `python scripts/download_weights.py`.

---

## 1. Web demo (≈ 5 minutes)

**1. Overview (0:00 – 0:30).** Problem statement, sensors (OHRC, TMC-2, IIRS,
LRO NAC, SELENE), CPU-only and offline-capable.

**2. Studio — load real data (0:30 – 1:15).**
Drop `ref_iirs.png` into **REF (FIXED)** and `mov_tmc2.png` into **MOVING**.
Pitch: genuine Chandrayaan-2 TMC-2 and IIRS from the same orbit; panchromatic
camera vs 256-band infrared spectrometer; 4× resolution gap.

**3. Configure (1:15 – 1:45).** Descriptor pipeline **Dense Structural CFOG**;
metadata REF **IIRS** / **78.32**, MOV **TMC-2** / **19.6** (pixel size of the
crop — decimated 4× from 4.9 m).

**4. Execute (1:45 – 2:15).** The page scrolls to the log. The stage bar shows
the dense path. Expect ~6–12 s.

**5. Results (2:15 – 3:15).** The page scrolls to the metric cards: ~98 / 100
verified correspondences, RMSE ≈ 0.7 px, coverage 100 % of the image overlap,
decision ACCEPTED. Drag the **split slider**; try **overlay blink** and the
**difference map**.

<img src="screenshots/web_studio_result.png" width="100%"/>

**6. Correspondences (3:15 – 3:45).** Inliers in green, outliers in red; hover a
point for its residual.

**7. Contrast (3:45 – 4:30, optional).** Re-run with **RIFT2 Multi-Scale**:
RIFT2 finds no usable matches, the log reports the automatic dense fallback, and
the run takes longer for the same answer. Point: dense structural matching is
what makes cross-sensor lunar registration work.

**8. Fail-safe (4:30 – 5:00, optional).** Upload two unrelated images; the run
ends `NOT_RELIABLE` and lists the failed criteria instead of returning a wrong
transform.

Tips
- Metric cards appear only after a run on the current images.
- Large images (multi-megapixel) take longer; choose Dense CFOG and enter GSDs.
- The Export button downloads sample data, not your run; per-run files are in
  `backend/outputs/run_<id>/`.

---

## 2. Mobile walkthrough (≈ 4 minutes)

Run the app (`flutter run`) with the backend reachable (emulator:
`http://10.0.2.2:8000`; phone: set the PC's LAN address on **About**).

1. **Home** — backend status and the four entry cards.
2. **Select lunar images** — pick a demo pair (synthetic prototypes, disclosed
   as such) or upload images; show **SWAP REFERENCE & MOVING**.
3. **Pipeline configuration** — feature method (SIFT, RIFT2, SuperPoint),
   matcher (BF, FLANN, SuperGlue, LightGlue), homography / affine, grid,
   preprocessing (CLAHE, denoising).
4. **Pipeline execution** — ten coarse stages with durations.
5. **Registration result** — decision banner, REF / REGISTERED / OVERLAY / DIFF
   comparison, metric cards, transformation matrix, report export.
6. **Spatial grid** and **Pipeline details** — grid occupancy before / after
   balancing; stage timeline from the backend.
7. **Robustness laboratory** — run an illumination sweep.
8. **Engine capabilities** — capability list served by the backend.

Without a backend the app replays bundled demo results (local demo mode).

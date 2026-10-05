# LunarMatch — Experiments

Two kinds of evaluation: **controlled robustness sweeps** on one image, and
**real cross-sensor validation** on Chandrayaan-2 data.

---

## 1. Robustness sweeps (`POST /api/v1/experiments/robustness`)

`app/services/experiment_service.py` takes one image, makes `variation_steps`
copies (3–10, default 5) with a controlled change spread evenly between `min_val`
and `max_val` (default −50 … 50), and registers the original against each copy
with the requested pipeline settings.

| `experiment_type` | Change applied for parameter value *v* |
| :--- | :--- |
| `illumination` | brightness offset of *v* grey levels |
| `scale` | scale factor max(0.5, 1 + *v*/100) |
| `rotation` | in-plane rotation of *v* degrees |
| `translation` | horizontal shift of *v* px |

For each step it records inliers, inlier ratio, spatial coverage, RMSE, runtime
and status. Results are saved to
`backend/experiments/results/{experiment_id}.json` and carry the disclaimer
*"Controlled robustness experiment — for algorithmic profiling only"*: the
copies are synthetic perturbations of one image, not new observations.

**Where to run it**
- Web → Robustness tab → *Your image: controlled robustness sweep* (uses the
  Studio reference image and method, 5 steps).
- Mobile → Robustness laboratory (illumination, scale, rotation, translation).

The web Robustness tab's *Sun angle delta vs reprojection RMSE*, *SIFT vs RIFT2*
and *sun incidence probe* panels show bundled reference data, labelled
*Reference data · not your image*.

---

## 2. Real Chandrayaan-2 validation

Six TMC-2 (19.6 m) → IIRS (78.32 m) pairs built from raw ISSDC products
(`backend/validation/ch2_data.py`), orbit 1675, latitude −22.6° to +4.3°. Ground
truth comes from the PDS4 label corners; accuracy is reported after removing the
constant label offset (`gt_bias_rm_*`).

| Method | Registered | Bias-removed error (median, per pair) | Time per pair |
| :--- | :--- | :--- | :--- |
| Dense CFOG (standalone matcher) | 6/6 | 0.75 – 1.72 IIRS px (≈ 60 – 135 m) | ~5 s |
| Full pipeline, dense + sensors/GSD | 6/6 | median 1.36 px across pairs | 6.8 s mean |
| Full pipeline, RIFT2 (dense fallback) | 6/6 | median 1.36 px across pairs | 34.9 s mean |

Negative controls (unrelated scenes, noise) are rejected as `NOT_RELIABLE`.
Full method, instrument notes and per-pair table: [RealData.md](RealData.md).

Quick standalone check of the dense matcher on any pair set:

```bash
cd backend
python validation/diag/dense_pairs.py gsd "ch2_*"     # also "neg_*", "ohrc_tc_*", ...
```

Other validation tooling in `backend/validation/` and `backend/scripts/`:
`run_validation.py` (pipeline runs with ground-truth scoring),
`matcher_benchmark.py`, `robustness_sweep.py`, `generate_visuals.py`
(regenerates `docs/visuals/`).

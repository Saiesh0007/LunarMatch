# LunarMatch — Real Chandrayaan-2 Data

How LunarMatch ingests raw Chandrayaan-2 PDS4 products from ISSDC, how the
real-data validation pairs are built, and what they measured.

**Data source:** Chandrayaan-2 orbiter optical payloads (OHRC, TMC-2, IIRS),
ISSDC map browse — <https://chmapbrowse.issdc.gov.in/> (PS 26166 dataset link).

---

## 1. Where the data lives

Raw products are kept in the repository root, one folder per instrument, exactly
as ISSDC delivers them:

```
iir/   IIRS  — browse/ data/ miscellaneous/   (*.qub 256-band cube + *.xml label)
ohr/   OHRC  — browse/ data/ miscellaneous/   (*.img + *.xml)
tmc/   TMC-2 — browse/ data/                  (*.img + *.xml)
```

These folders are multi-GB and are listed in `.gitignore`; they are never committed.

Products currently on disk:

| Instrument | Product | GSD | Size | Coverage | Sun elevation |
| :--- | :--- | :--- | :--- | :--- | :--- |
| TMC-2 (fore camera, `nrf`) | `ch2_tmc_nrf_20200109T0733072590` | 4.9 m | 4000 × 182 901, uint16 | lat −23.4° → +6.7°, lon 0.4°–1.2° | 72.5° |
| IIRS | `ch2_iir_nri_20200109T0733065684` | 78.32 m | 250 × 11 028 × 256 bands, uint16 | lat −24.7° → +5.1°, lon 0.4°–1.2° | (in `.spm` sidecar) |
| OHRC | `ch2_ohr_nrp_20211228T2209123959` | 0.28 m | 12 000 × 79 796, uint8 | south pole, lat −89.9° → −89.25° | −0.04° |

TMC-2 and IIRS were acquired on the **same orbit (1675)** and image the same
strip — a genuine Chandrayaan-2 cross-sensor pair. The OHRC strip is a separate
polar scene with the Sun at the horizon and has no co-located partner yet.

---

## 2. Reading PDS4 products — `app/io/pds_reader.py`

- `read_pds4_label(xml)` parses both generic PDS4 fields and the ISRO ISDA
  mission area: `isda:pixel_resolution` (GSD), `isda:sun_elevation`,
  `isda:sun_azimuth`, the four ground corner coordinates, projection, attitude,
  line exposure, IIRS band centres, and the instrument name
  (`orbiter high resolution camera` → OHRC, `terrain mapping camera` → TMC-2,
  `imaging infrared spectrometer` → IIRS).
- `read_pds4_array(xml, band=None, rows=None, step=1)` memory-maps the raw
  `.img` / `.qub` described by the label. It reads a line window or a decimated
  preview without loading the file (a 400-line window reads in ~0.03 s), and for
  IIRS returns one band or the mean of a band list.

Without these fields the pipeline previously received no GSD or Sun geometry for
real Chandrayaan-2 inputs.

---

## 3. Instrument notes learned from the data

- **TMC-2 `nrf` is the fore-looking camera.** Its ground footprint leads the
  IIRS footprint by ~40 km along-track even though acquisition started only
  0.7 s apart, so line timing cannot be used to co-locate the two; ground corner
  coordinates are used instead.
- **IIRS dead bands.** Bands 1–5, the ~1218 nm order-sorting seam (band ~31)
  and everything from band 150 (≳3.4 µm) are empty. Bands **9–28
  (864–1184 nm)** are strong and closest to TMC-2's panchromatic response.
- **IIRS column striping.** Pushbroom detector striping is ~0.7× the scene
  signal; columns are equalised (median and spread) before matching.
- **Label geolocation disagrees by ~8 km.** After registration, TMC-2 and IIRS
  label coordinates differ by a near-constant **(2.7, 92–103) IIRS px ≈ 0.2 km ×
  7.9 km** along the entire 900 km strip. Six independent windows and two
  independent methods (dense CFOG and SIFT) agree, so this is a real
  inconsistency between the products' geolocation — label-only co-location is off
  by kilometres, registration recovers it.

---

## 4. Building validation pairs — `backend/validation/ch2_data.py`

```powershell
cd backend
.venv\Scripts\python validation\ch2_data.py            # defaults: ..\tmc and ..\iir, 6 pairs
.venv\Scripts\python validation\ch2_data.py --tmc <dir> --iirs <dir> --n 6
```

Writes `backend/data/real/pairs/ch2_tmc_iirs_1 … _6/`, each with:

| File | Content |
| :--- | :--- |
| `mov_tmc2.png` | TMC-2 crop, area-decimated 4× to **19.6 m/px**, 8-bit stretched (~560 × 820) |
| `ref_iirs.png` | Co-located IIRS crop, **78.32 m/px**, mean of bands 9–28, column-destriped (250 × 520) |
| `pair.json` | Provenance (product, line/sample ranges), GSDs, Sun angles, and 81 ground-truth checkpoints |

Ground truth comes from the labels' corner coordinates (bilinear in
line/sample). Because of the label offset above, accuracy is judged by the
**bias-removed** error (`gt_bias_rm_*` in `validation/run_validation.py`). The
reference window is padded 160 lines above and below so the moving crop stays
inside it despite the offset.

**Limits:** the builder expects a TMC-2 and an IIRS product from the same orbit
whose strips overlap. Other sensor combinations (e.g. OHRC → TMC-2) are not
automated yet.

---

## 5. Results

### Dense structural matcher on the six pairs

| Pair | Centre lat | Verified matches | Bias-removed error (median / p90) |
| :--- | :--- | :--- | :--- |
| ch2_tmc_iirs_1 | −22.6° | 90 / 100 | 1.72 / 3.82 px |
| ch2_tmc_iirs_2 | −17.2° | 100 / 100 | 1.31 / 2.70 px |
| ch2_tmc_iirs_3 | −11.9° | 98 / 100 | 1.39 / 3.53 px |
| ch2_tmc_iirs_4 | −6.5° | 100 / 100 | 1.04 / 3.46 px |
| ch2_tmc_iirs_5 | −1.1° | 100 / 100 | 0.75 / 1.46 px |
| ch2_tmc_iirs_6 | +4.3° | 100 / 100 | 1.41 / 3.25 px |

Errors are in IIRS pixels (78.32 m): **≈ 60–135 m median**. Each run takes ~5 s.

### Full pipeline, by Studio configuration (all six pairs)

| Configuration | Registered | Quality accepted | Mean time | Error (median / max) |
| :--- | :--- | :--- | :--- | :--- |
| RIFT2 multi-scale, no metadata | 6/6 | 6/6 | 34.9 s | 1.36 / 1.56 px |
| Dense CFOG | 6/6 | 6/6 | 10.7 s | 1.36 / 1.56 px |
| RIFT2 + sensors/GSD | 6/6 | 6/6 | 10.9 s | 1.36 / 1.57 px |
| **Dense CFOG + sensors/GSD** | 6/6 | 6/6 | **6.8 s** | 1.36 / 1.57 px |

RIFT2 finds no usable matches on these pairs; with RIFT2 selected, the
registration comes from the automatic dense fallback.

### Negative controls

Unrelated pairs (`neg_noise`, `neg_ohrc_s1_vs_tc_s3`, `neg_ohrc_s2_vs_tc_s1`)
are rejected as `NOT_RELIABLE` by the dense method, with and without GSD.

---

## 6. Using the data in the web Studio

The Studio uploads PNG / JPG / TIFF / BMP, not raw `.img` / `.qub`, so use the
prepared crops:

1. REF (FIXED): `backend\data\real\pairs\ch2_tmc_iirs_3\ref_iirs.png`
2. MOVING: `backend\data\real\pairs\ch2_tmc_iirs_3\mov_tmc2.png`
3. Descriptor pipeline: **Dense Structural CFOG**
4. Image metadata: REF **IIRS**, GSD **78.32**; MOV **TMC-2**, GSD **19.6**
   (the pixel size of the uploaded file — 4× the nominal 4.9 m because the crop was decimated)

<img src="screenshots/web_studio_result.png" width="100%"/>

*`ch2_tmc_iirs_3` in the Studio: 98 / 100 verified correspondences, RMSE 0.71 px, ACCEPTED.*

Whole browse strips (`*_b_brw_*.png`, e.g. 400 × 18 290 px) upload fine but are
too elongated to register usefully; crop co-located windows first. Two products
only register if they image the same ground.

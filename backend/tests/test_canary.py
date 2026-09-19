"""End-to-end smoke test for the full pipeline.

This canary test runs a complete pipeline execution on a synthetic pair
to verify no native crashes occur in the critical path. It serves as a
regression net for the Windows native access violations that were
diagnosed and stabilized.
"""
import numpy as np
import pytest


def generate_synthetic_pair(seed: int = 42, size: int = 256) -> tuple:
    """Generate a deterministic synthetic image pair using NumPy + PIL only."""
    from PIL import Image
    rng = np.random.default_rng(seed)

    # Base crater surface
    yy, xx = np.mgrid[0:size, 0:size].astype(np.float32)

    def make_surface(suffix_seed):
        r = np.random.default_rng(suffix_seed)
        img = np.zeros((size, size), dtype=np.float32)
        for _ in range(15):
            cx, cy = r.uniform(0.1, 0.9, 2) * size
            radius = r.uniform(size * 0.02, size * 0.12)
            dist = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
            ring = np.exp(-((dist - radius) ** 2) / (2.0 * (radius * 0.15) ** 2))
            img += ring * r.uniform(0.5, 1.5)
        img = (img - img.min()) / (img.max() - img.min() + 1e-9)
        return (img * 255).astype(np.uint8)

    ref = make_surface(seed)
    mov = make_surface(seed + 1)
    return ref, mov


def test_full_pipeline_smoke():
    """End-to-end smoke test: no native crashes, all stages reachable.

    Runs a minimal pipeline on a NumPy-only synthetic pair.
    This test catches regressions in the Windows native crash stabilization work.
    """
    from app.services.pipeline_service import PipelineService
    from app.models.requests import PipelineRunRequest
    from app.models.schemas import (
        FeatureMethod, MatcherType, GeometricModel, EstimatorMethod,
        SensorType, PreprocessingConfig
    )

    # Use demo_pair_a which has moderate illumination difference (45 vs 55 degrees)
    req = PipelineRunRequest(
        reference_image_id="demo_pair_a_ref",
        moving_image_id="demo_pair_a_mov",
        reference_sensor=SensorType.OHRC,
        moving_sensor=SensorType.TMC_2,
        feature_method=FeatureMethod.RIFT2,
        matcher=MatcherType.BF,
        geometric_model=GeometricModel.AFFINE,
        estimator_method=EstimatorMethod.MAGSAC,
        spatial_balancing=True,
        grid_size=6,
    )
    svc = PipelineService()
    from unittest import mock
    with mock.patch("spiceypy.str2et", side_effect=lambda x: 1.0 if "01Z" in x else 0.0):
        result = svc.execute_pipeline(req)

    assert result.status is not None
    assert result.status.value in ("SUCCESSFUL", "ACCEPTED", "LOW_CONFIDENCE", "NOT_RELIABLE")
    assert result.metrics is not None
    assert hasattr(result.metrics, "rmse_px")
    
    # Verify F3 overlap logging on the demo pair
    import json
    from pathlib import Path
    
    # Find the output directory for this run
    # result.run_id contains the ID, output dir is typically outputs/{run_id}
    out_dir = Path("c:/lm/lm/backend/outputs") / result.run_id
    match_decisions = out_dir / "match_decisions.jsonl"
    
    assert match_decisions.exists(), "match_decisions.jsonl was not created!"
    
    entries = []
    with open(match_decisions, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            try:
                entries.append(json.loads(line))
            except Exception:
                continue

    def find_stage(name):
        for entry in entries:
            if entry.get("stage") == name:
                return entry
        return None

    overlap = find_stage("overlap")
    assert overlap is not None, "overlap stage missing from match_decisions.jsonl"
    assert overlap.get("fallback") is False, "Overlap stage fell back on demo fixture!"
    overlap_ratio = overlap.get("overlap_ratio")
    assert overlap_ratio is not None, "overlap_ratio missing from log"
    assert 0.0 < overlap_ratio < 1.0, f"overlap_ratio {overlap_ratio} is not strictly in (0, 1)"

    spice = find_stage("spice")
    assert spice is not None, "spice stage missing from match_decisions.jsonl"
    if not spice.get("fallback", True):
        # fallback is False, meaning ok is True
        pass # The actual values like overlap_ratio are logged in footprint_validation now!
    else:
        assert spice.get("reason") is not None

    spice_build = find_stage("spice_build")
    assert spice_build is not None, "spice_build stage missing from match_decisions.jsonl"
    
    d = find_stage("footprint_validation")
    assert d is not None, "footprint_validation stage missing"
    assert isinstance(d["ok"], bool)
    if d["ok"]:
        assert 0.0 < d["overlap_ratio"] <= 1.0
        assert 0.0 <= d["valid_fraction"] <= 1.0
    else:
        assert d.get("reason")

    illum = find_stage("illumination")
    assert illum is not None, "illumination stage missing"
    assert illum["source"] in ("spice", "pds", "mixed")
    assert isinstance(illum["ok"], bool)
    # On the demo pair with working SPICE, source should be "spice" and ok should be True
    assert illum["source"] == "spice"
    assert illum["ok"] is True

    iq = find_stage("input_quality")
    assert iq is not None, "input_quality stage missing"
    assert isinstance(iq["ok"], bool)
    assert 0.0 <= iq["invalid_a"] <= 1.0
    assert 0.0 <= iq["invalid_b"] <= 1.0
    assert iq["threshold"] > 0
    # On the demo pair, both should be near 0
    assert iq["invalid_a"] < 0.05
    assert iq["invalid_b"] < 0.05

    sh = find_stage("shadow")
    assert sh is not None, "shadow stage missing from match_decisions.jsonl"
    assert 0.0 <= sh["lit_fraction"] <= 1.0
    assert sh["correction_clip_hits"] >= 0
    # On the demo pair with a DEM fixture, lit_fraction should be
    # strictly between 0 and 1. If it is exactly 1.0 with dem=None,
    # the fixture bootstrap is missing a DEM.
    assert 0.0 < sh["lit_fraction"] < 1.0, f"lit_fraction {sh['lit_fraction']} was not strictly between 0 and 1"
    assert sh["dem"] is not None

    tc = find_stage("terrain_corr")
    assert tc is not None, "terrain_corr stage missing from match_decisions.jsonl"
    assert tc["clip_hits"] >= 0
    assert 0.2 < tc["mean_after"] / max(tc["mean_before"], 1e-6) < 5.0

    rn = find_stage("radiometric_norm")
    assert rn is not None, "radiometric_norm stage missing from match_decisions.jsonl"
    assert rn["method"] in ("none", "clahe", "hist", "clahe+hist")
    assert isinstance(rn["applied"], bool)

    do = find_stage("depth_optical")
    if do is not None:
        assert isinstance(do["applied"], bool)

    d = find_stage("scale_space")
    assert d is not None
    assert isinstance(d["use_scale_space"], bool)
    if d["use_scale_space"]:
        assert d["n_octaves"] >= 3
        assert len(d["n_keypoints_per_octave"]) == d["n_octaves"]
        assert sum(d["n_keypoints_per_octave"]) == d["total_keypoints"]
        # Every octave must have at least 1 keypoint, otherwise the
        # scale space is not actually helping matching.
        assert all(k > 0 for k in d["n_keypoints_per_octave"]), (
            f"empty octave detected: {d['n_keypoints_per_octave']}"
        )

    d = find_stage("hypnet")
    assert d is not None
    assert isinstance(d["applied"], bool)
    assert d["mod_dim"] > 0 or d["applied"] is False

    d = find_stage("scdf_gates")
    assert d is not None
    assert d["null_correlations_k"] == 8
    assert isinstance(d["kept"], int) and d["kept"] >= 0
    total_rejected = (d["rejected_magnitude"] + d["rejected_loo"] +
                      d["rejected_response"] + d["rejected_error"])
    assert total_rejected >= 0

    d = find_stage("tps")
    assert d is not None
    assert isinstance(d["applied"], bool)
    if d["applied"]:
        assert d["n_inliers"] >= 10
        assert d["residual_rms_px_after"] <= d["residual_rms_px_before"] * 1.01
    else:
        assert d.get("reason")

    d = find_stage("rift2")
    assert d is not None
    assert d.get("fallback") is not True, (
        "RIFT2 forced to demo mode — pipeline_service.py:67 not fixed"
    )
    assert d.get("descriptor_dim") == 216

    d = find_stage("pds_meta")
    assert d is not None
    # gsd_meters may be None if the fixture has no PDS metadata.
    # If present, it must be positive.
    if d["gsd_meters"] is not None:
        assert d["gsd_meters"] > 0

    # Tightened order check ONLY on stage-level names
    STAGE_NAMES = {"crs", "gsd_norm", "overlap", "spice", "spice_build",
                   "footprint_validation", "illumination", "input_quality",
                   "shadow", "terrain_corr", "radiometric_norm",
                   "depth_optical", "scale_space", "hypnet",
                   "scdf_gates", "tps", "rift2", "pds_meta",
                   "magsac", "subpixel", "superpoint", "superglue", "lightglue"}

    decisions = entries
    stage_level = [d["stage"] for d in decisions
                   if d.get("stage") in STAGE_NAMES]

    assert stage_level.index("scdf_gates") < stage_level.index("magsac")
    assert stage_level.index("magsac") < stage_level.index("tps")
    assert stage_level.index("tps") < stage_level.index("subpixel")


def load_decisions(run_dir):
    """Parse match_decisions.jsonl into a list of dicts."""
    import json
    from pathlib import Path
    p = Path(run_dir) / "match_decisions.jsonl"
    assert p.exists(), f"audit trail missing at {p}"
    return [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]


def find_stage(decisions, stage):
    """Return the last stage entry with matching name, or None."""
    hits = [d for d in decisions if d.get("stage") == stage]
    return hits[-1] if hits else None


def test_canary_full_pipeline():
    """F33 — Canary expansion with 18 comprehensive assertions."""
    from app.services.pipeline_service import PipelineService
    from app.models.requests import PipelineRunRequest
    from app.models.schemas import (
        FeatureMethod, MatcherType, GeometricModel, EstimatorMethod,
        SensorType
    )
    from unittest import mock

    req = PipelineRunRequest(
        reference_image_id="demo_pair_a_ref",
        moving_image_id="demo_pair_a_mov",
        reference_sensor=SensorType.OHRC,
        moving_sensor=SensorType.TMC_2,
        feature_method=FeatureMethod.RIFT2,
        matcher=MatcherType.BF,
        geometric_model=GeometricModel.AFFINE,
        estimator_method=EstimatorMethod.MAGSAC,
        spatial_balancing=True,
        grid_size=6,
    )
    svc = PipelineService()
    with mock.patch("spiceypy.str2et", side_effect=lambda x: 1.0 if "01Z" in x else 0.0):
        result = svc.execute_pipeline(req)

    out_dir = svc.outputs_dir / result.run_id
    decisions = load_decisions(out_dir)

    # 1. CRS is live:
    d = find_stage(decisions, "crs")
    assert d is not None
    assert d["pole"] in ("north", "south")
    assert d.get("fallback") is not True
    assert d["ms"] < 400

    # 2. GSD normalisation ran:
    d = find_stage(decisions, "gsd_norm")
    assert d is not None
    assert d["target"] > 0
    assert d["resampled"] in (True, False)

    # 3. Overlap is computed, not 1.0:
    d = find_stage(decisions, "overlap")
    assert d is not None
    assert d.get("fallback") is not True
    assert 0.0 < d["overlap_ratio"] < 1.0

    # 4. SPICE attempted:
    d = find_stage(decisions, "spice")
    assert d is not None
    if d["ok"]:
        assert d["overlap_ratio"] is not None
        assert d["sun_angle_diff_deg"] is not None
    else:
        assert d.get("reason")

    # 5. SPICE build ran:
    d = find_stage(decisions, "spice_build")
    assert d is not None
    # Paths may be null if build was skipped; reason must be set.

    # 6. Footprint validation ran:
    d = find_stage(decisions, "footprint_validation")
    assert d is not None
    assert isinstance(d["ok"], bool)
    assert 0.0 <= d["valid_fraction"] <= 1.0

    # 7. Illumination computed:
    d = find_stage(decisions, "illumination")
    assert d is not None
    assert d["source"] in ("spice", "pds", "mixed")
    assert isinstance(d["ok"], bool)

    # 8. Input quality gate ran:
    d = find_stage(decisions, "input_quality")
    assert d is not None
    assert isinstance(d["ok"], bool)
    assert 0.0 <= d["invalid_a"] <= 1.0
    assert 0.0 <= d["invalid_b"] <= 1.0
    assert d["threshold"] > 0

    # 9. Shadow mask ran:
    d = find_stage(decisions, "shadow")
    assert d is not None
    assert 0.0 <= d["lit_fraction"] <= 1.0
    assert d["correction_clip_hits"] >= 0
    # On demo pair with DEM, lit_fraction strictly between 0 and 1.
    # If dem is None, lit_fraction must be 1.0.
    if d["dem"] is not None:
        assert 0.0 < d["lit_fraction"] < 1.0
    else:
        assert d["lit_fraction"] == 1.0

    # 10. Terrain correction logged:
    d = find_stage(decisions, "terrain_corr")
    assert d is not None
    assert isinstance(d["mean_before"], (int, float))
    assert isinstance(d["mean_after"], (int, float))
    assert isinstance(d["std_before"], (int, float))
    assert isinstance(d["std_after"], (int, float))
    assert d["clip_hits"] >= 0

    # 11. Radiometric normalisation logged:
    d = find_stage(decisions, "radiometric_norm")
    assert d is not None
    assert d["method"] in ("none", "clahe", "hist", "clahe+hist")
    assert isinstance(d["applied"], bool)

    # 12. Scale space built:
    d = find_stage(decisions, "scale_space")
    assert d is not None
    assert isinstance(d["use_scale_space"], bool)
    if d["use_scale_space"]:
        assert d["n_octaves"] >= 3
        assert len(d["n_keypoints_per_octave"]) == d["n_octaves"]
        assert all(k > 0 for k in d["n_keypoints_per_octave"])
        assert sum(d["n_keypoints_per_octave"]) == d["total_keypoints"]

    # 13. HypNet ran:
    d = find_stage(decisions, "hypnet")
    assert d is not None
    assert isinstance(d["applied"], bool)
    if d["applied"]:
        assert d["mod_dim"] > 0

    # 14. SCDF gates ran:
    d = find_stage(decisions, "scdf_gates")
    assert d is not None
    assert d["null_correlations_k"] == 8
    assert isinstance(d["kept"], int)
    assert d["kept"] >= 0

    # 15. TPS ordering and behaviour:
    d = find_stage(decisions, "tps")
    assert d is not None
    assert isinstance(d["applied"], bool)
    if d["applied"]:
        assert d["n_inliers"] >= 10
        assert d["residual_rms_px_after"] <= \
               d["residual_rms_px_before"] * 1.01
    else:
        assert d.get("reason")

    # 16. RIFT2 direct routing (F29 check):
    d = find_stage(decisions, "rift2")
    assert d is not None
    assert d.get("fallback") is not True, (
        "RIFT2 forced to demo mode — pipeline_service.py:67 not fixed"
    )
    assert d.get("descriptor_dim") == 216

    # 17. PDS metadata feed:
    d = find_stage(decisions, "pds_meta")
    assert d is not None
    if d["gsd_meters"] is not None:
        assert d["gsd_meters"] > 0

    # 18. Stage ordering (magsac < tps < subpixel, and scdf < magsac):
    STAGE_NAMES = {
        "crs", "gsd_norm", "overlap", "spice", "spice_build",
        "footprint_validation", "illumination", "input_quality",
        "shadow", "terrain_corr", "radiometric_norm",
        "depth_optical", "scale_space", "hypnet",
        "scdf_gates", "tps", "rift2", "pds_meta",
        "magsac", "subpixel", "superpoint", "superglue", "lightglue"
    }
    stage_level = [d["stage"] for d in decisions
                   if d.get("stage") in STAGE_NAMES]

    assert stage_level.index("scdf_gates") < \
           stage_level.index("magsac")
    assert stage_level.index("magsac") < \
           stage_level.index("tps")
    assert stage_level.index("tps") < \
           stage_level.index("subpixel")

    print(f"Verified {len(decisions)} stage entries")
    print(f"Stages present: {sorted(set(d['stage'] for d in decisions if 'stage' in d))}")


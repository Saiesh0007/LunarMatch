"""Tests for F16 Depth-Optical Modality Handling.

Paper: RIFT (TIP2020.pdf), Fig. 9(d), Sec. II-C.
"""
import numpy as np
import pytest

from app.services.router import select_pipeline_config
from app.services.rift2 import _depth_aware_preprocess, RIFT2Extractor


def test_depth_routed():
    """router.select_pipeline_config("depth_optical") returns config with depth_preprocess=True."""
    config = select_pipeline_config("depth_optical")
    assert config.depth_preprocess is True
    assert config.get("depth_preprocess") is True
    assert config["depth_preprocess"] is True
    assert config.sensors_differ is True
    assert config.pc_orientations == 6
    assert config.pc_scales == 4
    assert config.descriptor == "rift2"


def test_depth_aliases():
    """All four alias strings return the same or equal config."""
    aliases = ["depth_optical", "depth-optical", "depth_vs_optical", "depth_to_optical"]
    configs = [select_pipeline_config(alias) for alias in aliases]
    first = configs[0]
    for cfg in configs[1:]:
        assert cfg == first
        assert cfg.depth_preprocess is True


def test_depth_preprocess_applied():
    """Run _depth_aware_preprocess on a synthetic depth image (gradient from 0 to 100).

    Assert:
      - returned image is uint8
      - inverted is True
      - depth_range == [0.0, 100.0]
      - edges are visible: std(processed) > std(original)
    """
    # 100x100 ramp from 0 to 100
    img = np.tile(np.linspace(0, 100, 100, dtype=np.float32), (100, 1))

    processed, stats = _depth_aware_preprocess(img)

    assert processed.dtype == np.uint8
    assert stats["inverted"] is True
    assert stats["depth_range"] == [0.0, 100.0]
    assert np.std(processed) > np.std(img)


def test_non_depth_pair_unaffected():
    """router.select_pipeline_config("optical_optical") returns config with depth_preprocess=False or missing."""
    config = select_pipeline_config("optical_optical")
    assert not config.get("depth_preprocess", False)


def test_determinism():
    """Same input -> identical output for _depth_aware_preprocess."""
    rng = np.random.default_rng(26166)
    img = rng.uniform(10.0, 500.0, (128, 128)).astype(np.float32)

    proc1, stats1 = _depth_aware_preprocess(img)
    proc2, stats2 = _depth_aware_preprocess(img)

    assert np.array_equal(proc1, proc2)
    assert stats1 == stats2


def test_rift2_extractor_depth_preprocess_integration():
    """Verify RIFT2Extractor integrates depth_preprocess config flag."""
    extractor = RIFT2Extractor(max_features=100, config={"depth_preprocess": True})
    img = np.tile(np.linspace(0, 100, 64, dtype=np.float32), (64, 1))
    kps, descs = extractor.extract(img)
    assert isinstance(kps, list)
    assert isinstance(descs, np.ndarray)

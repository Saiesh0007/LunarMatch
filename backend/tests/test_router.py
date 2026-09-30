import json

import numpy as np

from app.services.router import detect_sensor, reduce_iirs_to_grayscale, select_pipeline_config


EXPECTED = {
    ("OHRC", "OHRC"): ("rift2_multiscale", "bf_ratio", "magsac", "affine", 3),
    ("OHRC", "TMC2"): ("rift2_multiscale", "bf_ratio", "magsac", "affine", 3),
    ("OHRC", "IIRS"): ("rift2", "mi_dense", "magsac", "affine", 1),
    ("OHRC", "LRO_NAC"): ("hopc_rift2_fusion", "bf_ratio", "magsac", "affine", 3),
    ("TMC2", "LRO_NAC"): ("rift2", "flann_ratio", "magsac", "similarity", 1),
    ("TMC2", "SELENE"): ("rift2", "flann_ratio", "ransac", "similarity", 1),
    ("IIRS", "LRO_NAC"): ("hopc", "mi_dense", "magsac", "affine", 1),
    ("unknown", "unknown"): ("rift2_multiscale", "bf_ratio", "magsac", "affine", 3),
}


def test_router_table_matches_spec():
    for pair, expected in EXPECTED.items():
        config = select_pipeline_config({"sensor": pair[0]}, {"sensor": pair[1]})
        assert (config.feature_method, config.matcher, config.estimator, config.geometry_model, config.pyramid_levels) == expected


def test_router_falls_back_to_unknown():
    config = select_pipeline_config({"sensor": "alien"}, {"sensor": "unknown"})
    assert (config.source_sensor, config.reference_sensor) == ("unknown", "unknown")
    assert config.feature_method == "rift2_multiscale"


def test_router_user_override_wins():
    config = select_pipeline_config({"sensor": "OHRC"}, {"sensor": "TMC2"}, user_override="hopc")
    assert config.feature_method == "hopc"
    assert "override" in config.rationale.lower()


def test_sensor_detection_from_filename():
    assert detect_sensor({}, "OHRC_123.img") == "OHRC"
    assert detect_sensor({}, "ch2_ohrc_scene.img") == "OHRC"
    assert detect_sensor({}, "tmc-2_scene.img") == "TMC2"


def test_sensor_detection_from_metadata():
    assert detect_sensor({"INSTRUMENT_ID": "OHRC"}) == "OHRC"
    assert detect_sensor({"INSTRUMENT_NAME": "LRO NAC CAMERA"}) == "LRO_NAC"
    assert detect_sensor({"sensor": "IIRS"}) == "IIRS"


def test_iirs_reduction_returns_grayscale():
    cube = np.random.default_rng(1).random((12, 10, 6), dtype=np.float32)
    grayscale, method = reduce_iirs_to_grayscale(cube, band_mask_path="missing-mask.json")
    assert grayscale.shape == (12, 10)
    assert grayscale.dtype == np.float32
    assert 0.0 <= grayscale.min() <= grayscale.max() <= 1.0
    assert method == "band_mean_fallback"


def test_iirs_reduction_falls_back_to_band_mean(tmp_path):
    cube = np.random.default_rng(2).random((4, 5, 3), dtype=np.float32)
    mask_path = tmp_path / "mask.json"
    mask_path.write_text(json.dumps({"mask": [True, False, True]}), encoding="utf-8")
    grayscale, method = reduce_iirs_to_grayscale(cube, str(mask_path))
    np.testing.assert_allclose(grayscale, cube[:, :, [0, 2]].mean(axis=2))
    assert method == "band_mean_fallback"


def test_routing_rationale_is_populated():
    for pair in EXPECTED:
        assert select_pipeline_config({"sensor": pair[0]}, {"sensor": pair[1]}).rationale


def test_router_sensors_differ():
    cfg_same = select_pipeline_config("optical_optical")
    assert cfg_same.sensors_differ is False
    assert cfg_same.get("sensors_differ") is False

    cfg_diff1 = select_pipeline_config("ohrc_vs_tmc2")
    assert cfg_diff1.sensors_differ is True
    assert cfg_diff1.get("sensors_differ") is True

    cfg_diff2 = select_pipeline_config("optical_sar")
    assert cfg_diff2.sensors_differ is True
    assert cfg_diff2.get("sensors_differ") is True


def test_router_use_hypnet():
    cfg_opt = select_pipeline_config("optical_optical")
    assert cfg_opt.use_hypnet is True
    assert cfg_opt.get("use_hypnet") is True

    cfg_cross = select_pipeline_config("ohrc_vs_tmc2")
    assert cfg_cross.use_hypnet is True
    assert cfg_cross.get("use_hypnet") is True

    cfg_sar = select_pipeline_config("optical_sar")
    assert cfg_sar.use_hypnet is False
    assert cfg_sar.get("use_hypnet") is False


def test_router_use_tps():
    cfg_opt = select_pipeline_config("optical_optical")
    assert cfg_opt.use_tps is True
    assert cfg_opt.get("use_tps") is True

    cfg_cross = select_pipeline_config("ohrc_vs_tmc2")
    assert cfg_cross.use_tps is True
    assert cfg_cross.get("use_tps") is True



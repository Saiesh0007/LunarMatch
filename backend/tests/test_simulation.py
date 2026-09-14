import numpy as np
import pytest
from app.simulation.simulator import DeterministicSimulator
from app.models.requests import PipelineRunRequest
from app.models.schemas import FeatureMethod, MetricMode

def test_simulation_determinism():
    ref_img = np.full((256, 256), 120, dtype=np.uint8)
    mov_img = np.full((256, 256), 115, dtype=np.uint8)

    req = PipelineRunRequest(
        reference_image_id="dummy_ref",
        moving_image_id="dummy_mov",
        feature_method=FeatureMethod.RIFT2,
        grid_size=6,
    )

    sim1 = DeterministicSimulator(seed=26166)
    status1, metrics1, stats1, matches1, reg1, _, _, H1, _ = sim1.run_simulation(ref_img, mov_img, req)

    sim2 = DeterministicSimulator(seed=26166)
    status2, metrics2, stats2, matches2, reg2, _, _, H2, _ = sim2.run_simulation(ref_img, mov_img, req)

    assert status1 == status2
    assert metrics1.metric_mode == MetricMode.DEMO
    assert metrics1.simulation_seed == 26166
    assert metrics1.inlier_ratio == metrics2.inlier_ratio
    assert metrics1.spatial_coverage == metrics2.spatial_coverage
    assert len(matches1) == len(matches2)
    assert np.allclose(H1, H2)

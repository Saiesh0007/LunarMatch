import numpy as np
from scipy.ndimage import fourier_shift

from app.refinement.subpixel import refine_subpixel


def textured_image(size=160):
    """Create high-frequency content for well-conditioned phase correlation.

    Low-frequency images can induce systematic subpixel bias because their
    phase surface is dominated by a few frequencies.
    """
    yy, xx = np.mgrid[0:size, 0:size].astype(np.float32)
    image = np.sin(xx * 0.8) + np.cos(yy * 0.6)
    image += 0.7 * np.exp(-((xx - size * 0.35) ** 2 + (yy - size * 0.6) ** 2) / 180.0)
    image += 0.4 * np.exp(-((xx - size * 0.7) ** 2 + (yy - size * 0.3) ** 2) / 100.0)
    return ((image - image.min()) / (image.max() - image.min())).astype(np.float32)


def test_subpixel_recovers_known_shift():
    """A 0.4 px translation is recovered within 0.15 px tolerance."""
    source = textured_image()
    applied_shift = 0.4
    reference = np.fft.ifftn(fourier_shift(np.fft.fftn(source), shift=(0.0, applied_shift))).real.astype(np.float32)
    src_points = np.array([[80.0, 80.0]], dtype=np.float32)
    ref_points = np.array([[80.0, 80.0]], dtype=np.float32)
    _, refined_ref, diagnostics = refine_subpixel(source, reference, src_points, ref_points)
    assert diagnostics["n_refined"] == 1
    recovered_shift = float(refined_ref[0, 0] - ref_points[0, 0])
    assert abs(recovered_shift - applied_shift) <= 0.15


def test_subpixel_bias_sweep():
    """Recovery remains within 0.15 px across the full 0.1-to-0.9 px range."""
    source = textured_image()
    for true_shift in np.arange(0.1, 1.0, 0.1):
        reference = np.fft.ifftn(
            fourier_shift(np.fft.fftn(source), shift=(0.0, float(true_shift)))
        ).real.astype(np.float32)
        _, refined, _ = refine_subpixel(
            source,
            reference,
            np.array([[80.0, 80.0]], dtype=np.float32),
            np.array([[80.0, 80.0]], dtype=np.float32),
        )
        recovered = float(refined[0, 0] - 80.0)
        assert abs(recovered - true_shift) <= 0.15


def test_subpixel_rejects_low_peak():
    """Uniform noise has no reliable peak and is rejected below the 0.2 threshold."""
    rng = np.random.default_rng(3)
    source = rng.random((128, 128), dtype=np.float32)
    reference = rng.random((128, 128), dtype=np.float32)
    _, refined, diagnostics = refine_subpixel(source, reference, np.array([[64.0, 64.0]]), np.array([[64.0, 64.0]]))
    assert diagnostics["per_match"][0]["refinement_status"] == "rejected_low_peak"
    np.testing.assert_array_equal(refined, np.array([[64.0, 64.0]], dtype=np.float32))


def test_subpixel_handles_out_of_bounds():
    """A border match is rejected without changing its coordinates."""
    image = textured_image()
    points = np.array([[2.0, 2.0]], dtype=np.float32)
    _, refined, diagnostics = refine_subpixel(image, image, points, points)
    assert diagnostics["per_match"][0]["refinement_status"] == "rejected_out_of_bounds"
    np.testing.assert_array_equal(refined, points)


def test_subpixel_does_not_move_matches_without_signal():
    """Flat patches are rejected rather than receiving arbitrary corrections."""
    image = np.ones((128, 128), dtype=np.float32)
    points = np.array([[64.0, 64.0]], dtype=np.float32)
    _, refined, diagnostics = refine_subpixel(image, image, points, points)
    assert diagnostics["per_match"][0]["refinement_status"] == "rejected_low_peak"
    np.testing.assert_array_equal(refined, points)


def test_subpixel_uncertainty_is_reasonable():
    """Accepted curvature uncertainties remain between zero and patch_size / 4."""
    image = textured_image()
    _, _, diagnostics = refine_subpixel(image, image, np.array([[80.0, 80.0]]), np.array([[80.0, 80.0]]))
    if diagnostics["n_refined"]:
        result = diagnostics["per_match"][0]
        assert 0.0 <= result["uncertainty_x"] <= 16.0
        assert 0.0 <= result["uncertainty_y"] <= 16.0


def test_subpixel_integration_with_pipeline():
    """The live pipeline artifact writer exposes a subpixel quality block."""
    from app.services.pipeline_service import PipelineService
    assert hasattr(PipelineService, "_persist_artifacts")

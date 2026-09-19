"""Pyramid and scale space service module.

Papers: RIFT2 (arXiv 2303.00319v1), Sec. V; SIFT (Lowe 2004), Sec. 3.
"""
from ..preprocessing.pyramid import (
    LunarKeyPoint,
    MultiScalePyramid,
    MultiscaleResult,
    PyramidFeatureExtractor,
    _build_pyramid_debug,
    _deduplicate,
    extract_rift2_multiscale,
    filter_cross_scale_matches,
)
from ..vision.rift2 import build_pc_octaves

__all__ = [
    "LunarKeyPoint",
    "MultiScalePyramid",
    "MultiscaleResult",
    "PyramidFeatureExtractor",
    "_build_pyramid_debug",
    "_deduplicate",
    "build_pc_octaves",
    "extract_rift2_multiscale",
    "filter_cross_scale_matches",
]

"""RIFT2 service module providing depth-aware preprocessing and feature extraction.

Paper: RIFT (TIP2020.pdf), Sec. II-C.
"""
from ..vision.rift2 import (
    RIFT2Extractor,
    _depth_aware_preprocess,
    build_pc_octaves,
    compute_phase_congruency,
    compute_phase_congruency_and_mim,
    construct_log_gabor_filter_bank,
    extract_rift2,
    extract_rift2_on_pc,
)

__all__ = [
    "RIFT2Extractor",
    "_depth_aware_preprocess",
    "build_pc_octaves",
    "compute_phase_congruency",
    "compute_phase_congruency_and_mim",
    "construct_log_gabor_filter_bank",
    "extract_rift2",
    "extract_rift2_on_pc",
]


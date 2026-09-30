"""Tests for F3: Shapely footprint overlap logic."""
import pytest
from app.services.quality import compute_footprint_overlap


def _make_meta(transform, width, height):
    return {
        "transform": transform,
        "samples": width,
        "lines": height
    }


def test_half_offset_squares():
    """Two 10x10 squares, offset by 5 in X. Intersection=50, Union=150. IoU=1/3."""
    # (a, b, c, d, e, f)
    # c=x, f=y, a=pixel_width, e=pixel_height
    # Square 1: TopLeft (0, 0), BottomRight (10, -10)
    meta_a = _make_meta((1.0, 0.0, 0.0, 0.0, -1.0, 0.0), 10, 10)
    # Square 2: TopLeft (5, 0), BottomRight (15, -10)
    meta_b = _make_meta((1.0, 0.0, 5.0, 0.0, -1.0, 0.0), 10, 10)
    
    iou = compute_footprint_overlap(meta_a, meta_b)
    assert abs(iou - 1/3) < 1e-5


def test_disjoint():
    """Two disjoint 10x10 squares. IoU=0."""
    meta_a = _make_meta((1.0, 0.0, 0.0, 0.0, -1.0, 0.0), 10, 10)
    meta_b = _make_meta((1.0, 0.0, 20.0, 0.0, -1.0, 0.0), 10, 10)
    
    iou = compute_footprint_overlap(meta_a, meta_b)
    assert iou == 0.0


def test_nested():
    """One 5x5 square inside a 10x10 square. Intersection=25, Union=100. IoU=0.25."""
    meta_a = _make_meta((1.0, 0.0, 0.0, 0.0, -1.0, 0.0), 10, 10) # 0 to 10
    meta_b = _make_meta((1.0, 0.0, 2.0, 0.0, -1.0, -2.0), 5, 5)  # 2 to 7
    
    iou = compute_footprint_overlap(meta_a, meta_b)
    assert abs(iou - 0.25) < 1e-5


def test_identical():
    """Identical 10x10 squares. IoU=1.0."""
    meta_a = _make_meta((1.0, 0.0, 0.0, 0.0, -1.0, 0.0), 10, 10)
    meta_b = _make_meta((1.0, 0.0, 0.0, 0.0, -1.0, 0.0), 10, 10)
    
    iou = compute_footprint_overlap(meta_a, meta_b)
    assert iou == 1.0


def test_missing_transform():
    """Missing transform should fallback to 1.0."""
    meta_a = {"samples": 10, "lines": 10}
    meta_b = {"samples": 10, "lines": 10}
    assert compute_footprint_overlap(meta_a, meta_b) == 1.0

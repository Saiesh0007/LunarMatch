"""Data quality and validation logic.

Includes geometric footprint overlap calculation using Shapely.
"""
from shapely.geometry import box
import numpy as np


def compute_footprint_overlap(meta_a: dict, meta_b: dict, crs: str = "lunar-ps") -> float:
    """Compute the Intersection over Union (IoU) of two image footprints.
    
    Args:
        meta_a: Metadata dict for the first image containing 'transform', 'lines', 'samples'.
        meta_b: Metadata dict for the second image.
        crs: Coordinate reference system identifier.
        
    Returns:
        Intersection over Union (IoU) overlap ratio [0.0, 1.0].
        - 0.0 for disjoint
        - 1.0 for identical
        - area_small / area_large for perfectly nested
    """
    if "transform" not in meta_a or "transform" not in meta_b:
        return 1.0
        
    t_a = meta_a["transform"]
    t_b = meta_b["transform"]
    
    if t_a is None or t_b is None:
        return 1.0

    if len(t_a) == 6:
        # rasterio transform tuple: (a, b, c, d, e, f)
        # a = pixel width, b = row rotation, c = top left x
        # d = col rotation, e = pixel height, f = top left y
        a_a, a_b, a_c, a_d, a_e, a_f = t_a
        width_a, height_a = meta_a.get("samples", 0), meta_a.get("lines", 0)
        
        b_a, b_b, b_c, b_d, b_e, b_f = t_b
        width_b, height_b = meta_b.get("samples", 0), meta_b.get("lines", 0)
    else:
        return 1.0
        
    # Calculate bounds for A
    min_x_a = min(a_c, a_c + a_a * width_a)
    max_x_a = max(a_c, a_c + a_a * width_a)
    min_y_a = min(a_f, a_f + a_e * height_a)
    max_y_a = max(a_f, a_f + a_e * height_a)
    
    # Calculate bounds for B
    min_x_b = min(b_c, b_c + b_a * width_b)
    max_x_b = max(b_c, b_c + b_a * width_b)
    min_y_b = min(b_f, b_f + b_e * height_b)
    max_y_b = max(b_f, b_f + b_e * height_b)
    
    box_a = box(min_x_a, min_y_a, max_x_a, max_y_a)
    box_b = box(min_x_b, min_y_b, max_x_b, max_y_b)
    
    area_a = box_a.area
    area_b = box_b.area
    
    if area_a == 0 or area_b == 0:
        return 0.0
        
    intersection = box_a.intersection(box_b).area
    union = area_a + area_b - intersection
    
    if union == 0:
        return 0.0
        
    # Handle the perfectly nested case natively via standard IoU? 
    # The spec says "nested -> area_small / area_large". 
    # But IoU is area(intersection) / area(union).
    # If nested, intersection = area_small, union = area_large. 
    # So IoU naturally produces area_small / area_large!
    iou = intersection / union
    
    return float(np.clip(iou, 0.0, 1.0))

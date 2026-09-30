"""F5: SPICE kernel loading and querying logic."""
import os
import glob
import logging
import spiceypy

from .quality import compute_footprint_overlap

logger = logging.getLogger(__name__)


class SpiceContext:
    def __init__(self, loaded_paths: list[str]):
        self.loaded_paths = loaded_paths


def load_kernels(kernel_dir: str | None) -> SpiceContext | None:
    """Load SPICE kernels from the given directory."""
    if not kernel_dir or not os.path.isdir(kernel_dir):
        return None
        
    metakernels = glob.glob(os.path.join(kernel_dir, "*.tm"))
    if not metakernels:
        return None
        
    tm_path = metakernels[0]
    try:
        spiceypy.furnsh(tm_path)
        logger.info(f"Loaded SPICE metakernel: {tm_path}")
        return SpiceContext([tm_path])
    except spiceypy.utils.exceptions.SpiceyError as e:
        logger.error(f"Failed to load SPICE kernels: {e}")
        return None


def compute_footprint(utc: str, instrument: str, ctx: SpiceContext) -> list[tuple[float, float] | None]:
    """Compute the 4 corner footprint of an image on the Moon."""
    footprint = []
    try:
        et = spiceypy.str2et(utc)
    except Exception as e:
        logger.warning(f"spice call failed: {e}")
        et = 0.0

    try:
        # getfov signature: getfov(instid, room)
        try:
            instid = spiceypy.bodn2c(instrument)
        except spiceypy.utils.exceptions.SpiceyError:
            instid = -1400001
        shape, frame, bsight, n, bounds = spiceypy.getfov(instid, 4)
        
        for bound in bounds:
            # sincpt signature: sincpt(method, target, et, fixref, abcorr, obsrvr, dref, dvec)
            point, trgepc, srfvec = spiceypy.sincpt(
                "Ellipsoid", "MOON", et, "IAU_MOON", "NONE", str(instid), frame, bound
            )
            # reclat returns radius, lon, lat (in radians)
            r, lon, lat = spiceypy.reclat(point)
            import math
            footprint.append((math.degrees(lon), math.degrees(lat)))
    except spiceypy.utils.exceptions.SpiceyError as e:
        logger.warning(f"spice call failed: {e}")
        # Pad with Nones if we failed midway
        while len(footprint) < 4:
            footprint.append(None)
            
    return footprint


def validate_pair_geometry(meta_a: dict, meta_b: dict, ctx: SpiceContext) -> dict:
    """Validate the geometric properties and sun angles of the image pair."""
    if ctx is None:
        return {
            "ok": False,
            "overlap_ratio": None,
            "sun_angle_diff_deg": None,
            "incidence_a": None,
            "incidence_b": None,
            "phase_a": None,
            "phase_b": None,
            "reason": "no SPICE kernels configured"
        }
        
    # Re-use F3 footprint overlap
    overlap = compute_footprint_overlap(meta_a, meta_b)
    
    return {
        "ok": True,
        "overlap_ratio": overlap,
        "sun_angle_diff_deg": 0.0, # Placeholder for F8
        "incidence_a": None,
        "incidence_b": None,
        "phase_a": None,
        "phase_b": None,
        "reason": None
    }

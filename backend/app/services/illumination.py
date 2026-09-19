import math
from typing import Dict, Any, Optional

def compute_illumination(meta: Dict[str, Any], spice_ctx: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """
    F8: Sun-angle / illumination computation.
    
    If spice_ctx is provided, uses SPICE ilumin to compute incidence, emission, and phase.
    Approximates solar_elevation_deg = 90 - incidence_deg (flat surface assumption).
    Otherwise, falls back to PDS metadata.
    """
    if spice_ctx is not None:
        try:
            import spiceypy
            utc_time = meta.get("time_utc", "2020-07-01T00:32:51Z")
            et = spiceypy.str2et(utc_time)
            
            target = 'MOON'
            obs = -1400000
            frame = 'IAU_MOON'
            
            # 1. Get FOV and boresight
            shape, name, bsight, n, bounds = spiceypy.getfov(obs, 4)
            
            # 2. Get surface intersection (centroid)
            point, trgepc, srfvec = spiceypy.sincpt('Ellipsoid', target, et, frame, 'NONE', str(obs), frame, bsight)
            
            # 3. Compute illumination angles at the centroid
            trgepc, srfvec, phase, incdnc, emissn = spiceypy.ilumin(
                "Ellipsoid", target, et, frame, 'NONE', str(obs), point
            )
            
            incidence_deg = math.degrees(incdnc)
            emission_deg = math.degrees(emissn)
            phase_deg = math.degrees(phase)
            
            # For a flat surface, elevation = 90 - incidence
            solar_elevation_deg = 90.0 - incidence_deg
            
            # azimuth derivation is skipped for now
            solar_azimuth_deg = None
            
            return {
                "incidence_deg": incidence_deg,
                "emission_deg": emission_deg,
                "phase_deg": phase_deg,
                "solar_elevation_deg": solar_elevation_deg,
                "solar_azimuth_deg": solar_azimuth_deg,
                "source": "spice",
                "reason": None
            }
        except Exception as e:
            return {
                "incidence_deg": None,
                "emission_deg": None,
                "phase_deg": None,
                "solar_elevation_deg": None,
                "solar_azimuth_deg": None,
                "source": "spice",
                "reason": f"SPICE ilumin failed: {e}"
            }
    
    # Fallback to PDS
    elev = meta.get("solar_elevation_deg")
    azim = meta.get("solar_azimuth_deg")
    
    if elev is None and azim is None:
        return {
            "incidence_deg": None,
            "emission_deg": None,
            "phase_deg": None,
            "solar_elevation_deg": None,
            "solar_azimuth_deg": None,
            "source": "pds",
            "reason": "PDS solar fields absent"
        }
        
    return {
        "incidence_deg": None,
        "emission_deg": None,
        "phase_deg": None,
        "solar_elevation_deg": elev,
        "solar_azimuth_deg": azim,
        "source": "pds",
        "reason": None
    }


def pair_sun_angle_ok(meta_a: Dict[str, Any], meta_b: Dict[str, Any], spice_ctx: Optional[Dict[str, Any]], max_diff_deg: float = 20.0) -> bool:
    """
    Computes illumination for both images. Returns True if both have a non-None solar_elevation_deg,
    AND their absolute difference is <= max_diff_deg.
    Otherwise returns False.
    """
    illum_a = compute_illumination(meta_a, spice_ctx)
    illum_b = compute_illumination(meta_b, spice_ctx)
    
    elev_a = illum_a.get("solar_elevation_deg")
    elev_b = illum_b.get("solar_elevation_deg")
    
    if elev_a is None or elev_b is None:
        return False
        
    return abs(elev_a - elev_b) <= max_diff_deg

"""Bootstrap the 1024x1024 demo fixture and DEM fixtures for R6 timing measurements and F10 shadow masking.

Upscales the canonical 640x640 demo pair A to 1024x1024 using INTER_CUBIC.
Produces:
  - tests/fixtures/demo_b1a1_1024_ref.png (+ .aux.xml)
  - tests/fixtures/demo_b1a1_1024_mov.png (+ .aux.xml)
  - tests/fixtures/demo_b1a1_1024_dem.tif
  - tests/fixtures/pair_a_ref_dem.tif (and data/examples/pair_a_ref_dem.tif)
"""
import sys
import json
from pathlib import Path

import cv2
import numpy as np
import rasterio
from rasterio.transform import Affine
from rasterio.crs import CRS

# Ensure the app module is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.simulation.scenario_generator import generate_lunar_crater_surface, apply_controlled_variation


def generate_gaussian_dem(shape: tuple, seed: int = 26166, base_elevation: float = 2500.0) -> np.ndarray:
    """Generate a synthetic Gaussian crater field DEM in uint16 range [0, 5000] meters."""
    height, width = shape
    dem = np.full((height, width), base_elevation, dtype=np.float32)
    rng = np.random.default_rng(seed)
    num_craters = int(rng.integers(5, 11))
    y_indices, x_indices = np.indices((height, width))

    for _ in range(num_craters):
        cx = rng.uniform(0, width)
        cy = rng.uniform(0, height)
        r = rng.uniform(30, 150)
        depth = rng.uniform(100, 500)
        dist_sq = (x_indices - cx) ** 2 + (y_indices - cy) ** 2
        crater_profile = depth * np.exp(-dist_sq / (0.5 * r ** 2))
        dem -= crater_profile

    return np.clip(dem, 1, 5000).astype(np.uint16)


def main():
    backend_dir = Path(__file__).resolve().parent.parent
    fixtures_dir = Path(__file__).resolve().parent / "fixtures"
    fixtures_dir.mkdir(parents=True, exist_ok=True)
    examples_dir = backend_dir / "data" / "examples"
    examples_dir.mkdir(parents=True, exist_ok=True)

    ref_path = fixtures_dir / "demo_b1a1_1024_ref.png"
    mov_path = fixtures_dir / "demo_b1a1_1024_mov.png"

    # Generate the canonical 640x640 pair (same as image_service seed 26166)
    ref_640 = generate_lunar_crater_surface(width=640, height=640, sun_azimuth_deg=45.0, seed=26166)
    mov_640, _ = apply_controlled_variation(
        ref_640, scale=1.03, rotation_deg=3.5, tx_px=14.0, ty_px=-10.0,
        contrast_factor=1.08, brightness_offset=-5.0, seed=26166,
    )

    # Upscale to 1024x1024 via INTER_CUBIC
    ref_1024 = cv2.resize(ref_640, (1024, 1024), interpolation=cv2.INTER_CUBIC)
    mov_1024 = cv2.resize(mov_640, (1024, 1024), interpolation=cv2.INTER_CUBIC)

    cv2.imwrite(str(ref_path), ref_1024)
    cv2.imwrite(str(mov_path), mov_1024)

    # GeoTransform and CRS (Lunar Polar Stereographic)
    transform_1024 = Affine(30.0, 0.0, -1000000.0, 0.0, -30.0, 1000000.0)
    transform_640 = Affine(30.0, 0.0, -1000000.0, 0.0, -30.0, 1000000.0)
    crs_wkt = (
        'PROJCS["unknown",GEOGCS["unknown",DATUM["unknown",SPHEROID["unknown",1737400,0]],'
        'PRIMEM["Reference meridian",0],UNIT["degree",0.0174532925199433,AUTHORITY["EPSG","9122"]]],'
        'PROJECTION["Polar_Stereographic"],PARAMETER["latitude_of_origin",-90],'
        'PARAMETER["central_meridian",0],PARAMETER["false_easting",0],PARAMETER["false_northing",0],'
        'UNIT["metre",1],AXIS["Easting",NORTH],AXIS["Northing",NORTH]]'
    )
    crs = CRS.from_wkt(crs_wkt)

    # Write PAM aux.xml files so rasterio can open PNGs with CRS and geotransform
    pam_xml_1024 = f"""<PAMDataset>
  <SRS dataAxisToSRSAxisMapping="1,2">{crs_wkt}</SRS>
  <GeoTransform>-1000000.0, 30.0, 0.0, 1000000.0, 0.0, -30.0</GeoTransform>
</PAMDataset>"""
    (fixtures_dir / "demo_b1a1_1024_ref.png.aux.xml").write_text(pam_xml_1024, encoding="utf-8")
    (fixtures_dir / "demo_b1a1_1024_mov.png.aux.xml").write_text(pam_xml_1024, encoding="utf-8")

    # ---------------------------------------------------------
    # 1. 1024x1024 DEM Generation (F10)
    # ---------------------------------------------------------
    dem_1024 = generate_gaussian_dem((1024, 1024), seed=26166, base_elevation=2500.0)
    dem_1024_path = fixtures_dir / "demo_b1a1_1024_dem.tif"

    with rasterio.open(
        dem_1024_path, "w", driver="GTiff",
        height=dem_1024.shape[0], width=dem_1024.shape[1],
        count=1, dtype=dem_1024.dtype, crs=crs,
        transform=transform_1024, nodata=0
    ) as dst:
        dst.write(dem_1024, 1)

    # Also write demo_b1a1_1024_ref_dem.tif for direct stem lookup
    with rasterio.open(
        fixtures_dir / "demo_b1a1_1024_ref_dem.tif", "w", driver="GTiff",
        height=dem_1024.shape[0], width=dem_1024.shape[1],
        count=1, dtype=dem_1024.dtype, crs=crs,
        transform=transform_1024, nodata=0
    ) as dst:
        dst.write(dem_1024, 1)

    # ---------------------------------------------------------
    # 2. 640x640 DEM Generation for Demo Pair A
    # ---------------------------------------------------------
    dem_640 = generate_gaussian_dem((640, 640), seed=26166, base_elevation=2500.0)
    for target_dir in [fixtures_dir, examples_dir]:
        for fname in ["pair_a_ref_dem.tif", "pair_a_dem.tif", "demo_pair_a_ref_dem.tif"]:
            with rasterio.open(
                target_dir / fname, "w", driver="GTiff",
                height=dem_640.shape[0], width=dem_640.shape[1],
                count=1, dtype=dem_640.dtype, crs=crs,
                transform=transform_640, nodata=0
            ) as dst:
                dst.write(dem_640, 1)
    # Self-check assertion required by F10 specification:
    with rasterio.open(ref_path) as ref_ds, rasterio.open(dem_1024_path) as dem_ds:
        assert ref_ds.shape == dem_ds.shape, f"Shape mismatch: {ref_ds.shape} != {dem_ds.shape}"
        assert ref_ds.transform == dem_ds.transform, f"Transform mismatch: {ref_ds.transform} != {dem_ds.transform}"
        assert ref_ds.crs == dem_ds.crs, f"CRS mismatch: {ref_ds.crs} != {dem_ds.crs}"

    # Write metadata sidecar
    meta = {
        "source": "canonical demo pair A (seed 26166), upscaled 640->1024 via INTER_CUBIC",
        "purpose": "R6 timing benchmark fixture at 1024x1024",
        "ref_shape": list(ref_1024.shape),
        "mov_shape": list(mov_1024.shape),
        "dem_fixture": "demo_b1a1_1024_dem.tif",
        "dem_seed": 26166,
        "dem_range_m": [1, 5000],
    }
    (fixtures_dir / "demo_b1a1_1024.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")

    print(f"ref: {ref_path}  shape={ref_1024.shape}")
    print(f"mov: {mov_path}  shape={mov_1024.shape}")
    print(f"dem: {dem_1024_path}  shape={dem_1024.shape}")
    print("DEM self-check assertions: PASS")
    print("Fixture bootstrap complete.")


if __name__ == "__main__":
    main()

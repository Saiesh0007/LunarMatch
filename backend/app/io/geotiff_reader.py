import json
from pathlib import Path

import numpy as np
from PIL import Image

from .pds_reader import read_pds4_label


def read_geotiff_metadata(path: str) -> dict:
    """Read CRS, affine transform, dimensions, and GSD from a raster.

    Args:
        path: GeoTIFF or IMG path.
    Returns:
        Normalized raster metadata.
    Raises:
        FileNotFoundError: If the raster does not exist.
        ImportError: If rasterio is unavailable for this format.
    """
    raster_path = Path(path)
    if not raster_path.exists():
        raise FileNotFoundError(path)
    try:
        import rasterio
    except ImportError as exc:
        raise ImportError("rasterio is required to read GeoTIFF metadata") from exc
    with rasterio.open(raster_path) as dataset:
        transform = dataset.transform
        return {
            "crs": dataset.crs.to_string() if dataset.crs else None,
            "transform": (transform.a, transform.b, transform.c, transform.d, transform.e, transform.f),
            "gsd_meters": float(abs(transform.a)) if dataset.crs else float("nan"),
            "lines": dataset.height,
            "samples": dataset.width,
            "sensor_hint": _sensor_from_filename(raster_path.name),
        }


def _sensor_from_filename(filename: str) -> str | None:
    name = filename.upper()
    for token in ("OHRC", "TMC2", "IIRS", "LRO_NAC", "SELENE"):
        if token in name.replace("-", "_"):
            return token
    return None


def load_lunar_image(path: str) -> tuple[np.ndarray, dict]:
    """Load PDS, GeoTIFF, IMG, or PNG imagery as normalized grayscale.

    Args:
        path: Image or PDS4 label path.
    Returns:
        Float32 grayscale image in [0, 1] and merged metadata.
    Raises:
        FileNotFoundError: If the input does not exist.
        ValueError: If the format cannot be decoded.
    """
    image_path = Path(path)
    if not image_path.exists():
        raise FileNotFoundError(path)
    suffix = image_path.suffix.lower()
    if suffix == ".xml":
        return _load_array_from_label(image_path)
    metadata = {}
    if suffix in (".tif", ".tiff", ".img"):
        import rasterio
        with rasterio.open(image_path) as dataset:
            array = dataset.read(1).astype(np.float32)
        metadata = read_geotiff_metadata(str(image_path))
    else:
        array = np.asarray(Image.open(image_path).convert("L"), dtype=np.float32)
        sidecar = image_path.with_suffix(".json")
        if sidecar.exists():
            metadata = json.loads(sidecar.read_text(encoding="utf-8"))
    minimum, maximum = float(np.nanmin(array)), float(np.nanmax(array))
    if maximum > minimum:
        array = (array - minimum) / (maximum - minimum)
    return np.nan_to_num(array).astype(np.float32), metadata


def _load_array_from_label(label_path: Path) -> tuple[np.ndarray, dict]:
    """Load an adjacent image referenced by a minimal PDS label."""
    metadata = read_pds4_label(str(label_path))
    for candidate in (label_path.with_suffix(".tif"), label_path.with_suffix(".png"), label_path.with_suffix(".img")):
        if candidate.exists():
            image, image_metadata = load_lunar_image(str(candidate))
            image_metadata.update(metadata)
            return image, image_metadata
    raise ValueError(f"No image companion found for PDS4 label: {label_path}")

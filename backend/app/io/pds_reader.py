import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Optional, Sequence, Tuple

import numpy as np


def _local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1].lower()


def _find_text(root: ET.Element, names: tuple[str, ...]) -> str | None:
    wanted = {name.lower() for name in names}
    for element in root.iter():
        if _local(element.tag) in wanted and element.text and element.text.strip():
            return element.text.strip()
    return None


def _number(value: str | None, integer: bool = False):
    if value is None:
        return None
    try:
        return int(float(value)) if integer else float(value)
    except ValueError:
        return None


def _first(*values):
    for value in values:
        if value is not None:
            return value
    return None


# Chandrayaan-2 (ISRO ISDA) instrument names as written in Observing_System_Component
_INSTRUMENT_NAMES = {
    "orbiter high resolution camera": "OHRC",
    "terrain mapping camera": "TMC-2",
    "imaging infrared spectrometer": "IIRS",
}
_LID_TOKENS = {".ohr:": "OHRC", ".tmc:": "TMC-2", ".iir:": "IIRS"}

# PDS4 Element_Array data types -> numpy dtypes
_PDS4_DTYPES = {
    "unsignedbyte": "u1", "signedbyte": "i1",
    "unsignedlsb2": "<u2", "signedlsb2": "<i2", "unsignedmsb2": ">u2", "signedmsb2": ">i2",
    "unsignedlsb4": "<u4", "signedlsb4": "<i4", "unsignedmsb4": ">u4", "signedmsb4": ">i4",
    "ieee754lsbsingle": "<f4", "ieee754msbsingle": ">f4",
    "ieee754lsbdouble": "<f8", "ieee754msbdouble": ">f8",
}


def _instrument(root: ET.Element) -> str | None:
    for component in root.iter():
        if _local(component.tag) != "observing_system_component":
            continue
        name = type_ = None
        for child in component:
            if _local(child.tag) == "name" and child.text:
                name = child.text.strip()
            elif _local(child.tag) == "type" and child.text:
                type_ = child.text.strip().lower()
        if type_ == "instrument" and name:
            return _INSTRUMENT_NAMES.get(name.lower(), name)
    lid = (_find_text(root, ("logical_identifier",)) or "").lower()
    for token, sensor in _LID_TOKENS.items():
        if token in lid:
            return sensor
    return None


def _array_spec(root: ET.Element, label_path: Path) -> dict | None:
    """Location, element type and axes of the first array in the label's File_Area_Observational."""
    for area in root.iter():
        if _local(area.tag) != "file_area_observational":
            continue
        file_name = None
        for element in area.iter():
            if _local(element.tag) == "file_name" and element.text:
                file_name = element.text.strip()
                break
        for array in area:
            if not _local(array.tag).startswith("array"):
                continue
            offset = _number(_find_text(array, ("offset",)), integer=True) or 0
            data_type = (_find_text(array, ("data_type",)) or "").lower()
            axes = []
            for axis in array:
                if _local(axis.tag) == "axis_array":
                    axes.append((
                        (_find_text(axis, ("axis_name",)) or "").lower(),
                        _number(_find_text(axis, ("elements",)), integer=True),
                        _number(_find_text(axis, ("sequence_number",)), integer=True) or len(axes) + 1,
                    ))
            axes.sort(key=lambda a: a[2])
            return {
                "file": str(label_path.with_name(file_name)) if file_name else None,
                "offset": offset,
                "data_type": data_type,
                "dtype": _PDS4_DTYPES.get(data_type),
                "axes": [(name, n) for name, n, _ in axes],
            }
    return None


def _axis_len(spec: dict | None, *names: str) -> int | None:
    if not spec:
        return None
    for name, n in spec["axes"]:
        if name in names:
            return n
    return None


def _corners(root: ET.Element) -> dict | None:
    out = {}
    for key in ("upper_left", "upper_right", "lower_left", "lower_right"):
        lat = _number(_find_text(root, (f"{key}_latitude",)))
        lon = _number(_find_text(root, (f"{key}_longitude",)))
        if lat is None or lon is None:
            return None
        out[key] = (lat, lon)
    return out


def _band_centers(root: ET.Element) -> list[float] | None:
    centers = [_number(e.text) for e in root.iter() if _local(e.tag) == "center_wavelength" and e.text]
    return centers or None


def read_pds4_label(path: str) -> dict:
    """Parse a PDS4 XML label into normalized image metadata.

    Understands both generic PDS4 field names and the ISRO ISDA mission-area
    fields of Chandrayaan-2 OHRC / TMC-2 / IIRS products (isda:sun_elevation,
    isda:pixel_resolution, corner coordinates, Axis_Array dimensions).

    Args:
        path: XML label path.
    Returns:
        Metadata including instrument, acquisition, geometry, and GSD fields,
        plus ``array`` (raw data file location/type/axes) when the label
        describes one.
    Raises:
        FileNotFoundError: If the label does not exist.
        ValueError: If the label is not well-formed XML.
    """
    label_path = Path(path)
    if not label_path.exists():
        raise FileNotFoundError(path)
    try:
        root = ET.parse(label_path).getroot()
    except ET.ParseError as exc:
        raise ValueError(f"Malformed PDS4 XML label: {path}") from exc
    spec = _array_spec(root, label_path)
    return {
        "instrument_id": _first(_find_text(root, ("instrument_id",)), _instrument(root),
                                _find_text(root, ("instrument_name",))),
        "start_time_utc": _find_text(root, ("start_date_time", "start_time_utc")),
        "stop_time_utc": _find_text(root, ("stop_date_time", "stop_time_utc")),
        "solar_elevation_deg": _number(_find_text(root, ("solar_elevation", "solar_elevation_deg", "sun_elevation"))),
        "solar_azimuth_deg": _number(_find_text(root, ("solar_azimuth", "solar_azimuth_deg", "sun_azimuth"))),
        "lines": _first(_number(_find_text(root, ("lines", "line_count")), integer=True), _axis_len(spec, "line")),
        "samples": _first(_number(_find_text(root, ("samples", "sample_count")), integer=True), _axis_len(spec, "sample")),
        "bands": _axis_len(spec, "band"),
        "gsd_meters": _number(_find_text(root, ("pixel_scale", "gsd_meters", "ground_sample_distance", "pixel_resolution"))),
        "line_exposure_ms": _number(_find_text(root, ("line_exposure_duration",))),
        "spacecraft_altitude_km": _number(_find_text(root, ("spacecraft_altitude",))),
        "attitude_deg": {k: _number(_find_text(root, (k,))) for k in ("roll", "pitch", "yaw")},
        "projection": _find_text(root, ("projection",)),
        "area": _find_text(root, ("area",)),
        "corners": _corners(root),
        "band_centers_nm": _band_centers(root),
        "array": spec,
    }


def read_pds4_array(
    label_path: str,
    band: Optional[int | Sequence[int]] = None,
    rows: Optional[Tuple[int, int]] = None,
    step: int = 1,
) -> np.ndarray:
    """Read the raw array a PDS4 label describes, without loading the whole file.

    Args:
        label_path: PDS4 XML label (its File_Area_Observational names the data file).
        band: for 3-D cubes, a 0-based band index or a list of indices (averaged).
              Defaults to the mean of all bands.
        rows: optional ``(start, stop)`` line window, in full-resolution lines.
        step: keep every ``step``-th line and sample (cheap decimation for previews).
    Returns:
        2-D array (lines x samples) in the file's native dtype for a single band,
        float32 when several bands are averaged.
    Raises:
        ValueError: If the label has no readable array.
    """
    meta = read_pds4_label(label_path)
    spec = meta.get("array")
    if not spec or not spec.get("dtype") or not spec.get("file"):
        raise ValueError(f"PDS4 label describes no readable array: {label_path}")
    shape = tuple(n for _, n in spec["axes"])
    data = np.memmap(spec["file"], dtype=np.dtype(spec["dtype"]), mode="r", offset=spec["offset"], shape=shape)
    names = [name for name, _ in spec["axes"]]
    r0, r1 = rows if rows else (0, None)
    if len(shape) == 2:
        return np.asarray(data[r0:r1:step, ::step])
    if len(shape) != 3:
        raise ValueError(f"Unsupported array rank {len(shape)} in {label_path}")
    band_axis = names.index("band") if "band" in names else 0
    cube = np.moveaxis(data, band_axis, 0)  # bands first; remaining axes keep line, sample order
    if band is None:
        band = range(shape[band_axis])
    if isinstance(band, (int, np.integer)):
        return np.asarray(cube[int(band), r0:r1:step, ::step])
    acc = None
    for b in band:
        plane = np.asarray(cube[int(b), r0:r1:step, ::step], dtype=np.float32)
        acc = plane if acc is None else acc + plane
    return acc / float(len(band))

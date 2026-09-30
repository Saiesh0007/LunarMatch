import xml.etree.ElementTree as ET
from pathlib import Path


def _local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1].lower()


def _find_text(root: ET.Element, names: tuple[str, ...]) -> str | None:
    wanted = {name.lower() for name in names}
    for element in root.iter():
        if _local(element.tag) in wanted and element.text:
            return element.text.strip()
    return None


def _number(value: str | None, integer: bool = False):
    if value is None:
        return None
    try:
        return int(float(value)) if integer else float(value)
    except ValueError:
        return None


def read_pds4_label(path: str) -> dict:
    """Parse a PDS4 XML label into normalized image metadata.

    Args:
        path: XML label path.
    Returns:
        Metadata including instrument, acquisition, geometry, and GSD fields.
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
    return {
        "instrument_id": _find_text(root, ("instrument_id", "instrument_name")),
        "start_time_utc": _find_text(root, ("start_date_time", "start_time_utc")),
        "solar_elevation_deg": _number(_find_text(root, ("solar_elevation", "solar_elevation_deg"))),
        "solar_azimuth_deg": _number(_find_text(root, ("solar_azimuth", "solar_azimuth_deg"))),
        "lines": _number(_find_text(root, ("lines", "line_count")), integer=True),
        "samples": _number(_find_text(root, ("samples", "sample_count")), integer=True),
        "gsd_meters": _number(_find_text(root, ("pixel_scale", "gsd_meters", "ground_sample_distance"))),
    }

import pytest

from app.io.pds_reader import read_pds4_label


LABEL = """<Product_Observational xmlns='urn:test'><Observation_Area><Time_Coordinates><Start_Date_Time>2024-01-02T03:04:05Z</Start_Date_Time></Time_Coordinates><Mission_Area><Instrument_Id>OHRC</Instrument_Id><Solar_Elevation>42.5</Solar_Elevation><Solar_Azimuth>120.0</Solar_Azimuth></Mission_Area><File_Area_Observational><Array_2D_Image><Lines>12</Lines><Samples>20</Samples><Pixel_Scale>5.0</Pixel_Scale></Array_2D_Image></File_Area_Observational></Observation_Area></Product_Observational>"""


def test_parse_synthetic_ohrc_label(tmp_path):
    path = tmp_path / "ohrc.xml"
    path.write_text(LABEL, encoding="utf-8")
    metadata = read_pds4_label(str(path))
    assert metadata["instrument_id"] == "OHRC"
    assert metadata["lines"] == 12
    assert metadata["gsd_meters"] == 5.0


def test_parse_tmc_solar_elevation(tmp_path):
    path = tmp_path / "tmc.xml"
    path.write_text(LABEL.replace("OHRC", "TMC-2").replace("42.5", "17.5"), encoding="utf-8")
    metadata = read_pds4_label(str(path))
    assert metadata["instrument_id"] == "TMC-2"
    assert metadata["solar_elevation_deg"] == 17.5


def test_missing_optional_fields(tmp_path):
    path = tmp_path / "minimal.xml"
    path.write_text("<Product_Observational><Instrument_Id>IIRS</Instrument_Id></Product_Observational>", encoding="utf-8")
    metadata = read_pds4_label(str(path))
    assert metadata["instrument_id"] == "IIRS"
    assert metadata["solar_azimuth_deg"] is None


def test_malformed_xml(tmp_path):
    path = tmp_path / "bad.xml"
    path.write_text("<Product_Observational>", encoding="utf-8")
    with pytest.raises(ValueError, match="Malformed PDS4"):
        read_pds4_label(str(path))

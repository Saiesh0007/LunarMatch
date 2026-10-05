import numpy as np
import pytest

from app.io.pds_reader import read_pds4_array, read_pds4_label
from app.services.router import detect_sensor


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


ISDA_LABEL = """<?xml version="1.0" encoding="UTF-8"?>
<Product_Observational xmlns="http://pds.nasa.gov/pds4/pds/v1" xmlns:isda="https://isda.issdc.gov.in/pds4/isda/v1">
  <Identification_Area><logical_identifier>urn:isro:isda:ch2_cho.tmc:data_raw:test</logical_identifier></Identification_Area>
  <Observation_Area>
    <Time_Coordinates><start_date_time>2020-01-09T07:33:07.2590Z</start_date_time><stop_date_time>2020-01-09T07:42:59.1279Z</stop_date_time></Time_Coordinates>
    <Observing_System><Observing_System_Component><name>Chandrayaan 2 Orbiter</name><type>Spacecraft</type></Observing_System_Component>
      <Observing_System_Component><name>terrain mapping camera</name><type>Instrument</type></Observing_System_Component></Observing_System>
    <Mission_Area><isda:Product_Parameters>
      <isda:pixel_resolution unit="m/pixel">4.90</isda:pixel_resolution>
      <isda:sun_azimuth unit="deg">60.179619</isda:sun_azimuth>
      <isda:sun_elevation unit="deg">72.471309</isda:sun_elevation>
      <isda:projection>Selenographic</isda:projection>
      <isda:upper_left_latitude unit="deg">-23.4</isda:upper_left_latitude><isda:upper_left_longitude unit="deg">1.2</isda:upper_left_longitude>
      <isda:upper_right_latitude unit="deg">-23.4</isda:upper_right_latitude><isda:upper_right_longitude unit="deg">0.4</isda:upper_right_longitude>
      <isda:lower_left_latitude unit="deg">6.7</isda:lower_left_latitude><isda:lower_left_longitude unit="deg">1.2</isda:lower_left_longitude>
      <isda:lower_right_latitude unit="deg">6.7</isda:lower_right_latitude><isda:lower_right_longitude unit="deg">0.5</isda:lower_right_longitude>
    </isda:Product_Parameters></Mission_Area>
  </Observation_Area>
  <File_Area_Observational>
    <File><file_name>DATAFILE</file_name></File>
    ARRAY
  </File_Area_Observational>
</Product_Observational>"""

ARRAY_2D = """<Array_2D_Image><offset unit="byte">0</offset><axes>2</axes>
      <Element_Array><data_type>UnsignedLSB2</data_type></Element_Array>
      <Axis_Array><axis_name>Line</axis_name><elements>6</elements><sequence_number>1</sequence_number></Axis_Array>
      <Axis_Array><axis_name>Sample</axis_name><elements>4</elements><sequence_number>2</sequence_number></Axis_Array></Array_2D_Image>"""

ARRAY_3D = """<Array_3D_Spectrum><offset unit="byte">0</offset><axes>3</axes>
      <Element_Array><data_type>UnsignedLSB2</data_type></Element_Array>
      <Axis_Array><axis_name>BAND</axis_name><elements>3</elements><sequence_number>1</sequence_number>
        <Band_Bin_Set><Band_Bin><center_wavelength unit="nm">712.3</center_wavelength></Band_Bin></Band_Bin_Set></Axis_Array>
      <Axis_Array><axis_name>LINE</axis_name><elements>6</elements><sequence_number>2</sequence_number></Axis_Array>
      <Axis_Array><axis_name>SAMPLE</axis_name><elements>4</elements><sequence_number>3</sequence_number></Axis_Array></Array_3D_Spectrum>"""


def _write_isda(tmp_path, array_xml, data):
    data.astype("<u2").tofile(tmp_path / "raw.img")
    label = tmp_path / "raw.xml"
    label.write_text(ISDA_LABEL.replace("DATAFILE", "raw.img").replace("ARRAY", array_xml), encoding="utf-8")
    return label


def test_parse_chandrayaan2_isda_label(tmp_path):
    label = _write_isda(tmp_path, ARRAY_2D, np.arange(24).reshape(6, 4))
    metadata = read_pds4_label(str(label))
    assert metadata["instrument_id"] == "TMC-2"
    assert metadata["gsd_meters"] == 4.9
    assert metadata["solar_elevation_deg"] == pytest.approx(72.471309)
    assert metadata["solar_azimuth_deg"] == pytest.approx(60.179619)
    assert (metadata["lines"], metadata["samples"]) == (6, 4)
    assert metadata["corners"]["lower_right"] == (6.7, 0.5)
    assert detect_sensor(metadata) == "TMC2"


def test_read_raw_2d_image_window(tmp_path):
    data = np.arange(24).reshape(6, 4)
    label = _write_isda(tmp_path, ARRAY_2D, data)
    np.testing.assert_array_equal(read_pds4_array(str(label)), data)
    np.testing.assert_array_equal(read_pds4_array(str(label), rows=(2, 6), step=2), data[2:6:2, ::2])


def test_read_raw_bsq_cube_band_and_mean(tmp_path):
    cube = np.arange(72).reshape(3, 6, 4)
    label = _write_isda(tmp_path, ARRAY_3D, cube)
    assert read_pds4_label(str(label))["bands"] == 3
    np.testing.assert_array_equal(read_pds4_array(str(label), band=1), cube[1])
    np.testing.assert_allclose(read_pds4_array(str(label), band=[0, 2]), cube[[0, 2]].mean(axis=0))

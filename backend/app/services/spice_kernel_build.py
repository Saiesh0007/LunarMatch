"""F6: SPICE kernel synthesis logic."""
import os
import spiceypy
import numpy as np


def build_ik(camera_params: dict, out_path: str) -> str:
    """Build a text IK (Instrument Kernel)."""
    fov_x = camera_params.get("fov_x_rad", 0.005) if camera_params else 0.005
    fov_y = camera_params.get("fov_y_rad", 0.005) if camera_params else 0.005
    
    lon = camera_params.get("lon", 0.0) if camera_params else 0.0
    lat = camera_params.get("lat", 0.0) if camera_params else 0.0
    lon_rad = np.radians(lon)
    lat_rad = np.radians(lat)
    
    bx = -np.cos(lat_rad) * np.cos(lon_rad)
    by = -np.cos(lat_rad) * np.sin(lon_rad)
    bz = -np.sin(lat_rad)
    
    dot = bz
    rx = -dot * bx
    ry = -dot * by
    rz = 1.0 - dot * bz
    mag = np.sqrt(rx*rx + ry*ry + rz*rz)
    if mag < 1e-6:
        rx, ry, rz = 1.0, 0.0, 0.0
    else:
        rx, ry, rz = rx/mag, ry/mag, rz/mag
    
    # Using INS-1400000 and INS-1400001 (OHRC SYNTHETIC)
    ik_content = f"""KPL/IK

\\begindata

   INS-1400000_FOCAL_LENGTH = ( {camera_params.get('focal_length', 1.0)} )
   INS-1400000_PIXEL_SIZE   = ( {camera_params.get('pixel_size', 30e-6)} )
   INS-1400000_PIXEL_SAMPLES= ( {camera_params.get('samples', 1024)} )
   INS-1400000_PIXEL_LINES  = ( {camera_params.get('lines', 1024)} )
   
   INS-1400000_FOV_FRAME    = 'OHRC_SYNTHETIC'
   INS-1400000_FOV_SHAPE    = 'RECTANGLE'
   INS-1400000_BORESIGHT    = ( {bx:.6f}, {by:.6f}, {bz:.6f} )
   
   INS-1400000_FOV_CLASS_SPEC = 'ANGLES'
   INS-1400000_FOV_REF_VECTOR = ( {rx:.6f}, {ry:.6f}, {rz:.6f} )
   INS-1400000_FOV_REF_ANGLE  = ( {fov_y} )
   INS-1400000_FOV_CROSS_ANGLE= ( {fov_x} )
   INS-1400000_FOV_ANGLE_UNITS= 'RADIANS'

   INS-1400001_FOCAL_LENGTH = ( {camera_params.get('focal_length', 1.0)} )
   INS-1400001_PIXEL_SIZE   = ( {camera_params.get('pixel_size', 30e-6)} )
   INS-1400001_PIXEL_SAMPLES= ( {camera_params.get('samples', 1024)} )
   INS-1400001_PIXEL_LINES  = ( {camera_params.get('lines', 1024)} )
   
   INS-1400001_FOV_FRAME    = 'OHRC_SYNTHETIC'
   INS-1400001_FOV_SHAPE    = 'RECTANGLE'
   INS-1400001_BORESIGHT    = ( {bx:.6f}, {by:.6f}, {bz:.6f} )
   
   INS-1400001_FOV_CLASS_SPEC = 'ANGLES'
   INS-1400001_FOV_REF_VECTOR = ( {rx:.6f}, {ry:.6f}, {rz:.6f} )
   INS-1400001_FOV_REF_ANGLE  = ( {fov_y} )
   INS-1400001_FOV_CROSS_ANGLE= ( {fov_x} )
   INS-1400001_FOV_ANGLE_UNITS= 'RADIANS'

\\begintext
"""
    with open(out_path, "w") as f:
        f.write(ik_content)
    return out_path


def build_fk(offsets: dict, out_path: str) -> str:
    """Build a text FK (Frames Kernel)."""
    lon = offsets.get("lon", 0.0)
    lat = offsets.get("lat", 0.0)
    
    fk_text = f"""KPL/FK
    
    \\begindata
        FRAME_OHRC_SYNTHETIC = -1400000
        FRAME_-1400000_NAME = 'OHRC_SYNTHETIC'
        FRAME_-1400000_CLASS = 4
        FRAME_-1400000_CLASS_ID = -1400000
        FRAME_-1400000_CENTER = 301
        
        TKFRAME_-1400000_RELATIVE = 'IAU_MOON'
        TKFRAME_-1400000_SPEC = 'ANGLES'
        TKFRAME_-1400000_UNITS = 'DEGREES'
        TKFRAME_-1400000_AXES = ( 1, 2, 3 )
        TKFRAME_-1400000_ANGLES = ( 0.0, 0.0, 0.0 )
        
        NAIF_BODY_NAME += ( 'OHRC_SYNTHETIC', 'OHRC_INSTRUMENT' )
        NAIF_BODY_CODE += ( -1400000, -1400001 )
        
        BODY301_RADII = ( 1737.4, 1737.4, 1737.4 )
        BODY301_POLE_RA = ( 269.9949, 0.0, 0.0 )
        BODY301_POLE_DEC = ( 66.5392, 0.0, 0.0 )
        BODY301_PM = ( 38.3213, 13.17635815, 0.0 )
    \\begintext
    """
    with open(out_path, 'w') as f:
        f.write(fk_text)
    return out_path


def build_spk(ephemeris: list[dict], out_path: str) -> str:
    """Build a binary SPK (Type 9) using spiceypy."""
    handle = spiceypy.spkopn(out_path, 'OHRC_SPK', 0)
    
    # Type 9 requires states and epochs.
    if ephemeris and len(ephemeris) >= 2:
        state1 = [ephemeris[0].get('x', 1837.4), ephemeris[0].get('y', 0.0), ephemeris[0].get('z', 0.0),
                  ephemeris[0].get('vx', 0.0), ephemeris[0].get('vy', 1.6), ephemeris[0].get('vz', 0.0)]
        state2 = [ephemeris[1].get('x', 1837.4), ephemeris[1].get('y', 0.0), ephemeris[1].get('z', 0.0),
                  ephemeris[1].get('vx', 0.0), ephemeris[1].get('vy', 1.6), ephemeris[1].get('vz', 0.0)]
    else:
        state1 = [1837.4, 0.0, 0.0, 0.0, 1.6, 0.0]
        state2 = [1837.4, 0.0, 0.0, 0.0, 1.6, 0.0]
    cdata = np.array([state1, state2], dtype=np.float64)
    epochs = [-1e9, 2e9]
    
    spiceypy.spkw09(
        handle=handle,
        body=-1400000,
        center=301,
        inframe='IAU_MOON',
        first=-1e9,
        last=2e9,
        segid='OHRC_SYNTHETIC',
        degree=1,
        n=2,
        states=cdata.tolist(),
        epochs=epochs
    )

    spiceypy.spkw09(
        handle=handle,
        body=-1400001,
        center=301,
        inframe='IAU_MOON',
        first=-1e9,
        last=2e9,
        segid='OHRC_INSTRUMENT',
        degree=1,
        n=2,
        states=cdata.tolist(),
        epochs=epochs
    )
    
    # Fake MOON relative to SSB for SPKSSB resolution
    spiceypy.spkw09(
        handle=handle,
        body=301,
        center=0,
        inframe='J2000',
        first=-1e9,
        last=2e9,
        segid='MOON_FAKE',
        degree=1,
        n=2,
        states=[[0.0, 0.0, 0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]],
        epochs=epochs
    )
    
    # Fake SUN relative to SSB for illumination
    spiceypy.spkw09(
        handle=handle,
        body=10,
        center=0,
        inframe='J2000',
        first=-1e9,
        last=2e9,
        segid='SUN_FAKE',
        degree=1,
        n=2,
        states=[[1.495978707e8, 1e7, 1e7, 0.0, 0.0, 0.0], [1.495978707e8, 1e7, 1e7, 0.0, 0.0, 0.0]],
        epochs=epochs
    )
    
    spiceypy.spkcls(handle)
    return out_path


def build_ck(orientations: list[dict], out_path: str) -> str:
    """Build a binary CK (Type 3) using spiceypy."""
    handle = spiceypy.ckopn(out_path, 'OHRC_CK', 0)
    
    sclkdp = [0.0, 60.0]
    quats = [[1.0, 0.0, 0.0, 0.0], [1.0, 0.0, 0.0, 0.0]]
    avvs = [[0.0, 0.0, 0.0], [0.0, 0.0, 0.0]]
    starts = [0.0]
    
    spiceypy.ckw03(
        handle=handle,
        begtim=0.0,
        endtim=120.0,
        inst=-1400000,
        ref='IAU_MOON',
        avflag=True,
        segid='OHRC_SYNTHETIC',
        nrec=2,
        sclkdp=sclkdp,
        quats=quats,
        avvs=avvs,
        nints=1,
        starts=starts
    )
    spiceypy.ckcls(handle)
    return out_path


def build_lsk(out_path: str) -> str:
    """Build a text LSK (Leapseconds Kernel)."""
    lsk_content = """KPL/LSK

\\begindata

   DELTET/DELTA_T_A       =   32.184
   DELTET/K               =    1.657E-3
   DELTET/EB              =    1.671E-2
   DELTET/M               = (  6.239996 1.99096871E-7 )
   DELTET/DELTA_AT        = ( 10,   @1972-JAN-1
                              11,   @1972-JUL-1
                              12,   @1973-JAN-1
                              13,   @1974-JAN-1
                              14,   @1975-JAN-1
                              15,   @1976-JAN-1
                              16,   @1977-JAN-1
                              17,   @1978-JAN-1
                              18,   @1979-JAN-1
                              19,   @1980-JAN-1
                              20,   @1981-JUL-1
                              21,   @1982-JUL-1
                              22,   @1983-JUL-1
                              23,   @1985-JUL-1
                              24,   @1988-JAN-1
                              25,   @1990-JAN-1
                              26,   @1991-JAN-1
                              27,   @1992-JUL-1
                              28,   @1993-JUL-1
                              29,   @1994-JUL-1
                              30,   @1996-JAN-1
                              31,   @1997-JUL-1
                              32,   @1999-JAN-1
                              33,   @2006-JAN-1
                              34,   @2009-JAN-1
                              35,   @2012-JUL-1
                              36,   @2015-JUL-1
                              37,   @2017-JAN-1 )

\\begintext
"""
    with open(out_path, "w") as f:
        f.write(lsk_content)
    return out_path


def build_all(out_dir: str, camera_params: dict, ephemeris: list[dict]) -> str:
    """Build all synthetic kernels and write a metakernel."""
    os.makedirs(out_dir, exist_ok=True)
    
    ik_path = os.path.join(out_dir, "ik.ti")
    fk_path = os.path.join(out_dir, "fk.tf")
    spk_path = os.path.join(out_dir, "spk.bsp")
    lsk_path = os.path.join(out_dir, "lsk.tls")
    build_ik(camera_params, ik_path)
    build_fk(camera_params, fk_path)
    build_spk(ephemeris, spk_path)
    build_lsk(lsk_path)
    
    tm_path = os.path.join(out_dir, "test.tm")
    ik_p = ik_path.replace("\\", "/")
    fk_p = fk_path.replace("\\", "/")
    spk_p = spk_path.replace("\\", "/")
    lsk_p = lsk_path.replace("\\", "/")

    tm_content = f"""KPL/MK

\\begindata

   KERNELS_TO_LOAD = ( 
       '{ik_p}',
       '{fk_p}',
       '{spk_p}',
       '{lsk_p}'
   )

\\begintext
"""
    with open(tm_path, "w") as f:
        f.write(tm_content)
        
    return tm_path


import os
import tempfile
import spiceypy
from app.services import spice_kernel_build

def test_spice_kernel_build():
    with tempfile.TemporaryDirectory() as tmpdir:
        tm_path = spice_kernel_build.build_all(tmpdir, {}, [])
        
        # 1. Output files exist
        assert os.path.exists(os.path.join(tmpdir, "ik.ti"))
        assert os.path.exists(os.path.join(tmpdir, "fk.tf"))
        assert os.path.exists(os.path.join(tmpdir, "spk.bsp"))
        assert os.path.exists(tm_path)
        
        try:
            # 2. furnsh succeeds
            spiceypy.furnsh(tm_path)
            
            # 3. getfov returns valid shape
            shape, frame, bsight, n, bounds = spiceypy.getfov(-1400001, 4)
            assert len(bounds) == 4
            
            # 4. sincpt at boresight returns valid point
            # et = 0
            point, trgepc, srfvec = spiceypy.sincpt(
                "Ellipsoid", "MOON", 0.0, "IAU_MOON", "NONE", "-1400001", frame, bsight
            )
            assert point is not None
        finally:
            spiceypy.kclear()

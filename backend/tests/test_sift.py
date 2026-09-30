import pytest
from app.vision.sift_extractor import SIFTExtractor
from app.simulation.scenario_generator import generate_lunar_crater_surface

def test_sift_extractor():
    img = generate_lunar_crater_surface(width=256, height=256, seed=123)
    extractor = SIFTExtractor(nfeatures=500)
    kps, desc = extractor.extract(img)
    
    assert len(kps) > 10, "SIFT should detect features on crater terrain"
    assert desc.shape[0] == len(kps)
    assert desc.shape[1] == 128

import pytest
from app.vision.sift_extractor import SIFTExtractor
from app.vision.matcher import FeatureMatcher
from app.simulation.scenario_generator import generate_lunar_crater_surface, apply_controlled_variation
from app.models.schemas import MatcherType

def test_feature_matching_bf_and_flann():
    ref_img = generate_lunar_crater_surface(width=256, height=256, seed=123)
    mov_img, _ = apply_controlled_variation(ref_img, scale=1.02, rotation_deg=2.0, tx_px=5.0, ty_px=-3.0, seed=123)

    extractor = SIFTExtractor(nfeatures=500)
    kps_ref, desc_ref = extractor.extract(ref_img)
    kps_mov, desc_mov = extractor.extract(mov_img)

    # Test BF Matcher
    bf_matcher = FeatureMatcher(matcher_type=MatcherType.BF, ratio_threshold=0.8)
    matches_bf, cand_bf = bf_matcher.match(kps_ref, desc_ref, kps_mov, desc_mov)
    assert cand_bf > 0
    assert len(matches_bf) > 0

    # Test FLANN Matcher
    flann_matcher = FeatureMatcher(matcher_type=MatcherType.FLANN, ratio_threshold=0.8)
    matches_flann, cand_flann = flann_matcher.match(kps_ref, desc_ref, kps_mov, desc_mov)
    assert cand_flann > 0
    assert len(matches_flann) > 0

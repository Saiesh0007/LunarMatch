import numpy as np

from src.features import extract
from src.matching import match, filter_ratio


def _make_pair():
    rng = np.random.RandomState(42)
    img = rng.randint(0, 255, (200, 200), dtype=np.uint8)
    return img, img.copy()


def test_match_bf():
    img_a, img_b = _make_pair()
    _, desc_a = extract(img_a)
    _, desc_b = extract(img_b)
    knn, good = match(desc_a, desc_b, method="bf")
    assert len(knn) > 0
    assert len(good) > 0
    assert len(good) <= len(knn)


def test_match_flann():
    img_a, img_b = _make_pair()
    _, desc_a = extract(img_a)
    _, desc_b = extract(img_b)
    knn, good = match(desc_a, desc_b, method="flann")
    assert len(good) > 0


def test_match_insufficient_descriptors():
    desc_a = np.float32([[1.0]])
    desc_b = np.float32([[2.0]])
    knn, good = match(desc_a, desc_b)
    assert len(knn) == 0
    assert len(good) == 0


def test_ratio_filtering_reduces():
    img_a, img_b = _make_pair()
    _, desc_a = extract(img_a)
    _, desc_b = extract(img_b)
    knn, good_strict = match(desc_a, desc_b, ratio_thresh=0.5)
    _, good_loose = match(desc_a, desc_b, ratio_thresh=0.9)
    assert len(good_strict) <= len(good_loose)

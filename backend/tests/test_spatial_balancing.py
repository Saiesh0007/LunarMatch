import pytest
from app.models.schemas import MatchPairModel
from app.vision.spatial import SpatialBalancing

def test_spatial_balancing_grid():
    matches = []
    # Create 30 clustered matches in the top-left quadrant (x: 10..50, y: 10..50)
    for i in range(30):
        matches.append(
            MatchPairModel(
                ref_idx=i, mov_idx=i, distance=float(i * 2),
                ref_pt=[20.0 + (i % 5), 20.0 + (i // 5)],
                mov_pt=[20.0, 20.0],
                is_inlier=True
            )
        )
    # And 5 matches in bottom-right (x: 400..450, y: 400..450)
    for i in range(30, 35):
        matches.append(
            MatchPairModel(
                ref_idx=i, mov_idx=i, distance=float(i),
                ref_pt=[420.0 + (i % 3), 420.0],
                mov_pt=[420.0, 420.0],
                is_inlier=True
            )
        )

    # Balance on a 6x6 grid with max 5 per cell
    balanced, stats = SpatialBalancing.balance(matches, img_width=500, img_height=500, grid_size=6, max_per_cell=5)

    assert len(balanced) <= 10  # 5 from top-left cell + 5 from bottom-right cell
    assert stats.total_cells == 36
    assert stats.occupied_cells_after == 2
    assert stats.coverage_percentage_after == round((2 / 36) * 100.0, 2)

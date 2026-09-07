from typing import List, Tuple, Dict
from collections import defaultdict
import numpy as np
from ..models.schemas import MatchPairModel, SpatialGridStats
from ..utils.logging import logger

class SpatialBalancing:
    """
    Spatially balanced correspondence selection across an N x N grid.
    Prevents correspondences from clustering exclusively around high-contrast crater rims
    while leaving low-texture mare plains without geometric constraints.
    """

    @staticmethod
    def balance(
        matches: List[MatchPairModel],
        img_width: int,
        img_height: int,
        grid_size: int = 6,
        max_per_cell: int = 5,
    ) -> Tuple[List[MatchPairModel], SpatialGridStats]:
        """
        Partition reference image into grid_size x grid_size cells.
        Retain top `max_per_cell` matches per cell based on match distance.
        """
        total_cells = grid_size * grid_size
        if not matches or img_width <= 0 or img_height <= 0:
            stats = SpatialGridStats(
                grid_size=grid_size,
                total_cells=total_cells,
                occupied_cells_before=0,
                occupied_cells_after=0,
                coverage_percentage_before=0.0,
                coverage_percentage_after=0.0,
                coverage_gain_percentage=0.0,
            )
            return [], stats

        cell_w = img_width / grid_size
        cell_h = img_height / grid_size

        # Map each match to a grid cell based on its Reference image coordinate
        grid_buckets: Dict[Tuple[int, int], List[MatchPairModel]] = defaultdict(list)
        for m in matches:
            col = min(grid_size - 1, max(0, int(m.ref_pt[0] // cell_w)))
            row = min(grid_size - 1, max(0, int(m.ref_pt[1] // cell_h)))
            grid_buckets[(row, col)].append(m)

        occupied_before = len(grid_buckets)
        coverage_before = (occupied_before / total_cells) * 100.0

        # Select top-k best matches per cell (sorted by distance ascending)
        spatially_selected: List[MatchPairModel] = []
        for cell_coord, cell_matches in grid_buckets.items():
            # Sort by ascending feature distance (best quality first)
            cell_matches_sorted = sorted(cell_matches, key=lambda m: m.distance)
            selected_in_cell = cell_matches_sorted[:max_per_cell]
            for sm in selected_in_cell:
                sm.is_spatially_selected = True
                spatially_selected.append(sm)

        # Count occupied cells after selection
        occupied_after = len(grid_buckets)
        coverage_after = (occupied_after / total_cells) * 100.0
        gain = coverage_after - coverage_before

        stats = SpatialGridStats(
            grid_size=grid_size,
            total_cells=total_cells,
            occupied_cells_before=occupied_before,
            occupied_cells_after=occupied_after,
            coverage_percentage_before=round(coverage_before, 2),
            coverage_percentage_after=round(coverage_after, 2),
            coverage_gain_percentage=round(gain, 2),
        )

        logger.info(
            f"Spatial Balancing ({grid_size}x{grid_size}): {len(matches)} -> {len(spatially_selected)} "
            f"selected matches | Coverage: {stats.coverage_percentage_before}% ({occupied_before}/{total_cells} cells)"
        )
        return spatially_selected, stats

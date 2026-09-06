import numpy as np


def spatial_balance(pts_ref, matches, inlier_mask, image_shape, grid_size=8, max_per_cell=5):
    h, w = image_shape[:2]
    cell_h = h / grid_size
    cell_w = w / grid_size

    inlier_indices = np.where(inlier_mask)[0]
    if len(inlier_indices) == 0:
        return np.array([], dtype=int)

    cells = {}
    for idx in inlier_indices:
        pt = pts_ref[idx]
        row = min(int(pt[1] / cell_h), grid_size - 1)
        col = min(int(pt[0] / cell_w), grid_size - 1)
        cell_key = (row, col)
        dist = matches[idx].distance if idx < len(matches) else float("inf")
        if cell_key not in cells:
            cells[cell_key] = []
        cells[cell_key].append((idx, dist))

    selected = []
    for cell_key in cells:
        cell_matches = sorted(cells[cell_key], key=lambda x: x[1])
        for idx, _ in cell_matches[:max_per_cell]:
            selected.append(idx)

    return np.array(selected, dtype=int)


def compute_coverage(selected_pts, image_shape, grid_size=8):
    if len(selected_pts) == 0:
        return 0.0

    h, w = image_shape[:2]
    cell_h = h / grid_size
    cell_w = w / grid_size

    occupied = set()
    for pt in selected_pts:
        row = min(int(pt[1] / cell_h), grid_size - 1)
        col = min(int(pt[0] / cell_w), grid_size - 1)
        occupied.add((row, col))

    total_cells = grid_size * grid_size
    return len(occupied) / total_cells

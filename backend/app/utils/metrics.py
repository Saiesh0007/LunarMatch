import math

def safe_divide(numerator: float, denominator: float, default: float = float('nan')) -> float:
    """Return numerator / denominator, or default if denominator is ~0 or result is non-finite."""
    if abs(denominator) < 1e-12:
        return default
    result = numerator / denominator
    if not math.isfinite(result):
        return default
    return result
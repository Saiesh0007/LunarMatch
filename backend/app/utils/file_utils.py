import json
from pathlib import Path
from typing import Any, Dict
import numpy as np

def to_json_serializable(val: Any) -> Any:
    """Recursively convert NumPy data types and Path objects to native JSON serializable types."""
    if isinstance(val, (np.integer, np.int64, np.int32)):
        return int(val)
    elif isinstance(val, (np.floating, np.float32, np.float64)):
        if np.isnan(val) or np.isinf(val):
            return None
        return round(float(val), 6)
    elif isinstance(val, np.ndarray):
        return [to_json_serializable(x) for x in val.tolist()]
    elif isinstance(val, dict):
        return {str(k): to_json_serializable(v) for k, v in val.items()}
    elif isinstance(val, (list, tuple, set)):
        return [to_json_serializable(x) for x in val]
    elif isinstance(val, Path):
        return str(val)
    return val

def save_json(file_path: Path, data: Any) -> None:
    """Save data to JSON file safely."""
    file_path.parent.mkdir(parents=True, exist_ok=True)
    serializable = to_json_serializable(data)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(serializable, f, indent=2)

def load_json(file_path: Path) -> Dict[str, Any]:
    """Load JSON file safely."""
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

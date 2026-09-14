import json
import math
import gc
from pathlib import Path
from typing import Any, Dict


def _safe_float(val: Any) -> Any:
    """Convert a value to float, handling numpy types without calling
    numpy's native isnan/isinf which can crash on Windows under memory pressure."""
    try:
        f = float(val)
    except (TypeError, ValueError, OverflowError):
        return None
    if f != f:  # NaN check without importing numpy
        return None
    if f == float("inf") or f == float("-inf"):
        return None
    return round(f, 6)


def to_json_serializable(val: Any) -> Any:
    """Recursively convert NumPy data types, Path objects, and non-finite floats to JSON-safe values.

    Non-finite floats (inf, -inf, nan) are converted to None so that every artifact
    emitted by the pipeline is directly JSON-serializable without raising.
    Uses pure-Python float checks to avoid native numpy calls that can crash
    under memory pressure on Windows.
    """
    if isinstance(val, dict):
        return {str(k): to_json_serializable(v) for k, v in val.items()}
    if isinstance(val, (list, tuple, set)):
        return [to_json_serializable(x) for x in val]
    if isinstance(val, Path):
        return str(val)
    # Handle numpy arrays via duck-typing (avoid importing numpy at module level
    # since native numpy calls can crash under memory pressure on Windows)
    if hasattr(val, "tolist") and hasattr(val, "ndim"):
        try:
            # Disable GC during numpy conversion to prevent native crashes
            # where GC runs during a numpy C call on a corrupted array.
            # Respects existing GC state — only re-enables if we disabled it.
            gc_was_enabled = gc.isenabled()
            if gc_was_enabled:
                gc.disable()
            try:
                return [to_json_serializable(x) for x in val.tolist()]
            finally:
                if gc_was_enabled:
                    gc.enable()
        except (TypeError, ValueError, OverflowError):
            return str(val)
    # Check for numpy scalar types by class module string
    cls = type(val)
    cls_module = getattr(cls, "__module__", "")
    if cls_module.startswith("numpy"):
        return _safe_float(val)
    if isinstance(val, float):
        if math.isnan(val) or math.isinf(val):
            return None
        return val
    if isinstance(val, int):
        return val
    if isinstance(val, str):
        return val
    if val is None or val is True or val is False:
        return val
    # Fallback: try to convert to float, then str
    f = _safe_float(val)
    if f is not None:
        return f
    return str(val)


def save_json(file_path: Path, data: Any) -> None:
    """Save data to JSON file safely.

    Disables GC during serialization to prevent Windows native access violations
    that occur when Python's garbage collector runs during numpy C operations
    on large arrays produced by the pipeline.

    Respects the existing GC state: if GC was already disabled by the caller
    (e.g. _persist_artifacts), it will not be re-enabled here.
    """
    file_path.parent.mkdir(parents=True, exist_ok=True)

    gc_was_enabled = gc.isenabled()
    if gc_was_enabled:
        gc.disable()
    try:
        serializable = to_json_serializable(data)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(serializable, f, indent=2, default=str)
    finally:
        if gc_was_enabled:
            gc.enable()


def load_json(file_path: Path) -> Dict[str, Any]:
    """Load JSON file safely."""
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

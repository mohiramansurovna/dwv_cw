from typing import Any
import pandas as pd # pyright: ignore[reportMissingModuleSource]

def make_json_safe(value: Any) -> Any:
    """Convert pandas/numpy values into plain Python types for logs and exports."""
    if isinstance(value, dict):
        return {str(key): make_json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [make_json_safe(item) for item in value]
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    if isinstance(value, (pd.Series, pd.Index)):
        return [make_json_safe(item) for item in value.tolist()]
    if hasattr(value, "item"):
        try:
            return value.item()
        except Exception:
            return str(value)
    return value
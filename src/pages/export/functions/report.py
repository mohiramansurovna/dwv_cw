from __future__ import annotations

import pandas as pd

from src.data.functions.exporters import make_json_safe
from src.data.functions.profile import profile_dataframe
from src.data.functions.store import build_report_payload


def build_safe_export_report(df: pd.DataFrame) -> dict:
    """Build the export report payload and normalize it for JSON/download use."""
    profile = profile_dataframe(df)
    report = build_report_payload()
    report["final_profile"] = {
        "duplicates_count": profile["duplicates_count"],
        "missing_summary": profile["missing"].to_dict(orient="records"),
    }
    return make_json_safe(report)

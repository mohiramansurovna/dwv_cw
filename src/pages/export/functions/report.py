from __future__ import annotations

import pandas as pd
import streamlit as st

from src.data.functions.exporters import make_json_safe
from src.data.functions.profile import profile_dataframe
from src.data.functions.store import build_report_payload
from src.pages.visualize.functions.state import SAVED_CHARTS_KEY


def build_safe_export_report(df: pd.DataFrame) -> tuple[dict, list[dict]]:
    """Build the export report payload and normalize it for JSON/download use."""
    profile = profile_dataframe(df)
    report = build_report_payload()
    saved_charts = st.session_state.get(SAVED_CHARTS_KEY, [])
    report["saved_chart_definitions"] = saved_charts
    report["final_profile"] = {
        "duplicates_count": profile["duplicates_count"],
        "missing_summary": profile["missing"].to_dict(orient="records"),
    }
    return make_json_safe(report), saved_charts

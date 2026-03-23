from __future__ import annotations

import streamlit as st


SAVED_CHARTS_KEY = "saved_charts"


def ensure_saved_charts() -> list[dict]:
    """Create or return the in-session list of saved chart definitions."""
    if SAVED_CHARTS_KEY not in st.session_state:
        st.session_state[SAVED_CHARTS_KEY] = []
    return st.session_state[SAVED_CHARTS_KEY]


def save_chart_spec(spec: dict) -> None:
    """Append the current chart configuration to the saved export list."""
    saved = ensure_saved_charts()
    saved.append(spec)

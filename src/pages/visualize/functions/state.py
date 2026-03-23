from __future__ import annotations

from io import BytesIO
import re

import streamlit as st


CHARTS_KEY = "charts"


def ensure_saved_charts() -> list[dict]:
    """Create or return the in-session list of saved chart image payloads."""
    if CHARTS_KEY not in st.session_state:
        st.session_state[CHARTS_KEY] = []
    return st.session_state[CHARTS_KEY]


def save_chart_image(fig, chart_type: str, x_column: str | None, y_column: str | None) -> str:
    """Serialize the current figure as a PNG image and save it in session state."""
    saved = ensure_saved_charts()
    chart_number = len(saved) + 1
    filename = build_chart_filename(chart_number, chart_type, x_column, y_column)
    buffer = BytesIO()
    fig.savefig(buffer, format="png", dpi=200, bbox_inches="tight")
    saved.append(
        {
            "filename": filename,
            "image_bytes": buffer.getvalue(),
            "chart_type": chart_type,
        }
    )
    return filename


def build_chart_filename(
    chart_number: int,
    chart_type: str,
    x_column: str | None,
    y_column: str | None,
) -> str:
    """Build a stable, readable image filename for each saved chart."""
    parts = [f"{chart_number:02d}", chart_type.replace("_", "-")]
    if x_column:
        parts.append(_slugify(x_column))
    if y_column:
        parts.append(_slugify(y_column))
    return "_".join(parts) + ".png"


def _slugify(value: str) -> str:
    """Turn a label into a filename-safe token."""
    cleaned = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower()).strip("-")
    return cleaned or "chart"

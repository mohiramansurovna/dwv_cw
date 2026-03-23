from __future__ import annotations

import streamlit as st


PAGE_OPTIONS: list[tuple[str, str, str]] = [
    ("upload", "Upload & Overview", ":material/upload_file:"),
    ("prepare", "Cleaning Studio", ":material/mop:"),
    ("visualize", "Visualization", ":material/finance_mode:"),
    ("export", "Export & Report", ":material/download:"),
]


def render_navigation_sidebar(default_page: str = "upload") -> str:
    """Render the icon-only page switcher shown in the left sidebar."""
    page_keys = [key for key, _, _ in PAGE_OPTIONS]
    if "active_page" not in st.session_state or st.session_state["active_page"] not in page_keys:
        st.session_state["active_page"] = default_page

    with st.sidebar:
        selected_page = st.ratio(
            "Workflow",
            options=page_keys,
            format_func=lambda key: next(
                icon for option_key, _, icon in PAGE_OPTIONS if option_key == key
            ),
            key="active_page",
            label_visibility="collapsed",
            ratio='false'
        )

    return selected_page

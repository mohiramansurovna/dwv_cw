from __future__ import annotations

import streamlit as st


PAGE_OPTIONS: list[tuple[str, str, str]] = [
    ("upload", "Upload & Overview", ":material/upload_file:"),
    ("prepare", "Cleaning Studio", ":material/mop:"),
    ("visualize", "Visualization", ":material/finance_mode:"),
    ("export", "Export & Report", ":material/download:"),
]


def render_navigation_sidebar(default_page: str = "upload") -> str:
    page_keys = [key for key, _, _ in PAGE_OPTIONS]

    if "active_page" not in st.session_state or st.session_state["active_page"] not in page_keys:
        st.session_state["active_page"] = default_page

    with st.sidebar:
        st.header("Workflow")

        for key, label, icon in PAGE_OPTIONS:
            is_active = st.session_state["active_page"] == key

            if st.button(
                f"{icon} {label}",
                key=f"nav_{key}",
                use_container_width=True,
                type="primary" if is_active else "tertiary"
            ):
                st.session_state["active_page"] = key
                st.rerun()

    return st.session_state["active_page"]
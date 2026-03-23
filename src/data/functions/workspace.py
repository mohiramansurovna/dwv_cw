from __future__ import annotations

import streamlit as st

from src.data.functions.store import (
    clear_session,
    get_current_data,
    get_source_name,
    get_transform_log,
    has_data,
    reset_all,
    undo_last_step,
)


def render_history_panel_content() -> None:
    """showing changes history"""
    st.subheader("History")

    log = get_transform_log()
    if not log:
        st.caption("No changes yet")
        return

    st.caption(f"{len(log)} step(s) recorded")
    for index, item in enumerate(reversed(log), start=1):
        with st.expander(f"{index}. {item['operation']}", expanded=False):
            st.caption(item["timestamp"])
            st.write(f"**Affected columns:** {', '.join(item['affected_columns']) or '-'}")
            st.write(f"**Parameters:** {item['parameters'] or '-'}")
            st.write(f"**Before shape:** {item['shape_before']}")
            st.write(f"**After shape:** {item['shape_after']}")
            if item.get("preview"):
                st.write(f"**Impact preview:** {item['preview']}")


def render_workspace_panel_content() -> None:
    """Render dataset status, workspace actions, and the transformation history."""
    st.subheader("Workspace")

    source_name = get_source_name()
    st.caption(f"Source: {source_name}" if source_name else "Source: no dataset loaded")

    df = get_current_data()
    if df is not None:
        rows_col, cols_col = st.columns(2)
        rows_col.metric("Rows", f"{df.shape[0]:,}")
        cols_col.metric("Cols", df.shape[1])

    st.divider()
    render_history_panel_content()

    undo_clicked = st.button(
        "Undo last step",
        use_container_width=True,
        disabled=not has_data() or not get_transform_log(),
    )
    if undo_clicked:
        if undo_last_step():
            st.success("Last transformation removed.")
            st.rerun()
        st.warning("No step available to undo.")

    reset_clicked = st.button(
        "Reset to original dataset",
        use_container_width=True,
        disabled=not has_data(),
    )
    if reset_clicked:
        if reset_all():
            st.success("Working copy reset.")
            st.rerun()

    clear_clicked = st.button(
        "Reset session",
        use_container_width=True,
    )
    if clear_clicked:
        clear_session()
        st.success("Session cleared.")
        st.rerun()


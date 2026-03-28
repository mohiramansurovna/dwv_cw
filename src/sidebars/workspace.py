from __future__ import annotations
import streamlit as st  # pyright: ignore[reportMissingImports]

from src.data.store import get_store
from src.sidebars.history_actions import clear_session, reset_all, undo_last_step

def render_source()->None:
    st.subheader("Workspace")
    store=get_store()
    st.caption(f"Source: {store['source_name']}" if store['source_name'] else "Source: no dataset loaded")

    if store['current_df'] is not None:
        rows_col, cols_col = st.columns(2)
        rows_col.metric("Rows", f"{store['current_df'].shape[0]:,}")
        cols_col.metric("Cols", store['current_df'].shape[1])

def render_history()->None:
    st.subheader("History")
    store=get_store()
    if not store['transform_log']:
        st.caption("No changes yet")
        return
    st.caption(f"{len(store['transform_log'])} step(s) recorded")
    for index, item in enumerate(reversed(store['transform_log']), start=1):
        with st.expander(f"{index}. {item['operation']}", expanded=False):
            st.caption(item["timestamp"])
            st.write(f"**Affected columns:** {', '.join(item['affected_columns']) or '-'}")
            st.write(f"**Parameters:** {item['parameters'] or '-'}")
            st.write(f"**Before shape:** {item['shape_before']}")
            st.write(f"**After shape:** {item['shape_after']}")
            if item.get("preview"):
                st.write(f"**Impact preview:** {item['preview']}")


def render_buttons() -> None:
    store = get_store()

    has_data = store["current_df"] is not None
    has_history = len(store["transform_log"]) > 0

    undo_clicked = st.button(
        "Undo last step",
        use_container_width=True,
        disabled=not has_data or not has_history,
    )
    if undo_clicked:
        if undo_last_step():
            st.success("Last transformation removed.")
            st.rerun()
        else:
            st.warning("No step available to undo.")

    reset_clicked = st.button(
        "Reset to original dataset",
        use_container_width=True,
        disabled=not has_data,
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



def render_workspace() -> None:
    render_source()
    st.divider()
    render_history()
    render_buttons()

    

    

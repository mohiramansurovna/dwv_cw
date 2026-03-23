from __future__ import annotations

import pandas as pd
import streamlit as st

from src.data.functions.store import apply_step
from src.data.functions.transforms import dataframe_to_csv_bytes


VALIDATION_RESULT_KEY = "validation_result"
VALIDATION_TITLE_KEY = "validation_title"


def apply_and_rerun(
    new_df: pd.DataFrame,
    operation: str,
    parameters: dict,
    affected_columns: list[str],
    preview: dict,
) -> None:
    """Save a completed transformation and immediately refresh the page state."""
    apply_step(
        new_df,
        operation=operation,
        parameters=parameters,
        affected_columns=affected_columns,
        preview=preview,
    )
    st.success(f"{operation} applied.")
    st.rerun()


def set_validation_result(title: str, violations: pd.DataFrame) -> None:
    """Store the latest validation output so it survives reruns."""
    st.session_state[VALIDATION_TITLE_KEY] = title
    st.session_state[VALIDATION_RESULT_KEY] = violations


def render_validation_result() -> None:
    """Display the current validation result table and export option."""
    violations = st.session_state.get(VALIDATION_RESULT_KEY)
    title = st.session_state.get(VALIDATION_TITLE_KEY, "Validation result")
    if violations is None:
        return

    st.divider()
    st.subheader(title)
    if violations.empty:
        st.success("No violations found.")
        return

    st.warning(f"{len(violations)} violation(s) found.")
    st.dataframe(violations, use_container_width=True, hide_index=True)
    st.download_button(
        "Download violations CSV",
        data=dataframe_to_csv_bytes(violations),
        file_name="validation_violations.csv",
        mime="text/csv",
        use_container_width=True,
    )

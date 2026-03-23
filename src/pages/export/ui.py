from __future__ import annotations

import json

import streamlit as st

from src.data.functions.exporters import (
    json_to_bytes,
    make_json_safe,
    report_to_markdown,
    text_to_bytes,
)
from src.data.functions.profile import profile_dataframe
from src.data.functions.store import (
    build_report_payload,
    get_current_data,
    get_recipe_json,
)
from src.data.functions.transforms import dataframe_to_csv_bytes, dataframe_to_excel_bytes
from src.data.ui import render_workspace_panel
from src.pages.visualize.ui import SAVED_CHARTS_KEY


def render_export_page() -> None:
    left, right = st.columns([3.2, 1.2])
    df = get_current_data()

    with left:
        st.title("Export & Report")

        if df is None:
            st.info("Load a dataset before exporting.")
        else:
            profile = profile_dataframe(df)
            report = build_report_payload()
            saved_charts = st.session_state.get(SAVED_CHARTS_KEY, [])
            report["saved_chart_definitions"] = saved_charts
            report["final_profile"] = {
                "duplicates_count": profile["duplicates_count"],
                "missing_summary": profile["missing"].to_dict(orient="records"),
            }
            safe_report = make_json_safe(report)

            summary_cols = st.columns(4)
            summary_cols[0].metric("Final rows", f"{df.shape[0]:,}")
            summary_cols[1].metric("Final columns", df.shape[1])
            summary_cols[2].metric("Transformations", len(safe_report["transformations"]))
            summary_cols[3].metric("Saved charts", len(saved_charts))

            st.subheader("Download outputs")
            download_cols = st.columns(2)
            download_cols[0].download_button(
                "Download cleaned CSV",
                data=dataframe_to_csv_bytes(df),
                file_name="cleaned_dataset.csv",
                mime="text/csv",
                use_container_width=True,
            )
            download_cols[1].download_button(
                "Download cleaned Excel",
                data=dataframe_to_excel_bytes(df),
                file_name="cleaned_dataset.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )

            report_cols = st.columns(3)
            report_cols[0].download_button(
                "Download report JSON",
                data=json_to_bytes(safe_report),
                file_name="transformation_report.json",
                mime="application/json",
                use_container_width=True,
            )
            report_cols[1].download_button(
                "Download report Markdown",
                data=text_to_bytes(report_to_markdown(safe_report)),
                file_name="transformation_report.md",
                mime="text/markdown",
                use_container_width=True,
            )
            report_cols[2].download_button(
                "Download recipe JSON",
                data=get_recipe_json().encode("utf-8"),
                file_name="dwv_recipe.json",
                mime="application/json",
                use_container_width=True,
            )

            st.subheader("Final dataset preview")
            st.dataframe(df.head(50), use_container_width=True)

            st.subheader("Report preview")
            st.json(safe_report)

            if saved_charts:
                st.subheader("Saved charts for the dashboard report")
                st.code(json.dumps(make_json_safe(saved_charts), indent=2), language="json")

    with right:
        render_workspace_panel()

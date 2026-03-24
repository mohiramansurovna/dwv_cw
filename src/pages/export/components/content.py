from __future__ import annotations

import pandas as pd
import streamlit as st

from src.pages.export.components.transforms import (
    dataframe_to_csv_bytes, 
    dataframe_to_excel_bytes, 
    json_to_bytes, 
    report_to_markdown, 
    text_to_bytes,
    get_recipe_json
)
from src.pages.export.components.charts import build_charts_zip
from src.pages.export.components.report import build_report
from src.pages.visualize.functions.state import ensure_saved_charts


def render_export_content(df: pd.DataFrame) -> None:
    safe_report = build_report(df)
    saved_charts = ensure_saved_charts()

    summary_cols = st.columns(4)
    summary_cols[0].metric("Final rows", f"{df.shape[0]:,}")
    summary_cols[1].metric("Final columns", df.shape[1])
    summary_cols[2].metric("Transformations", len(safe_report["transformations"]))
    summary_cols[3].metric("Saved charts", len(saved_charts))

    st.subheader("Download outputs")
    download_cols = st.columns(3)
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
    download_cols[2].download_button(
        "Download charts ZIP",
        data=build_charts_zip(saved_charts) if saved_charts else b"",
        file_name="charts.zip",
        mime="application/zip",
        use_container_width=True,
        disabled=not saved_charts,
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


    if saved_charts:
        st.subheader("Saved charts")
        for chart in saved_charts:
            st.caption(chart["filename"])
            st.image(chart["image_bytes"], use_container_width=True)
    
    st.subheader("Report preview")
    st.json(safe_report)

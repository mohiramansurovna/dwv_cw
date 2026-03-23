from __future__ import annotations

import json
from io import BytesIO

import pandas as pd


def make_json_safe(value):
    """Convert nested pandas/numpy values into plain JSON-friendly Python values."""
    if isinstance(value, dict):
        return {str(key): make_json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [make_json_safe(item) for item in value]
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    if isinstance(value, (pd.Series, pd.Index)):
        return [make_json_safe(item) for item in value.tolist()]
    if hasattr(value, "item"):
        try:
            return value.item()
        except Exception:
            return str(value)
    return value


def report_to_markdown(report: dict) -> str:
    """Render the export report as a lightweight human-readable Markdown file."""
    report = make_json_safe(report)
    lines = [
        "# Transformation Report",
        "",
        f"- Generated at: {report.get('generated_at', '-')}",
        f"- Source: {report.get('source_name', '-')}",
        f"- Final shape: {report.get('final_shape', '-')}",
        f"- Steps recorded: {len(report.get('transformations', []))}",
        "",
        "## Steps",
        "",
    ]

    if not report.get("transformations"):
        lines.append("No transformations have been applied yet.")
    else:
        for index, step in enumerate(report["transformations"], start=1):
            lines.extend(
                [
                    f"### {index}. {step['operation']}",
                    f"- Timestamp: {step['timestamp']}",
                    f"- Affected columns: {', '.join(step['affected_columns']) or '-'}",
                    f"- Parameters: `{json.dumps(step['parameters'])}`",
                    f"- Shape before: {step['shape_before']}",
                    f"- Shape after: {step['shape_after']}",
                    "",
                ]
            )
    return "\n".join(lines)


def json_to_bytes(payload: dict | list) -> bytes:
    """Encode a dict/list payload as downloadable UTF-8 JSON bytes."""
    return json.dumps(make_json_safe(payload), indent=2).encode("utf-8")


def text_to_bytes(payload: str) -> bytes:
    """Encode plain text as UTF-8 bytes for download buttons."""
    return payload.encode("utf-8")


def dataframe_to_excel_bytes(df: pd.DataFrame, sheet_name: str = "data") -> bytes:
    """Create a downloadable Excel workbook in memory from a dataframe."""
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name=sheet_name)
    return buffer.getvalue()

from __future__ import annotations

from io import BytesIO
from zipfile import ZIP_DEFLATED, ZipFile


def build_charts_zip(saved_charts: list[dict]) -> bytes:
    """Package saved chart images into a ZIP file under a charts/ folder."""
    buffer = BytesIO()
    with ZipFile(buffer, mode="w", compression=ZIP_DEFLATED) as archive:
        for chart in saved_charts:
            archive.writestr(f"charts/{chart['filename']}", chart["image_bytes"])
    return buffer.getvalue()

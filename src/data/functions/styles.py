from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import streamlit as st


@lru_cache(maxsize=None)
def _read_css(path: str) -> str:
    """Read a CSS file once so repeated reruns do not hit the filesystem again."""
    return Path(path).read_text(encoding="utf-8")


def apply_css(path: Path) -> None:
    """Inject a CSS file into the current Streamlit page."""
    st.markdown(f"<style>{_read_css(str(path))}</style>", unsafe_allow_html=True)

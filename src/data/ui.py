from pathlib import Path

from src.data.functions.navigation import render_navigation_sidebar
from src.data.functions.styles import apply_css
from src.data.functions.workspace import (
    render_history_panel_content,
    render_workspace_panel_content,
)


DATA_CSS_PATH = Path(__file__).with_name("data.css")


def render_data_sidebar(default_page: str = "upload") -> str:
    """Load shared styles and render the left navigation sidebar."""
    apply_css(DATA_CSS_PATH)
    return render_navigation_sidebar(default_page=default_page)


def render_history_panel() -> None:
    """Thin UI wrapper around the shared transformation-history panel."""
    render_history_panel_content()


def render_workspace_panel() -> None:
    """Thin UI wrapper around the shared right-side workspace panel."""
    render_workspace_panel_content()

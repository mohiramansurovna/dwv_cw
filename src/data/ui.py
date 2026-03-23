from pathlib import Path

from src.data.functions.navigation import render_navigation_sidebar
from src.data.functions.workspace import (
    render_history_panel_content,
    render_workspace_panel_content,
)


DATA_CSS_PATH = Path(__file__).with_name("data.css")


def render_data_sidebar(default_page: str = "upload") -> str:
    """render left navigation sidebar."""
    return render_navigation_sidebar(default_page=default_page)


def render_history_panel() -> None:
    """history panel."""
    render_history_panel_content()


def render_workspace_panel() -> None:
    """right-side workspace panel."""
    render_workspace_panel_content()

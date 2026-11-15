from __future__ import annotations

from PySide6.QtWidgets import QApplication

from gamelauncher.ui.state import ViewState
from gamelauncher.ui.views.library_view import LibraryView


def test_library_view_tracks_live_search_and_state() -> None:
    app = QApplication.instance() or QApplication([])
    view = LibraryView()

    view.set_results([])
    assert view.state == ViewState.EMPTY
    assert view.search_text == ""

    view.set_results([{"id": 1, "name": "Quest Runner"}])
    view.apply_search("quest")
    assert view.search_text == "quest"
    assert view.state == ViewState.SUCCESS

    view.set_results([])
    assert view.state == ViewState.EMPTY
    app.processEvents()


def test_library_view_supports_grid_and_list_modes() -> None:
    app = QApplication.instance() or QApplication([])
    view = LibraryView()

    view.set_layout_mode("grid")
    assert view.layout_mode == "grid"

    view.set_layout_mode("list")
    assert view.layout_mode == "list"

    view.set_results([{"id": 1, "name": "Alpha"}])
    assert view.state == ViewState.SUCCESS
    app.processEvents()

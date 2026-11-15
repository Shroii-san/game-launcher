from __future__ import annotations

from PySide6.QtWidgets import QApplication

from gamelauncher.ui.state import ViewState
from gamelauncher.ui.widgets.state_panel import StatePanel
from gamelauncher.ui.widgets.toast import Toast


def test_viewstate_has_expected_states() -> None:
    assert {state.name for state in ViewState} == {"LOADING", "EMPTY", "ERROR", "SUCCESS"}


def test_state_panel_updates_message_and_state() -> None:
    app = QApplication.instance() or QApplication([])
    panel = StatePanel()

    panel.set_state(ViewState.EMPTY, "No games found")
    assert panel.state == ViewState.EMPTY
    assert panel.message == "No games found"

    panel.set_state(ViewState.SUCCESS, "Ready")
    assert panel.state == ViewState.SUCCESS
    assert panel.message == "Ready"
    app.processEvents()


def test_toast_tracks_visible_message() -> None:
    app = QApplication.instance() or QApplication([])
    toast = Toast()

    toast.show_message("Game ready")
    assert toast.current_message == "Game ready"
    app.processEvents()

from __future__ import annotations

from PySide6.QtWidgets import QApplication

from gamelauncher.ui.state import ViewState
from gamelauncher.ui.views.settings_view import SettingsView


def test_settings_view_tracks_directory_state() -> None:
    app = QApplication.instance() or QApplication([])
    view = SettingsView()

    view.set_state(ViewState.EMPTY, "No settings")
    assert view.state == ViewState.EMPTY

    view.set_games_root("/tmp/games")
    view.set_archive_dir("/tmp/archive")
    assert view.games_root == "/tmp/games"
    assert view.archive_dir == "/tmp/archive"
    app.processEvents()


def test_settings_view_validates_confirmed_directory_update() -> None:
    app = QApplication.instance() or QApplication([])
    view = SettingsView()

    is_valid = view.validate_directory_change("/tmp/ready", "/tmp/archive")
    assert is_valid is True

    result = view.validate_directory_change("", "/tmp/archive")
    assert result is False
    app.processEvents()

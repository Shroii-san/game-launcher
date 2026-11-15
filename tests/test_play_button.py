from __future__ import annotations

from PySide6.QtWidgets import QApplication

from gamelauncher.core.errors import LaunchError
from gamelauncher.ui.widgets.play_button import PlayButton


class StubRunService:
    def __init__(self, *, should_fail: bool = False) -> None:
        self.should_fail = should_fail
        self.calls: list[dict[str, object]] = []

    def launch(self, game: dict[str, object]) -> dict[str, object]:
        self.calls.append(game)
        if self.should_fail:
            raise LaunchError(
                "WINE_MISSING",
                "Wine is required to run this game.",
                user_message="Wine is required to run this game.",
            )
        return {"game_id": 1, "exit_code": 0, "running": True}


def test_play_button_disables_while_running() -> None:
    app = QApplication.instance() or QApplication([])
    button = PlayButton()

    button.set_game({"id": 1, "name": "Demo", "run_type": "exe"})
    button.set_running(True)

    assert button.isEnabled() is False
    assert button.status == "running"
    app.processEvents()


def test_play_button_launches_game_and_handles_error() -> None:
    app = QApplication.instance() or QApplication([])
    service = StubRunService(should_fail=True)
    button = PlayButton(run_service=service)

    button.set_game({"id": 1, "name": "Demo", "run_type": "exe"})
    button.handle_click()

    assert len(service.calls) == 1
    assert button.status == "error"
    assert "Wine" in button.error_message
    app.processEvents()

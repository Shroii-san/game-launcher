from __future__ import annotations

from typing import Any

from PySide6.QtWidgets import QPushButton

from gamelauncher.core.errors import LaunchError


class PlayButton(QPushButton):
    def __init__(self, run_service: Any | None = None, parent: Any | None = None) -> None:
        super().__init__("Play", parent)
        self.run_service = run_service
        self.status = "idle"
        self.error_message = ""
        self.game: dict[str, Any] | None = None
        self.clicked.connect(self.handle_click)
        self._update_button_state()

    def set_game(self, game: dict[str, Any]) -> None:
        self.game = game
        self.status = "idle"
        self.error_message = ""
        self._update_button_state()

    def set_running(self, is_running: bool) -> None:
        self.status = "running" if is_running else "idle"
        self.error_message = ""
        self._update_button_state()

    def handle_click(self) -> None:
        if self.status == "running":
            return
        if not self.game:
            return

        self.status = "running"
        self.error_message = ""
        self._update_button_state()

        if self.run_service is None:
            self.status = "idle"
            self._update_button_state()
            return

        try:
            self.run_service.launch(self.game)
        except LaunchError as exc:
            self.status = "error"
            self.error_message = str(exc.user_message or exc)
            self._update_button_state()
            return

        self.status = "success"
        self._update_button_state()

    def _update_button_state(self) -> None:
        if self.status == "running":
            self.setEnabled(False)
            self.setText("Running...")
            return
        if self.status == "error":
            self.setEnabled(True)
            self.setText("Play")
            return
        if self.status == "success":
            self.setEnabled(False)
            self.setText("Launched")
            return
        self.setEnabled(True)
        self.setText("Play")

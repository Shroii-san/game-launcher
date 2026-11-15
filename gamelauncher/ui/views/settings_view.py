from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import (
    QCheckBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from gamelauncher.ui.state import ViewState


class SettingsView(QWidget):
    """Settings editor for directory configuration with explicit risk confirmation."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.state = ViewState.EMPTY
        self.message = "No settings configured."
        self.games_root = ""
        self.archive_dir = ""

        self._status_label = QLabel("Settings")
        self._status_label.setStyleSheet("font-size: 18px; font-weight: 600;")
        self._status_message = QLabel(self.message)
        self._status_message.setWordWrap(True)

        self._warning = QLabel(
            "Changing these folders can make existing games disappear from the library. "
            "Use this at your own risk."
        )
        self._warning.setWordWrap(True)
        self._warning.setStyleSheet(
            "color: #b45309; background: #fff7ed; border: 1px solid #fbbf24; "
            "border-radius: 6px; padding: 8px;"
        )

        self._games_root_input = QLineEdit()
        self._archive_dir_input = QLineEdit()
        self._confirm_checkbox = QCheckBox("I understand the risk and want to continue.")
        self._save_button = QPushButton("Save settings")
        self._save_button.clicked.connect(self.save_settings)

        form_layout = QFormLayout()
        form_layout.addRow("Games root", self._games_root_input)
        form_layout.addRow("Archive dir", self._archive_dir_input)

        layout = QVBoxLayout(self)
        layout.addWidget(self._status_label)
        layout.addWidget(self._status_message)
        layout.addWidget(self._warning)
        layout.addLayout(form_layout)
        layout.addWidget(self._confirm_checkbox)
        layout.addWidget(self._save_button)

        self.set_state(ViewState.EMPTY, "No settings configured.")

    def set_state(self, state: ViewState, message: str) -> None:
        self.state = state
        self.message = message
        self._status_label.setText(state.label)
        self._status_message.setText(message)

    def set_games_root(self, path: str | Path) -> None:
        value = str(path).strip()
        self.games_root = value
        self._games_root_input.setText(value)

    def set_archive_dir(self, path: str | Path) -> None:
        value = str(path).strip()
        self.archive_dir = value
        self._archive_dir_input.setText(value)

    def validate_directory_change(
        self,
        games_root: str | Path | None,
        archive_dir: str | Path | None,
    ) -> bool:
        values = [games_root, archive_dir]
        for value in values:
            if value is None:
                return False
            if not str(value).strip():
                return False
        return True

    def save_settings(self) -> bool:
        games_root = self._games_root_input.text().strip()
        archive_dir = self._archive_dir_input.text().strip()

        if not self.validate_directory_change(games_root, archive_dir):
            self.set_state(ViewState.ERROR, "Games root and archive dir are required.")
            return False

        if not self._confirm_checkbox.isChecked():
            self.set_state(
                ViewState.ERROR,
                "Please confirm the warning before changing directories.",
            )
            return False

        self.games_root = games_root
        self.archive_dir = archive_dir
        self.set_state(ViewState.SUCCESS, "Directory settings saved.")
        return True

from __future__ import annotations

import shlex
from typing import Any

from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from gamelauncher.core.errors import ValidationError
from gamelauncher.core.paths import validate_path


class GameDialogValidator:
    @staticmethod
    def validate(
        name: str,
        folder_path: str,
        *,
        run_type: str = "custom",
        run_argv: list[str] | tuple[str, ...] | None = None,
    ) -> dict[str, Any]:
        errors: dict[str, str] = {}

        if not str(name).strip():
            errors["name"] = "Game name is required."

        if not str(folder_path).strip():
            errors["folder_path"] = "Folder path is required."
        else:
            try:
                validate_path(folder_path)
            except ValidationError as exc:
                errors["folder_path"] = str(exc.user_message or exc)

        if run_type not in {"exe", "sh", "custom"}:
            errors["run_type"] = "Run type is invalid."

        normalized = [str(part).strip() for part in (run_argv or []) if str(part).strip()]
        if run_type in {"exe", "sh"} and not normalized:
            errors["command"] = "Command is required for executable games."

        return {"valid": not errors, "errors": errors}


class GameDialog(QDialog):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.is_edit_mode = False

        self.setWindowTitle("Game Details")
        self.resize(520, 320)

        self.name_field = QLineEdit()
        self.folder_field = QLineEdit()
        self.run_type_combo = QComboBox()
        self.run_type_combo.addItems(["custom", "exe", "sh"])
        self.command_field = QLineEdit()
        self.command_field.setReadOnly(True)
        self.command_field.setPlaceholderText("wine game.exe")

        self.edit_command_button = QPushButton("Edit")
        self.edit_command_button.clicked.connect(self.enable_command_editing)

        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: #b91c1c; font-weight: 600;")
        self.error_label.setWordWrap(True)

        form_layout = QFormLayout()
        form_layout.addRow("Name", self.name_field)
        form_layout.addRow("Folder", self.folder_field)
        form_layout.addRow("Run type", self.run_type_combo)

        command_row = QWidget()
        command_layout = QHBoxLayout(command_row)
        command_layout.setContentsMargins(0, 0, 0, 0)
        command_layout.addWidget(self.command_field)
        command_layout.addWidget(self.edit_command_button)
        form_layout.addRow("Command", command_row)

        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        self.cancel_button = QPushButton("Cancel")
        self.save_button = QPushButton("Save")
        self.cancel_button.clicked.connect(self.reject)
        self.save_button.clicked.connect(self._handle_submit)
        buttons_layout.addWidget(self.cancel_button)
        buttons_layout.addWidget(self.save_button)

        root_layout = QVBoxLayout(self)
        root_layout.addLayout(form_layout)
        root_layout.addWidget(self.error_label)
        root_layout.addLayout(buttons_layout)

    def set_game_data(self, game_data: dict[str, Any]) -> None:
        self.is_edit_mode = True
        self.name_field.setText(str(game_data.get("name", "")))
        self.folder_field.setText(str(game_data.get("folder_path", "")))
        run_type = str(game_data.get("run_type", "custom"))
        if run_type in {"custom", "exe", "sh"}:
            self.run_type_combo.setCurrentText(run_type)
        raw_argv = game_data.get("run_argv") or []
        if isinstance(raw_argv, str):
            command_text = raw_argv
        else:
            command_text = " ".join(str(part) for part in raw_argv)
        self.command_field.setText(command_text)
        self.command_field.setReadOnly(True)

    def enable_command_editing(self) -> None:
        self.command_field.setReadOnly(False)
        self.command_field.setFocus()

    def validate(self) -> dict[str, Any]:
        run_argv = _parse_command(self.command_field.text())
        return GameDialogValidator.validate(
            self.name_field.text(),
            self.folder_field.text(),
            run_type=self.run_type_combo.currentText(),
            run_argv=run_argv,
        )

    def _handle_submit(self) -> None:
        result = self.validate()
        if not result["valid"]:
            self.error_label.setText("; ".join(result["errors"].values()))
            return
        self.error_label.setText("")
        self.accept()

    def get_game_data(self) -> dict[str, Any]:
        return {
            "name": self.name_field.text().strip(),
            "folder_path": self.folder_field.text().strip(),
            "run_type": self.run_type_combo.currentText(),
            "run_argv": _parse_command(self.command_field.text()),
        }


def _parse_command(command_text: str) -> list[str]:
    command = command_text.strip()
    if not command:
        return []
    try:
        return shlex.split(command)
    except ValueError:
        return [command]

from __future__ import annotations

from PySide6.QtWidgets import QApplication

from gamelauncher.ui.dialogs.game_dialog import GameDialog, GameDialogValidator


def test_game_dialog_validator_rejects_blank_name_and_bad_folder(tmp_path) -> None:
    validation = GameDialogValidator.validate("", str(tmp_path / "games"))
    assert validation["valid"] is False
    assert "name" in validation["errors"]

    validation = GameDialogValidator.validate("Demo Game", str(tmp_path / "games"))
    assert validation["valid"] is True
    assert validation["errors"] == {}


def test_game_dialog_command_field_is_read_only_until_edit_clicked() -> None:
    app = QApplication.instance() or QApplication([])
    dialog = GameDialog()

    assert dialog.command_field.isReadOnly() is True
    dialog.enable_command_editing()
    assert dialog.command_field.isReadOnly() is False
    app.processEvents()


def test_game_dialog_populates_existing_game_for_edit_mode() -> None:
    app = QApplication.instance() or QApplication([])
    dialog = GameDialog()
    dialog.set_game_data(
        {
            "name": "Quest Runner",
            "folder_path": "/tmp/games/quest",
            "run_type": "exe",
            "run_argv": ["wine", "quest.exe"],
        }
    )

    assert dialog.name_field.text() == "Quest Runner"
    assert dialog.command_field.text() == "wine quest.exe"
    assert dialog.is_edit_mode is True
    app.processEvents()

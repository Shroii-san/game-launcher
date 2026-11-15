from __future__ import annotations

import logging
import sys
from types import TracebackType

from PySide6.QtWidgets import QApplication, QMessageBox


def format_exception_details(
    exc: BaseException,
    context: str | None = None,
) -> str:
    """Build a technical detail string without exposing the raw traceback in UI."""
    lines = [
        f"Exception type: {type(exc).__name__}",
        f"Message: {str(exc) or 'No message'}",
    ]
    if context:
        lines.append(f"Context: {context}")
    return "\n".join(lines)


def build_exception_dialog_text(
    exc: BaseException,
    context: str | None = None,
) -> tuple[str, str]:
    """Return a friendly message for the user and a technical detail string for copy."""
    user_message = f"Terjadi kesalahan yang tidak terduga. ({type(exc).__name__})"
    detail = format_exception_details(exc, context)
    return user_message, detail


def _show_exception_dialog(exc: BaseException, *, context: str | None = None) -> None:
    app = QApplication.instance()
    if app is None:
        return

    user_message, details = build_exception_dialog_text(exc, context)
    parent = app.activeWindow()
    dialog = QMessageBox(parent)
    dialog.setWindowTitle("Terjadi kesalahan")
    dialog.setText(user_message)
    dialog.setInformativeText("Detail teknis telah disimpan di log dan dapat disalin.")
    copy_button = dialog.addButton("Salin detail", QMessageBox.ButtonRole.ActionRole)
    dialog.addButton(QMessageBox.StandardButton.Ok)
    dialog.exec()

    if dialog.clickedButton() is copy_button:
        clipboard = QApplication.clipboard()
        if clipboard is not None:
            clipboard.setText(details)


def _handle_exception(
    exc_type: type[BaseException],
    exc_value: BaseException | None,
    exc_tb: TracebackType | None,
) -> None:
    logger = logging.getLogger("gamelauncher")
    if exc_value is None:
        exc_value = exc_type()

    logger.exception(
        "Unhandled exception: %s",
        exc_value,
        exc_info=(exc_type, exc_value, exc_tb),
    )

    context = "Unhandled exception in UI" if exc_tb is not None else "Unexpected runtime error"
    if exc_value is not None:
        _show_exception_dialog(exc_value, context=context)


def install_global_exception_handler() -> None:
    """Install a Qt-friendly exception hook that logs the crash and shows a user-safe dialog."""
    if getattr(sys, "_gamelauncher_exception_hook_installed", False):
        return

    sys.excepthook = _handle_exception
    sys._gamelauncher_exception_hook_installed = True

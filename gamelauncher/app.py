from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import QApplication, QMessageBox

from gamelauncher.logging_setup import setup_logging
from gamelauncher.startup import ensure_directory, run_startup_checks
from gamelauncher.ui.main_window import MainWindow


def main() -> int:
    logger = setup_logging()
    logger.info("Starting Game Launcher")

    app = QApplication.instance() or QApplication([])
    app.setApplicationName("Game Launcher")

    settings = {
        "games_root": Path.home() / "Games",
        "archive_dir": (Path.home() / "Games") / "_archives",
    }
    startup_result = run_startup_checks(settings, create_missing_dirs=False)

    for warning in startup_result.warnings:
        logger.warning(warning)

    window = MainWindow()

    if startup_result.missing_dirs:
        missing_text = "\n".join(f"- {path}" for path in startup_result.missing_dirs)
        reply = QMessageBox.question(
            window,
            "Direktori tidak ditemukan",
            f"Direktori berikut tidak ditemukan. Ingin dibuat ulang?\n\n{missing_text}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            for path in startup_result.missing_dirs:
                if ensure_directory(path):
                    logger.info("Recovered missing directory: %s", path)

    if startup_result.warnings:
        missing = [warning for warning in startup_result.warnings if "Direktori" not in warning]
        if missing:
            QMessageBox.warning(
                window,
                "Peringatan startup",
                "\n".join(missing),
            )

    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())

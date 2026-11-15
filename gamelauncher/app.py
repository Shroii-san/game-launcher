from __future__ import annotations

from PySide6.QtWidgets import QApplication

from gamelauncher.logging_setup import setup_logging
from gamelauncher.ui.main_window import MainWindow


def main() -> int:
    logger = setup_logging()
    logger.info("Starting Game Launcher")

    app = QApplication.instance() or QApplication([])
    app.setApplicationName("Game Launcher")

    window = MainWindow()
    window.show()

    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

from PySide6.QtWidgets import QApplication, QMainWindow


def main() -> int:
    app = QApplication([])
    app.setApplicationName("Game Launcher")

    window = QMainWindow()
    window.setWindowTitle("Game Launcher")
    window.resize(1200, 800)
    window.show()

    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())

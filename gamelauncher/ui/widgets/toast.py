from __future__ import annotations

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


class Toast(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.current_message = ""
        self._label = QLabel()
        self._label.setWordWrap(True)

        layout = QVBoxLayout(self)
        layout.addWidget(self._label)
        self.setLayout(layout)
        self.setVisible(False)

        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self.hide)

    def show_message(self, message: str, duration_ms: int = 2500) -> None:
        self.current_message = message
        self._label.setText(message)
        self.setVisible(True)
        self.raise_()
        self._timer.stop()
        self._timer.start(duration_ms)

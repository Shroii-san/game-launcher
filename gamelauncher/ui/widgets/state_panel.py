from __future__ import annotations

from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from gamelauncher.ui.state import ViewState


class StatePanel(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.state = ViewState.EMPTY
        self.message = ""

        self._title = QLabel("Empty")
        self._title.setStyleSheet("font-size: 18px; font-weight: 600;")
        self._message = QLabel("No content available")
        self._message.setWordWrap(True)

        layout = QVBoxLayout(self)
        layout.addWidget(self._title)
        layout.addWidget(self._message)
        self.setLayout(layout)

        self.set_state(ViewState.EMPTY, "No games to display.")

    def set_state(self, state: ViewState, message: str) -> None:
        self.state = state
        self.message = message
        self._title.setText(state.label)
        self._message.setText(message)
        self.setProperty("state", state.value)
        style = self.style()
        if style is not None:
            style.unpolish(self)
            style.polish(self)

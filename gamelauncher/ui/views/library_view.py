from __future__ import annotations

from typing import Any

from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QListWidget,
    QListWidgetItem,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from gamelauncher.ui.state import ViewState
from gamelauncher.ui.widgets.state_panel import StatePanel


class LibraryView(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.state = ViewState.LOADING
        self.search_text = ""
        self.layout_mode = "grid"
        self.results: list[dict[str, Any]] = []

        self._toolbar = QWidget()
        self._toolbar_layout = QHBoxLayout(self._toolbar)
        self._toolbar_layout.setContentsMargins(0, 0, 0, 0)

        self._sort_combo = QComboBox()
        self._sort_combo.addItems(["Name", "Status"])
        self._sort_combo.setCurrentText("Name")
        self._sort_combo.currentTextChanged.connect(self._handle_sort_change)

        self._layout_combo = QComboBox()
        self._layout_combo.addItems(["grid", "list"])
        self._layout_combo.setCurrentText("grid")
        self._layout_combo.currentTextChanged.connect(self.set_layout_mode)

        self._toolbar_layout.addStretch()
        self._toolbar_layout.addWidget(self._layout_combo)
        self._toolbar_layout.addWidget(self._sort_combo)

        self.state_panel = StatePanel()
        self.state_panel.set_state(ViewState.LOADING, "Loading library...")

        self._list_widget = QListWidget()
        self._list_widget.setAlternatingRowColors(True)

        self._stack = QStackedWidget()
        self._stack.addWidget(self.state_panel)
        self._stack.addWidget(self._list_widget)
        self._stack.setCurrentWidget(self.state_panel)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._toolbar)
        layout.addWidget(self._stack)

        self.set_results([])

    def _handle_sort_change(self, value: str) -> None:
        self._sort_combo.setCurrentText(value)

    def apply_search(self, text: str) -> None:
        self.search_text = text.strip()
        self._sync_state()

    def set_results(self, results: list[dict[str, Any]]) -> None:
        self.results = results
        self._list_widget.clear()
        for item in results:
            title = str(item.get("name") or item.get("title") or "Untitled")
            self._list_widget.addItem(QListWidgetItem(title))
        self._sync_state()

    def set_layout_mode(self, mode: str) -> None:
        normalized = "grid" if mode.lower() == "grid" else "list"
        self.layout_mode = normalized
        self._layout_combo.setCurrentText(normalized)
        self._sync_state()

    def set_state(self, state: ViewState, message: str) -> None:
        self.state = state
        self.state_panel.set_state(state, message)
        self._stack.setCurrentWidget(self.state_panel)

    def _sync_state(self) -> None:
        if not self.results:
            if self.search_text:
                self.set_state(ViewState.EMPTY, f'No results for "{self.search_text}".')
            else:
                self.set_state(ViewState.EMPTY, "No games to display.")
            return

        self.state = ViewState.SUCCESS
        self.state_panel.set_state(ViewState.SUCCESS, f"{len(self.results)} game(s) ready")
        self._stack.setCurrentWidget(self._list_widget)

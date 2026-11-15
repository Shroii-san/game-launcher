from __future__ import annotations

from PySide6.QtCore import QSettings
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from gamelauncher.ui.dialogs.game_dialog import GameDialog
from gamelauncher.ui.state import ViewState
from gamelauncher.ui.theme import apply_theme
from gamelauncher.ui.views.library_view import LibraryView
from gamelauncher.ui.widgets.toast import Toast


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.settings = QSettings("Shroii-san", "GameLauncher")
        self.current_theme = self.settings.value("theme", "light", type=str)
        self.library_view = LibraryView(self)
        self.toast = Toast(self)
        self.theme_button = QPushButton("Dark mode")
        self.add_game_button = QPushButton("Add game")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search games...")
        self.search_input.setClearButtonEnabled(True)
        self.search_input.textChanged.connect(self.library_view.apply_search)
        self.add_game_button.clicked.connect(self.open_game_dialog)

        self._build_ui()
        self.set_theme(self.current_theme or "light")
        self.set_state(ViewState.LOADING, "Loading library...")

    def _build_ui(self) -> None:
        self.setWindowTitle("Game Launcher")
        self.resize(1200, 800)

        central_widget = QWidget(self)
        root_layout = QVBoxLayout(central_widget)
        root_layout.setContentsMargins(20, 20, 20, 20)
        root_layout.setSpacing(18)

        header_layout = QHBoxLayout()
        title_label = QLabel("Game Launcher")
        title_label.setStyleSheet("font-size: 24px; font-weight: 600;")
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.search_input)
        header_layout.addWidget(self.add_game_button)
        header_layout.addWidget(self.theme_button)
        self.theme_button.clicked.connect(self.toggle_theme)

        root_layout.addLayout(header_layout)

        self.content_panel = QWidget()
        content_layout = QVBoxLayout(self.content_panel)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.addWidget(self.library_view, stretch=1)
        root_layout.addWidget(self.content_panel, stretch=1)

        self.setCentralWidget(central_widget)

    def set_theme(self, theme_name: str) -> None:
        self.current_theme = theme_name
        self.settings.setValue("theme", theme_name)
        apply_theme(self, theme_name)
        if theme_name == "dark":
            self.theme_button.setText("Light mode")
        else:
            self.theme_button.setText("Dark mode")

    def toggle_theme(self) -> None:
        next_theme = "dark" if self.current_theme == "light" else "light"
        self.set_theme(next_theme)

    def set_state(self, state: ViewState, message: str) -> None:
        self.library_view.set_state(state, message)

    def open_game_dialog(self) -> None:
        dialog = GameDialog(self)
        dialog.exec()

    def show_toast(self, message: str, duration_ms: int = 2500) -> None:
        self.toast.show_message(message, duration_ms)

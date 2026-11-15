from __future__ import annotations

from typing import Any

THEMES: dict[str, str] = {
    "light": """
        QWidget { background: #f5f3ee; color: #1f2937; }
        QMainWindow { background: #f5f3ee; }
        QLabel { color: #1f2937; }
        StatePanel, Toast {
            background: #ffffff;
            border: 1px solid #d6d3d1;
            border-radius: 12px;
        }
        QPushButton {
            background: #e7e5e4;
            border: 1px solid #d6d3d1;
            border-radius: 8px;
            padding: 6px 12px;
        }
    """,
    "dark": """
        QWidget { background: #111827; color: #f9fafb; }
        QMainWindow { background: #111827; }
        QLabel { color: #f9fafb; }
        StatePanel, Toast {
            background: #1f2937;
            border: 1px solid #374151;
            border-radius: 12px;
        }
        QPushButton {
            background: #374151;
            border: 1px solid #4b5563;
            border-radius: 8px;
            padding: 6px 12px;
        }
    """,
}


def apply_theme(target: Any, theme_name: str = "light") -> str:
    stylesheet = THEMES.get(theme_name, THEMES["light"])
    if hasattr(target, "setStyleSheet"):
        target.setStyleSheet(stylesheet)
    return stylesheet

from __future__ import annotations

from pathlib import Path
from typing import Any

from gamelauncher.core.errors import ValidationError
from gamelauncher.services.exe_detector import detect_executable
from gamelauncher.services.game_service import GameService


class ManualGameService:
    """Create a game entry from a selected folder by detecting its launcher."""

    def __init__(self, conn: Any) -> None:
        self.conn = conn
        self.game_service = GameService(conn)

    def add_from_folder(
        self,
        folder_path: str | Path,
        *,
        name: str | None = None,
    ) -> dict[str, Any]:
        root = Path(folder_path).expanduser()
        if not root.exists() or not root.is_dir():
            raise ValidationError(
                "INVALID_PATH",
                "Selected folder is not a valid directory.",
                user_message="Selected folder is not a valid directory.",
            )

        detected = detect_executable(root)
        if detected is None:
            raise ValidationError(
                "EXE_NOT_FOUND",
                "No executable launcher found in the selected folder.",
                user_message="No executable launcher found in the selected folder.",
            )

        run_type = "exe" if detected.suffix.lower() == ".exe" else "sh"
        payload = {
            "name": (name or root.name).strip() or root.name,
            "folder_path": str(root),
            "run_type": run_type,
            "run_argv": [str(detected)],
            "run_env": {},
            "description": "",
        }
        return self.game_service.create_game(**payload)

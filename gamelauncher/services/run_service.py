from __future__ import annotations

import os
import shutil
import subprocess
from collections.abc import Mapping
from typing import Any

from gamelauncher.core.errors import LaunchError
from gamelauncher.launcher import build_command


class RunService:
    """Launch a game while preventing double-launch of the same game."""

    def __init__(self) -> None:
        self._running: dict[int, int] = {}
        self._last_exit_codes: dict[int, int] = {}

    def launch(self, game: Mapping[str, Any]) -> dict[str, Any]:
        game_id = int(game.get("id", -1))
        if game_id in self._running:
            raise LaunchError(
                "GAME_ALREADY_RUNNING",
                "Game is already running.",
                user_message="Game is already running.",
            )

        run_type = str(game.get("run_type", "custom")).lower()
        if run_type == "exe" and shutil.which("wine") is None:
            raise LaunchError(
                "WINE_MISSING",
                "Wine is required to run this game.",
                user_message="Wine is required to run this game.",
            )

        command = build_command(game)
        cwd = str(game.get("folder_path") or ".")
        env = os.environ.copy()
        run_env = dict(game.get("run_env") or {})
        env.update({str(k): str(v) for k, v in run_env.items()})

        completed = subprocess.run(
            command,
            cwd=cwd,
            env=env,
            text=True,
            capture_output=True,
            check=False,
        )

        self._running[game_id] = completed.returncode
        self._last_exit_codes[game_id] = completed.returncode
        return {
            "game_id": game_id,
            "command": command,
            "cwd": cwd,
            "exit_code": completed.returncode,
            "running": True,
            "stdout": completed.stdout,
            "stderr": completed.stderr,
        }

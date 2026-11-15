from __future__ import annotations

import sqlite3
from pathlib import Path

from gamelauncher.core.errors import ValidationError
from gamelauncher.core.paths import validate_path

DEFAULT_GAMES_ROOT = Path.home() / "Games"


class SettingsService:
    """Manage persisted filesystem settings with validation and confirmation checks."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def get_setting(self, key: str, default: str | None = None) -> str | None:
        row = self.conn.execute(
            "SELECT value FROM settings WHERE key = ?",
            (key,),
        ).fetchone()
        if row is None:
            return default
        return row["value"]

    def get_settings(self) -> dict[str, Path]:
        return {
            "games_root": self.get_games_root(),
            "archive_dir": self.get_archive_dir(),
        }

    def get_games_root(self) -> Path:
        value = self.get_setting("games_root")
        if value is None:
            return DEFAULT_GAMES_ROOT
        return Path(value).expanduser()

    def get_archive_dir(self) -> Path:
        value = self.get_setting("archive_dir")
        if value is not None:
            return Path(value).expanduser()
        return self.get_games_root() / "_archives"

    def set_games_root(self, path: str | Path, *, confirmed: bool = False) -> Path:
        return self._set_directory_setting("games_root", path, confirmed=confirmed)

    def set_archive_dir(self, path: str | Path, *, confirmed: bool = False) -> Path:
        return self._set_directory_setting("archive_dir", path, confirmed=confirmed)

    def update_directories(
        self,
        *,
        games_root: str | Path | None = None,
        archive_dir: str | Path | None = None,
        confirmed: bool = False,
    ) -> dict[str, Path]:
        if games_root is not None:
            self.set_games_root(games_root, confirmed=confirmed)
        if archive_dir is not None:
            self.set_archive_dir(archive_dir, confirmed=confirmed)
        return self.get_settings()

    def _set_directory_setting(
        self,
        key: str,
        path: str | Path,
        *,
        confirmed: bool,
    ) -> Path:
        if not confirmed:
            raise ValidationError(
                "CONFIRMATION_REQUIRED",
                "Directory change requires confirmation before it is saved.",
                user_message="Directory change requires confirmation.",
            )

        candidate = validate_path(path)
        if candidate.exists() and not candidate.is_dir():
            raise ValidationError(
                "INVALID_PATH",
                "Directory path must reference a directory.",
                user_message="Directory path must reference a directory.",
            )

        candidate.mkdir(parents=True, exist_ok=True)
        self.conn.execute(
            "INSERT INTO settings (key, value) VALUES (?, ?) "
            "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
            (key, str(candidate)),
        )
        self.conn.commit()
        return candidate

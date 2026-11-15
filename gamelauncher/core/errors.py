from __future__ import annotations

from gamelauncher.core.messages import get_user_message


class LauncherError(Exception):
    """Base exception for user-facing launcher failures."""

    def __init__(self, code: str, detail: str = "", user_message: str | None = None) -> None:
        self.code = code
        self.detail = detail
        self.user_message = user_message or get_user_message(code)
        super().__init__(self.user_message)


class ArchiveError(LauncherError):
    pass


class MediaError(LauncherError):
    pass


class LaunchError(LauncherError):
    pass


class ConfigError(LauncherError):
    pass


class ValidationError(LauncherError):
    pass

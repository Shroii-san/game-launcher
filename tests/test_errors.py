import pytest

from gamelauncher.core.errors import (
    ArchiveError,
    ConfigError,
    LauncherError,
    LaunchError,
    MediaError,
    ValidationError,
)
from gamelauncher.core.messages import ERROR_MESSAGES, get_user_message


@pytest.mark.parametrize(
    ("error_cls", "code", "detail"),
    [
        (ArchiveError, "ARCHIVE_CORRUPT", "7z reported CRC mismatch"),
        (MediaError, "MEDIA_INVALID", "Not a valid image"),
        (LaunchError, "WINE_MISSING", "wine command not found"),
        (ConfigError, "PATH_FORBIDDEN", "/etc"),
        (ValidationError, "INVALID_NAME", "Game name cannot be blank"),
    ],
)
def test_specific_errors_expose_code_and_message(error_cls, code, detail) -> None:
    err = error_cls(code, detail)

    assert err.code == code
    assert err.detail == detail
    assert err.user_message == ERROR_MESSAGES[code]
    assert str(err) == ERROR_MESSAGES[code]


def test_get_user_message_returns_friendly_text_for_known_error() -> None:
    err = LauncherError("DISK_FULL", "Not enough free space")

    assert get_user_message(err) == ERROR_MESSAGES["DISK_FULL"]


def test_get_user_message_uses_default_for_unknown_error() -> None:
    err = LauncherError("UNKNOWN_ERROR", "Some unexpected issue")

    assert get_user_message(err) == "Terjadi kesalahan yang tidak terduga."

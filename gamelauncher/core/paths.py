from __future__ import annotations

from pathlib import Path

from gamelauncher.core.errors import ValidationError

SYSTEM_DIRECTORIES = {
    Path("/"),
    Path("/bin"),
    Path("/boot"),
    Path("/dev"),
    Path("/etc"),
    Path("/home"),
    Path("/lib"),
    Path("/media"),
    Path("/opt"),
    Path("/proc"),
    Path("/root"),
    Path("/run"),
    Path("/sbin"),
    Path("/srv"),
    Path("/sys"),
    Path("/tmp"),
    Path("/usr"),
    Path("/var"),
}


def _resolve_path(raw_path: str | Path) -> Path:
    if raw_path is None:
        raise ValidationError(
            "INVALID_PATH",
            "Path cannot be empty.",
            user_message="Path cannot be empty.",
        )

    candidate = Path(raw_path)
    if not str(candidate).strip():
        raise ValidationError(
            "INVALID_PATH",
            "Path cannot be empty.",
            user_message="Path cannot be empty.",
        )

    if ".." in candidate.parts:
        raise ValidationError(
            "PATH_FORBIDDEN",
            "Path traversal is not allowed.",
            user_message="Path traversal is not allowed.",
        )

    resolved = candidate.expanduser().resolve(strict=False)
    if resolved in SYSTEM_DIRECTORIES or any(
        part in {"bin", "etc", "usr", "sbin", "lib", "sys", "var"} for part in resolved.parts
    ):
        raise ValidationError(
            "PATH_FORBIDDEN",
            "Path points to a system directory.",
            user_message="Path points to a system directory.",
        )

    return resolved


def validate_path(path: str | Path, *, base_dir: str | Path | None = None) -> Path:
    """Validate a user-supplied path for game storage and execution targets."""

    resolved = _resolve_path(path)

    candidate = Path(path)
    if candidate.is_symlink():
        raise ValidationError(
            "PATH_FORBIDDEN",
            "symlink path is not allowed.",
            user_message="symlink path is not allowed.",
        )

    if base_dir is not None:
        allowed_root = Path(base_dir).expanduser().resolve(strict=False)
        try:
            resolved.relative_to(allowed_root)
        except ValueError as exc:
            raise ValidationError(
                "PATH_FORBIDDEN",
                "Path is outside the allowed base directory.",
                user_message="Path is outside the allowed base directory.",
            ) from exc

    if resolved.exists() and resolved.is_symlink():
        raise ValidationError(
            "PATH_FORBIDDEN",
            "symlink path is not allowed.",
            user_message="symlink path is not allowed.",
        )

    return resolved

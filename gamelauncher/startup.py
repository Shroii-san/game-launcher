from __future__ import annotations

import shutil
from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path

DEFAULT_GAMES_ROOT = Path.home() / "Games"


@dataclass(frozen=True)
class StartupCheckResult:
    warnings: list[str] = field(default_factory=list)
    recovered_dirs: list[str] = field(default_factory=list)
    missing_dirs: list[str] = field(default_factory=list)


def ensure_directory(path: str | Path) -> bool:
    """Create a directory if it is missing and return whether it exists."""
    target = Path(path).expanduser()
    if target.exists():
        return True
    target.mkdir(parents=True, exist_ok=True)
    return True


def check_runtime_dependencies() -> list[str]:
    """Return warnings for missing runtime tools that are optional at startup."""
    dependency_map = {
        "wine": "Wine",
        "7z": "7z",
    }

    warnings: list[str] = []
    for binary_name, label in dependency_map.items():
        if shutil.which(binary_name) is None:
            warnings.append(f"{label} tidak terpasang. Beberapa fitur mungkin tidak tersedia.")
    return warnings


def run_startup_checks(
    settings: Mapping[str, object] | None = None,
    *,
    create_missing_dirs: bool = False,
) -> StartupCheckResult:
    """Collect startup warnings and recover missing configured directories."""
    normalized = dict(settings or {})
    warnings = check_runtime_dependencies()
    recovered_dirs: list[str] = []
    missing_dirs: list[str] = []

    for key in ("games_root", "archive_dir"):
        value = normalized.get(key)
        if value is None:
            continue

        path = Path(str(value)).expanduser()
        if path.exists():
            continue

        if create_missing_dirs:
            ensure_directory(path)
            recovered_dirs.append(str(path))
            continue

        missing_dirs.append(str(path))

    if missing_dirs:
        warnings.append(
            "Direktori konfigurasi tidak ditemukan. "
            "Aplikasi akan menanyakan apakah ingin dibuat ulang."
        )

    return StartupCheckResult(
        warnings=warnings,
        recovered_dirs=recovered_dirs,
        missing_dirs=missing_dirs,
    )

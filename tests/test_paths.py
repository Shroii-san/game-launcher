from pathlib import Path

import pytest

from gamelauncher.core.errors import ValidationError
from gamelauncher.core.paths import validate_path


def test_validate_path_rejects_traversal_segments(tmp_path: Path) -> None:
    bad_path = tmp_path / "games" / ".." / "settings"

    with pytest.raises(ValidationError, match="Path traversal"):
        validate_path(bad_path)


def test_validate_path_rejects_symlink_outside_base(tmp_path: Path) -> None:
    safe_root = tmp_path / "safe"
    safe_root.mkdir()
    outside = tmp_path / "outside"
    outside.mkdir()
    marker = outside / "evil.txt"
    marker.write_text("bad", encoding="utf-8")
    link_path = safe_root / "link"
    link_path.symlink_to(outside)

    with pytest.raises(ValidationError, match="symlink"):
        validate_path(link_path, base_dir=safe_root)


def test_validate_path_rejects_system_directories() -> None:
    for bad in ["/", "/etc", "/usr", "/bin"]:
        with pytest.raises(ValidationError, match="system"):
            validate_path(bad)


def test_validate_path_accepts_safe_directory(tmp_path: Path) -> None:
    base_dir = tmp_path / "games"
    base_dir.mkdir()
    safe = base_dir / "Game One"

    result = validate_path(safe, base_dir=base_dir)

    assert result == safe.resolve()

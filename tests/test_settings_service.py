from pathlib import Path

import pytest

from gamelauncher.core.errors import ValidationError
from gamelauncher.db.engine import get_connection
from gamelauncher.db.migration import upgrade_database
from gamelauncher.services.settings_service import SettingsService


def test_settings_service_uses_default_paths_when_missing(tmp_path) -> None:
    db_path = tmp_path / "launcher.db"
    upgrade_database(db_path)
    conn = get_connection(db_path)
    service = SettingsService(conn)

    assert service.get_games_root() == Path.home() / "Games"
    assert service.get_archive_dir() == Path.home() / "Games" / "_archives"


def test_settings_service_updates_and_creates_directories(tmp_path) -> None:
    db_path = tmp_path / "launcher.db"
    upgrade_database(db_path)
    conn = get_connection(db_path)
    service = SettingsService(conn)

    games_root = tmp_path / "custom" / "games"
    archive_dir = tmp_path / "custom" / "archives"

    service.update_directories(
        games_root=str(games_root),
        archive_dir=str(archive_dir),
        confirmed=True,
    )

    assert service.get_games_root() == games_root
    assert service.get_archive_dir() == archive_dir
    assert games_root.exists()
    assert archive_dir.exists()


def test_settings_service_requires_confirmation_and_rejects_bad_paths(tmp_path) -> None:
    db_path = tmp_path / "launcher.db"
    upgrade_database(db_path)
    conn = get_connection(db_path)
    service = SettingsService(conn)

    with pytest.raises(ValidationError, match="confirmation"):
        service.set_games_root(str(tmp_path / "new-root"), confirmed=False)

    with pytest.raises(ValidationError, match="Path traversal is not allowed"):
        service.set_games_root("../outside-root", confirmed=True)

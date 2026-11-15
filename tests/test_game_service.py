import pytest

from gamelauncher.core.errors import ValidationError
from gamelauncher.db.engine import get_connection
from gamelauncher.db.migration import upgrade_database
from gamelauncher.services.game_service import GameService


def test_game_service_creates_game_and_keeps_fts_in_sync(tmp_path) -> None:
    db_path = tmp_path / "launcher.db"
    upgrade_database(db_path)
    conn = get_connection(db_path)
    service = GameService(conn)

    genre_id = conn.execute("SELECT id FROM genres WHERE name = 'Action'").fetchone()["id"]

    created = service.create_game(
        name="Test Game",
        folder_path=str(tmp_path / "games" / "Test Game"),
        run_type="exe",
        run_argv=["wine", "game.exe"],
        run_env={"WINEPREFIX": "/tmp/prefix"},
        description="Deskripsi uji coba",
        genre_ids=[genre_id],
    )

    assert created["name"] == "Test Game"
    assert created["genre_ids"] == [genre_id]

    fts_row = conn.execute(
        "SELECT name, description FROM games_fts WHERE rowid = ?",
        (created["id"],),
    ).fetchone()
    assert fts_row is not None
    assert fts_row["name"] == "Test Game"
    assert fts_row["description"] == "Deskripsi uji coba"

    updated = service.update_game(
        created["id"],
        description="Deskripsi baru",
        run_argv=["wine", "updated.exe"],
    )
    assert updated["description"] == "Deskripsi baru"
    assert updated["run_argv"] == ["wine", "updated.exe"]

    synced = conn.execute(
        "SELECT description FROM games_fts WHERE rowid = ?",
        (created["id"],),
    ).fetchone()
    assert synced is not None
    assert synced["description"] == "Deskripsi baru"


def test_game_service_rejects_invalid_path(tmp_path) -> None:
    db_path = tmp_path / "launcher.db"
    upgrade_database(db_path)
    conn = get_connection(db_path)
    service = GameService(conn)

    with pytest.raises(ValidationError, match="Path traversal is not allowed"):
        service.create_game(
            name="Bad Game",
            folder_path="../outside-game",
        )

import pytest

from gamelauncher.core.errors import ValidationError
from gamelauncher.db.engine import get_connection
from gamelauncher.db.migration import upgrade_database
from gamelauncher.services.manual_game_service import ManualGameService


def test_manual_game_service_creates_game_from_selected_folder(tmp_path) -> None:
    game_dir = tmp_path / "My Game Bundle"
    game_dir.mkdir()
    exe_path = game_dir / "game.exe"
    exe_path.write_bytes(b"")

    db_path = tmp_path / "launcher.db"
    upgrade_database(db_path)
    conn = get_connection(db_path)
    service = ManualGameService(conn)

    created = service.add_from_folder(game_dir)

    assert created["name"] == "My Game Bundle"
    assert created["run_type"] == "exe"
    assert created["run_argv"] == [str(exe_path)]
    assert created["folder_path"] == str(game_dir)


def test_manual_game_service_rejects_folder_without_usable_launcher(tmp_path) -> None:
    game_dir = tmp_path / "No Launcher"
    game_dir.mkdir()
    (game_dir / "readme.txt").write_text("just a text file")

    db_path = tmp_path / "launcher.db"
    upgrade_database(db_path)
    conn = get_connection(db_path)
    service = ManualGameService(conn)

    with pytest.raises(ValidationError) as exc:
        service.add_from_folder(game_dir)

    assert exc.value.code == "EXE_NOT_FOUND"

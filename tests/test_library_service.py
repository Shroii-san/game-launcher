from gamelauncher.db.engine import get_connection
from gamelauncher.db.migration import upgrade_database
from gamelauncher.services.game_service import GameService
from gamelauncher.services.library_service import LibraryService


def test_library_service_filters_and_pages_results(tmp_path) -> None:
    db_path = tmp_path / "launcher.db"
    upgrade_database(db_path)
    conn = get_connection(db_path)

    game_service = GameService(conn)
    genre_id = conn.execute("SELECT id FROM genres WHERE name = 'Action'").fetchone()["id"]
    tag_row = conn.execute("SELECT id FROM tags WHERE name = 'Co-op'").fetchone()
    if tag_row is None:
        conn.execute("INSERT INTO tags (name) VALUES ('Co-op')")
        conn.commit()
    tag_id = conn.execute("SELECT id FROM tags WHERE name = 'Co-op'").fetchone()["id"]

    game_service.create_game(
        name="Alpha Quest",
        folder_path=str(tmp_path / "games" / "Alpha Quest"),
        genre_ids=[genre_id],
        tag_ids=[tag_id],
    )
    game_service.create_game(
        name="Beta Quest",
        folder_path=str(tmp_path / "games" / "Beta Quest"),
        genre_ids=[genre_id],
        tag_ids=[tag_id],
    )
    game_service.create_game(
        name="Gamma Story",
        folder_path=str(tmp_path / "games" / "Gamma Story"),
        genre_ids=[genre_id],
    )

    library = LibraryService(conn)
    rows = library.list_games(query="quest", genre_ids=[genre_id], tag_ids=[tag_id], limit=1)

    assert [row["name"] for row in rows] == ["Alpha Quest"]

    page_two = library.list_games(
        query="quest",
        genre_ids=[genre_id],
        tag_ids=[tag_id],
        limit=1,
        last_name="Alpha Quest",
        last_id=1,
    )
    assert [row["name"] for row in page_two] == ["Beta Quest"]


def test_library_service_ignores_games_outside_filter(tmp_path) -> None:
    db_path = tmp_path / "launcher.db"
    upgrade_database(db_path)
    conn = get_connection(db_path)

    game_service = GameService(conn)
    genre_id = conn.execute("SELECT id FROM genres WHERE name = 'Action'").fetchone()["id"]
    other_genre_id = conn.execute("SELECT id FROM genres WHERE name = 'Adventure'").fetchone()["id"]

    game_service.create_game(
        name="Solo Action",
        folder_path=str(tmp_path / "games" / "Solo Action"),
        genre_ids=[genre_id],
    )
    game_service.create_game(
        name="Other Adventure",
        folder_path=str(tmp_path / "games" / "Other Adventure"),
        genre_ids=[other_genre_id],
    )

    library = LibraryService(conn)
    rows = library.list_games(query="", genre_ids=[genre_id])
    assert [row["name"] for row in rows] == ["Solo Action"]

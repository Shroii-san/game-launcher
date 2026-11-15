from gamelauncher.core.constants import DEFAULT_GENRES
from gamelauncher.db.engine import get_connection
from gamelauncher.db.migration import upgrade_database
from gamelauncher.db.repositories.games import GameRepository
from gamelauncher.db.repositories.taxonomy import TaxonomyRepository


def test_taxonomy_repository_crud_and_relation(tmp_path) -> None:
    db_path = tmp_path / "launcher.db"
    upgrade_database(db_path)
    conn = get_connection(db_path)

    taxonomy = TaxonomyRepository(conn)
    genre_id = taxonomy.create_genre("Action")
    developer_id = taxonomy.create_developer("Studio Test")
    tag_id = taxonomy.create_tag("Co-op")

    assert taxonomy.get_genre(genre_id)["name"] == "Action"
    assert taxonomy.get_developer(developer_id)["name"] == "Studio Test"
    assert taxonomy.get_tag(tag_id)["name"] == "Co-op"

    game_repo = GameRepository(conn)
    game_id = game_repo.create_game(
        name="Test Game",
        folder_path=str(tmp_path / "games" / "Test Game"),
        run_type="exe",
        run_argv='["wine", "game.exe"]',
        run_env='{"WINEPREFIX": "/tmp/prefix"}',
        genre_ids=[genre_id],
        developer_ids=[developer_id],
        tag_ids=[tag_id],
    )

    saved = game_repo.get_game(game_id)
    assert saved["name"] == "Test Game"
    assert saved["genre_ids"] == [genre_id]
    assert saved["developer_ids"] == [developer_id]
    assert saved["tag_ids"] == [tag_id]

    updated = game_repo.update_game(
        game_id,
        name="Updated Game",
        description="new description",
        genre_ids=[genre_id],
        developer_ids=[],
        tag_ids=[],
    )
    assert updated["name"] == "Updated Game"
    assert updated["description"] == "new description"
    assert updated["developer_ids"] == []
    assert updated["tag_ids"] == []

    game_repo.delete_game(game_id)
    assert game_repo.get_game(game_id) is None


def test_default_genres_are_seeded_for_taxonomy_repository(tmp_path) -> None:
    db_path = tmp_path / "launcher.db"
    upgrade_database(db_path)
    conn = get_connection(db_path)

    taxonomy = TaxonomyRepository(conn)
    rows = taxonomy.list_genres()

    assert [row["name"] for row in rows[:3]] == list(DEFAULT_GENRES[:3])
    assert any(row["is_default"] == 1 for row in rows)

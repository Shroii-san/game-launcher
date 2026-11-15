import sqlite3

from gamelauncher.core.constants import DEFAULT_DESCRIPTION_TEMPLATE, DEFAULT_GENRES
from gamelauncher.db.migration import upgrade_database


def test_upgrade_database_creates_schema_and_seed_data(tmp_path) -> None:
    db_path = tmp_path / "launcher.db"

    upgrade_database(db_path)

    with sqlite3.connect(db_path) as conn:
        tables = {
            row[0]
            for row in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
            )
        }
        assert {"games", "genres", "settings"}.issubset(tables)

        genre_names = [
            row[0]
            for row in conn.execute("SELECT name FROM genres WHERE is_default = 1 ORDER BY id")
        ]
        assert genre_names == list(DEFAULT_GENRES)

        template = conn.execute(
            "SELECT value FROM settings WHERE key = 'default_description_template'"
        ).fetchone()
        assert template is not None
        assert template[0] == DEFAULT_DESCRIPTION_TEMPLATE

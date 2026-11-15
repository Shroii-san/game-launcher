"""Initial schema and default seed data.

Revision ID: 20261115_0001
Revises:
Create Date: 2026-11-15 00:00:00.000000
"""

from __future__ import annotations

from alembic import op

from gamelauncher.core.constants import DEFAULT_DESCRIPTION_TEMPLATE, DEFAULT_GENRES

revision = "20261115_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("PRAGMA foreign_keys = ON")
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS games (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL CHECK (length(name) BETWEEN 1 AND 200),
            folder_path TEXT NOT NULL UNIQUE,
            run_type TEXT NOT NULL DEFAULT 'custom' CHECK (
                run_type IN ('exe', 'sh', 'custom')
            ),
            run_argv TEXT NOT NULL DEFAULT '[]',
            run_env TEXT NOT NULL DEFAULT '{}',
            run_cwd TEXT,
            needs_confirmation INTEGER NOT NULL DEFAULT 0 CHECK (
                needs_confirmation IN (0, 1)
            ),
            wine_prefix_mode TEXT NOT NULL DEFAULT 'global' CHECK (
                wine_prefix_mode IN ('global', 'per_game')
            ),
            status TEXT NOT NULL DEFAULT 'none' CHECK (
                status IN ('none', 'completed', 'stalled')
            ),
            description TEXT NOT NULL DEFAULT '',
            is_missing INTEGER NOT NULL DEFAULT 0 CHECK (is_missing IN (0, 1)),
            play_count INTEGER NOT NULL DEFAULT 0,
            last_played_at TEXT,
            created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
            updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
        )
        """
    )
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS genres (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL UNIQUE COLLATE NOCASE CHECK (length(name) BETWEEN 1 AND 50),
            is_default INTEGER NOT NULL DEFAULT 0 CHECK (is_default IN (0, 1))
        )
        """
    )
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS tags (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL UNIQUE COLLATE NOCASE CHECK (length(name) BETWEEN 1 AND 50)
        )
        """
    )
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS developers (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL UNIQUE COLLATE NOCASE CHECK (length(name) BETWEEN 1 AND 100)
        )
        """
    )
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS user_groups (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL UNIQUE COLLATE NOCASE CHECK (length(name) BETWEEN 1 AND 50),
            sort_order INTEGER NOT NULL DEFAULT 0
        )
        """
    )
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
        """
    )
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS game_genres (
            game_id INTEGER NOT NULL REFERENCES games(id) ON DELETE CASCADE,
            genre_id INTEGER NOT NULL REFERENCES genres(id) ON DELETE CASCADE,
            PRIMARY KEY (game_id, genre_id)
        )
        """
    )
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS game_tags (
            game_id INTEGER NOT NULL REFERENCES games(id) ON DELETE CASCADE,
            tag_id INTEGER NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
            PRIMARY KEY (game_id, tag_id)
        )
        """
    )
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS game_developers (
            game_id INTEGER NOT NULL REFERENCES games(id) ON DELETE CASCADE,
            developer_id INTEGER NOT NULL REFERENCES developers(id) ON DELETE CASCADE,
            PRIMARY KEY (game_id, developer_id)
        )
        """
    )
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS game_user_groups (
            game_id INTEGER NOT NULL REFERENCES games(id) ON DELETE CASCADE,
            group_id INTEGER NOT NULL REFERENCES user_groups(id) ON DELETE CASCADE,
            PRIMARY KEY (game_id, group_id)
        )
        """
    )
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS media (
            id INTEGER PRIMARY KEY,
            game_id INTEGER NOT NULL REFERENCES games(id) ON DELETE CASCADE,
            kind TEXT NOT NULL CHECK (kind IN ('image', 'video')),
            source_type TEXT NOT NULL CHECK (source_type IN ('local', 'url')),
            source_ref TEXT,
            stored_path TEXT,
            thumb_path TEXT,
            sha256 TEXT,
            width INTEGER,
            height INTEGER,
            duration_ms INTEGER,
            size_bytes INTEGER,
            status TEXT NOT NULL DEFAULT 'pending' CHECK (
                status IN ('pending', 'processing', 'ready', 'failed')
            ),
            error_code TEXT,
            is_cover INTEGER NOT NULL DEFAULT 0 CHECK (is_cover IN (0, 1)),
            sort_order INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
        )
        """
    )
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS mods (
            id INTEGER PRIMARY KEY,
            game_id INTEGER NOT NULL REFERENCES games(id) ON DELETE CASCADE,
            kind TEXT NOT NULL CHECK (kind IN ('mod', 'save')),
            name TEXT NOT NULL CHECK (length(name) BETWEEN 1 AND 200),
            stored_path TEXT NOT NULL,
            size_bytes INTEGER,
            note TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
        )
        """
    )
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS install_links (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL CHECK (length(name) BETWEEN 1 AND 100),
            url TEXT NOT NULL CHECK (url LIKE 'http://%' OR url LIKE 'https://%'),
            sort_order INTEGER NOT NULL DEFAULT 0
        )
        """
    )
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY,
            type TEXT NOT NULL CHECK (
                type IN ('extract', 'compress_video', 'download_media', 'scan')
            ),
            status TEXT NOT NULL DEFAULT 'queued' CHECK (
                status IN ('queued', 'running', 'done', 'failed', 'cancelled')
            ),
            game_id INTEGER REFERENCES games(id) ON DELETE SET NULL,
            payload TEXT NOT NULL DEFAULT '{}',
            progress INTEGER NOT NULL DEFAULT 0 CHECK (progress BETWEEN 0 AND 100),
            error_code TEXT,
            error_detail TEXT,
            created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
            started_at TEXT,
            finished_at TEXT
        )
        """
    )
    op.execute(
        """
        CREATE VIRTUAL TABLE IF NOT EXISTS games_fts USING fts5 (
            name, description, meta,
            tokenize = 'unicode61 remove_diacritics 2'
        )
        """
    )

    op.execute("CREATE INDEX IF NOT EXISTS idx_games_name ON games (name COLLATE NOCASE, id)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_games_created ON games (created_at, id)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_games_last_played ON games (last_played_at, id)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_games_status ON games (status)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_media_game ON media (game_id, status, sort_order)")
    op.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS uq_media_one_cover ON media (game_id) WHERE is_cover = 1"
    )
    op.execute("CREATE INDEX IF NOT EXISTS idx_mods_game ON mods (game_id, kind)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs (status, created_at)")

    for genre_name in DEFAULT_GENRES:
        escaped_name = genre_name.replace("'", "''")
        op.execute(f"INSERT OR IGNORE INTO genres (name, is_default) VALUES ('{escaped_name}', 1)")

    escaped_template = DEFAULT_DESCRIPTION_TEMPLATE.replace("'", "''")
    op.execute(
        "INSERT OR REPLACE INTO settings (key, value) "
        "VALUES ('default_description_template', '"
        f"{escaped_template}'"
        ")"
    )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS games_fts")
    op.execute("DROP TABLE IF EXISTS jobs")
    op.execute("DROP TABLE IF EXISTS install_links")
    op.execute("DROP TABLE IF EXISTS mods")
    op.execute("DROP TABLE IF EXISTS media")
    op.execute("DROP TABLE IF EXISTS game_user_groups")
    op.execute("DROP TABLE IF EXISTS game_developers")
    op.execute("DROP TABLE IF EXISTS game_tags")
    op.execute("DROP TABLE IF EXISTS game_genres")
    op.execute("DROP TABLE IF EXISTS settings")
    op.execute("DROP TABLE IF EXISTS user_groups")
    op.execute("DROP TABLE IF EXISTS developers")
    op.execute("DROP TABLE IF EXISTS tags")
    op.execute("DROP TABLE IF EXISTS genres")
    op.execute("DROP TABLE IF EXISTS games")

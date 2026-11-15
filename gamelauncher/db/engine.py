from __future__ import annotations

import sqlite3
import threading
from pathlib import Path

DEFAULT_DB_PATH = Path.home() / ".local" / "share" / "gamelauncher" / "launcher.db"
_THREAD_CONNECTIONS: threading.local = threading.local()


def _normalize_db_path(db_path: str | Path | None) -> Path:
    if db_path is None:
        return DEFAULT_DB_PATH
    return Path(db_path).expanduser()


def _get_thread_connections() -> dict[str, sqlite3.Connection]:
    if not hasattr(_THREAD_CONNECTIONS, "connections"):
        _THREAD_CONNECTIONS.connections = {}
    return _THREAD_CONNECTIONS.connections


def _apply_pragmas(connection: sqlite3.Connection) -> sqlite3.Connection:
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    connection.execute("PRAGMA journal_mode = WAL")
    connection.execute("PRAGMA busy_timeout = 5000")
    return connection


def get_connection(db_path: str | Path | None = None) -> sqlite3.Connection:
    """Return the SQLite connection bound to the current thread."""

    resolved_path = _normalize_db_path(db_path)
    resolved_path.parent.mkdir(parents=True, exist_ok=True)

    key = str(resolved_path.resolve())
    connections = _get_thread_connections()
    connection = connections.get(key)
    if connection is None:
        connection = sqlite3.connect(str(resolved_path), timeout=30)
        connections[key] = _apply_pragmas(connection)

    return connection


def initialize_database(db_path: str | Path | None = None) -> sqlite3.Connection:
    """Ensure the database directory and required PRAGMA settings are active."""

    connection = get_connection(db_path)
    connection.execute(
        "CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT NOT NULL)"
    )
    return connection


def close_connections() -> None:
    """Close all thread-local database connections for the current thread."""

    for connection in _get_thread_connections().values():
        connection.close()
    _get_thread_connections().clear()

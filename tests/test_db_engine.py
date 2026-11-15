import threading

from gamelauncher.db.engine import get_connection


def test_get_connection_is_thread_local(tmp_path) -> None:
    db_path = tmp_path / "launcher.db"
    main_conn = get_connection(db_path)

    seen: list[object] = []

    def worker() -> None:
        seen.append(get_connection(db_path))

    thread = threading.Thread(target=worker)
    thread.start()
    thread.join()

    assert main_conn is get_connection(db_path)
    assert len(seen) == 1
    assert seen[0] is not main_conn


def test_get_connection_applies_required_pragmas(tmp_path) -> None:
    conn = get_connection(db_path := tmp_path / "launcher.db")

    assert conn.execute("PRAGMA foreign_keys").fetchone()[0] == 1
    assert conn.execute("PRAGMA journal_mode").fetchone()[0].lower() == "wal"
    assert conn.execute("PRAGMA busy_timeout").fetchone()[0] == 5000
    assert str(db_path) in str(conn.execute("PRAGMA database_list").fetchall()[0][2])

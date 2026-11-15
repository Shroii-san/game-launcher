from __future__ import annotations

import sqlite3


class TaxonomyRepository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def _normalize_name(self, value: str) -> str:
        return value.strip()

    def _get_or_create(self, table: str, column: str, name: str) -> int:
        normalized = self._normalize_name(name)
        if not normalized:
            raise ValueError(f"{column} name cannot be empty")

        row = self.conn.execute(
            f"SELECT id FROM {table} WHERE {column} = ? COLLATE NOCASE",
            (normalized,),
        ).fetchone()
        if row is not None:
            return int(row["id"])

        cursor = self.conn.execute(
            f"INSERT INTO {table} ({column}) VALUES (?)",
            (normalized,),
        )
        self.conn.commit()
        return int(cursor.lastrowid)

    def create_genre(self, name: str) -> int:
        return self._get_or_create("genres", "name", name)

    def get_genre(self, genre_id: int) -> dict[str, object] | None:
        row = self.conn.execute(
            "SELECT id, name, is_default FROM genres WHERE id = ?",
            (genre_id,),
        ).fetchone()
        return dict(row) if row is not None else None

    def list_genres(self) -> list[dict[str, object]]:
        rows = self.conn.execute("SELECT id, name, is_default FROM genres ORDER BY id").fetchall()
        return [dict(row) for row in rows]

    def update_genre(
        self,
        genre_id: int,
        name: str,
    ) -> dict[str, object] | None:
        normalized = self._normalize_name(name)
        if not normalized:
            raise ValueError("genre name cannot be empty")
        self.conn.execute(
            "UPDATE genres SET name = ? WHERE id = ?",
            (normalized, genre_id),
        )
        self.conn.commit()
        return self.get_genre(genre_id)

    def delete_genre(self, genre_id: int) -> None:
        self.conn.execute("DELETE FROM genres WHERE id = ?", (genre_id,))
        self.conn.commit()

    def create_developer(self, name: str) -> int:
        return self._get_or_create("developers", "name", name)

    def get_developer(self, developer_id: int) -> dict[str, object] | None:
        row = self.conn.execute(
            "SELECT id, name FROM developers WHERE id = ?",
            (developer_id,),
        ).fetchone()
        return dict(row) if row is not None else None

    def list_developers(self) -> list[dict[str, object]]:
        rows = self.conn.execute("SELECT id, name FROM developers ORDER BY id").fetchall()
        return [dict(row) for row in rows]

    def update_developer(
        self,
        developer_id: int,
        name: str,
    ) -> dict[str, object] | None:
        normalized = self._normalize_name(name)
        if not normalized:
            raise ValueError("developer name cannot be empty")
        self.conn.execute(
            "UPDATE developers SET name = ? WHERE id = ?",
            (normalized, developer_id),
        )
        self.conn.commit()
        return self.get_developer(developer_id)

    def delete_developer(self, developer_id: int) -> None:
        self.conn.execute("DELETE FROM developers WHERE id = ?", (developer_id,))
        self.conn.commit()

    def create_tag(self, name: str) -> int:
        return self._get_or_create("tags", "name", name)

    def get_tag(self, tag_id: int) -> dict[str, object] | None:
        row = self.conn.execute(
            "SELECT id, name FROM tags WHERE id = ?",
            (tag_id,),
        ).fetchone()
        return dict(row) if row is not None else None

    def list_tags(self) -> list[dict[str, object]]:
        rows = self.conn.execute("SELECT id, name FROM tags ORDER BY id").fetchall()
        return [dict(row) for row in rows]

    def update_tag(
        self,
        tag_id: int,
        name: str,
    ) -> dict[str, object] | None:
        normalized = self._normalize_name(name)
        if not normalized:
            raise ValueError("tag name cannot be empty")
        self.conn.execute(
            "UPDATE tags SET name = ? WHERE id = ?",
            (normalized, tag_id),
        )
        self.conn.commit()
        return self.get_tag(tag_id)

    def delete_tag(self, tag_id: int) -> None:
        self.conn.execute("DELETE FROM tags WHERE id = ?", (tag_id,))
        self.conn.commit()

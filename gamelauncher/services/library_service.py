from __future__ import annotations

import sqlite3
from typing import Any


class LibraryService:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def list_games(
        self,
        *,
        query: str = "",
        genre_ids: list[int] | None = None,
        tag_ids: list[int] | None = None,
        status: str | None = None,
        sort_by: str = "name",
        order: str = "asc",
        limit: int = 40,
        last_name: str | None = None,
        last_id: int | None = None,
    ) -> list[dict[str, Any]]:
        clauses: list[str] = []
        params: list[Any] = []

        cleaned_query = query.strip()
        if cleaned_query:
            clauses.append("g.id IN (SELECT rowid FROM games_fts WHERE games_fts MATCH ?)")
            params.append(self._fts_query(cleaned_query))

        if genre_ids:
            for genre_id in genre_ids:
                clauses.append(
                    "EXISTS ("
                    "SELECT 1 FROM game_genres gg "
                    "WHERE gg.game_id = g.id AND gg.genre_id = ?)"
                )
                params.append(genre_id)

        if tag_ids:
            for tag_id in tag_ids:
                clauses.append(
                    "EXISTS (SELECT 1 FROM game_tags gt WHERE gt.game_id = g.id AND gt.tag_id = ?)"
                )
                params.append(tag_id)

        if status is not None:
            clauses.append("g.status = ?")
            params.append(status)

        if last_name is not None and last_id is not None:
            comparison = ">" if order.lower() == "asc" else "<"
            clauses.append(f"(g.name COLLATE NOCASE, g.id) {comparison} (?, ?)")
            params.extend([last_name, last_id])

        order_column = "g.name" if sort_by == "name" else f"g.{sort_by}"
        direction = "ASC" if order.lower() == "asc" else "DESC"

        sql = "SELECT g.id, g.name, g.status, g.folder_path FROM games g"
        if clauses:
            sql += " WHERE " + " AND ".join(clauses)
        sql += f" ORDER BY {order_column} COLLATE NOCASE {direction}, g.id {direction}"
        sql += " LIMIT ?"
        params.append(max(1, min(int(limit), 100)))

        rows = self.conn.execute(sql, params).fetchall()
        return [dict(row) for row in rows]

    @staticmethod
    def _fts_query(value: str) -> str:
        token = value.strip().replace('"', "").replace("'", "")
        if not token:
            return ""
        return token

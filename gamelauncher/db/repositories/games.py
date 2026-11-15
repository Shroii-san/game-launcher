from __future__ import annotations

import json
import sqlite3
from typing import Any


class GameRepository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    @staticmethod
    def _serialize_json(value: str | list[str] | dict[str, str] | None, *, default: str = "[]") -> str:
        if value is None:
            return default
        if isinstance(value, str):
            return value
        return json.dumps(value)

    @staticmethod
    def _parse_json(value: str | None) -> Any:
        if value is None:
            return None
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value

    def create_game(
        self,
        *,
        name: str,
        folder_path: str,
        run_type: str = "custom",
        run_argv: str | list[str] | None = None,
        run_env: str | dict[str, str] | None = None,
        description: str = "",
        genre_ids: list[int] | None = None,
        developer_ids: list[int] | None = None,
        tag_ids: list[int] | None = None,
        group_ids: list[int] | None = None,
    ) -> int:
        payload_argv = self._serialize_json(run_argv, default="[]")
        payload_env = self._serialize_json(run_env, default="{}")

        cursor = self.conn.execute(
            """
            INSERT INTO games (
                name, folder_path, run_type, run_argv, run_env, description,
                needs_confirmation, wine_prefix_mode, status, is_missing, play_count
            ) VALUES (?, ?, ?, ?, ?, ?, 0, 'global', 'none', 0, 0)
            """,
            (
                name,
                folder_path,
                run_type,
                payload_argv,
                payload_env,
                description,
            ),
        )
        self.conn.commit()
        game_id = int(cursor.lastrowid)

        self._replace_relation(game_id, "game_genres", genre_ids or [], "genre_id")
        self._replace_relation(game_id, "game_developers", developer_ids or [], "developer_id")
        self._replace_relation(game_id, "game_tags", tag_ids or [], "tag_id")
        self._replace_relation(game_id, "game_user_groups", group_ids or [], "group_id")
        return game_id

    def get_game(self, game_id: int) -> dict[str, Any] | None:
        row = self.conn.execute(
            """
            SELECT id, name, folder_path, run_type, run_argv, run_env, needs_confirmation,
                   wine_prefix_mode, status, description, is_missing, play_count,
                   last_played_at, created_at, updated_at
            FROM games WHERE id = ?
            """,
            (game_id,),
        ).fetchone()
        if row is None:
            return None

        record = dict(row)
        record["run_argv"] = self._parse_json(record["run_argv"])
        record["run_env"] = self._parse_json(record["run_env"])
        record["genre_ids"] = self._fetch_relation_ids(game_id, "game_genres", "genre_id")
        record["developer_ids"] = self._fetch_relation_ids(game_id, "game_developers", "developer_id")
        record["tag_ids"] = self._fetch_relation_ids(game_id, "game_tags", "tag_id")
        record["group_ids"] = self._fetch_relation_ids(game_id, "game_user_groups", "group_id")
        return record

    def update_game(
        self,
        game_id: int,
        *,
        name: str | None = None,
        folder_path: str | None = None,
        run_type: str | None = None,
        run_argv: str | list[str] | None = None,
        run_env: str | dict[str, str] | None = None,
        description: str | None = None,
        genre_ids: list[int] | None = None,
        developer_ids: list[int] | None = None,
        tag_ids: list[int] | None = None,
        group_ids: list[int] | None = None,
    ) -> dict[str, Any] | None:
        current = self.get_game(game_id)
        if current is None:
            return None

        update_fields: list[tuple[str, Any]] = []
        if name is not None:
            update_fields.append(("name", name))
        if folder_path is not None:
            update_fields.append(("folder_path", folder_path))
        if run_type is not None:
            update_fields.append(("run_type", run_type))
        if run_argv is not None:
            update_fields.append(("run_argv", self._serialize_json(run_argv)))
        if run_env is not None:
            update_fields.append(("run_env", self._serialize_json(run_env)))
        if description is not None:
            update_fields.append(("description", description))

        if update_fields:
            assignments = ", ".join(f"{column} = ?" for column, _ in update_fields)
            params = [value for _, value in update_fields]
            self.conn.execute(
                f"UPDATE games SET {assignments} WHERE id = ?",
                [*params, game_id],
            )

        if genre_ids is not None:
            self._replace_relation(game_id, "game_genres", genre_ids, "genre_id")
        if developer_ids is not None:
            self._replace_relation(game_id, "game_developers", developer_ids, "developer_id")
        if tag_ids is not None:
            self._replace_relation(game_id, "game_tags", tag_ids, "tag_id")
        if group_ids is not None:
            self._replace_relation(game_id, "game_user_groups", group_ids, "group_id")

        self.conn.commit()
        return self.get_game(game_id)

    def delete_game(self, game_id: int) -> None:
        self.conn.execute("DELETE FROM games WHERE id = ?", (game_id,))
        self.conn.commit()

    def _replace_relation(self, game_id: int, table: str, values: list[int], column_name: str) -> None:
        self.conn.execute(f"DELETE FROM {table} WHERE game_id = ?", (game_id,))
        if not values:
            return
        for value in values:
            self.conn.execute(
                f"INSERT INTO {table} (game_id, {column_name}) VALUES (?, ?)",
                (game_id, value),
            )

    def _fetch_relation_ids(self, game_id: int, table: str, column_name: str) -> list[int]:
        rows = self.conn.execute(
            f"SELECT {column_name} FROM {table} WHERE game_id = ? ORDER BY {column_name}",
            (game_id,),
        ).fetchall()
        return [int(row[0]) for row in rows]

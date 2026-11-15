from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class Genre:
    id: int | None = None
    name: str = ""
    is_default: bool = False


@dataclass(slots=True)
class Developer:
    id: int | None = None
    name: str = ""


@dataclass(slots=True)
class Tag:
    id: int | None = None
    name: str = ""


@dataclass(slots=True)
class UserGroup:
    id: int | None = None
    name: str = ""
    sort_order: int = 0


@dataclass(slots=True)
class Media:
    id: int | None = None
    game_id: int | None = None
    kind: str = "image"
    source_type: str = "local"
    source_ref: str | None = None
    stored_path: str | None = None
    thumb_path: str | None = None
    sha256: str | None = None
    width: int | None = None
    height: int | None = None
    duration_ms: int | None = None
    size_bytes: int | None = None
    status: str = "pending"
    error_code: str | None = None
    is_cover: bool = False
    sort_order: int = 0
    created_at: str | None = None


@dataclass(slots=True)
class Job:
    id: int | None = None
    type: str = "scan"
    status: str = "queued"
    game_id: int | None = None
    payload: dict[str, Any] = field(default_factory=dict)
    progress: int = 0
    error_code: str | None = None
    error_detail: str | None = None
    created_at: str | None = None
    started_at: str | None = None
    finished_at: str | None = None


@dataclass(slots=True)
class Game:
    id: int | None = None
    name: str = ""
    folder_path: str = ""
    run_type: str = "custom"
    run_argv: list[str] = field(default_factory=list)
    run_env: dict[str, str] = field(default_factory=dict)
    run_cwd: str | None = None
    needs_confirmation: bool = False
    wine_prefix_mode: str = "global"
    status: str = "none"
    description: str = ""
    is_missing: bool = False
    play_count: int = 0
    last_played_at: str | None = None
    created_at: str | None = None
    updated_at: str | None = None
    genre_ids: list[int] = field(default_factory=list)
    developer_ids: list[int] = field(default_factory=list)
    tag_ids: list[int] = field(default_factory=list)
    group_ids: list[int] = field(default_factory=list)

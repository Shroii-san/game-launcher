from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Any


def _normalize_argv(raw_argv: Any) -> list[str]:
    if raw_argv is None:
        return []
    if isinstance(raw_argv, str):
        try:
            value = json.loads(raw_argv)
        except json.JSONDecodeError:
            return [raw_argv]
        if isinstance(value, list):
            return [str(item) for item in value]
        return [str(value)]
    if isinstance(raw_argv, (list, tuple)):
        return [str(item) for item in raw_argv]
    return [str(raw_argv)]


def build_command(game: Mapping[str, Any]) -> list[str]:
    """Build a safe launch command for a game record from the database."""

    run_type = str(game.get("run_type", "custom")).lower()
    run_argv = _normalize_argv(game.get("run_argv"))
    run_env = dict(game.get("run_env") or {})

    if run_type == "exe":
        command = ["wine"]
        if run_argv:
            command.append(run_argv[0])
        wine_prefix = run_env.get("WINEPREFIX") or run_env.get("wineprefix")
        if wine_prefix:
            command.extend(["--prefix", str(wine_prefix)])
        if len(run_argv) > 1:
            command.extend(run_argv[1:])
        return command

    if run_type == "sh":
        if run_argv:
            return ["bash", *run_argv]
        return ["bash"]

    if run_argv:
        return run_argv
    return ["bash"]

from __future__ import annotations

import os
from pathlib import Path

from alembic import command
from alembic.config import Config


def upgrade_database(db_path: str | Path) -> None:
    """Upgrade the SQLite database to the latest Alembic revision."""

    resolved_path = Path(db_path).expanduser()
    resolved_path.parent.mkdir(parents=True, exist_ok=True)

    script_dir = Path(__file__).resolve().parent / "migrations"
    alembic_cfg = Config()
    alembic_cfg.set_main_option("script_location", str(script_dir))
    alembic_cfg.set_main_option("sqlalchemy.url", f"sqlite:///{resolved_path}")
    alembic_cfg.set_main_option("prepend_sys_path", str(Path(__file__).resolve().parents[2]))
    alembic_cfg.set_main_option("path_separator", os.pathsep)

    command.upgrade(alembic_cfg, "head")

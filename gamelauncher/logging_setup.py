from __future__ import annotations

import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path

APP_NAME = "gamelauncher"


def get_xdg_state_dir() -> Path:
    base_dir = Path(os.environ.get("XDG_STATE_HOME") or Path.home() / ".local" / "state")
    return base_dir / APP_NAME


def get_log_file_path() -> Path:
    return get_xdg_state_dir() / "gamelauncher.log"


def setup_logging() -> logging.Logger:
    state_dir = get_xdg_state_dir()
    state_dir.mkdir(parents=True, exist_ok=True)

    log_file = get_log_file_path()
    logger = logging.getLogger(APP_NAME)
    logger.setLevel(logging.INFO)
    logger.propagate = False

    for handler in list(logger.handlers):
        logger.removeHandler(handler)
        handler.close()

    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=5 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))
    logger.addHandler(file_handler)
    logger.info("Logging initialized at %s", log_file)
    return logger

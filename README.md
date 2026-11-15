# Game Launcher

A desktop game launcher for Ubuntu built with Python and PySide6.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
python -m gamelauncher
```

## Local checks

```bash
ruff check .
ruff format --check .
pytest
```

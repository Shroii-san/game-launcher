from __future__ import annotations

from pathlib import Path

IGNORED_EXECUTABLE_PREFIXES = (
    "unins",
    "setup",
    "vcredist",
    "dxsetup",
    "unitycrashhandler",
)
GAME_LIKE_KEYWORDS = (
    "start",
    "run",
    "launch",
    "game",
    "main",
    "play",
    "client",
    "launcher",
)


def detect_executable(folder_path: str | Path) -> Path | None:
    """Return the best candidate executable for a game folder.

    The detector prefers shell launchers named like start/run/launch or game-like
    executables while ignoring known installers and uninstallers.
    """

    root = Path(folder_path).expanduser()
    if not root.exists() or not root.is_dir():
        return None

    best_path: Path | None = None
    best_score = -1

    for candidate in sorted(root.rglob("*")):
        if not candidate.is_file():
            continue

        suffix = candidate.suffix.lower()
        if suffix not in {".exe", ".sh"}:
            continue

        score = _score_candidate(candidate, root)
        if score <= 0:
            continue

        if score > best_score or (
            score == best_score and best_path is not None and candidate < best_path
        ):
            best_path = candidate
            best_score = score

    return best_path


def _score_candidate(candidate: Path, root: Path) -> int:
    name = candidate.name.lower()
    stem = candidate.stem.lower()

    if any(name.startswith(prefix) for prefix in IGNORED_EXECUTABLE_PREFIXES):
        return 0
    if any(
        token in name
        for token in (
            "unins",
            "setup",
            "vcredist",
            "dxsetup",
            "unitycrashhandler",
        )
    ):
        return 0

    score = 0
    if candidate.suffix.lower() == ".sh":
        score += 5
    if candidate.suffix.lower() == ".exe":
        score += 4

    if candidate.parent == root:
        score += 2

    if candidate.name.lower().startswith(GAME_LIKE_KEYWORDS):
        score += 12
    if any(keyword in stem for keyword in GAME_LIKE_KEYWORDS):
        score += 10

    if candidate.suffix.lower() == ".sh" and stem in {"start", "run", "launch"}:
        score += 15
    if candidate.suffix.lower() == ".exe" and stem in {"game", "main", "play"}:
        score += 15

    return score

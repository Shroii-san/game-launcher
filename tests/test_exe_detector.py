from pathlib import Path

from gamelauncher.services.exe_detector import detect_executable


def test_detect_executable_prefers_game_like_names(tmp_path: Path) -> None:
    game_dir = tmp_path / "GameFolder"
    game_dir.mkdir()
    (game_dir / "setup.exe").write_bytes(b"")
    (game_dir / "game.exe").write_bytes(b"")

    detected = detect_executable(game_dir)

    assert detected == game_dir / "game.exe"


def test_detect_executable_ignores_installer_and_uninstaller_duplicates(tmp_path: Path) -> None:
    game_dir = tmp_path / "GameFolder"
    game_dir.mkdir()
    (game_dir / "unins000.exe").write_bytes(b"")
    (game_dir / "vcredist_x64.exe").write_bytes(b"")
    (game_dir / "UnityCrashHandler64.exe").write_bytes(b"")
    (game_dir / "start.sh").write_text("#!/usr/bin/env bash\n")
    (game_dir / "start.sh").chmod(0o755)

    detected = detect_executable(game_dir)

    assert detected == game_dir / "start.sh"

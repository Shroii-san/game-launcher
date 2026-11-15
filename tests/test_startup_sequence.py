from __future__ import annotations

from pathlib import Path

from gamelauncher.startup import StartupCheckResult, ensure_directory, run_startup_checks


def test_run_startup_checks_reports_missing_runtime_dependencies(monkeypatch) -> None:
    def fake_which(name: str) -> str | None:
        if name in {"wine", "7z"}:
            return None
        return "/usr/bin/true"

    monkeypatch.setattr("gamelauncher.startup.shutil.which", fake_which)

    result = run_startup_checks({"games_root": Path("/tmp/launcher-games")})

    assert isinstance(result, StartupCheckResult)
    assert any("wine" in warning.lower() for warning in result.warnings)
    assert any("7z" in warning.lower() for warning in result.warnings)


def test_ensure_directory_recovers_missing_directory(tmp_path) -> None:
    missing_dir = tmp_path / "missing" / "games"

    assert ensure_directory(missing_dir) is True
    assert missing_dir.exists()
    assert missing_dir.is_dir()

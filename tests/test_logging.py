from gamelauncher.logging_setup import get_xdg_state_dir, setup_logging


def test_xdg_state_dir_uses_xdg_state_home(monkeypatch, tmp_path) -> None:
    state_home = tmp_path / "state-home"
    monkeypatch.setenv("XDG_STATE_HOME", str(state_home))

    result = get_xdg_state_dir()

    assert result == state_home / "gamelauncher"


def test_setup_logging_creates_rotating_log_file(monkeypatch, tmp_path) -> None:
    state_home = tmp_path / "state-home"
    monkeypatch.setenv("XDG_STATE_HOME", str(state_home))

    logger = setup_logging()
    logger.info("hello from test")

    log_file = state_home / "gamelauncher" / "gamelauncher.log"
    assert log_file.exists()
    assert "hello from test" in log_file.read_text(encoding="utf-8")

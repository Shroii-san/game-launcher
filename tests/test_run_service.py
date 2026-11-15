import stat

import pytest

from gamelauncher.core.errors import LaunchError
from gamelauncher.launcher import build_command
from gamelauncher.services.run_service import RunService


def test_build_command_for_exe_uses_wine_and_wineprefix() -> None:
    command = build_command(
        {
            "run_type": "exe",
            "folder_path": "/tmp/demo",
            "run_argv": ["/tmp/demo/game.exe"],
            "run_env": {"WINEPREFIX": "/tmp/prefix"},
        }
    )

    assert command[0] == "wine"
    assert command[1] == "/tmp/demo/game.exe"
    assert command[2] == "--prefix"
    assert command[3] == "/tmp/prefix"


def test_run_service_blocks_duplicate_launch_and_records_exit_code(tmp_path) -> None:
    script = tmp_path / "launch.sh"
    script.write_text("#!/usr/bin/env bash\nexit 7\n")
    script.chmod(script.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

    service = RunService()
    result = service.launch(
        {
            "id": 1,
            "name": "Demo Game",
            "folder_path": str(tmp_path),
            "run_type": "sh",
            "run_argv": [str(script)],
            "run_env": {},
        }
    )

    assert result["exit_code"] == 7
    assert result["running"] is True

    with pytest.raises(LaunchError, match="already running"):
        service.launch(
            {
                "id": 1,
                "name": "Demo Game",
                "folder_path": str(tmp_path),
                "run_type": "sh",
                "run_argv": [str(script)],
                "run_env": {},
            }
        )

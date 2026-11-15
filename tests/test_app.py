from gamelauncher import __version__
from gamelauncher.app import main


def test_version() -> None:
    assert __version__ == "0.1.0"


def test_main_is_callable() -> None:
    assert callable(main)

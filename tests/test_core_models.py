from gamelauncher.core.constants import (
    DEFAULT_DESCRIPTION_TEMPLATE,
    DEFAULT_GENRES,
    get_default_genres,
)
from gamelauncher.core.models import Developer, Game, Genre, Tag, UserGroup


def test_default_genres_matches_project_defaults() -> None:
    expected = (
        "Action",
        "Adventure",
        "RPG",
        "Strategy",
        "Simulation",
        "Puzzle",
        "Platformer",
        "Shooter",
        "Horror",
        "Racing",
        "Sports",
        "Visual Novel",
        "Roguelike",
        "Indie",
    )

    assert DEFAULT_GENRES == expected
    assert get_default_genres() == expected


def test_default_description_template_is_available() -> None:
    assert DEFAULT_DESCRIPTION_TEMPLATE == (
        "Belum ada deskripsi untuk game ini.\n\n"
        "Developer : -\n"
        "Genre     : -\n"
        "Cara main : tekan Play\n\n"
        "Tambahkan deskripsi lewat tombol Edit."
    )


def test_domain_models_store_expected_fields() -> None:
    genre = Genre(id=1, name="RPG", is_default=True)
    developer = Developer(id=2, name="Studio Test")
    tag = Tag(id=3, name="Co-op")
    group = UserGroup(id=4, name="Lagi dimainkan", sort_order=1)
    game = Game(
        id=10,
        name="Test Game",
        folder_path="/games/Test Game",
        run_type="exe",
        run_argv=["wine", "game.exe"],
        run_env={"WINEPREFIX": "/tmp/prefix"},
        needs_confirmation=True,
        description="",
        genre_ids=[1],
        developer_ids=[2],
        tag_ids=[3],
        group_ids=[4],
    )

    assert genre.name == "RPG"
    assert developer.name == "Studio Test"
    assert tag.name == "Co-op"
    assert group.name == "Lagi dimainkan"
    assert game.run_argv == ["wine", "game.exe"]
    assert game.genre_ids == [1]
    assert game.description == ""

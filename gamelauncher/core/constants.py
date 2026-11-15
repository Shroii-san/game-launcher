from __future__ import annotations

DEFAULT_GENRES = (
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

DEFAULT_DESCRIPTION_TEMPLATE = (
    "Belum ada deskripsi untuk game ini.\n\n"
    "Developer : -\n"
    "Genre     : -\n"
    "Cara main : tekan Play\n\n"
    "Tambahkan deskripsi lewat tombol Edit."
)


def get_default_genres() -> tuple[str, ...]:
    """Return the built-in genre list used by the launcher."""

    return DEFAULT_GENRES

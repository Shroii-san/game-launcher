from __future__ import annotations

ERROR_MESSAGES = {
    "ARCHIVE_CORRUPT": ("Arsip ini tampaknya rusak atau tidak lengkap. Coba unduh ulang."),
    "DISK_FULL": (
        "Ruang penyimpanan tidak cukup untuk mengekstrak game ini. "
        "Kosongkan sekitar 4 GB lalu coba lagi."
    ),
    "MEDIA_INVALID": "File ini bukan media yang valid, jadi tidak ditambahkan.",
    "WINE_MISSING": ("Game ini butuh Wine untuk dijalankan, tapi Wine belum terpasang."),
    "EXE_NOT_FOUND": ("File game tidak ditemukan. Mungkin sudah dipindah atau dihapus."),
    "PATH_FORBIDDEN": "Path yang Anda pilih tidak aman untuk digunakan.",
    "INVALID_NAME": ("Nama tidak valid. Pastikan nama game tidak kosong dan sesuai format."),
    "INVALID_URL": "URL yang Anda masukkan tidak valid.",
    "URL_BLOCKED": "URL ini tidak diizinkan karena berpotensi tidak aman.",
    "FILE_TOO_LARGE": "Ukuran file terlalu besar untuk diproses.",
    "UNKNOWN_ERROR": "Terjadi kesalahan yang tidak terduga.",
}

DEFAULT_USER_MESSAGE = "Terjadi kesalahan yang tidak terduga."


def get_user_message(error_or_code: object) -> str:
    if isinstance(error_or_code, str):
        code = error_or_code
    elif hasattr(error_or_code, "code"):
        code = error_or_code.code
    else:
        code = str(error_or_code)

    return ERROR_MESSAGES.get(code, DEFAULT_USER_MESSAGE)

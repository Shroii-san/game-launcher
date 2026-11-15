# Arsitektur Aplikasi Game Launcher

Arsitektur ini dirancang agar selaras dengan skema database serta mudah untuk diuji (*testable*). **Prinsip utamanya:** Layer UI tidak pernah menyentuh database, menjalankan *subprocess*, atau mengakses sistem file secara langsung.

---

## 1. Layer dan Aturan Dependensi

```text
UI (PySide6)            -> Hanya berkomunikasi dengan Service
Service (Use Case)      -> Aturan bisnis, logika validasi, manajemen transaksi
Repository              -> Satu-satunya layer yang menyentuh SQLite
Infrastructure          -> Wrapper 7z, ffmpeg, wine, filesystem, HTTP, watchdog
Core (Domain)           -> Model, exception, konstanta (tanpa import dari layer lain)
```

* **Aturan Panah Satu Arah:** `UI` $\rightarrow$ `Service` $\rightarrow$ `Repository` / `Infrastructure` $\rightarrow$ `Core`. Layer bawah tidak boleh meng-import layer di atasnya.
* **Alasan:** Logika validasi terpusat di *Service*, sehingga aturan bisnis tetap berlaku meskipun UI dilewati. Selain itu, pengujian pada *Service* dapat dilakukan secara penuh tanpa perlu membuka jendela aplikasi (GUI).

---

## 2. Struktur Folder

```text
gamelauncher/
  app.py                  # Entry point, wiring dependency
  core/
    models.py             # Dataclass: Game, Media, Job, dll.
    errors.py             # Hierarki exception + kode error
    messages.py           # Pemetaan kode error -> pesan ramah (Bahasa Indonesia)
    constants.py          # Genre bawaan, batas ukuran, ekstensi yang diizinkan
    paths.py              # Resolve & validasi path (anti path-traversal)
  db/
    engine.py             # Koneksi, PRAGMA, manajemen session
    migrations/           # Skrip migrasi Alembic
    repositories/
      games.py
      media.py
      mods.py
      taxonomy.py
      jobs.py
      settings.py
      links.py
  infra/
    archive.py            # Wrapper 7z/unar + proteksi zip bomb & path traversal
    video.py              # ffprobe + ffmpeg transcode
    image.py              # Validasi + re-encode menggunakan Pillow
    downloader.py         # HTTP client aman (anti SSRF)
    launcher.py           # Subprocess, wine, environment variables, log proses
    watcher.py            # Watchdog -> event sistem file
    exe_detector.py       # Heuristik skor deteksi executable utama
  services/
    game_service.py       # CRUD, scan folder, sinkronisasi FTS
    library_service.py    # Search, filter, sort, keyset pagination
    extract_service.py    # Alur auto-extract arsip
    media_service.py      # Validasi + antrian kompresi media
    mod_service.py        # Manajemen modifikasi game
    run_service.py        # Menjalankan game, mencegah double-launch
    settings_service.py   # Ubah direktori + konfirmasi pengguna
    taxonomy_service.py   # Genre, tag, developer, grup + reset genre bawaan
  workers/
    job_queue.py          # Antrian pekerjaan + batas konkurensi
    handlers.py           # Handler eksekusi per tipe job
  ui/
    main_window.py
    viewmodels/           # State + signal untuk tiap layar
    views/
      library_view.py
      detail_view.py
      settings_view.py
    widgets/
      game_card.py
      hover_preview.py
      state_panel.py
      toast.py
    theme/
      light.qss
      dark.qss
    state.py              # Enum ViewState: LOADING / EMPTY / ERROR / SUCCESS
tests/
  unit/
  integration/
  fixtures/               # Termasuk arsip & file media berbahaya untuk uji keamanan
```

> **Mengapa ada `viewmodels/`?**  
> Setiap layar memiliki satu objek *ViewModel* yang memegang *state* (`LOADING`, `EMPTY`, `ERROR`, `SUCCESS`) beserta datanya. *View* hanya bertugas menampilkan state tersebut. Pola ini memastikan keempat state wajib selalu konsisten dan tidak tercecer di banyak widget.

---

## 3. Model Threading

Manajemen *thread* adalah bagian yang paling krusial untuk mencegah *bug* dan *freeze* pada aplikasi desktop:

| Aturan | Alasan |
| :--- | :--- |
| **UI hanya diubah dari *main thread*** | Qt tidak *thread-safe*. Worker berkomunikasi ke UI menggunakan Qt *Signal*. |
| **Satu koneksi SQLite per *thread*, *session* pendek** | Koneksi SQLite tidak boleh dibagi antar *thread*. Mode WAL mengizinkan proses baca secara bersamaan. |
| **Transaksi DB singkat (hindari menahan saat I/O lama)** | Mencegah error `"database is locked"`. |
| **Proses eksternal (`7z`, `ffmpeg`) dijalankan di *worker*** | Menggunakan `subprocess` di background agar UI tidak *freeze*. |
| **Watcher hanya mengirim *event*, tidak memproses** | Menjaga *thread* `watchdog` tetap ringan dan responsif. |

### Batas Konkurensi di `job_queue`

| Tipe Job | Maksimal Paralel | Alasan |
| :--- | :---: | :--- |
| `extract` | **1** | Operasi Disk I/O sangat berat; menjalankan paralel justru memperlambat proses. |
| `compress_video` | **1** | Operasi CPU sangat berat; dibatasi agar aplikasi tetap ringan digunakan. |
| `download_media` | **2** | Dibatasi oleh *bandwidth* jaringan. |
| `scan` | **1** | Menghindari tabrakan data dengan proses ekstraksi yang sedang berjalan. |

---

## 4. Alur Utama (Core Workflows)

### A. Auto-Extract Hingga Game Siap Main
```text
watcher: arsip baru terdeteksi
  -> tunggu ukuran file stabil (debounce)
  -> buat job 'extract' (status: queued, tercatat di DB)
  -> worker: pre-check (ruang disk, rasio kompresi, bentrok nama folder)
  -> ekstrak ke games_root/<nama> (tolak '../' dan symlink keluar)
  -> job 'scan' otomatis: deteksi executable, buat baris baru di tabel games
  -> pasang deskripsi template, sinkronisasi indeks FTS
  -> signal ke UI: tampilkan toast "Game X siap dimainkan", perbarui daftar game
  -> jika gagal: tandai job 'failed' + error_code, UI tampilkan pesan ramah
```

### B. Menjalankan Game
```text
klik tombol Play
  -> run_service: pastikan game tidak sedang berjalan
  -> cek keberadaan folder & file executable (jika hilang: tampilkan error ramah, tandai is_missing)
  -> bangun argv (+ WINEPREFIX sesuai mode) berdasarkan data dari DB
  -> launcher.py: jalankan subprocess tanpa shell, atur cwd yang benar, arahkan output ke log
  -> UI: ubah tombol menjadi disabled + tampilkan status "Sedang berjalan"
  -> proses selesai: perbarui play_count & last_played_at, kembalikan status tombol
```

### C. Upload Media
```text
pilih file lokal atau masukkan URL
  -> validasi cepat di UI (cek ekstensi & ukuran file)              [Validator UI]
  -> media_service: validasi ulang + pemeriksaan magic bytes        [Validator Logic]
  -> jika URL: downloader aman (blokir IP private, batas ukuran & redirect)
  -> jika gambar: re-encode dengan Pillow | jika video: ffprobe lalu buat job 'compress_video'
  -> simpan file dengan nama hash, ubah status: pending -> processing -> ready
  -> buat thumbnail, kirim signal ke UI untuk memperbarui galeri
```

---

## 5. Penanganan Error Lintas Layer

```text
Infra melempar exception teknis (OSError, SubprocessError, dll.)
  -> Service menangkap dan membungkusnya menjadi LauncherError(code, detail)
  -> UI / ViewModel menerjemahkan 'code' menjadi pesan ramah via messages.py
  -> Detail teknis dicatat ke file log, bukan ditampilkan ke layar pengguna
```

* **Global Handler (`sys.excepthook`):** Bertindak sebagai jaring pengaman terakhir jika terjadi *unhandled exception*. Menampilkan dialog *"Terjadi kesalahan tak terduga"* disertai tombol **Salin Detail**.
* **Sentralisasi Pesan:** Contoh kode error meliputi `ARCHIVE_CORRUPT`, `DISK_FULL`, `WINE_MISSING`, `EXE_NOT_FOUND`, `MEDIA_INVALID`, `URL_BLOCKED`, dan `PATH_FORBIDDEN`. Semua dipetakan di satu tempat (`messages.py`), sehingga mengubah kalimat peringatan tidak akan menyentuh logika aplikasi.

---

## 6. Urutan Startup Aplikasi

1. **Muat pengaturan & validasi direktori:** Jika direktori utama hilang/dipindah, tampilkan dialog pemulihan (bukan *crash*).
2. **Migrasi & Seeding:** Jalankan migrasi Alembic, lalu isi (*seed*) genre bawaan dan template deskripsi jika belum ada.
3. **Cek dependensi eksternal:** Periksa ketersediaan `7z`, `ffmpeg`, dan `wine`. Dependensi yang tidak ditemukan ditampilkan sebagai peringatan ringan, bukan memblokir aplikasi.
4. **Pemulihan antrian pekerjaan:** Ubah status *job* yang tertinggal dalam status `running` (akibat aplikasi tertutup paksa) kembali menjadi `queued`.
5. **Inisialisasi UI:** Tampilkan jendela utama dalam state `LOADING`, lalu muat data *library* secara asinkron.
6. **Layanan latar belakang:** Jalankan `watcher` dan lakukan *initial scan* untuk mendeteksi folder atau arsip yang masuk saat aplikasi dalam keadaan mati.

---

## 7. Strategi Pengujian (Testing)

Karena seluruh logika bisnis dan state berada di *Service* dan *ViewModel*, hampir keseluruhan sistem dapat diuji tanpa harus membuka antarmuka grafis (GUI):

| Level Pengujian | Target yang Diuji | Contoh Skenario Uji |
| :--- | :--- | :--- |
| **Unit Test** | Validator, `exe_detector`, `paths`, `messages` | Path `../../etc` ditolak. File `unins000.exe` tidak terpilih sebagai game utama. |
| **Integration Test** | *Service* + SQLite *in-memory* + *Infra* tiruan (*mock*) | Simulasi alur ekstrak $\rightarrow$ scan $\rightarrow$ data game berhasil masuk ke DB. |
| **Security Test** | *Fixture* file berbahaya | Arsip `.zip` berisi `../`, *zip bomb* berukuran kecil, file `.exe` yang diubah ekstensi menjadi `.jpg`, serta URL SSRF `http://127.0.0.1`. |
| **UI State Test** | *ViewModel* (bukan *Widget*) | Hasil pencarian kosong menghasilkan state `ViewState.EMPTY`. |

---

## 8. Roadmap Pengerjaan (MVP ke V1)

### Fase 1: Fondasi & MVP (Minimum Viable Product)
1. **`core/` & `db/`:** Implementasi `errors`, `paths`, `models`, koneksi `engine`, migrasi awal, dan `games` repository.
2. **Manajemen Data:** Implementasi `game_service` dan `library_service` (CRUD, pencarian FTS, *keyset pagination*) beserta *unit/integration test*.
3. **Eksekusi Game:** Implementasi `exe_detector`, `launcher`, dan `run_service`.
4. **Antarmuka Dasar:** Pembuatan *library grid/list*, *state panel*, tema *light/dark*, dan halaman detail game.
5. **Pengaturan:** Implementasi `settings_service` (perubahan direktori dengan konfirmasi).

### Fase 2: Otomatisasi & Media (V1)
* Setelah fondasi MVP stabil, lanjutkan pengembangan ke sistem *worker queue*, alur *auto-extract* (`watcher` + `extract_service`), serta manajemen dan kompresi media (`media_service`).
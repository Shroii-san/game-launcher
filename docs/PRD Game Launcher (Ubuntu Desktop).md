# PRD: Game Launcher (Ubuntu Desktop)

Versi 1.0 | Pemilik: Shiroi | Status: Siap dikerjakan

## 1. Ringkasan

| Item | Isi |
| --- | --- |
| Nama kerja | Game Launcher |
| Platform | Aplikasi desktop Ubuntu, pemakaian pribadi (single user) |
| Tujuan | Satu tempat untuk melihat, mengelola, dan menjalankan game portabel/pre-installed |
| Non-goal | Bukan store, bukan multi-user, bukan manajer download, tanpa akun/cloud sync, tanpa fetch metadata otomatis dari internet |

**Masalah:** game portabel tersebar di banyak folder dan arsip, sulit dicari, dan harus diekstrak serta dijalankan manual lewat terminal atau Wine.

**Hasil yang diharapkan:** arsip masuk ke folder arsip, otomatis diekstrak dan terdeteksi, lalu game bisa dimainkan dengan satu klik.

**Prinsip kualitas:** dibuat untuk skala sistem siap pakai, bukan sekadar jadi. Artinya ada validasi, error handling, pesan ramah pengguna, keamanan untuk file tak tepercaya, dan empat state UI di setiap tampilan.

## 2. Rekomendasi Teknis

Ini saran berdasarkan best practice, bisa diubah.

| Aspek | Saran | Alasan |
| --- | --- | --- |
| Bahasa | Python 3.11+ | Sudah dikuasai |
| UI | PySide6 (Qt) | Kivy dirancang untuk touch/mobile. Qt matang untuk desktop: sidebar, infinite scroll, video player, dark mode |
| Database | SQLite + SQLAlchemy + Alembic | Ringan, cukup untuk data lokal, migrasi skema aman |
| Ekstraksi | `7z` (p7zip-full, p7zip-rar), `unar` sebagai fallback | Satu tool untuk hampir semua format |
| Watcher | `watchdog` (inotify) | Deteksi arsip dan folder baru |
| Video | `ffmpeg` dan `ffprobe` | Kompresi, validasi, thumbnail |
| Gambar | Pillow | Validasi dan re-encode |
| Eksekusi | `subprocess` dengan list argumen, tanpa `shell=True` | Mencegah command injection |

Proses berat (ekstrak, scan, ffmpeg) berjalan di worker thread/queue agar UI tidak freeze.

## 3. Konfigurasi Direktori

| Setting | Default | Bisa diubah | Catatan |
| --- | --- | --- | --- |
| Games root (prefix) | `~/Games` | Ya, dengan peringatan "at own risk" | Semua hasil ekstrak masuk ke sini |
| Archive dir | `~/Games/_archives` | Ya | Watcher otomatis pindah ke path baru, auto extract tetap berfungsi |
| Media dir | `~/.local/share/gamelauncher/media` | Ya | Video terkompresi dan thumbnail |
| Mod/save dir | Per game | Ya | Terpisah dari folder game |
| Wine prefix global | `~/.local/share/gamelauncher/wineprefix` | Ya | Dibuat saat game .exe pertama dijalankan |

Aturan perubahan direktori:

- Tampilkan dialog konfirmasi: "Mengubah ini bisa membuat game tidak ditemukan. Lanjutkan?"
- Game lama tidak dipindah otomatis. Tawarkan "Pindahkan" atau "Biarkan di lokasi lama".
- Path divalidasi: ada, bisa ditulis, dan bukan direktori sistem (`/`, `/etc`, `/usr`, `/bin`, dll).

## 4. Fitur Fungsional

### F1. CRUD Game

- **Create:** otomatis dari scan, atau manual (pilih folder yang sudah ada).
- **Read:** list dan halaman detail.
- **Update:** nama, deskripsi, genre, tag, developer, grup, cover, run command, status, opsi Wine prefix.
- **Delete:** dua opsi, "Hapus dari library saja" atau "Hapus beserta file" (konfirmasi dua langkah).

Field game: `id, name, folder_path, run_command, run_type (exe/sh/custom), wine_prefix_mode (global/per_game), genres[], tags[], developers[], groups[], status (none/completed/stalled), description, cover_id, created_at, last_played_at, play_count`

Deskripsi diisi saat create/edit. Jika game masuk dari scan atau export tanpa deskripsi, pakai template standar (lihat F11), bukan kosong.

### F2. Search dan Filter

- Search nama, tag, developer, dan deskripsi.
- Filter genre, tag, developer, grup, dan status (multi-select, logika AND).
- Semua bekerja live (lihat U1).

### F3. Auto Extract

- Watcher memantau archive dir.
- Format: zip, rar, 7z, tar, tar.gz, tar.bz2, tar.xz, dan format lain yang didukung 7z.
- Alur: arsip terdeteksi, tunggu ukuran file stabil (agar tidak mengekstrak file yang masih dicopy), ekstrak ke `games_root/<nama>`.
- Hasil ekstrak default selalu di games root yang sama dengan game lain.
- **Arsip tetap disimpan di direktori asal** setelah ekstrak.
- Konflik nama: tanya user (timpa / rename / lewati), tidak pernah menimpa diam-diam.
- Arsip multi-part (`.part1.rar`, `.7z.001`): tunggu semua part lengkap.
- Arsip berpassword: minta password lewat dialog.
- Perubahan archive dir atau games root tidak boleh merusak auto extract.

Proteksi arsip:

- Cegah path traversal (`../`) dan symlink yang keluar dari folder tujuan.
- Cek ruang disk dan rasio kompresi sebelum ekstrak (anti zip bomb).
- Job ekstrak dicatat di database agar bisa dilanjutkan atau diulang setelah crash.

### F4. Auto Scan dan Deteksi Executable

- Folder baru di games root otomatis masuk library.
- Heuristik deteksi, urut prioritas:
  1. File `.sh` bernama `start`, `run`, `launch`, atau mirip nama game.
  2. File `.exe` yang bukan `unins*`, `setup*`, `vcredist*`, `dxsetup*`, `UnityCrashHandler*`.
  3. Jika ada beberapa kandidat, ambil skor tertinggi dan tandai "perlu dikonfirmasi" agar user bisa memilih.
- Command default:
  - `.exe`: `wine "<path>"` dengan working directory di folder exe
  - `.sh`: `bash "<path>"` (executable bit di-set jika belum)
- Jika Wine belum terpasang, tampilkan pesan jelas dan petunjuk instalasi.

### F5. Run Script

- Tombol "Play" di card dan halaman detail.
- Command tampil **read-only** secara default. Tombol "Edit" membuka mode ubah dengan peringatan singkat.
- Eksekusi lewat `subprocess` tanpa shell. Output dan exit code masuk ke log.
- Status proses: sedang berjalan, selesai, gagal (dengan pesan ramah dan tombol "Lihat log").
- Cegah double-launch untuk game yang sama.

### F6. Mod dan Savegame

- Upload file atau folder mod/save ke folder khusus per game.
- Daftar dan hapus per game.
- Backup savegame otomatis sebelum ditimpa.
- Validasi: hanya arsip/folder, batas ukuran, tanpa path traversal.

### F7. Media (Gambar dan Video)

- Sumber: file lokal atau URL internet.
- Gambar: jpg, png, gif. Video: mp4, webm, mkv.
- **Kompresi video wajib**, ringan di GPU dan cepat diproses:
  - H.264, `-preset ultrafast`, CRF tinggi (sekitar 30 sampai 32)
  - Resolusi maksimal 720p, fps maksimal 30, bitrate dibatasi
  - Audio dibuang secara default (hanya untuk preview)
  - Video asli tidak disimpan setelah kompresi sukses
- Proses di background dengan progress bar.

**Zero trust untuk media:**

- Jangan percaya ekstensi atau MIME dari sumber. Cek magic bytes.
- Gambar di-decode dan di-re-encode dengan Pillow (membuang metadata dan payload tersembunyi).
- Video dicek dengan `ffprobe`, lalu di-transcode ffmpeg sehingga hasilnya file baru, bukan file asli.
- Batas ukuran file, durasi, dan dimensi (anti decompression bomb).
- Nama file diganti hash/UUID, path asli tidak dipakai.
- URL: hanya `http/https`, blokir alamat lokal/private (anti SSRF), batas ukuran download, timeout, batas redirect.
- File media tidak pernah dieksekusi atau dibuka dengan handler sistem.

### F8. Grouping Khusus

- Grup adalah koleksi buatan user, terpisah dari genre dan tag (contoh: "Lagi dimainkan", "Antrian", "Co-op").
- Satu game bisa masuk beberapa grup.
- Grup bisa dibuat, di-rename, dihapus, dan diurutkan. Menghapus grup tidak menghapus game.

### F9. Status Game

- Tandai **Selesai** atau **Mentok update developer**.
- Tampil sebagai badge di card dan list, dan bisa difilter.

### F10. Link Install Game Lain

- Section/tombol berisi daftar situs buatan user (nama, URL, urutan).
- Jumlah dan isi diatur user (soft limit UI sekitar 20).
- Dibuka di browser default sistem, bukan webview internal.
- Validasi: URL harus `http/https`.

### F11. Genre, Developer, dan Template Deskripsi

- **Genre** bebas dibuat user. Saat pertama jalan, terisi genre bawaan: Action, Adventure, RPG, Strategy, Simulation, Puzzle, Platformer, Shooter, Horror, Racing, Sports, Visual Novel, Roguelike, Indie.
- Ada tombol **"Kembalikan genre bawaan"**. Genre bawaan yang hilang dibuat ulang, genre buatan user dan relasi game tidak disentuh.
- Menghapus genre yang dipakai game memunculkan konfirmasi dengan jumlah game terdampak.
- **Developer** adalah kolom khusus (bukan tag), many-to-many ke game, dengan halaman sendiri.
- **Template deskripsi default** (bisa diubah di setting), dipakai untuk game hasil scan/export tanpa deskripsi:

```
Belum ada deskripsi untuk game ini.

Developer : -
Genre     : -
Cara main : tekan Play

Tambahkan deskripsi lewat tombol Edit.
```

### F12. Wine Prefix

- Default: satu prefix global untuk semua game `.exe`, dibuat lazy saat game `.exe` pertama dijalankan (dengan loading state "Menyiapkan Wine, ini hanya sekali").
- Per game ada opsi "Pakai Wine prefix terpisah" untuk game yang butuh setting khusus.
- Prefix per game disimpan di luar folder game: `~/.local/share/gamelauncher/prefixes/<id>`. Folder game tetap bersih, dan saat game dihapus, prefix ditawarkan untuk ikut dihapus.
- Command otomatis memakai `WINEPREFIX=<path>` sesuai pilihan dan tetap tampil read-only.

## 5. Fitur UI

| Kode | Fitur | Detail |
| --- | --- | --- |
| U1 | Livesearch | Debounce sekitar 250 ms, hasil update langsung tanpa tombol "Cari" |
| U2 | Grid / List | Toggle, pilihan diingat |
| U3 | Sorting | Nama, terakhir dimainkan, tanggal ditambah, play count, status |
| U4 | Infinite scroll | Muat per batch (sekitar 40 item), lazy-load thumbnail, tanpa tombol prev/next |
| U5 | Halaman detail | Cover, galeri media, deskripsi, genre/tag/developer/grup, status, run command (read-only), mod/save, info folder |
| U6 | Sidebar kiri | Di halaman detail, daftar game menjadi sidebar (tetap bisa search/filter), game aktif ditandai |
| U7 | Light/Dark mode | Ikut sistem atau manual, disimpan di setting |
| U8 | Hover preview | Di mode grid, hover card memunculkan 3 media (gambar/video) di sisi kiri card |
| U9 | Section link install | Tombol/panel di toolbar atau sidebar |
| U10 | Tag/genre/developer/grup clickable | Klik membuka halaman daftar game dengan filter itu aktif |

**Catatan U8 (hover preview):**

- Delay sekitar 300 ms sebelum muncul agar tidak berkedip.
- Posisi flip ke kanan jika card ada di tepi kiri layar.
- Hanya satu video autoplay pada satu waktu (mute, loop). Decoder dibebaskan saat hover berakhir.
- Jika media kurang dari 3, tampilkan yang ada. Jika kosong, popup tidak muncul.

**Catatan U10 (halaman hasil klik):**

- Judul jelas, contoh: "Genre: RPG (12 game)".
- Memakai komponen library yang sama (grid/list, sorting, infinite scroll, livesearch).
- Filter aktif tampil sebagai chip yang bisa dihapus. Klik tag lain menambah chip (logika AND).
- Empty state: "Belum ada game dengan genre ini" dan tombol "Kembali ke library".
- Tombol Back mengembalikan posisi scroll sebelumnya.

## 6. Empat State UI

Setiap tampilan wajib punya loading, empty, error, dan success state.

| Tampilan | Loading | Empty | Error | Success |
| --- | --- | --- | --- | --- |
| Library | Skeleton card | "Belum ada game. Taruh arsip di folder X atau tambah manual" | "Gagal memuat library" + Coba lagi | List tampil |
| Hasil search/filter | Indikator kecil | "Tidak ada game yang cocok" + reset filter | Pesan + Coba lagi | Hasil tampil |
| Ekstrak arsip | Progress bar + nama arsip | Antrian kosong | "Arsip rusak/terkunci/disk penuh" + aksi | Toast "Game X siap dimainkan" |
| Upload media | Progress + tahap (validasi, kompres) | Placeholder "Tambah gambar/video" | "File tidak valid" + alasan | Thumbnail muncul |
| Mod/save | Progress | "Belum ada mod/save" | Pesan jelas | Terdaftar di list |
| Menjalankan game | Tombol disabled + spinner | - | "Game gagal dijalankan" + Lihat log | Status "Sedang berjalan" |
| Link install | - | "Belum ada situs. Tambahkan" | Validasi URL | Tersimpan |

## 7. Validasi, Error Handling, dan Exception

**Validator UI** (langsung di form):

- Nama tidak kosong, panjang maksimal, tanpa karakter terlarang.
- Path ada dan bisa diakses. URL berformat valid.
- Tombol submit disabled selama input tidak valid, pesan error muncul di bawah field.

**Validator logic** (di service layer, independen dari UI):

- Semua input divalidasi ulang di service karena UI bisa dilewati.
- Cek duplikat (nama, folder), izin file, ruang disk, dan sanitasi path.
- Run command dipecah menjadi list argumen, tanpa interpolasi shell.

**Error handling dan exception:**

- Hierarki exception sendiri: `LauncherError` dengan turunan `ArchiveError`, `MediaError`, `LaunchError`, `ConfigError`, `ValidationError`.
- Exception tidak pernah bocor ke UI. Ada global handler sebagai jaring pengaman.
- Setiap error punya kode internal, pesan ramah pengguna, dan detail teknis yang hanya masuk log.
- Stack trace tidak pernah tampil di UI. Ada tombol opsional "Salin detail" untuk debugging.
- Log berputar (rotating) di `~/.local/state/gamelauncher/`.

Contoh pesan:

| Kondisi | Pesan ke user |
| --- | --- |
| Disk penuh | "Ruang penyimpanan tidak cukup untuk mengekstrak game ini. Kosongkan sekitar 4 GB lalu coba lagi." |
| Wine tidak ada | "Game ini butuh Wine untuk dijalankan, tapi Wine belum terpasang." |
| Arsip rusak | "Arsip ini tampaknya rusak atau tidak lengkap. Coba unduh ulang." |
| Video ditolak | "File ini bukan video yang valid, jadi tidak ditambahkan." |
| Executable hilang | "File game tidak ditemukan. Mungkin sudah dipindah atau dihapus." |

## 8. Model Data (garis besar)

- `games`
- `genres` (dengan `is_default`), `game_genres`
- `tags`, `game_tags`
- `developers`, `game_developers`
- `groups`, `game_groups`
- `media` (id, game\_id, type, source, stored\_path, hash, status)
- `mods` (id, game\_id, kind mod/save, path)
- `install_links` (id, name, url, order)
- `settings` (key, value), termasuk template deskripsi dan path direktori
- `jobs` (ekstrak/kompres: status, error\_code) agar proses terputus bisa dipulihkan

Migrasi skema lewat Alembic agar update aplikasi tidak merusak data.

## 9. Kebutuhan Non-Fungsional

| Aspek | Target |
| --- | --- |
| Performa | Library 1.000 game tetap lancar. Search kurang dari 100 ms |
| Responsif | UI tidak pernah freeze, proses berat di worker |
| Resource | Satu video preview aktif pada satu waktu, thumbnail di-cache |
| Keamanan | Zero trust untuk media dan arsip, tanpa shell injection, path divalidasi |
| Keandalan | Job ekstrak/kompres bisa dilanjutkan atau diulang setelah crash |
| Data | Backup otomatis database (5 salinan terakhir) |
| Pengujian | Unit test untuk validator, deteksi exe, ekstraksi. Uji dengan arsip jahat (traversal, zip bomb) dan media palsu |
| Distribusi | Paket `.deb` atau AppImage, cek dependensi (7z, ffmpeg, wine) saat pertama jalan |

## 10. Rencana Rilis

| Fase | Isi |
| --- | --- |
| MVP | Config direktori, scan manual, CRUD, run script, search/filter, grid/list, light/dark mode, empat state dasar, Wine prefix global |
| V1 | Auto extract, auto scan dan deteksi exe, media plus kompresi video, infinite scroll, halaman detail plus sidebar, genre/developer clickable |
| V1.5 | Hover preview, grouping, status selesai/mentok, mod/save, link install, Wine prefix per game |
| V2 | Hardening zero trust penuh, recovery job, packaging, test lengkap |

## 11. Kriteria Penerimaan

- Arsip baru di archive dir, lalu game muncul di library dan bisa dimainkan tanpa langkah manual.
- Mengubah games root atau archive dir, lalu auto extract tetap berfungsi.
- Arsip tetap ada di direktori asal setelah ekstrak.
- Semua video yang diupload tersimpan dalam versi terkompresi.
- File media palsu (misalnya `.exe` yang diganti menjadi `.jpg`) ditolak dengan pesan jelas.
- Klik tag, genre, atau developer membuka daftar game terfilter.
- Tombol "Kembalikan genre bawaan" memulihkan genre bawaan tanpa menghapus data lain.
- Tidak ada layar yang menampilkan stack trace.
- Setiap tampilan punya loading, empty, error, dan success state.

## 12. Keputusan yang Sudah Diambil

| Topik | Keputusan |
| --- | --- |
| Arsip setelah ekstrak | Disimpan di direktori asal |
| Wine prefix | Default global, opsi per game bagi yang butuh |
| Genre | Bebas dibuat user, ada genre bawaan dan tombol reset |
| Deskripsi | Diisi saat create/edit, template standar jika kosong |
| Developer | Kolom khusus, bukan tag |
| Metadata otomatis dari internet | Di luar scope |

## 13. Risiko dan Mitigasi

| Risiko | Mitigasi |
| --- | --- |
| Deteksi executable salah | Skor kandidat, tandai "perlu dikonfirmasi", user bisa mengubah |
| Game Windows tertentu tidak jalan di Wine | Opsi prefix per game, log jelas, command bisa diubah |
| Arsip atau media berbahaya | Zero trust, validasi magic bytes, re-encode, batas ukuran, anti traversal |
| Ekstrak terganggu di tengah jalan | Tabel `jobs`, deteksi arsip stabil, pemulihan setelah crash |
| User mengubah prefix dan game hilang | Dialog konfirmasi, opsi pindahkan, pengecekan path saat startup |

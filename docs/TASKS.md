# TASKS: Game Launcher (Ubuntu Desktop)

Total 56 task. Format: `ID` Nama task. Selesai bila: kriteria. Butuh: task yang harus selesai dulu.

Aturan kerja:

- Kerjakan vertikal (satu jalur utuh dulu), bukan semua layer sekaligus.
- Test ditulis bersamaan dengan task, bukan di akhir.
- Satu task = satu commit kecil.
- Jangan lompat ke fase berikutnya sebelum gerbang fase ini lolos.
- Perlu perhatian ekstra: 1.11, 2.1, 2.2, 2.11.

---

## Fase 0: Setup

- [x] **0.1** Repo, venv, `pyproject.toml`, struktur folder
      Selesai bila: `python -m gamelauncher` menampilkan jendela kosong. Butuh: -
- [x] **0.2** Tooling: ruff, pytest, pre-commit
      Selesai bila: `pytest` dan `ruff check` hijau di repo kosong. Butuh: 0.1
- [x] **0.3** Logging berputar + path XDG
      Selesai bila: log tertulis di `~/.local/state/gamelauncher/`. Butuh: 0.1

Catatan SemVer: setelah fase 0 selesai, versi rilis yang dipakai adalah `0.1.0`.

---

## Fase 1: MVP

### Fondasi (core dan DB)

- [x] **1.1** `core/errors` + `messages`
      Selesai bila: hierarki exception + peta kode ke pesan ramah, ada test. Butuh: 0.2
- [x] **1.2** `core/paths`
      Selesai bila: tolak `../`, symlink keluar, dan direktori sistem; test lengkap. Butuh: 1.1
- [x] **1.3** `core/models` + `constants`
      Selesai bila: dataclass + genre bawaan + template deskripsi tersedia. Butuh: 0.1
- [x] **1.4** `db/engine`
      Selesai bila: koneksi per thread, PRAGMA (FK, WAL, busy_timeout) aktif, ada test. Butuh: 0.3
- [x] **1.5** Migrasi Alembic awal
      Selesai bila: skema lengkap + seed genre + template; upgrade dari DB kosong sukses. Butuh: 1.3, 1.4
- [x] **1.6** Repository `games` dan `taxonomy`
      Selesai bila: CRUD + relasi genre/tag/developer, tes dengan SQLite memori. Butuh: 1.5

### Service

- [x] **1.7** `game_service`
      Selesai bila: CRUD + validator logic + sinkron FTS dalam satu transaksi. Butuh: 1.2, 1.6
- [x] **1.8** `library_service`
      Selesai bila: search FTS, filter (AND), sort, keyset pagination; 1.000 data dummy < 100 ms. Butuh: 1.7
- [x] **1.9** `settings_service`
      Selesai bila: ubah games root/archive dir dengan validasi + konfirmasi; dir hilang tidak membuat crash. Butuh: 1.2
- [x] **1.10** `exe_detector`
      Selesai bila: heuristik skor + daftar abaikan (`unins*`, `setup*`, dll), tes dengan folder fixture. Butuh: 1.3
- [x] **1.11** `launcher` + `run_service`
      Selesai bila: `.sh` dan `.exe` (Wine global, lazy init) jalan tanpa shell; double-launch dicegah; exit code tercatat. Butuh: 1.7, 1.10
- [x] **1.12** Tambah game manual dari folder
      Selesai bila: pilih folder, exe terdeteksi, game masuk DB. Butuh: 1.7, 1.10

### UI

- [x] **1.13** Shell UI: main window, tema light/dark, `ViewState`, `state_panel`, `toast`
      Selesai bila: ganti tema persisten; panel Loading/Empty/Error/Success bisa dipakai ulang. Butuh: 0.1
- [x] **1.14** Library view: grid + list, livesearch, filter, sort
      Selesai bila: search tanpa tombol; 4 state tampil benar. Butuh: 1.8, 1.13
- [x] **1.15** Dialog create/edit game
      Selesai bila: validator UI + validator logic; command read-only, tombol Edit untuk mengubah. Butuh: 1.7, 1.13
- [ ] **1.16** Tombol Play + status proses
      Selesai bila: Play, disabled saat berjalan, error ramah + Lihat log. Butuh: 1.11, 1.14
- [ ] **1.17** Settings view
      Selesai bila: ubah direktori dengan dialog "at own risk". Butuh: 1.9, 1.13
- [ ] **1.18** Startup sequence + cek dependensi
      Selesai bila: dependensi hilang jadi peringatan, bukan crash; direktori hilang memunculkan dialog pemulihan. Butuh: 1.9
- [ ] **1.19** Global exception handler
      Selesai bila: error tak terduga menampilkan dialog ramah + Salin detail, tanpa stack trace. Butuh: 1.1, 1.13

### Gerbang MVP

- [ ] Tambah folder game, tampil di library
- [ ] Bisa dicari, difilter, diurutkan
- [ ] Play jalan (`.sh` dan `.exe` via Wine)
- [ ] Ganti tema dan ubah direktori berfungsi
- [ ] Tidak ada stack trace di layar
- [ ] Semua test hijau

---

## Fase 2: V1

### Worker dan ekstraksi

- [ ] **2.1** Repo `jobs` + `job_queue`
      Selesai bila: antrian dengan batas paralel per tipe; job `running` jadi `queued` saat startup. Butuh: 1.4
- [ ] **2.2** `infra/archive` (7z/unar)
      Selesai bila: zip, rar, 7z, tar.\* terekstrak; tolak traversal/symlink; cek disk + rasio kompres; tes arsip jahat. Butuh: 1.2
- [ ] **2.3** Arsip multi-part + password
      Selesai bila: part lengkap baru diproses; password diminta lewat dialog. Butuh: 2.2
- [ ] **2.4** `watcher` + debounce ukuran stabil
      Selesai bila: file yang masih dicopy tidak diproses; watcher pindah saat archive dir diubah. Butuh: 2.1, 1.9
- [ ] **2.5** `extract_service`
      Selesai bila: event, job, ekstrak ke games root, scan, game masuk DB; arsip tetap di asal. Butuh: 2.2, 2.4, 1.12
- [ ] **2.6** Dialog konflik nama
      Selesai bila: pilihan timpa/rename/lewati; tidak pernah menimpa diam-diam. Butuh: 2.5
- [ ] **2.7** UI progres ekstrak
      Selesai bila: progress bar, toast sukses, pesan ramah untuk gagal (disk penuh, rusak, terkunci). Butuh: 2.5, 1.13
- [ ] **2.8** Scan folder baru + "perlu dikonfirmasi"
      Selesai bila: game dengan banyak kandidat exe ditandai, user bisa memilih. Butuh: 2.5

### Media

- [ ] **2.9** Repo `media` + `infra/image`
      Selesai bila: magic bytes dicek, re-encode Pillow, batas dimensi/ukuran, nama hash. Butuh: 1.6
- [ ] **2.10** `infra/video`
      Selesai bila: ffprobe validasi + transcode (H.264, ultrafast, CRF tinggi, 720p, 30 fps, tanpa audio); video asli dibuang setelah sukses. Butuh: 2.1
- [ ] **2.11** `infra/downloader`
      Selesai bila: hanya http/https, blokir IP lokal/private, batas ukuran/redirect, timeout; tes SSRF. Butuh: 2.1
- [ ] **2.12** `media_service`
      Selesai bila: validasi + antrian + status pending sampai ready/failed + thumbnail + cover. Butuh: 2.9, 2.10, 2.11
- [ ] **2.13** UI media
      Selesai bila: dialog upload (lokal/URL), galeri, progres tahap, error ramah. Butuh: 2.12, 1.13

### Navigasi dan taksonomi

- [ ] **2.14** Infinite scroll
      Selesai bila: batch 40, lazy-load thumbnail, tanpa prev/next, tidak loncat saat data berubah. Butuh: 1.14
- [ ] **2.15** Halaman detail
      Selesai bila: cover, galeri, deskripsi, metadata, command read-only, info folder. Butuh: 2.13, 1.14
- [ ] **2.16** Sidebar daftar game
      Selesai bila: daftar jadi sidebar kiri di halaman detail, tetap bisa search/filter, game aktif ditandai. Butuh: 2.15
- [ ] **2.17** `taxonomy_service` + UI kelola
      Selesai bila: genre/tag/developer CRUD (konfirmasi jumlah game terdampak); tombol "Kembalikan genre bawaan". Butuh: 1.6, 1.13
- [ ] **2.18** Chip clickable (U10)
      Selesai bila: klik genre/tag/developer membuka daftar terfilter; chip bisa dihapus; scroll kembali saat Back. Butuh: 2.14, 2.17

### Gerbang V1

- [ ] Arsip baru di archive dir, game muncul dan bisa dimainkan tanpa langkah manual
- [ ] Video upload selalu terkompresi
- [ ] `.exe` palsu berekstensi `.jpg` ditolak
- [ ] Klik genre membuka daftar terfilter

---

## Fase 3: V1.5

- [ ] **3.1** Hover preview (U8)
      Selesai bila: delay 300 ms, 3 media di kiri card (flip jika di tepi), satu video aktif, decoder dilepas saat hover selesai, tidak muncul jika media kosong. Butuh: 2.13, 2.14
- [ ] **3.2** Grouping
      Selesai bila: CRUD grup, game di banyak grup, urutan grup, filter/chip grup. Butuh: 2.17
- [ ] **3.3** Status Selesai / Mentok update
      Selesai bila: badge di card/list, filter status, toggle dari detail. Butuh: 2.15
- [ ] **3.4** `mod_service` + UI
      Selesai bila: upload mod/save per game, validasi, daftar + hapus, backup save sebelum menimpa. Butuh: 2.15
- [ ] **3.5** Link install (F10)
      Selesai bila: CRUD situs, validasi http/https, buka di browser default. Butuh: 1.13
- [ ] **3.6** Wine prefix per game
      Selesai bila: checkbox di edit game, prefix di `prefixes/<id>`, `WINEPREFIX` otomatis, tawarkan hapus prefix saat game dihapus. Butuh: 1.11
- [ ] **3.7** Hapus game dua opsi
      Selesai bila: "Dari library saja" atau "beserta file" (konfirmasi dua langkah), cascade ke file media/mod. Butuh: 2.12, 3.4

### Gerbang V1.5

- [ ] Seluruh fitur di PRD sudah ada dan bisa dipakai

---

## Fase 4: V2

- [ ] **4.1** Suite test keamanan
      Selesai bila: fixture zip traversal, zip bomb kecil, symlink jahat, media palsu, URL `127.0.0.1`, polyglot; semua ditolak dengan pesan ramah. Butuh: Fase 2
- [ ] **4.2** Cleanup file yatim
      Selesai bila: pembersih untuk file tanpa baris DB, dan baris DB yang filenya hilang (`is_missing`). Butuh: 3.7
- [ ] **4.3** Pemulihan job
      Selesai bila: uji crash di tengah ekstrak/kompres, job bisa lanjut atau diulang. Butuh: 2.1
- [ ] **4.4** Backup DB otomatis
      Selesai bila: 5 salinan terakhir, restore diuji. Butuh: 1.5
- [ ] **4.5** Uji performa
      Selesai bila: 1.000 game dummy, search < 100 ms, scroll lancar, memori stabil. Butuh: 2.14
- [ ] **4.6** Audit empat state
      Selesai bila: semua layar punya Loading/Empty/Error/Success. Butuh: semua UI
- [ ] **4.7** Audit pesan error
      Selesai bila: tidak ada pesan teknis bocor; semua kode error punya pesan di `messages.py`. Butuh: 1.1
- [ ] **4.8** Packaging
      Selesai bila: `.deb` atau AppImage, cek dependensi saat pertama jalan, ikon + `.desktop`. Butuh: -
- [ ] **4.9** README singkat + panduan pengguna
      Selesai bila: cara pasang, struktur folder, troubleshooting umum. Butuh: 4.8

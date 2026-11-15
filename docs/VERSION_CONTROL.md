# Panduan Version Control: Game Launcher

Panduan ini berlaku untuk seluruh pengembangan proyek. Singkat, bisa dipindai, dan dipakai sebagai acuan harian.

File konfigurasi yang menyertai panduan ini:

| File | Lokasi di repo | Fungsi |
|---|---|---|
| `.gitignore` | root | Daftar file yang tidak boleh masuk git |
| `pull_request_template.md` | `.github/` | Template otomatis saat membuat PR |
| `ci.yml` | `.github/workflows/` | Pipeline GitHub Actions (lint + test) |

Ketiganya **harus berupa file terpisah di lokasi tersebut**, karena Git dan GitHub hanya membacanya dari sana. Panduan ini hanya menjelaskan cara memakainya.

---

## 1. Ringkasan Alur Kerja

```
1. git switch main && git pull
2. git switch -c feat/1.2-path-validator
3. kerjakan, commit kecil (conventional, atomic)
4. git push -u origin feat/1.2-path-validator
5. buka PR (judul conventional, isi template)
6. CI hijau, review diff sendiri
7. squash and merge, hapus branch
8. centang task di TASKS.md
9. (akhir fase) beri tag versi
```

Prinsip:
- `main` selalu dalam keadaan bisa jalan.
- Satu branch = satu task di `TASKS.md`.
- Satu PR = satu tujuan.
- Tidak ada push langsung ke `main`.

---

## 2. Penamaan Branch

Format: `<tipe>/<id-task>-<deskripsi-pendek>`

```
feat/1.2-path-validator
feat/2.2-archive-extract
fix/2.5-extract-name-conflict
chore/0.2-tooling
docs/4.9-readme
test/4.1-security-suite
```

Aturan:
- Huruf kecil, kata dipisah tanda hubung.
- ID task dimasukkan agar hubungan dengan `TASKS.md` jelas.
- Jangan satu branch untuk banyak task.
- Branch dihapus setelah merge.

---

## 3. Conventional Commits

Format: `tipe(scope): deskripsi`

| Tipe | Untuk |
|---|---|
| `feat` | Fitur baru |
| `fix` | Perbaikan bug |
| `refactor` | Ubah struktur tanpa ubah perilaku |
| `test` | Tambah/ubah test |
| `docs` | Dokumentasi |
| `chore` | Tooling, dependensi, konfigurasi |
| `perf` | Peningkatan performa |
| `build` / `ci` | Packaging / pipeline |

Scope memakai nama modul: `core`, `paths`, `db`, `archive`, `media`, `launcher`, `services`, `ui`, dan seterusnya.

Contoh:

```
feat(paths): tolak path traversal dan symlink keluar
fix(archive): cegah ekstrak ke luar folder tujuan
test(media): tambah fixture jpg palsu berisi exe
refactor(services): pisahkan validasi dari game_service
```

Aturan pesan:
- Baris pertama maksimal sekitar 72 karakter, bentuk perintah ("tambah", "perbaiki").
- Jelaskan **kenapa**, bukan hanya apa. Gunakan body commit bila perlu.
- Perubahan yang merusak kompatibilitas (misalnya skema DB) diberi `!` dan penjelasan:

```
feat(db)!: ganti kolom run_command menjadi run_argv

BREAKING CHANGE: data lama perlu migrasi, jalankan alembic upgrade head.
```

---

## 4. Atomic Commit

Satu commit = satu perubahan logis yang utuh.

Pecah per lapisan atau tujuan, bukan per file. Contoh satu task (2.2 archive):

```
feat(core): tambah ArchiveError dan kode error terkait
feat(archive): ekstrak zip/rar/7z lewat 7z
feat(archive): validasi traversal dan symlink saat ekstrak
test(archive): tambah fixture arsip jahat
```

Tips:
- Tiap commit sebaiknya lulus test sendiri.
- Pakai `git add -p` untuk memilih potongan perubahan.
- Cek `git status` dan `git diff --staged` sebelum commit.
- Jangan commit kode yang dikomentari, debug print, atau perubahan tak terkait.

---

## 5. Pull Request

Judul PR memakai format conventional, karena dengan squash merge judul itulah yang menjadi pesan commit di `main`:

```
feat(paths): tolak path traversal dan symlink keluar
```

Isi PR mengikuti template di `.github/pull_request_template.md` (otomatis muncul saat membuat PR).

Sebelum membuat PR:

```bash
git fetch origin
git rebase origin/main          # perbarui branch dari main
git rebase -i origin/main       # opsional: rapikan commit
git push --force-with-lease     # aman untuk branch pribadi
```

Aturan force push:
- Pakai `--force-with-lease`, bukan `--force`.
- Jangan pernah force push ke `main`.

Review diri sendiri sebelum merge:
- Buka tab "Files changed", baca seluruh diff seolah orang lain yang menulis.
- Cari debug print, path pribadi, secret, dan perubahan di luar tujuan PR.

---

## 6. Strategi Merge

| Strategi | Hasil di `main` | Catatan |
|---|---|---|
| Merge commit | Semua commit + satu commit merge | Riwayat ramai |
| **Squash and merge** | Satu commit per PR | **Dipakai di proyek ini** |
| Rebase and merge | Semua commit branch, lurus | Perlu commit branch yang rapi |

Alasan squash: commit kecil di dalam branch boleh agak berantakan, hasil akhir di `main` tetap satu commit bersih per task. Kalau nanti ingin menjaga atomic commit terlihat di `main`, pindah ke rebase and merge.

---

## 7. Proteksi Branch `main`

Atur di GitHub: Settings, Branches, Add branch protection rule untuk `main`.

- Require a pull request before merging: aktif
- Require status checks to pass before merging: aktif, pilih check `test` dari CI
- Require linear history: aktif (opsional)
- Require approvals: **jangan diaktifkan** (solo, tidak bisa menyetujui PR sendiri)

Di Settings, General, Pull Requests:
- Allow squash merging: aktif
- Allow merge commits dan rebase merging: boleh dimatikan agar tidak salah pilih
- Automatically delete head branches: aktif

---

## 8. GitHub Actions (CI) untuk Pemula

**Apa itu:** GitHub Actions menjalankan perintah otomatis di server GitHub setiap kali ada kejadian tertentu (misalnya PR dibuat). Di proyek ini dipakai untuk menjalankan lint dan test, sehingga gerbang "semua test hijau" tidak bergantung pada ingatan.

**Istilah:**

| Istilah | Arti |
|---|---|
| Workflow | Satu file `.yml` di `.github/workflows/` |
| Trigger (`on`) | Kejadian yang memicu: `push`, `pull_request`, dll |
| Job | Sekumpulan langkah yang jalan di satu mesin |
| Step | Satu langkah: perintah shell atau action siap pakai |
| Runner | Mesin yang menjalankan job (`ubuntu-latest`) |
| Action | Paket langkah siap pakai, misalnya `actions/checkout` |

**Cara kerja di proyek ini:**
1. Kamu push branch dan buka PR.
2. GitHub otomatis menjalankan `ci.yml`.
3. Di halaman PR muncul status: kuning (berjalan), hijau (lolos), merah (gagal).
4. Kalau merah: buka "Details", lihat langkah mana yang gagal, perbaiki di lokal, push lagi. CI jalan ulang otomatis.

**Kebiasaan penting:** jalankan perintah yang sama di lokal sebelum push, supaya CI tidak gagal karena hal sepele:

```bash
ruff check .
ruff format --check .
pytest
```

**Catatan keamanan:**
- Versi action dikunci (`@v4`, `@v5`), jangan memakai `@main` atau `@latest`.
- Workflow hanya diberi izin baca (`permissions: contents: read`).
- Jangan menaruh secret di file workflow. Kalau suatu saat perlu, pakai Settings, Secrets.

**Pengujian GUI di CI:** CI tidak punya layar. Test dijalankan dengan `QT_QPA_PLATFORM=offscreen`. Itu sebabnya logic dan viewmodel dipisah dari widget, supaya hampir semua bisa dites tanpa GUI.

**Asumsi file `ci.yml`:** proyek memakai `pyproject.toml` dengan extra `dev` (berisi pytest, ruff, dan lain-lain), diinstal lewat `pip install -e ".[dev]"`. Sesuaikan jika berbeda.

---

## 9. Versioning dan Rilis

Pakai Semantic Versioning: `MAJOR.MINOR.PATCH`.

| Versi | Tonggak |
|---|---|
| `0.1.0` | Gerbang MVP lolos |
| `0.2.0` | Gerbang V1 lolos |
| `0.3.0` | Gerbang V1.5 lolos |
| `1.0.0` | V2 (hardening + packaging) selesai |
| `x.y.Z` | Perbaikan bug kecil setelah rilis |

Cara memberi tag:

```bash
git switch main && git pull
git tag -a v0.1.0 -m "MVP"
git push origin v0.1.0
```

Lalu buat GitHub Release dari tag tersebut (lampirkan `.deb` atau AppImage di fase packaging). Simpan `CHANGELOG.md`, yang bisa disusun dari pesan commit conventional.

---

## 10. Aturan Khusus Proyek Ini

| Hal | Aturan |
|---|---|
| Migrasi Alembic | File migrasi yang sudah ada di `main` tidak diedit. Perubahan skema = migrasi baru. PR yang mengubah skema wajib menyertakan migrasinya |
| Fixture jahat (zip bomb, traversal) | Jangan commit file besar. Buat secara programatik di test, atau simpan versi sangat kecil dengan komentar jelas |
| Media/binary besar | Jangan commit. Pakai file sangat kecil atau hasilkan lewat skrip |
| Data pribadi | Path pribadi, daftar game, dan database `*.db` tidak boleh masuk repo |
| Secret/token | Tidak pernah masuk repo. Jika terlanjur ter-commit, anggap sudah bocor: cabut/ganti, jangan hanya menghapus commit |

---

## 11. Kebiasaan Harian

- Commit sering, push sering. Branch yang hanya ada di laptop berisiko hilang.
- Satu PR = satu tujuan. Bug lain yang ditemukan di tengah jalan dicatat dulu, dikerjakan di branch terpisah.
- Jangan lompat ke fase berikutnya sebelum gerbang fase ini lolos.
- Tarik `main` terbaru sebelum membuat branch baru.

---

## 12. Salah Commit? Cara Memperbaiki

| Situasi | Perintah |
|---|---|
| Pesan commit terakhir salah (belum push) | `git commit --amend` |
| Batalkan commit terakhir, simpan perubahan | `git reset --soft HEAD~1` |
| Batalkan perubahan di file (belum commit) | `git restore <file>` |
| Keluarkan file dari staging | `git restore --staged <file>` |
| Commit sudah ada di `main` | `git revert <hash>` (jangan menulis ulang riwayat) |
| File sensitif terlanjur ter-commit | Cabut/ganti secret-nya dulu, baru bersihkan riwayat |
| Lupa branch baru, sudah terlanjur commit di `main` lokal | Buat branch dari posisi itu: `git branch feat/xxx`, lalu `git reset --hard origin/main` di `main` |

---

## 13. Setup Awal (sekali saja)

1. Buat repo di GitHub, clone ke lokal (di WSL, simpan repo di filesystem Linux seperti `~/projects`, bukan di `/mnt/c`, supaya git dan inotify lebih cepat dan andal).
2. Salin `.gitignore`, `.github/pull_request_template.md`, `.github/workflows/ci.yml`, dan `docs/VERSION_CONTROL.md` ke repo.
3. Commit awal langsung ke `main` (satu-satunya pengecualian):
   `chore: inisialisasi repo dengan konfigurasi git dan CI`
4. Aktifkan proteksi `main` dan pengaturan merge (bagian 7). Aktifkan setelah CI pernah berjalan sekali, supaya check `test` bisa dipilih.
5. Mulai dari task 0.1 di branch `chore/0.1-project-setup`.

---

## 14. Contekan Cepat

```bash
git switch main && git pull                  # mulai dari main terbaru
git switch -c feat/<id>-<nama>               # branch baru
git add -p                                   # pilih perubahan per potongan
git commit -m "feat(scope): deskripsi"
git push -u origin <nama-branch>             # push pertama kali
git fetch origin && git rebase origin/main   # sinkron dengan main
git push --force-with-lease                  # setelah rebase
git branch -d <nama-branch>                  # hapus branch lokal setelah merge
git log --oneline --graph --decorate         # lihat riwayat ringkas
```

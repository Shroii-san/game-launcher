# Spesifikasi Skema Database SQLite

Dokumen ini menjelaskan keputusan desain, struktur relasi, definisi tabel (DDL), contoh *query* utama, serta tanggung jawab *service layer* untuk skema database SQLite.

---

## 1. Keputusan Desain & Alasannya

| Keputusan | Alasan |
| :--- | :--- |
| **Tabel grup dinamai `user_groups`, bukan `groups`** | `GROUPS` adalah *keyword* SQL di SQLite versi baru. Memakai nama tersebut memaksa penggunaan tanda kutip setiap saat dan rentan menimbulkan *error* yang membingungkan. |
| **`folder_path` disimpan absolut** | Sesuai PRD, game lama boleh dibiarkan di lokasi lama saat *games root* diganti. Jika menggunakan *path* relatif, referensi game akan putus. Ditambahkan pula kolom `is_missing` untuk menandai folder yang hilang. |
| **Run command disimpan sebagai JSON array (`run_argv`), bukan string** | Perintah dijalankan lewat `subprocess` tanpa *shell*. Menyimpan string mentah memaksa proses *parsing* dan membuka celah *command injection*. Tampilan *read-only* di UI dirangkai langsung dari *array* ini. |
| **Pencarian menggunakan FTS5** | Fitur *livesearch* pada 1.000+ game menggunakan `LIKE '%x%'` akan mulai lambat dan tidak mendukung peringkat relevansi. FTS5 sudah menjadi ekstensi bawaan SQLite. |
| **Cover menggunakan `media.is_cover`, bukan `games.cover_id`** | Menghindari *circular foreign key* (tabel `games` merujuk ke `media`, dan `media` merujuk kembali ke `games`). |
| **Infinite scroll menggunakan *keyset pagination*** | Penggunaan `OFFSET` semakin lambat pada halaman dalam dan hasil dapat bergeser/loncat jika ada data baru masuk saat *scrolling*. *Keyset* bekerja dengan prinsip "lanjut setelah item terakhir". |
| **Wine prefix tidak disimpan di DB** | *Path* dapat diturunkan secara deterministik (`prefixes/<game_id>`). Database cukup menyimpan mode-nya saja (`global` atau `per_game`). |
| **Genre bawaan ditandai `is_default`** | Daftar bawaan dikelola di dalam kode aplikasi. Tombol reset cukup menyisipkan kembali nama genre yang hilang menggunakan `INSERT OR IGNORE`. |

---

## 2. Ringkasan Relasi Tabel

| Relasi | Tipe Relasi | Keterangan |
| :--- | :--- | :--- |
| `games` $\leftrightarrow$ `genres`, `tags`, `developers`, `user_groups` | *Many-to-Many* | Menggunakan tabel penghubung (*junction tables*). |
| `games` $\rightarrow$ `media` | *One-to-Many* | `ON DELETE CASCADE`. |
| `games` $\rightarrow$ `mods` | *One-to-Many* | `ON DELETE CASCADE`. |
| `games` $\rightarrow$ `jobs` | *One-to-Many* (Opsional) | `ON DELETE SET NULL` saat data game dihapus. |
| `install_links`, `settings` | Berdiri sendiri (*Standalone*) | Tidak memiliki *foreign key* ke tabel lain. |

---

## 3. Data Definition Language (DDL)

```sql
-- Jalankan setiap kali membuka koneksi
PRAGMA foreign_keys = ON;
PRAGMA journal_mode = WAL;
PRAGMA busy_timeout = 5000;

-- ==========================================
-- TABEL UTAMA
-- ==========================================

CREATE TABLE games (
    id                 INTEGER PRIMARY KEY,
    name               TEXT    NOT NULL CHECK (length(name) BETWEEN 1 AND 200),
    folder_path        TEXT    NOT NULL UNIQUE,
    run_type           TEXT    NOT NULL DEFAULT 'custom'
                               CHECK (run_type IN ('exe', 'sh', 'custom')),
    run_argv           TEXT    NOT NULL DEFAULT '[]',     -- JSON array
    run_env            TEXT    NOT NULL DEFAULT '{}',     -- JSON object
    run_cwd            TEXT,
    needs_confirmation INTEGER NOT NULL DEFAULT 0 CHECK (needs_confirmation IN (0, 1)),
    wine_prefix_mode   TEXT    NOT NULL DEFAULT 'global'
                               CHECK (wine_prefix_mode IN ('global', 'per_game')),
    status             TEXT    NOT NULL DEFAULT 'none'
                               CHECK (status IN ('none', 'completed', 'stalled')),
    description        TEXT    NOT NULL DEFAULT '',
    is_missing         INTEGER NOT NULL DEFAULT 0 CHECK (is_missing IN (0, 1)),
    play_count         INTEGER NOT NULL DEFAULT 0,
    last_played_at     TEXT,
    created_at         TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    updated_at         TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
);

CREATE INDEX idx_games_name        ON games (name COLLATE NOCASE, id);
CREATE INDEX idx_games_created     ON games (created_at, id);
CREATE INDEX idx_games_last_played ON games (last_played_at, id);
CREATE INDEX idx_games_status      ON games (status);

-- ==========================================
-- TABEL MASTER & KATEGORI
-- ==========================================

CREATE TABLE genres (
    id         INTEGER PRIMARY KEY,
    name       TEXT    NOT NULL UNIQUE COLLATE NOCASE CHECK (length(name) BETWEEN 1 AND 50),
    is_default INTEGER NOT NULL DEFAULT 0 CHECK (is_default IN (0, 1))
);

CREATE TABLE tags (
    id   INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE COLLATE NOCASE CHECK (length(name) BETWEEN 1 AND 50)
);

CREATE TABLE developers (
    id   INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE COLLATE NOCASE CHECK (length(name) BETWEEN 1 AND 100)
);

CREATE TABLE user_groups (
    id         INTEGER PRIMARY KEY,
    name       TEXT    NOT NULL UNIQUE COLLATE NOCASE CHECK (length(name) BETWEEN 1 AND 50),
    sort_order INTEGER NOT NULL DEFAULT 0
);

-- ==========================================
-- TABEL PENGHUBUNG (MANY-TO-MANY)
-- ==========================================

CREATE TABLE game_genres (
    game_id  INTEGER NOT NULL REFERENCES games(id)  ON DELETE CASCADE,
    genre_id INTEGER NOT NULL REFERENCES genres(id) ON DELETE CASCADE,
    PRIMARY KEY (game_id, genre_id)
);
CREATE INDEX idx_game_genres_genre ON game_genres (genre_id);

CREATE TABLE game_tags (
    game_id INTEGER NOT NULL REFERENCES games(id) ON DELETE CASCADE,
    tag_id  INTEGER NOT NULL REFERENCES tags(id)  ON DELETE CASCADE,
    PRIMARY KEY (game_id, tag_id)
);
CREATE INDEX idx_game_tags_tag ON game_tags (tag_id);

CREATE TABLE game_developers (
    game_id      INTEGER NOT NULL REFERENCES games(id)      ON DELETE CASCADE,
    developer_id INTEGER NOT NULL REFERENCES developers(id) ON DELETE CASCADE,
    PRIMARY KEY (game_id, developer_id)
);
CREATE INDEX idx_game_developers_dev ON game_developers (developer_id);

CREATE TABLE game_user_groups (
    game_id  INTEGER NOT NULL REFERENCES games(id)       ON DELETE CASCADE,
    group_id INTEGER NOT NULL REFERENCES user_groups(id) ON DELETE CASCADE,
    PRIMARY KEY (game_id, group_id)
);
CREATE INDEX idx_game_user_groups_group ON game_user_groups (group_id);

-- ==========================================
-- TABEL ASET & EKSTENSI GAME
-- ==========================================

CREATE TABLE media (
    id          INTEGER PRIMARY KEY,
    game_id     INTEGER NOT NULL REFERENCES games(id) ON DELETE CASCADE,
    kind        TEXT    NOT NULL CHECK (kind IN ('image', 'video')),
    source_type TEXT    NOT NULL CHECK (source_type IN ('local', 'url')),
    source_ref  TEXT,
    stored_path TEXT,
    thumb_path  TEXT,
    sha256      TEXT,
    width       INTEGER,
    height      INTEGER,
    duration_ms INTEGER,
    size_bytes  INTEGER,
    status      TEXT    NOT NULL DEFAULT 'pending'
                        CHECK (status IN ('pending', 'processing', 'ready', 'failed')),
    error_code  TEXT,
    is_cover    INTEGER NOT NULL DEFAULT 0 CHECK (is_cover IN (0, 1)),
    sort_order  INTEGER NOT NULL DEFAULT 0,
    created_at  TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
);

CREATE INDEX idx_media_game ON media (game_id, status, sort_order);
CREATE UNIQUE INDEX uq_media_one_cover ON media (game_id) WHERE is_cover = 1;

CREATE TABLE mods (
    id          INTEGER PRIMARY KEY,
    game_id     INTEGER NOT NULL REFERENCES games(id) ON DELETE CASCADE,
    kind        TEXT    NOT NULL CHECK (kind IN ('mod', 'save')),
    name        TEXT    NOT NULL CHECK (length(name) BETWEEN 1 AND 200),
    stored_path TEXT    NOT NULL,
    size_bytes  INTEGER,
    note        TEXT    NOT NULL DEFAULT '',
    created_at  TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
);

CREATE INDEX idx_mods_game ON mods (game_id, kind);

-- ==========================================
-- TABEL UTILITAS & SISTEM
-- ==========================================

CREATE TABLE install_links (
    id         INTEGER PRIMARY KEY,
    name       TEXT    NOT NULL CHECK (length(name) BETWEEN 1 AND 100),
    url        TEXT    NOT NULL CHECK (url LIKE 'http://%' OR url LIKE 'https://%'),
    sort_order INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE settings (
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL -- JSON
);

CREATE TABLE jobs (
    id           INTEGER PRIMARY KEY,
    type         TEXT    NOT NULL
                         CHECK (type IN ('extract', 'compress_video', 'download_media', 'scan')),
    status       TEXT    NOT NULL DEFAULT 'queued'
                         CHECK (status IN ('queued', 'running', 'done', 'failed', 'cancelled')),
    game_id      INTEGER REFERENCES games(id) ON DELETE SET NULL,
    payload      TEXT    NOT NULL DEFAULT '{}', -- JSON
    progress     INTEGER NOT NULL DEFAULT 0 CHECK (progress BETWEEN 0 AND 100),
    error_code   TEXT,
    error_detail TEXT,
    created_at   TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    started_at   TEXT,
    finished_at  TEXT
);

CREATE INDEX idx_jobs_status ON jobs (status, created_at);

-- ==========================================
-- FULL-TEXT SEARCH (FTS5)
-- ==========================================

-- Kolom meta berisi gabungan genre + tag + developer, diisi oleh service layer.
-- Nilai rowid pada games_fts disamakan dengan games.id.
CREATE VIRTUAL TABLE games_fts USING fts5 (
    name, description, meta,
    tokenize = 'unicode61 remove_diacritics 2'
);
```

---

## 4. Contoh Query Penting

### A. Livesearch + Filter Genre + Keyset Pagination (Urut Nama)
```sql
SELECT g.id, g.name, g.status
FROM games g
JOIN games_fts f ON f.rowid = g.id
WHERE games_fts MATCH :query
  AND EXISTS (
      SELECT 1 
      FROM game_genres gg 
      WHERE gg.game_id = g.id AND gg.genre_id = :genre_id
  )
  AND (g.name COLLATE NOCASE, g.id) > (:last_name, :last_id)
ORDER BY g.name COLLATE NOCASE, g.id
LIMIT 40;
```
> **Catatan:** Untuk menerapkan filter `AND` pada beberapa *tag* sekaligus, ulangi blok `EXISTS` untuk masing-masing *tag*. Pendekatan ini paling jelas dan cepat untuk jumlah *tag* yang kecil.

### B. Hover Preview (Mengambil 3 Media Utama)
```sql
SELECT id, kind, thumb_path, stored_path
FROM media
WHERE game_id = :game_id 
  AND status = 'ready'
ORDER BY is_cover DESC, sort_order, id
LIMIT 3;
```

---

## 5. Tanggung Jawab Service Layer (Di Luar Cakupan Database)

Hal-hal berikut tidak dapat ditangani secara otomatis oleh database dan **wajib** diimplementasikan pada *service layer* aplikasi:

* **Penghapusan File di Disk:** Klausa `ON DELETE CASCADE` hanya menghapus baris data di tabel. Penghapusan fisik file media, mod, maupun direktori game harus dilakukan oleh kode aplikasi, disertai mekanisme *cleanup* berkala untuk membersihkan *orphan files* (file yatim).
* **Sinkronisasi `games_fts`:** Setiap kali data game dibuat atau diubah, *service* harus memperbarui baris yang sesuai di tabel virtual `games_fts` di dalam satu transaksi database yang sama.
* **Validasi Path:** `CHECK` *constraint* di SQLite tidak memadai untuk keamanan sistem berkas. *Service* wajib memvalidasi bahwa *path* bukan merupakan direktori sistem dan tidak mengandung *path traversal* (seperti `../`).
* **Pemulihan *Background Jobs* (Job Recovery):** Saat aplikasi pertama kali dijalankan (*startup*), semua *job* yang masih berstatus `running` harus diubah kembali menjadi `queued` (menandakan aplikasi sempat *crash* atau tertutup paksa di tengah proses).
* **Seeding Data Awal:** Pengisian (*seeding*) daftar genre bawaan serta *template* deskripsi dijalankan melalui skrip migrasi awal menggunakan Alembic.
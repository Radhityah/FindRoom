"""
database.py
===========
DATABASE FindRoom (SQLite).
File database: data/findroom.db  (dibuat otomatis saat server pertama kali jalan).

Tabel:
- users     : data orang yang login (NIM unik)
- bookings  : data booking ruang (terhubung ke users lewat NIM)

Semua orang (Deni, Yuni, dst) membaca & menulis ke database yang SAMA,
jadi booking Deni langsung terlihat oleh Yuni.
"""

import json
import os
import sqlite3
import sys
from contextlib import contextmanager

# Jika dijalankan sebagai .exe, simpan data di samping file .exe (bukan di folder sementara)
FOLDER = os.path.dirname(sys.executable) if getattr(sys, "frozen", False) else os.path.dirname(os.path.abspath(__file__))
FILE_DB = os.path.join(FOLDER, "data", "findroom.db")
FILE_USER_LAMA = os.path.join(FOLDER, "data", "users.json")
FILE_BOOKING_LAMA = os.path.join(FOLDER, "data", "bookings.json")


@contextmanager
def koneksi():
    """Membuka koneksi database, otomatis commit jika berhasil / rollback jika gagal."""
    os.makedirs(os.path.dirname(FILE_DB), exist_ok=True)
    db = sqlite3.connect(FILE_DB, timeout=10)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys = ON")
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def buat_tabel():
    """Membuat tabel jika belum ada, lalu memindahkan data JSON lama (jika ada)."""
    with koneksi() as db:
        db.execute("PRAGMA journal_mode = WAL")   # supaya banyak orang bisa baca bersamaan
        db.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                nim       TEXT PRIMARY KEY,
                name      TEXT NOT NULL,
                kelas     TEXT NOT NULL,
                angkatan  TEXT NOT NULL,
                phone     TEXT NOT NULL DEFAULT ''
            );

            CREATE TABLE IF NOT EXISTS bookings (
                id        TEXT PRIMARY KEY,
                room      TEXT NOT NULL,
                date      TEXT NOT NULL,      -- format YYYY-MM-DD
                start     TEXT NOT NULL,      -- format HH:MM
                "end"     TEXT NOT NULL,
                course    TEXT NOT NULL,
                purpose   TEXT NOT NULL,
                by_name   TEXT NOT NULL,
                by_nim    TEXT NOT NULL REFERENCES users(nim),
                kelas     TEXT NOT NULL,
                angkatan  TEXT NOT NULL,
                phone     TEXT NOT NULL,
                created   TEXT NOT NULL
            );

            CREATE INDEX IF NOT EXISTS idx_booking_ruang_tanggal ON bookings(room, date);
            CREATE INDEX IF NOT EXISTS idx_booking_nim ON bookings(by_nim);
        """)
        pindahkan_json_lama(db)


def pindahkan_json_lama(db):
    """Sekali saja: salin isi users.json & bookings.json lama ke database."""
    if db.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 0 and os.path.exists(FILE_USER_LAMA):
        with open(FILE_USER_LAMA, encoding="utf-8") as f:
            for u in json.load(f):
                db.execute(
                    "INSERT OR IGNORE INTO users (nim, name, kelas, angkatan, phone) VALUES (?,?,?,?,?)",
                    (u["nim"], u["name"], u["kelas"], u["angkatan"], u.get("phone", "")),
                )
    if db.execute("SELECT COUNT(*) FROM bookings").fetchone()[0] == 0 and os.path.exists(FILE_BOOKING_LAMA):
        with open(FILE_BOOKING_LAMA, encoding="utf-8") as f:
            for b in json.load(f):
                db.execute(
                    """INSERT OR IGNORE INTO bookings
                       (id, room, date, start, "end", course, purpose, by_name, by_nim, kelas, angkatan, phone, created)
                       VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                    (b["id"], b["room"], b["date"], b["start"], b["end"], b["course"], b["purpose"],
                     b["by_name"], b["by_nim"], b["kelas"], b["angkatan"], b["phone"], b["created"]),
                )


# ---------- USERS ----------
def ambil_user(nim):
    with koneksi() as db:
        baris = db.execute("SELECT * FROM users WHERE nim = ?", (nim,)).fetchone()
    return dict(baris) if baris else None


def simpan_user(nama, nim, kelas, angkatan):
    """Menambah user baru, atau memperbarui user lama (NIM sama). Mengembalikan data user."""
    with koneksi() as db:
        db.execute(
            """INSERT INTO users (nim, name, kelas, angkatan) VALUES (?,?,?,?)
               ON CONFLICT(nim) DO UPDATE SET name=excluded.name, kelas=excluded.kelas, angkatan=excluded.angkatan""",
            (nim, nama, kelas, angkatan),
        )
        return dict(db.execute("SELECT * FROM users WHERE nim = ?", (nim,)).fetchone())


def ubah_telepon(nim, nomor):
    with koneksi() as db:
        db.execute("UPDATE users SET phone = ? WHERE nim = ?", (nomor, nim))
        return dict(db.execute("SELECT * FROM users WHERE nim = ?", (nim,)).fetchone())


# ---------- BOOKINGS ----------
def semua_booking():
    with koneksi() as db:
        baris = db.execute('SELECT * FROM bookings ORDER BY date, start').fetchall()
    return [_ke_kamus(b) for b in baris]


def booking_pada(tanggal):
    with koneksi() as db:
        baris = db.execute("SELECT * FROM bookings WHERE date = ?", (tanggal,)).fetchall()
    return [_ke_kamus(b) for b in baris]


def ambil_booking(booking_id):
    with koneksi() as db:
        b = db.execute("SELECT * FROM bookings WHERE id = ?", (booking_id,)).fetchone()
    return _ke_kamus(b) if b else None


def tambah_booking(b):
    with koneksi() as db:
        db.execute(
            """INSERT INTO bookings
               (id, room, date, start, "end", course, purpose, by_name, by_nim, kelas, angkatan, phone, created)
               VALUES (:id,:room,:date,:start,:end,:course,:purpose,:by_name,:by_nim,:kelas,:angkatan,:phone,:created)""",
            b,
        )


def hapus_booking(booking_id):
    with koneksi() as db:
        db.execute("DELETE FROM bookings WHERE id = ?", (booking_id,))


def _ke_kamus(baris):
    return dict(baris)   # kolom "end" sudah bernama "end", sama seperti format lama

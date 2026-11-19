"""
app.py  —  FindRoom (FULL PYTHON)
=================================
Seluruh aplikasi ditulis dengan Python (Flask). Tidak ada file HTML / JavaScript terpisah.

Pembagian file:
- app.py          : server & alur aplikasi (file ini)
- desain.py       : seluruh tampilan (warna, ukuran, logo, login, denah, booking saya, profil, form, dst.)
- database.py     : database SQLite (data/findroom.db)
- logika.py       : aturan / pemeriksaan isian & bentrok jadwal
- data_kampus.py  : data gedung, ruang, jam kuliah, jadwal reguler

Cara kerja: setiap tombol di tampilan mengirim permintaan ke server ini, server memeriksa
aturan, membaca / menulis database, lalu membuat halaman baru. Semua orang yang membuka
server yang SAMA melihat data booking yang SAMA (booking Deni langsung terlihat oleh Yuni).

Cara menjalankan:  python app.py
"""

import os
import secrets
import socket
import sys
import threading
import webbrowser
import uuid
from datetime import date, datetime, timedelta
from urllib.parse import urlencode

from flask import Flask, Response, redirect, request, session

import database
import desain
from data_kampus import JUMLAH_HARI, SEMUA_RUANG, SLOT_JAM, jadwal_reguler
from logika import cari_bentrok, cek_booking, cek_login, rapikan_nomor_hp
from desain import LOGO_SVG

# Jika dijalankan sebagai .exe, simpan data di samping file .exe (bukan di folder sementara)
FOLDER = os.path.dirname(sys.executable) if getattr(sys, "frozen", False) else os.path.dirname(os.path.abspath(__file__))
FILE_RAHASIA = os.path.join(FOLDER, "data", "rahasia.key")

app = Flask(__name__)
database.buat_tabel()

# Kunci agar dua orang yang booking bersamaan tidak saling menimpa data
# (cek bentrok + simpan dijadikan satu langkah)
kunci = threading.Lock()


def siapkan_kunci_rahasia():
    """Kunci rahasia untuk menandai siapa yang sedang login (disimpan agar tidak berubah tiap restart)."""
    os.makedirs(os.path.dirname(FILE_RAHASIA), exist_ok=True)
    if not os.path.exists(FILE_RAHASIA):
        with open(FILE_RAHASIA, "w", encoding="utf-8") as f:
            f.write(secrets.token_hex(32))
    with open(FILE_RAHASIA, encoding="utf-8") as f:
        return f.read().strip()


app.secret_key = siapkan_kunci_rahasia()
app.permanent_session_lifetime = timedelta(days=365)   # login diingat lama, seperti aplikasi aslinya


@app.after_request
def jangan_simpan_cache(respon):
    respon.headers["Cache-Control"] = "no-store"
    return respon


# ---------- Bantuan ----------
def pengguna_aktif():
    """Data orang yang sedang login (None jika belum login)."""
    nim = session.get("nim")
    user = database.ambil_user(nim) if nim else None
    return user if user and user.get("kelas") else None


def baca_konteks(user):
    """Membaca tab, tanggal, dan gedung yang dipilih dari alamat / form."""
    sekarang = datetime.now()
    try:
        tab = int(request.values.get("tab", 0))
    except ValueError:
        tab = 0
    if tab not in (0, 1, 2):
        tab = 0

    tanggal = request.values.get("date", "")
    try:
        d = date.fromisoformat(tanggal)
        sah = sekarang.date() <= d < sekarang.date() + timedelta(days=JUMLAH_HARI)
    except ValueError:
        sah = False
    if not sah:
        tanggal = desain.tanggal_awal(sekarang)

    gedung = request.values.get("building", "")
    if gedung not in desain.BUILDINGS:
        gedung = next(iter(desain.BUILDINGS))
    return desain.Konteks(user, tab, tanggal, gedung, sekarang)


def simpan_toast(pesan, warna):
    session["toast"] = [pesan, warna]


def ambil_toast():
    t = session.pop("toast", None)
    return tuple(t) if t else None


def angka(nilai, default=-1):
    try:
        return int(nilai)
    except (TypeError, ValueError):
        return default


# ---------- Proses (aturan aplikasi) ----------
def proses_login(nama, nim, kelas, angkatan):
    """Hasil: (user, errors). Salah satunya kosong."""
    kesalahan = cek_login(nama, nim, kelas, angkatan)
    if kesalahan:
        return None, kesalahan
    with kunci:
        lama = database.ambil_user(nim)
        if lama and lama["name"].lower() != nama.lower():
            return None, {"nim": "NIM ini sudah terdaftar atas nama lain."}
        return database.simpan_user(nama, nim, kelas, angkatan), {}


def proses_booking(nim, ruang, tanggal, mulai, selesai, matkul, keperluan, nomor_hp):
    """Hasil berupa kamus: {"booking": ...} atau {"errors": ...} atau {"clashes": [...]}."""
    # 1. Periksa isian
    kesalahan = cek_booking(ruang, tanggal, mulai, selesai, matkul, keperluan, nomor_hp)
    if kesalahan:
        return {"errors": kesalahan}

    with kunci:
        # 2. Pastikan pemesan sudah login
        user = database.ambil_user(nim)
        if not user:
            return {"errors": {"time": "Silakan login ulang."}, "login_ulang": True}

        # 3. Cek bentrok dengan jadwal kuliah reguler & booking orang lain
        semua_jadwal = jadwal_reguler(date.fromisoformat(tanggal)) + database.booking_pada(tanggal)
        jadwal_bentrok = cari_bentrok(semua_jadwal, ruang, tanggal, mulai, selesai)
        if jadwal_bentrok:
            return {"clashes": jadwal_bentrok}

        # 4. Simpan booking baru
        booking = {
            "id": uuid.uuid4().hex[:10],
            "room": ruang,
            "date": tanggal,
            "start": mulai,
            "end": selesai,
            "course": matkul,
            "purpose": keperluan,
            "by_name": user["name"],
            "by_nim": user["nim"],
            "kelas": user["kelas"],
            "angkatan": user["angkatan"],
            "phone": rapikan_nomor_hp(nomor_hp),
            "created": datetime.now().isoformat(timespec="seconds"),
        }
        database.tambah_booking(booking)
        database.ubah_telepon(user["nim"], booking["phone"])   # ingat nomor HP untuk booking berikutnya
    return {"booking": booking}


def proses_batal(nim, booking_id):
    """Hasil: pesan kesalahan, atau None jika berhasil."""
    with kunci:
        booking = database.ambil_booking(booking_id)
        if not booking:
            return "Booking tidak ditemukan."
        if booking["by_nim"] != nim:
            return "Kamu hanya bisa membatalkan booking milikmu sendiri."
        selesai = datetime.combine(date.fromisoformat(booking["date"]), datetime.strptime(booking["end"], "%H:%M").time())
        if selesai <= datetime.now():
            return "Booking yang sudah selesai tidak bisa dibatalkan."
        database.hapus_booking(booking_id)
    return None


# ---------- Halaman ----------
@app.get("/")
def beranda():
    user = pengguna_aktif()
    if not user:
        return desain.halaman_login(toast=ambil_toast())

    c = baca_konteks(user)
    modal = None
    jenis = request.args.get("modal", "")
    room = request.args.get("room", "")
    if room in SEMUA_RUANG:
        if jenis == "sel" and 0 <= angka(request.args.get("slot")) < len(SLOT_JAM):
            modal = {"jenis": "sel", "room": room, "slot": angka(request.args.get("slot"))}
        elif jenis == "form":
            modal = {"jenis": "form", "room": room, "start": request.args.get("start", ""), "end": request.args.get("end", "")}
        elif jenis == "sukses":
            modal = {"jenis": "sukses", "room": room, "start": request.args.get("start", ""), "end": request.args.get("end", "")}
    if jenis == "batal":
        modal = {"jenis": "batal", "id": request.args.get("id", "")}
        if room in SEMUA_RUANG and 0 <= angka(request.args.get("slot")) < len(SLOT_JAM):
            modal["slot"] = angka(request.args.get("slot"))

    # Halaman memuat ulang sendiri tiap beberapa detik agar booking orang lain langsung terlihat.
    # Alamatnya diberi penanda "r" yang bergantian (1 / 2) supaya browser benar-benar memuat ulang,
    # dan penanda posisi "p" (denah / chip-aktif) agar layar kembali ke bagian yang sama.
    argumen = request.args.to_dict()
    posisi = argumen.get("p", "")
    posisi = posisi if posisi in ("denah", "chip-aktif") else ""
    argumen["r"] = "2" if argumen.get("r") == "1" else "1"
    alamat_segar = "/?" + urlencode(argumen) + (f"#{posisi}" if posisi else "")
    memuat_ulang = "r" in request.args      # halaman hasil muat ulang tidak perlu animasi masuk lagi
    return desain.halaman_utama(c, modal, ambil_toast(), segarkan_url=alamat_segar, tanpa_animasi=memuat_ulang)


@app.get("/logo.svg")
def logo():
    return Response(LOGO_SVG, mimetype="image/svg+xml")


# ---------- Login & keluar ----------
@app.post("/login")
def login():
    nilai = {
        "name": " ".join(str(request.form.get("name", "")).split()),
        "nim": str(request.form.get("nim", "")).strip(),
        "kelas": str(request.form.get("kelas", "")).strip(),
        "angkatan": str(request.form.get("angkatan", "")).strip(),
    }
    user, kesalahan = proses_login(nilai["name"], nilai["nim"], nilai["kelas"], nilai["angkatan"])
    if not user:
        return desain.halaman_login(request.form, kesalahan), 422
    session.permanent = True
    session["nim"] = user["nim"]
    return redirect("/?tab=0")


@app.post("/keluar")
def keluar():
    session.clear()
    return redirect("/")


# ---------- Booking ----------
@app.post("/booking")
def buat_booking():
    user = pengguna_aktif()
    if not user:
        return redirect("/")
    c = baca_konteks(user)
    ruang = str(request.form.get("room", ""))
    mulai = str(request.form.get("start", ""))
    selesai = str(request.form.get("end", ""))
    matkul = " ".join(str(request.form.get("course", "")).split())
    keperluan = str(request.form.get("purpose", ""))
    nomor_hp = str(request.form.get("phone", ""))

    hasil = proses_booking(user["nim"], ruang, c.tanggal, mulai, selesai, matkul, keperluan, nomor_hp)
    if hasil.get("login_ulang"):
        session.clear()
        return redirect("/")
    if "booking" in hasil:
        c.tab = 0
        return redirect(c.url("denah", modal="sukses", room=ruang, start=mulai, end=selesai))

    # Gagal: tampilkan lagi form booking lengkap dengan pesan dari Python
    errors = hasil.get("errors", {})
    pesan = errors.get("time", "")
    if hasil.get("clashes"):
        pesan = "Bentrok dengan: " + "; ".join(f"{j['start']} - {j['end']} {j['course']}" for j in hasil["clashes"])
    modal = {
        "jenis": "form", "room": ruang, "start": mulai, "end": selesai,
        "nilai": {"course": matkul, "purpose": keperluan, "phone": nomor_hp},
        "errors": errors, "pesan": pesan,
    }
    c.tab = 0
    return desain.halaman_utama(c, modal), 422


@app.post("/batal")
def batal_booking():
    user = pengguna_aktif()
    if not user:
        return redirect("/")
    c = baca_konteks(user)
    kesalahan = proses_batal(user["nim"], str(request.form.get("id", "")))
    if kesalahan:
        simpan_toast(kesalahan, "var(--danger)")
    else:
        simpan_toast("Booking dibatalkan. Kelas kembali tersedia.", "var(--success)")
    return redirect(c.url("denah" if c.tab == 0 else ""))


# ---------- Menjalankan server ----------
def ip_laptop():
    """Mencari alamat IP laptop di WiFi, supaya bisa dibuka dari HP."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except OSError:
        return "127.0.0.1"
    finally:
        s.close()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print("\n  Server FindRoom (Python) berjalan!")
    print(f"  - Buka di laptop : http://localhost:{port}")
    print(f"  - Buka di HP     : http://{ip_laptop()}:{port}   (HP & laptop harus satu WiFi)")
    print("  Tekan Ctrl+C untuk menghentikan server.\n")
    threading.Timer(1.5, lambda: webbrowser.open(f"http://localhost:{port}")).start()   # buka browser otomatis
    app.run(host="0.0.0.0", port=port, debug=False, threaded=True)

"""
logika.py
=========
Berisi LOGIKA / ATURAN aplikasi FindRoom:
- memeriksa isian login
- memeriksa isian booking
- mengecek apakah jadwal bentrok
"""

from datetime import date, datetime, timedelta

from data_kampus import JAM_BUKA, JAM_TUTUP, JUMLAH_HARI, KELAS, KEPERLUAN, SEMUA_RUANG


def ke_menit(jam):
    """Mengubah jam "09:10" menjadi menit (9 x 60 + 10 = 550) supaya mudah dibandingkan."""
    j, m = jam.split(":")
    return int(j) * 60 + int(m)


def jam_valid(jam):
    """Benar jika teks jam berformat JJ:MM, misalnya 07:30."""
    try:
        datetime.strptime(jam, "%H:%M")
        return True
    except (TypeError, ValueError):
        return False


def rapikan_nomor_hp(nomor):
    """
    Mengubah nomor HP ke format 08xxxxxxxxxx.
    Contoh: "+62 812-3456-7890" -> "081234567890".
    Jika tidak valid, hasilnya None.
    """
    angka = "".join(huruf for huruf in str(nomor or "") if huruf.isdigit())
    if angka.startswith("62"):
        angka = "0" + angka[2:]
    elif angka.startswith("8"):
        angka = "0" + angka
    if angka.startswith("08") and 10 <= len(angka) <= 14:
        return angka
    return None


def bentrok(mulai_a, selesai_a, mulai_b, selesai_b):
    """
    Dua jadwal BENTROK jika:
    jadwal A mulai sebelum jadwal B selesai  DAN  jadwal B mulai sebelum jadwal A selesai.
    Contoh: 09:10-10:50 dan 10:00-11:00 -> bentrok.
    """
    return ke_menit(mulai_a) < ke_menit(selesai_b) and ke_menit(mulai_b) < ke_menit(selesai_a)


def cari_bentrok(daftar_jadwal, ruang, tanggal, mulai, selesai):
    """Mengembalikan semua jadwal di ruang & tanggal yang sama yang jamnya bertabrakan."""
    return [
        j for j in daftar_jadwal
        if j["room"] == ruang and j["date"] == tanggal and bentrok(j["start"], j["end"], mulai, selesai)
    ]


def cek_login(nama, nim, kelas, angkatan):
    """Memeriksa isian login. Hasilnya kamus {nama_kolom: pesan_kesalahan}. Kosong = semua benar."""
    kesalahan = {}

    if not nama:
        kesalahan["name"] = "Nama wajib diisi."
    elif len(nama) < 3:
        kesalahan["name"] = "Nama terlalu pendek."

    if not nim:
        kesalahan["nim"] = "NIM wajib diisi."
    elif not nim.isdigit():
        kesalahan["nim"] = "NIM hanya boleh berisi angka."

    if kelas not in KELAS:
        kesalahan["kelas"] = "Pilih kelas kamu."

    if not angkatan:
        kesalahan["angkatan"] = "Angkatan wajib diisi."
    elif not (angkatan.isdigit() and len(angkatan) == 4):
        kesalahan["angkatan"] = "Angkatan harus berupa 4 angka tahun (contoh: 2023)."

    return kesalahan


def cek_booking(ruang, tanggal, mulai, selesai, matkul, keperluan, nomor_hp):
    """Memeriksa isian booking. Hasilnya kamus {nama_kolom: pesan_kesalahan}. Kosong = semua benar."""
    kesalahan = {}
    sekarang = datetime.now()

    if ruang not in SEMUA_RUANG:
        kesalahan["time"] = "Ruang tidak dikenal."

    # Tanggal harus antara hari ini sampai 13 hari ke depan
    try:
        hari = date.fromisoformat(tanggal)
    except (TypeError, ValueError):
        hari = None
        kesalahan["time"] = "Tanggal tidak valid."
    if hari and not (sekarang.date() <= hari < sekarang.date() + timedelta(days=JUMLAH_HARI)):
        kesalahan["time"] = f"Booking hanya untuk hari ini sampai {JUMLAH_HARI - 1} hari ke depan."

    # Jam mulai & selesai
    if "time" not in kesalahan:
        if not jam_valid(mulai) or not jam_valid(selesai):
            kesalahan["time"] = "Isi jam mulai dan jam selesai."
        elif ke_menit(selesai) <= ke_menit(mulai):
            kesalahan["time"] = "Jam selesai harus setelah jam mulai."
        elif ke_menit(mulai) < ke_menit(JAM_BUKA) or ke_menit(selesai) > ke_menit(JAM_TUTUP):
            kesalahan["time"] = f"Ruang hanya bisa dibooking pukul {JAM_BUKA} - {JAM_TUTUP}."
        elif datetime.combine(hari, datetime.strptime(mulai, "%H:%M").time()) < sekarang:
            kesalahan["time"] = "Jam mulai sudah lewat."

    if not matkul:
        kesalahan["course"] = "Isi nama mata kuliah / kegiatan."
    elif len(matkul) > 100:
        kesalahan["course"] = "Nama mata kuliah / kegiatan maksimal 100 karakter."

    if keperluan not in KEPERLUAN:
        kesalahan["course"] = kesalahan.get("course") or "Pilih keperluan."

    if not rapikan_nomor_hp(nomor_hp):
        kesalahan["phone"] = "Nomor HP tidak valid (contoh: 081234567890)."

    return kesalahan

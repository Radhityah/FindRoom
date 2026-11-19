"""
data_kampus.py
==============
Berisi DATA KAMPUS yang dipakai aplikasi FindRoom:
- daftar gedung & ruang
- jam kuliah (slot)
- daftar kelas & keperluan
- jadwal kuliah reguler (data simulasi)

Data ini dikirim ke tampilan (JavaScript) lewat server Python (app.py).
"""

import random
from datetime import date, timedelta

# Gedung dan ruangnya: [kode ruang, keterangan]
GEDUNG = {
    "Gedung FG": [
        ["202", ""], ["Perpus", "Perpustakaan"], ["204", ""], ["205", ""],
        ["300", ""], ["302", ""], ["303", ""], ["304", ""],
        ["305", ""], ["306", ""], ["307", ""], ["308", "Microteaching"],
    ],
    "Gedung SS": [
        ["Labkom 1", "Lab Komputer"], ["Labkom 2", "Lab Komputer"], ["Seminar", "Ruang Seminar"],
    ],
}

# Semua kode ruang dalam satu daftar, contoh: ["202", "Perpus", "204", ...]
SEMUA_RUANG = [kode for daftar in GEDUNG.values() for kode, _ in daftar]

# Jam kuliah: [jam mulai, jam selesai]
SLOT_JAM = [
    ["07:30", "09:10"],
    ["09:10", "10:50"],
    ["10:50", "12:30"],
    ["13:00", "14:40"],
    ["14:40", "16:20"],
    ["16:20", "18:00"],
]

JAM_BUKA = "07:00"     # booking paling awal
JAM_TUTUP = "18:00"    # booking paling akhir
JUMLAH_HARI = 14       # bisa booking hari ini sampai 13 hari ke depan

KELAS = ["A11", "A12", "A13", "B1", "B2", "C1", "C2", "D1", "D2"]

KEPERLUAN = [
    "Perkuliahan",
    "Kuliah Pengganti",
    "Praktikum Komputer",
    "Microteaching / Praktik Mengajar",
    "Seminar Proposal / Hasil",
    "Belajar Kelompok",
    "Rapat Organisasi",
    "Ujian / Kuis",
]

# Mata kuliah untuk jadwal reguler (simulasi): [mata kuliah, dosen]
MATKUL_BIASA = [
    ["Kalkulus Diferensial", "Dosen Kalkulus"],
    ["Kalkulus Integral", "Dosen Kalkulus"],
    ["Aljabar Linear Elementer", "Dosen Aljabar"],
    ["Struktur Aljabar", "Dosen Aljabar"],
    ["Analisis Real", "Dosen Analisis"],
    ["Geometri Analitik", "Dosen Geometri"],
    ["Statistika Matematika", "Dosen Statistika"],
    ["Persamaan Diferensial", "Dosen Persamaan Diferensial"],
    ["Matematika Diskrit", "Dosen Matematika Diskrit"],
    ["Teori Bilangan", "Dosen Teori Bilangan"],
    ["Program Linear", "Dosen Program Linear"],
    ["Strategi Pembelajaran Matematika", "Dosen Pendidikan Matematika"],
]
MATKUL_LAB = [
    ["Komputasi Matematika", "Dosen Komputasi"],
    ["Pemrograman Komputer", "Dosen Komputasi"],
    ["Media Pembelajaran Berbasis TIK", "Dosen Pendidikan Matematika"],
    ["Metode Numerik", "Dosen Metode Numerik"],
]
MATKUL_KHUSUS = {
    "308": [["Microteaching", "Dosen Pendidikan Matematika"]],
    "Perpus": [["Seminar Pendidikan Matematika", "Dosen Pembimbing"], ["Metodologi Penelitian", "Dosen Metodologi"]],
    "Seminar": [["Seminar Proposal", "Dosen Penguji"], ["Seminar Hasil", "Dosen Penguji"], ["Kuliah Umum", "Dosen Tamu"]],
}


def jadwal_reguler(tanggal):
    """
    Membuat jadwal kuliah reguler untuk satu tanggal (data simulasi).
    Hasilnya selalu sama untuk tanggal yang sama, karena angka acaknya memakai "seed".
    """
    if tanggal.weekday() == 6:      # hari Minggu kampus libur
        return []

    hasil = []
    for ruang in SEMUA_RUANG:
        for nomor_slot, (mulai, selesai) in enumerate(SLOT_JAM):
            acak = random.Random(f"{ruang}|{tanggal.isoformat()}|{nomor_slot}")

            peluang = 0.2 if tanggal.weekday() == 5 else 0.42    # Sabtu lebih sepi
            if ruang in MATKUL_KHUSUS:
                peluang = peluang / 2
                pilihan = MATKUL_KHUSUS[ruang]
            elif ruang.startswith("Labkom"):
                pilihan = MATKUL_LAB
            else:
                pilihan = MATKUL_BIASA

            if acak.random() < peluang:
                matkul, dosen = acak.choice(pilihan)
                hasil.append({
                    "room": ruang,
                    "date": tanggal.isoformat(),
                    "start": mulai,
                    "end": selesai,
                    "course": matkul,
                    "by_name": dosen,
                    "purpose": "Jadwal Kuliah Reguler",
                    "regular": True,
                })
    return hasil


def jadwal_semua_hari():
    """Jadwal reguler untuk hari ini sampai 13 hari ke depan, dikelompokkan per tanggal."""
    hari_ini = date.today()
    hasil = {}
    for i in range(JUMLAH_HARI):
        tanggal = hari_ini + timedelta(days=i)
        hasil[tanggal.isoformat()] = jadwal_reguler(tanggal)
    return hasil

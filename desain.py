"""
desain.py
=========
SELURUH TAMPILAN FindRoom dalam SATU file, ditulis sepenuhnya dengan Python.

Isi file ini (berurutan dari atas):
1. Warna, ukuran, animasi (CSS) dan logo (LOGO_SVG)  -> sama persis dengan desain asli
2. Pembuat halaman: login, denah, booking saya, profil, form booking, dst.
   (setiap "view" adalah satu fungsi Python yang menghasilkan teks HTML)

Tidak ada JavaScript. Setiap ketukan pada tampilan adalah tautan / tombol form
yang dikirim ke server Python (lihat app.py), lalu server membuat halaman baru.
"""

import html
import math
from datetime import date, datetime, timedelta
from urllib.parse import urlencode

import database
from data_kampus import GEDUNG, JAM_BUKA, JAM_TUTUP, JUMLAH_HARI, KELAS, KEPERLUAN, SLOT_JAM, jadwal_reguler
from logika import ke_menit

# ---------- Gaya tampilan (CSS) & logo ----------
CSS = r'''/* ================= FindRoom – gaya tampilan ================= */
:root {
  --primary: #2563eb;
  --primary-dark: #1e3a8a;
  --night: #172554;
  --rose: #e11d48;
  --gold: #f59e0b;
  --bg: #f4f5fb;
  --surface: #ffffff;
  --text: #0f172a;
  --muted: #64748b;
  --line: #e2e8f0;
  --success: #16a34a;
  --danger: #e11d48;

  --free-bg: #dcfce7;
  --free-line: #86efac;
  --partial-bg: #fef3c7;
  --partial-line: #f59e0b;
  --booked: #f43f5e;
  --past-bg: #eef2f6;

  --radius-lg: 26px;
  --radius-md: 18px;
  --radius-sm: 12px;
  --shadow: 0 12px 30px -12px rgba(23, 37, 84, 0.18);
  --shadow-strong: 0 24px 50px -18px rgba(37, 99, 235, 0.55);
  --grad: linear-gradient(135deg, var(--night) 0%, var(--primary) 55%, var(--rose) 100%);
  --font: "Plus Jakarta Sans", system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
}

* { box-sizing: border-box; margin: 0; padding: 0; }
html, body { height: 100%; }
body {
  font-family: var(--font);
  color: var(--text);
  background: #e9eaf5;
  -webkit-font-smoothing: antialiased;
  -webkit-tap-highlight-color: transparent;
}
button, input, select { font: inherit; color: inherit; }
button { cursor: pointer; border: none; background: none; }
[hidden] { display: none !important; }

/* Bingkai seukuran HP agar tetap rapi saat dibuka di laptop */
#app {
  max-width: 440px;
  min-height: 100vh;
  min-height: 100dvh;
  margin: 0 auto;
  background: var(--bg);
  position: relative;
  overflow-x: hidden;
}
@media (min-width: 480px) {
  #app { box-shadow: 0 0 60px rgba(23, 37, 84, 0.15); }
}

/* ================= LOGIN ================= */
.login {
  min-height: 100vh;
  min-height: 100dvh;
  display: flex;
  flex-direction: column;
  background: var(--grad);
  position: relative;
  overflow: hidden;
}
.login::before,
.login::after {
  content: "";
  position: absolute;
  border-radius: 50%;
  filter: blur(10px);
  pointer-events: none;
}
.login::before {
  width: 320px; height: 320px;
  top: -120px; right: -110px;
  background: radial-gradient(circle, rgba(244, 63, 94, 0.55), transparent 70%);
}
.login::after {
  width: 260px; height: 260px;
  top: 180px; left: -140px;
  background: radial-gradient(circle, rgba(253, 230, 138, 0.25), transparent 70%);
}

.login-hero {
  position: relative;
  z-index: 1;
  padding: 64px 28px 48px;
  text-align: center;
  color: #fff;
  animation: rise 0.7s ease both;
}
.logo-wrap {
  width: 112px; height: 112px;
  margin: 0 auto 22px;
  border-radius: 34px;
  padding: 6px;
  background: rgba(255, 255, 255, 0.12);
  border: 1px solid rgba(255, 255, 255, 0.3);
  backdrop-filter: blur(8px);
  box-shadow: 0 20px 40px -10px rgba(0, 0, 0, 0.35);
  animation: float 5s ease-in-out infinite;
}
.logo-wrap img { width: 100%; height: 100%; display: block; }

.brand {
  font-size: 40px;
  font-weight: 800;
  letter-spacing: -1px;
  line-height: 1;
}
.brand em {
  font-family: "Playfair Display", Georgia, serif;
  font-style: italic;
  font-weight: 600;
  color: #fde68a;
}
.tagline {
  margin-top: 12px;
  font-size: 14.5px;
  line-height: 1.6;
  color: rgba(255, 255, 255, 0.82);
}
.divider-dots {
  display: flex; gap: 6px; justify-content: center; margin-top: 18px;
}
.divider-dots span {
  width: 6px; height: 6px; border-radius: 50%;
  background: rgba(255, 255, 255, 0.4);
}
.divider-dots span:nth-child(2) { width: 22px; border-radius: 6px; background: #fde68a; }

.login-card {
  position: relative;
  z-index: 1;
  flex: 1;
  background: var(--surface);
  border-radius: 34px 34px 0 0;
  padding: 32px 24px 28px;
  box-shadow: 0 -20px 40px -20px rgba(0, 0, 0, 0.3);
  animation: rise 0.7s 0.1s ease both;
}
.login-card h2 { font-size: 24px; font-weight: 800; }
.login-card .sub { color: var(--muted); font-size: 13.5px; margin-top: 4px; margin-bottom: 22px; }

.field { position: relative; margin-bottom: 14px; }
.field label {
  display: block;
  font-size: 12.5px;
  font-weight: 700;
  color: var(--text);
  margin-bottom: 7px;
}
.field .control { position: relative; }
.field .icon {
  position: absolute;
  left: 15px; top: 50%;
  transform: translateY(-50%);
  width: 20px; height: 20px;
  color: var(--muted);
  pointer-events: none;
}
.field input,
.field select {
  width: 100%;
  height: 54px;
  padding: 0 16px 0 46px;
  border-radius: 16px;
  border: 1.5px solid var(--line);
  background: #f8fafc;
  font-size: 15px;
  outline: none;
  transition: border-color 0.2s, box-shadow 0.2s, background 0.2s;
  appearance: none;
}
.field input.plain { padding-left: 16px; }
.field input:focus,
.field select:focus {
  border-color: var(--primary);
  background: #fff;
  box-shadow: 0 0 0 4px rgba(37, 99, 235, 0.12);
}
.field.invalid input,
.field.invalid select { border-color: var(--danger); }
.field .err { color: var(--danger); font-size: 12px; margin-top: 6px; min-height: 0; }
.field .hint { color: var(--muted); font-size: 11.5px; margin-top: 6px; }
.field .chev {
  position: absolute; right: 16px; top: 50%; transform: translateY(-50%);
  width: 18px; height: 18px; color: var(--muted); pointer-events: none;
}
.field .icon svg,
.field .chev svg,
.modal-sheet span > svg { width: 100%; height: 100%; display: block; }

.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  height: 52px;
  padding: 0 22px;
  border-radius: 16px;
  font-weight: 700;
  font-size: 15px;
  transition: transform 0.15s, box-shadow 0.2s, opacity 0.2s;
  text-decoration: none;
}
.btn:active { transform: scale(0.97); }
.btn svg { width: 20px; height: 20px; }
.btn-primary { background: var(--grad); color: #fff; box-shadow: var(--shadow-strong); }
.btn-block { width: 100%; }
.btn-ghost { color: var(--muted); }
.btn-outline { border: 1.5px solid var(--line); color: var(--text); background: #fff; }
.btn-danger-outline { border: 1.5px solid var(--danger); color: var(--danger); background: #fff; }
.btn-wa { background: #16a34a; color: #fff; }
.btn-sm { height: 40px; padding: 0 14px; font-size: 13px; border-radius: 12px; }

.secure-note {
  display: flex; align-items: center; justify-content: center; gap: 6px;
  margin-top: 16px; color: var(--muted); font-size: 12px;
}
.secure-note svg { width: 14px; height: 14px; }

/* ================= SHELL ================= */
.screen { padding: 18px 16px 110px; animation: fade 0.35s ease both; }

.bottom-nav {
  position: fixed;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 100%;
  max-width: 440px;
  display: flex;
  justify-content: space-around;
  background: rgba(255, 255, 255, 0.92);
  backdrop-filter: blur(14px);
  border-top: 1px solid var(--line);
  padding: 8px 8px calc(10px + env(safe-area-inset-bottom));
  z-index: 20;
}
.bottom-nav button {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 3px;
  font-size: 11.5px;
  font-weight: 600;
  color: var(--muted);
  padding: 6px 0;
}
.bottom-nav .pill {
  width: 58px; height: 32px; border-radius: 16px;
  display: grid; place-items: center;
  transition: background 0.2s;
}
.bottom-nav svg { width: 22px; height: 22px; }
.bottom-nav button.active { color: var(--primary); }
.bottom-nav button.active .pill { background: rgba(37, 99, 235, 0.12); }

/* ================= DENAH ================= */
.hero-card {
  background: var(--grad);
  border-radius: var(--radius-lg);
  padding: 20px;
  color: #fff;
  box-shadow: var(--shadow-strong);
  position: relative;
  overflow: hidden;
}
.hero-card::after {
  content: "";
  position: absolute;
  width: 200px; height: 200px;
  right: -70px; top: -80px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(255, 255, 255, 0.22), transparent 70%);
}
.hero-top { display: flex; justify-content: space-between; align-items: flex-start; gap: 12px; }
.hero-top small { color: rgba(255, 255, 255, 0.85); font-size: 13.5px; }
.hero-top h1 { font-size: 22px; font-weight: 800; margin: 2px 0; }
.hero-top .date { font-size: 12px; color: rgba(255, 255, 255, 0.75); }
.hero-top img { width: 48px; height: 48px; border-radius: 15px; }
.sync {
  display: inline-block;
  margin-top: 8px;
  padding: 3px 10px;
  border-radius: 20px;
  font-size: 10.5px;
  font-weight: 600;
  background: rgba(255, 255, 255, 0.16);
  color: rgba(255, 255, 255, 0.85);
}
.sync.on { background: rgba(34, 197, 94, 0.25); color: #dcfce7; }
.stats { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin-top: 16px; }
.stat {
  background: rgba(255, 255, 255, 0.14);
  border-radius: 16px;
  padding: 12px;
}
.stat b { display: block; font-size: 22px; font-weight: 800; }
.stat span { font-size: 11px; color: rgba(255, 255, 255, 0.8); }

.section-title {
  display: flex; align-items: center; gap: 8px;
  font-size: 15px; font-weight: 700;
  margin: 22px 0 12px;
}
.section-title svg { width: 18px; height: 18px; color: var(--primary); }

.h-scroll {
  display: flex; gap: 10px;
  overflow-x: auto;
  padding-bottom: 6px;
  scrollbar-width: none;
}
.h-scroll::-webkit-scrollbar { display: none; }

.date-chip {
  flex: 0 0 58px;
  height: 76px;
  border-radius: 18px;
  background: var(--surface);
  border: 1px solid var(--line);
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  transition: all 0.2s;
}
.date-chip small { font-size: 10px; color: var(--muted); }
.date-chip b { font-size: 20px; font-weight: 800; }
.date-chip.active { background: var(--primary); border-color: var(--primary); color: #fff; box-shadow: var(--shadow-strong); }
.date-chip.active small { color: #dbeafe; }

.pill-btn {
  flex: 0 0 auto;
  display: flex; align-items: center; gap: 6px;
  padding: 10px 16px;
  border-radius: 30px;
  border: 1px solid var(--line);
  background: var(--surface);
  font-size: 13px; font-weight: 600;
}
.pill-btn svg { width: 16px; height: 16px; color: var(--muted); }
.pill-btn.active { background: var(--text); color: #fff; border-color: var(--text); }
.pill-btn.active svg { color: #fff; }

.legend { display: flex; gap: 12px; flex-wrap: wrap; margin: 18px 0 12px; }
.legend span { display: flex; align-items: center; gap: 5px; font-size: 12px; color: var(--muted); }
.legend i { width: 16px; height: 16px; border-radius: 5px; display: inline-block; }

.card {
  background: var(--surface);
  border-radius: 22px;
  padding: 16px;
  box-shadow: var(--shadow);
}
.grid-head { display: flex; justify-content: space-between; align-items: center; gap: 8px; }
.grid-head h3 { font-size: 16px; font-weight: 800; }
.grid-head small { color: var(--muted); font-size: 12px; }
.badge {
  padding: 6px 10px; border-radius: 20px;
  background: #eff6ff; color: var(--primary);
  font-size: 11px; font-weight: 700; white-space: nowrap;
}
.board {
  height: 8px; border-radius: 8px; margin: 14px 0;
  background: linear-gradient(90deg, rgba(37, 99, 235, 0.15), var(--primary), rgba(37, 99, 235, 0.15));
}
.grid-scroll { overflow-x: auto; scrollbar-width: thin; }
.room-grid {
  display: grid;
  grid-template-columns: 66px repeat(6, 40px);
  gap: 8px 6px;
  align-items: center;
  width: max-content;
}
.room-grid .col-head { text-align: center; line-height: 1.15; }
.room-grid .col-head b { font-size: 10px; display: block; }
.room-grid .col-head small { font-size: 9px; color: var(--muted); }
.room-grid .room-name b { font-size: 12px; font-weight: 800; display: block; }
.room-grid .room-name small { font-size: 9.5px; color: var(--muted); }

.cell {
  width: 40px; height: 40px;
  border-radius: 12px;
  border: 1.5px solid transparent;
  display: grid; place-items: center;
  transition: transform 0.15s;
}
.cell:active { transform: scale(0.9); }
.cell svg { width: 20px; height: 20px; }
.cell.free, .legend .free { background: var(--free-bg); border-color: var(--free-line); }
.cell.partial, .legend .partial { background: var(--partial-bg); border-color: var(--partial-line); color: #d97706; }
.cell.booked, .legend .booked { background: var(--booked); color: #fff; }
.cell.mine, .legend .mine { background: var(--primary); color: #fff; }
.cell.past, .legend .past { background: var(--past-bg); border-color: var(--line); color: #cbd5e1; }

/* ================= BOOKING SAYA ================= */
.page-title { font-size: 26px; font-weight: 800; letter-spacing: -0.5px; }
.page-sub { color: var(--muted); font-size: 13px; margin-top: 2px; }

.ticket {
  display: flex;
  background: var(--surface);
  border-radius: 22px;
  box-shadow: var(--shadow);
  overflow: hidden;
  margin-bottom: 14px;
}
.ticket .stub {
  width: 78px;
  background: var(--grad);
  color: #fff;
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  padding: 14px 0;
  position: relative;
}
.ticket .stub::after {
  content: "";
  position: absolute;
  right: -1px; top: 10px; bottom: 10px;
  border-right: 2px dashed rgba(255, 255, 255, 0.5);
}
.ticket.done .stub { background: linear-gradient(135deg, #94a3b8, #64748b); }
.ticket .stub small { font-size: 11px; color: #dbeafe; }
.ticket .stub b { font-size: 26px; font-weight: 800; line-height: 1.1; }
.ticket .body { flex: 1; padding: 13px 10px 13px 14px; min-width: 0; }
.ticket .body h4 { font-size: 15.5px; font-weight: 800; display: flex; align-items: center; gap: 8px; }
.ticket .body p { font-size: 12.5px; color: var(--muted); margin-top: 3px; }
.ticket .body .course { color: var(--text); font-weight: 600; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.ticket .body .purpose { color: var(--primary); font-weight: 600; font-size: 11.5px; }
.tag { font-size: 10px; font-weight: 700; padding: 2px 8px; border-radius: 10px; background: #dcfce7; color: var(--success); }
.ticket.done .tag { background: #f1f5f9; color: var(--muted); }
.ticket .del { align-self: center; padding: 10px; color: var(--danger); }
.ticket .del svg { width: 20px; height: 20px; }

.empty { text-align: center; padding: 32px 20px; margin-top: 20px; }
.empty .circle {
  width: 90px; height: 90px; border-radius: 50%;
  background: #eff6ff; color: var(--primary);
  display: grid; place-items: center; margin: 0 auto 14px;
}
.empty .circle svg { width: 44px; height: 44px; }
.empty h3 { font-size: 17px; }
.empty p { color: var(--muted); font-size: 13px; margin: 6px 0 18px; }

/* ================= PROFIL ================= */
.profile-card {
  background: var(--grad);
  border-radius: var(--radius-lg);
  padding: 22px;
  color: #fff;
  display: flex; align-items: center; gap: 16px;
  box-shadow: var(--shadow-strong);
}
.avatar {
  width: 66px; height: 66px; border-radius: 50%;
  background: #fff; color: var(--primary);
  display: grid; place-items: center;
  font-size: 22px; font-weight: 800; flex-shrink: 0;
  box-shadow: 0 0 0 4px rgba(255, 255, 255, 0.25);
}
.profile-card h2 { font-size: 18px; font-weight: 800; }
.profile-card p { font-size: 13px; color: rgba(255, 255, 255, 0.85); margin-top: 2px; }
.chip-light {
  display: inline-block; margin-top: 6px;
  padding: 3px 10px; border-radius: 20px;
  background: rgba(255, 255, 255, 0.2); font-size: 11px;
}
.two-col { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin: 16px 0; }
.two-col .card svg { width: 24px; height: 24px; color: var(--primary); }
.two-col .card b { display: block; font-size: 24px; font-weight: 800; }
.two-col .card span { font-size: 12px; color: var(--muted); }
.steps h3 { font-size: 16px; font-weight: 800; margin-bottom: 14px; }
.step { display: flex; gap: 12px; margin-bottom: 14px; }
.step:last-child { margin-bottom: 0; }
.step .num {
  width: 30px; height: 30px; border-radius: 10px; flex-shrink: 0;
  background: var(--grad); color: #fff; font-weight: 800;
  display: grid; place-items: center;
}
.step b { font-size: 14px; }
.step p { font-size: 12px; color: var(--muted); }
.footer-note { text-align: center; color: var(--muted); font-size: 11px; margin-top: 18px; }

/* ================= MODAL ================= */
.modal { position: fixed; inset: 0; z-index: 50; display: flex; align-items: flex-end; justify-content: center; }
.modal-backdrop { position: absolute; inset: 0; background: rgba(15, 23, 42, 0.5); backdrop-filter: blur(3px); animation: fade 0.2s ease; }
.modal-sheet {
  position: relative;
  width: 100%;
  max-width: 440px;
  max-height: 92vh;
  overflow-y: auto;
  background: var(--surface);
  border-radius: 28px 28px 0 0;
  padding: 10px 20px calc(20px + env(safe-area-inset-bottom));
  animation: slideUp 0.3s cubic-bezier(0.2, 0.9, 0.3, 1);
}
.modal-sheet .grabber { width: 44px; height: 5px; border-radius: 5px; background: var(--line); margin: 0 auto 16px; }
.modal-sheet h3 { font-size: 20px; font-weight: 800; }
.modal-sheet .muted { color: var(--muted); font-size: 13px; }
.modal-actions { display: flex; gap: 10px; justify-content: flex-end; margin-top: 18px; }
.modal-actions .btn { flex: 1; }

.room-chip {
  display: flex; align-items: center; gap: 8px;
  background: #eff6ff; border-radius: var(--radius-sm);
  padding: 12px; margin: 16px 0;
  font-size: 13px; font-weight: 700;
}
.room-chip svg { width: 18px; height: 18px; color: var(--primary); }
.room-chip span { margin-left: auto; color: var(--muted); font-weight: 500; }
.time-row { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
.form-error {
  background: #fff1f2; color: var(--danger);
  border-radius: var(--radius-sm); padding: 10px 12px;
  font-size: 12.5px; margin-bottom: 12px;
}

.info-row { display: flex; gap: 12px; align-items: center; margin-top: 12px; }
.info-row .ic {
  width: 36px; height: 36px; border-radius: 12px; flex-shrink: 0;
  background: #f1f5f9; color: var(--primary);
  display: grid; place-items: center;
}
.info-row .ic svg { width: 18px; height: 18px; }
.info-row small { display: block; font-size: 11px; color: var(--muted); }
.info-row b { font-size: 14px; font-weight: 600; }
.occupant { border: 1px solid var(--line); background: #f8fafc; border-radius: 16px; padding: 4px 12px 12px; margin-top: 12px; }
.occupant .actions { display: flex; gap: 8px; flex-wrap: wrap; margin-top: 12px; }
.status-badge { font-size: 11px; font-weight: 700; padding: 4px 10px; border-radius: 20px; }

/* ================= TOAST ================= */
.toast {
  position: fixed;
  left: 50%; bottom: 96px;
  transform: translateX(-50%);
  max-width: 400px; width: calc(100% - 32px);
  background: var(--text); color: #fff;
  padding: 14px 16px; border-radius: 14px;
  font-size: 13.5px;
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.25);
  z-index: 60;
  animation: rise 0.25s ease;
}

/* ================= ANIMASI ================= */
@keyframes rise { from { opacity: 0; transform: translateY(16px); } to { opacity: 1; transform: none; } }
@keyframes fade { from { opacity: 0; } to { opacity: 1; } }
@keyframes slideUp { from { transform: translateY(100%); } to { transform: none; } }
@keyframes float { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-6px); } }
.toast { animation-name: toastIn; }
@keyframes toastIn { from { opacity: 0; transform: translate(-50%, 12px); } to { opacity: 1; transform: translate(-50%, 0); } }'''

LOGO_SVG = r'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 128 128" fill="none">
  <!-- FindRoom: pin lokasi berisi pintu (Find the Room) + lencana jam (Define the Time) -->
  <defs>
    <linearGradient id="fr-bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#1E3A8A"/>
      <stop offset="0.38" stop-color="#2563EB"/>
      <stop offset="0.82" stop-color="#E11D48"/>
      <stop offset="1" stop-color="#BE123C"/>
    </linearGradient>
    <linearGradient id="fr-sheen" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#FFFFFF" stop-opacity="0.14"/>
      <stop offset="0.5" stop-color="#FFFFFF" stop-opacity="0"/>
    </linearGradient>
    <filter id="fr-blur" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur stdDeviation="2"/>
    </filter>
  </defs>

  <rect width="128" height="128" rx="35" fill="url(#fr-bg)"/>
  <rect width="128" height="128" rx="35" fill="url(#fr-sheen)"/>

  <g transform="translate(64 64) scale(0.92) translate(-64 -64)">
    <!-- bayangan pin -->
    <ellipse cx="64" cy="106" rx="20" ry="4" fill="#000000" fill-opacity="0.28" filter="url(#fr-blur)"/>
    <!-- pin lokasi -->
    <path d="M39.06 66.67 A30 30 0 1 1 88.94 66.67 L64 104 Z" fill="#FFFFFF"/>
    <!-- pintu -->
    <path d="M52 66 V44 a12 12 0 0 1 24 0 V66 Z" fill="#1E3A8A"/>
    <rect x="48" y="64" width="32" height="4.5" rx="2.2" fill="#1E3A8A"/>
    <circle cx="68.5" cy="50" r="2.4" fill="#FFFFFF"/>

    <!-- lencana jam -->
    <circle cx="93" cy="89" r="18" fill="#000000" fill-opacity="0.22" filter="url(#fr-blur)"/>
    <circle cx="93" cy="86" r="17" fill="#FFFFFF"/>
    <circle cx="93" cy="86" r="12.2" stroke="#E11D48" stroke-width="2.6"/>
    <circle cx="93" cy="76.5" r="1.1" fill="#1E3A8A"/>
    <circle cx="102.5" cy="86" r="1.1" fill="#1E3A8A"/>
    <circle cx="93" cy="95.5" r="1.1" fill="#1E3A8A"/>
    <circle cx="83.5" cy="86" r="1.1" fill="#1E3A8A"/>
    <path d="M93 86 V78.5" stroke="#1E3A8A" stroke-width="2.8" stroke-linecap="round"/>
    <path d="M93 86 L98.5 89" stroke="#E11D48" stroke-width="2.8" stroke-linecap="round"/>
    <circle cx="93" cy="86" r="2.2" fill="#1E3A8A"/>
  </g>
</svg>
'''


# ---------- Data kampus ----------
BUILDINGS = GEDUNG
ROOM_NOTE = {kode: ket for daftar in GEDUNG.values() for kode, ket in daftar}
SLOTS = SLOT_JAM

DAY_NAMES = ["Minggu", "Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu"]
DAY_SHORT = ["Min", "Sen", "Sel", "Rab", "Kam", "Jum", "Sab"]
MONTHS = ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun", "Jul", "Agu", "Sep", "Okt", "Nov", "Des"]

FREE, PARTIAL, BOOKED, MINE, PAST = "free", "partial", "booked", "mine", "past"

# Jeda (detik) tampilan memuat ulang sendiri agar booking orang lain langsung terlihat
JEDA_SEGAR = 15

# ---------- Ikon (SVG garis) ----------
ICON_PATHS = {
    'user': '<circle cx="12" cy="8" r="4"/><path d="M4 21c0-4 4-6 8-6s8 2 8 6"/>',
    'id': '<rect x="3" y="5" width="18" height="14" rx="3"/><circle cx="9" cy="12" r="2.5"/><path d="M14 10h4M14 14h3"/>',
    'school': '<path d="M2 9l10-5 10 5-10 5z"/><path d="M6 11v5c3 2.5 9 2.5 12 0v-5"/>',
    'chevron': '<path d="M6 9l6 6 6-6"/>',
    'arrow': '<path d="M5 12h14M13 6l6 6-6 6"/>',
    'lock': '<rect x="5" y="11" width="14" height="10" rx="2"/><path d="M8 11V8a4 4 0 0 1 8 0v3"/>',
    'grid': '<rect x="3" y="3" width="7" height="7" rx="2"/><rect x="14" y="3" width="7" height="7" rx="2"/><rect x="3" y="14" width="7" height="7" rx="2"/><rect x="14" y="14" width="7" height="7" rx="2"/>',
    'ticket': '<path d="M3 8a2 2 0 0 0 2-2h14a2 2 0 0 0 2 2v2a2 2 0 0 0 0 4v2a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-2a2 2 0 0 0 0-4z"/><path d="M13 6v12" stroke-dasharray="2 2"/>',
    'calendar': '<rect x="3" y="5" width="18" height="16" rx="3"/><path d="M3 10h18M8 3v4M16 3v4"/>',
    'building': '<path d="M4 21V5a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v16M16 9h2a2 2 0 0 1 2 2v10M2 21h20M8 7h4M8 11h4M8 15h4"/>',
    'monitor': '<rect x="3" y="4" width="18" height="12" rx="2"/><path d="M8 20h8M12 16v4"/>',
    'check': '<path d="M5 12l5 5 9-10"/>',
    'minus': '<path d="M6 12h12"/>',
    'hourglass': '<path d="M6 3h12M6 21h12M7 3c0 5 10 5 10 9s-10 4-10 9M17 3c0 5-10 5-10 9"/>',
    'door': '<path d="M6 21V5a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v16M3 21h18"/><circle cx="14" cy="12" r="1"/>',
    'clock': '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
    'book': '<path d="M4 5a2 2 0 0 1 2-2h13v16H6a2 2 0 0 0-2 2z"/><path d="M4 19V5M19 19v2H6"/>',
    'tag': '<path d="M3 12V4h8l10 10-8 8z"/><circle cx="7.5" cy="8" r="1.5"/>',
    'phone': '<path d="M5 3h4l2 5-2.5 1.5a11 11 0 0 0 6 6L16 13l5 2v4a2 2 0 0 1-2 2A17 17 0 0 1 3 5a2 2 0 0 1 2-2z"/>',
    'chat': '<path d="M4 20l1.5-4A8 8 0 1 1 9 19z"/>',
    'trash': '<path d="M4 7h16M10 11v6M14 11v6M6 7l1 13h10l1-13M9 7V4h6v3"/>',
    'plus': '<path d="M12 5v14M5 12h14"/>',
    'logout': '<path d="M15 4h3a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2h-3M10 17l-5-5 5-5M5 12h11"/>',
    'person': '<circle cx="12" cy="8" r="4"/><path d="M4 21c0-4 4-6 8-6s8 2 8 6"/>',
    'history': '<path d="M3 12a9 9 0 1 0 3-6.7L3 8"/><path d="M3 3v5h5M12 7v5l3 2"/>',
    'upcoming': '<circle cx="12" cy="12" r="9"/><path d="M10 8l4 4-4 4"/>',
    'bookmark': '<path d="M6 3h12v18l-6-4-6 4z"/>',
    'download': '<path d="M12 3v12M7 10l5 5 5-5M5 21h14"/>',
}


def icon(nama):
    return (
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
        f'stroke-linecap="round" stroke-linejoin="round">{ICON_PATHS[nama]}</svg>'
    )


# ---------- Utilitas ----------
def esc(teks):
    return html.escape("" if teks is None else str(teks), quote=True)


def hari_js(d):
    """Nomor hari ala JavaScript: Minggu = 0 ... Sabtu = 6."""
    return (d.weekday() + 1) % 7


def from_min(m):
    return f"{m // 60:02d}:{m % 60:02d}"


def format_date(d):
    return f"{DAY_NAMES[hari_js(d)]}, {d.day} {MONTHS[d.month - 1]} {d.year}"


def short_date(d):
    return f"{DAY_SHORT[hari_js(d)]}, {d.day} {MONTHS[d.month - 1]}"


def time_label(x):
    return f"{x['start']} - {x['end']}"


def end_datetime(tanggal_iso, hhmm):
    return datetime.combine(date.fromisoformat(tanggal_iso), datetime.strptime(hhmm, "%H:%M").time())


def room_title(r):
    if r[:1].isdigit() or r == "Seminar":
        return f"Ruang {r}"
    if r == "Perpus":
        return "Perpustakaan"
    return r


def now_minutes(sekarang):
    return sekarang.hour * 60 + sekarang.minute


def wa_url(phone):
    return f"https://wa.me/62{phone[1:]}"


def tanggal_awal(sekarang):
    """Tanggal yang dibuka pertama kali: hari ini, atau besok jika kuliah hari ini sudah habis."""
    d = sekarang.date()
    if now_minutes(sekarang) >= ke_menit(SLOTS[-1][1]):
        d += timedelta(days=1)
    return d.isoformat()


# ---------- Data satu hari (jadwal reguler + booking dari database) ----------
class DataHari:
    def __init__(self, tanggal_iso, user, sekarang):
        self.tanggal = tanggal_iso
        self.user = user
        self.sekarang = sekarang
        self.reguler = jadwal_reguler(date.fromisoformat(tanggal_iso))
        self.booking = database.booking_pada(tanggal_iso)

    def occupants(self, room, start, end):
        """Semua jadwal reguler & booking di ruang ini yang bertabrakan dengan jam start-end."""
        semua = [j for j in self.reguler if j["room"] == room] + [b for b in self.booking if b["room"] == room]
        hasil = [x for x in semua if ke_menit(x["start"]) < ke_menit(end) and ke_menit(start) < ke_menit(x["end"])]
        return sorted(hasil, key=lambda x: x["start"])

    def is_mine(self, info):
        return bool(not info.get("regular") and self.user and info.get("by_nim") == self.user["nim"])

    def status(self, room, si):
        start, end = SLOTS[si]
        infos = self.occupants(room, start, end)
        if end_datetime(self.tanggal, end) <= self.sekarang:
            return PAST, infos
        if not infos:
            return FREE, infos
        if any(self.is_mine(i) for i in infos):
            return MINE, infos
        # hitung berapa menit slot ini yang sudah terpakai
        s, e = ke_menit(start), ke_menit(end)
        covered, cursor = 0, s
        for info in infos:
            a = max(ke_menit(info["start"]), cursor)
            b = min(ke_menit(info["end"]), e)
            if b > a:
                covered += b - a
                cursor = b
        return (BOOKED if covered >= e - s else PARTIAL), infos

    def default_times(self, si):
        """Jam awal form booking = jam slot yang diketuk (dimajukan jika sebagian sudah lewat)."""
        start, end = SLOTS[si]
        if self.tanggal == self.sekarang.date().isoformat() and ke_menit(start) < now_minutes(self.sekarang):
            start = from_min(math.ceil(now_minutes(self.sekarang) / 5) * 5)
        return start, end

    def free_gap(self, room, si):
        """Jam kosong pertama di slot ini, atau None jika sudah penuh."""
        start, end = self.default_times(si)
        for info in self.occupants(room, start, end):
            if info["start"] <= start:
                start = info["end"] if info["end"] > start else start
            else:
                end = info["start"]
                break
        return (start, end) if start < end else None


# ---------- Tautan antar halaman ----------
class Konteks:
    """Keadaan tampilan: siapa yang login, tab, tanggal & gedung yang dipilih."""

    def __init__(self, user, tab, tanggal, gedung, sekarang):
        self.user, self.tab, self.tanggal, self.gedung, self.sekarang = user, tab, tanggal, gedung, sekarang
        self.data = DataHari(tanggal, user, sekarang)

    def url(self, frag="", **ganti):
        q = {"tab": self.tab, "date": self.tanggal, "building": self.gedung}
        q.update({k: v for k, v in ganti.items() if v is not None})
        if frag:
            q["p"] = frag      # ingat posisi layar, dipakai saat halaman memuat ulang sendiri
        return "/?" + urlencode(q) + (f"#{frag}" if frag else "")

    def hidden(self, **tambah):
        """Isian tersembunyi agar form POST tahu tab/tanggal/gedung yang sedang dibuka."""
        nilai = {"tab": self.tab, "date": self.tanggal, "building": self.gedung, **tambah}
        return "".join(f'<input type="hidden" name="{k}" value="{esc(v)}" />' for k, v in nilai.items())


# ================= KERANGKA HALAMAN =================
CSS_TAMBAHAN = """
/* --- tambahan kecil agar tautan <a> tampil sama seperti tombol <button> aslinya --- */
a { color: inherit; text-decoration: none; }
.btn { text-align: center; }
.date-chip:focus { outline: none; }
.bottom-nav a {
  flex: 1; display: flex; flex-direction: column; align-items: center; gap: 3px;
  font-size: 11.5px; font-weight: 600; color: var(--muted); padding: 6px 0;
}
.bottom-nav a.active { color: var(--primary); }
.bottom-nav a.active .pill { background: rgba(37, 99, 235, 0.12); }
/* pesan toast menghilang sendiri setelah beberapa detik (aslinya diatur JavaScript) */
.toast { animation: toastIn 0.25s ease, toastOut 0.4s ease 2.6s forwards; }
@keyframes toastOut { to { opacity: 0; visibility: hidden; } }
"""


def halaman(isi, modal_html="", tutup_url="/", toast=None, segarkan_url=None, tanpa_animasi=False):
    """Membungkus isi halaman dengan <html>, <head>, modal, dan toast (sama seperti index.html asli)."""
    if modal_html:
        modal = (
            f'<div id="modal" class="modal"><a class="modal-backdrop" href="{esc(tutup_url)}" aria-label="Tutup"></a>'
            f'<div class="modal-sheet" role="dialog" aria-modal="true"><div class="grabber"></div>{modal_html}</div></div>'
        )
    else:
        modal = (
            '<div id="modal" class="modal" hidden><div class="modal-backdrop"></div>'
            '<div class="modal-sheet" role="dialog" aria-modal="true"></div></div>'
        )
    if toast:
        pesan, warna = toast
        toast_html = f'<div id="toast" class="toast" style="background:{warna}">{esc(pesan)}</div>'
    else:
        toast_html = '<div id="toast" class="toast" hidden></div>'
    # Muat ulang otomatis hanya saat tidak ada form/jendela yang terbuka
    meta_segar = f'<meta http-equiv="refresh" content="{JEDA_SEGAR};url={esc(segarkan_url)}" />' if segarkan_url else ""
    gaya_diam = "<style>.screen{animation:none}</style>" if tanpa_animasi else ""
    return f"""<!DOCTYPE html>
<html lang="id">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover" />
  <meta name="theme-color" content="#1E3A8A" />
  <meta name="description" content="FindRoom – cek ruang kelas kosong dan booking langsung dari HP." />
  <title>FindRoom – Cari &amp; Booking Ruang Kelas</title>
  <link rel="icon" type="image/svg+xml" href="/logo.svg" />
  <meta name="mobile-web-app-capable" content="yes" />
  <meta name="apple-mobile-web-app-capable" content="yes" />
  <meta name="apple-mobile-web-app-title" content="FindRoom" />
  <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent" />
  {meta_segar}
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link
    href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Playfair+Display:ital,wght@1,600&display=swap"
    rel="stylesheet"
  />
  <style>{CSS}{CSS_TAMBAHAN}</style>
  {gaya_diam}
</head>
<body>
  <div id="app">{isi}</div>

  {modal}
  {toast_html}
</body>
</html>"""


# ================= LOGIN =================
def halaman_login(nilai=None, errors=None, toast=None):
    nilai, errors = nilai or {}, errors or {}

    def field_kelas():
        pilihan = "".join(
            f'<option{" selected" if k == nilai.get("kelas") else ""}>{k}</option>' for k in KELAS
        )
        awal = "" if nilai.get("kelas") in KELAS else " selected"
        return f'<option value="" disabled{awal}>Pilih Kelas</option>{pilihan}'

    def cls(key):
        return " invalid" if errors.get(key) else ""

    isi = f"""
    <section class="login">
      <div class="login-hero">
        <div class="logo-wrap"><img src="/logo.svg" alt="Logo FindRoom" /></div>
        <h1 class="brand">Find<em>Room</em></h1>
        <p class="tagline">Find the Room, Define the Time.</p>
        <div class="divider-dots"><span></span><span></span><span></span></div>
      </div>

      <form class="login-card" id="loginForm" method="post" action="/login" novalidate>
        <h2>Selamat Datang 👋</h2>
        <p class="sub">Masukkan identitas mahasiswa kamu untuk mulai.</p>

        <div class="field{cls("name")}" data-field="name">
          <label for="name">Nama Lengkap</label>
          <div class="control">
            <span class="icon">{icon("user")}</span>
            <input id="name" name="name" autocomplete="name" placeholder="Masukkan Nama" value="{esc(nilai.get("name", ""))}" />
          </div>
          <div class="err">{esc(errors.get("name", ""))}</div>
        </div>

        <div class="field{cls("nim")}" data-field="nim">
          <label for="nim">NIM</label>
          <div class="control">
            <span class="icon">{icon("id")}</span>
            <input id="nim" name="nim" inputmode="numeric" placeholder="Masukkan NIM" value="{esc(nilai.get("nim", ""))}" />
          </div>
          <div class="err">{esc(errors.get("nim", ""))}</div>
        </div>

        <div class="field{cls("kelas")}" data-field="kelas">
          <label for="kelas">Kelas</label>
          <div class="control">
            <span class="icon">{icon("school")}</span>
            <select id="kelas" name="kelas">
              {field_kelas()}
            </select>
            <span class="chev">{icon("chevron")}</span>
          </div>
          <div class="err">{esc(errors.get("kelas", ""))}</div>
        </div>

        <div class="field{cls("angkatan")}" data-field="angkatan">
          <label for="angkatan">Angkatan</label>
          <div class="control">
            <span class="icon">{icon("calendar")}</span>
            <input id="angkatan" name="angkatan" inputmode="numeric" maxlength="4" placeholder="Masukkan Angkatan" value="{esc(nilai.get("angkatan", ""))}" />
          </div>
          <div class="err">{esc(errors.get("angkatan", ""))}</div>
        </div>

        <button class="btn btn-primary btn-block" type="submit" style="margin-top:8px">
          Masuk Sekarang {icon("arrow")}
        </button>
        <p class="secure-note">{icon("lock")} Data tersimpan di server FindRoom (Python)</p>
      </form>
    </section>"""
    return halaman(isi, toast=toast)


# ================= DENAH =================
def home_view(c):
    user = c.user
    all_rooms = [r[0] for daftar in BUILDINGS.values() for r in daftar]
    counts = {FREE: 0, PARTIAL: 0, BOOKED: 0, MINE: 0, PAST: 0}
    for r in all_rooms:
        for i in range(len(SLOTS)):
            counts[c.data.status(r, i)[0]] += 1

    hari_ini = c.sekarang.date()
    dates = ""
    for i in range(JUMLAH_HARI):
        d = hari_ini + timedelta(days=i)
        iso = d.isoformat()
        aktif = iso == c.tanggal
        dates += f"""<a class="date-chip {"active" if aktif else ""}"{' id="chip-aktif"' if aktif else ""} href="{esc(c.url("chip-aktif", date=iso))}">
        <small>{"Hari ini" if i == 0 else DAY_SHORT[hari_js(d)]}</small><b>{d.day}</b><small>{MONTHS[d.month - 1]}</small>
      </a>"""

    buildings = ""
    for b in BUILDINGS:
        buildings += f"""
    <a class="pill-btn {"active" if b == c.gedung else ""}" href="{esc(c.url("denah", building=b))}">
      {icon("monitor" if b == "Gedung SS" else "building")}{b}
    </a>"""

    cell_icon = {PARTIAL: "hourglass", BOOKED: "check", MINE: "check", PAST: "minus"}
    grid = "<div></div>" + "".join(f'<div class="col-head"><b>{s}</b><small>{e}</small></div>' for s, e in SLOTS)
    for room, note in BUILDINGS[c.gedung]:
        grid += f'<div class="room-name"><b>{room}</b>{f"<small>{note}</small>" if note and room[:1].isdigit() else ""}</div>'
        for si in range(len(SLOTS)):
            st, _ = c.data.status(room, si)
            grid += (
                f'<a class="cell {st}" href="{esc(c.url("denah", modal="sel", room=room, slot=si))}" '
                f'aria-label="{esc(room)} {SLOTS[si][0]}">{icon(cell_icon[st]) if st in cell_icon else ""}</a>'
            )

    first_name = user["name"].split(" ")[0]
    d_pilih = date.fromisoformat(c.tanggal)
    return f"""
    <div class="hero-card">
      <div class="hero-top">
        <div>
          <small>Halo, {esc(first_name)} 👋</small>
          <h1>Cari kelas kosong?</h1>
          <div class="date">{format_date(d_pilih)}</div>
          <span class="sync on">● Terhubung ke server Python</span>
        </div>
        <img src="/logo.svg" alt="" />
      </div>
      <div class="stats">
        <div class="stat"><b>{counts[FREE]}</b><span>Slot kosong</span></div>
        <div class="stat"><b>{counts[BOOKED] + counts[PARTIAL] + counts[MINE]}</b><span>Terpakai</span></div>
        <div class="stat"><b>{counts[MINE]}</b><span>Punyaku</span></div>
      </div>
    </div>

    <div class="section-title">{icon("calendar")} Pilih Tanggal</div>
    <div class="h-scroll">{dates}</div>

    <div class="section-title">{icon("building")} Pilih Gedung</div>
    <div class="h-scroll">{buildings}</div>

    <div class="legend">
      <span><i class="free"></i>Kosong</span><span><i class="partial"></i>Sebagian</span>
      <span><i class="booked"></i>Terpakai</span><span><i class="mine"></i>Punyaku</span><span><i class="past"></i>Lewat</span>
    </div>

    <div class="card" id="denah">
      <div class="grid-head">
        <div><h3>Denah {c.gedung}</h3><small>{short_date(d_pilih)}</small></div>
        <span class="badge">Ketuk kotak hijau</span>
      </div>
      <div class="board"></div>
      <div class="grid-scroll"><div class="room-grid">{grid}</div></div>
    </div>"""


# ---------- Jendela (modal) ----------
def info_row(ic, label, value):
    return f'<div class="info-row"><span class="ic">{icon(ic)}</span><div><small>{label}</small><b>{esc(value)}</b></div></div>'


def modal_form_booking(c, room, start, end, nilai=None, errors=None, pesan=""):
    """Form booking (jam diisi sendiri + nomor HP)."""
    nilai, errors = nilai or {}, errors or {}
    user = c.user
    d_pilih = date.fromisoformat(c.tanggal)
    purposes = "".join(
        f'<option{" selected" if p == nilai.get("purpose") else ""}>{esc(p)}</option>' for p in KEPERLUAN
    )

    def cls(key):
        return " invalid" if errors.get(key) else ""

    return f"""
    <h3>Booking Ruang</h3>
    <p class="muted">{format_date(d_pilih)}</p>
    <div class="room-chip">{icon("door")} {room_title(room)} <span>{c.gedung}</span></div>

    <form id="bookForm" method="post" action="/booking" novalidate>
      {c.hidden(room=room)}
      <div class="form-error" id="formError"{"" if pesan else " hidden"}>{esc(pesan)}</div>
      <div class="time-row">
        <div class="field"><label for="start">Jam mulai</label>
          <div class="control"><span class="icon">{icon("clock")}</span>
            <input type="time" id="start" name="start" value="{esc(start)}" min="{JAM_BUKA}" max="{JAM_TUTUP}" step="300" /></div></div>
        <div class="field"><label for="end">Jam selesai</label>
          <div class="control"><span class="icon">{icon("clock")}</span>
            <input type="time" id="end" name="end" value="{esc(end)}" min="{JAM_BUKA}" max="{JAM_TUTUP}" step="300" /></div></div>
      </div>
      <div class="field{cls("course")}" data-field="course"><label for="course">Mata kuliah / kegiatan</label>
        <div class="control"><span class="icon">{icon("book")}</span>
          <input id="course" name="course" placeholder="Masukkan Mata Kuliah / Kegiatan" value="{esc(nilai.get("course", ""))}" /></div><div class="err">{esc(errors.get("course", ""))}</div></div>
      <div class="field"><label for="purpose">Keperluan</label>
        <div class="control"><span class="icon">{icon("tag")}</span>
          <select id="purpose" name="purpose">{purposes}</select>
          <span class="chev">{icon("chevron")}</span></div></div>
      <div class="field{cls("phone")}" data-field="phone"><label for="phone">Nomor HP / WhatsApp</label>
        <div class="control"><span class="icon">{icon("phone")}</span>
          <input id="phone" name="phone" type="tel" inputmode="tel" placeholder="Masukkan Nomor HP / WhatsApp" value="{esc(nilai.get("phone", user.get("phone") or ""))}" /></div>
        <div class="err">{esc(errors.get("phone", ""))}</div><div class="hint">Agar kamu bisa dihubungi teman atau dosen.</div></div>

      <div class="modal-actions">
        <a class="btn btn-ghost" href="{esc(c.url("denah"))}">Batal</a>
        <button type="submit" class="btn btn-primary">{icon("check")} Booking Sekarang</button>
      </div>
    </form>"""


def modal_sukses(c, room, start, end):
    d_pilih = date.fromisoformat(c.tanggal)
    return f"""
    <div style="text-align:center;padding:8px 0">
      <div style="width:78px;height:78px;border-radius:50%;margin:0 auto 14px;display:grid;place-items:center;
        background:linear-gradient(135deg,#22c55e,#16a34a);color:#fff;box-shadow:0 16px 30px -10px rgba(22,163,74,.6)">
        <span style="width:40px;height:40px;display:block">{icon("check")}</span></div>
      <h3>Booking Berhasil!</h3>
      <p class="muted" style="margin-top:6px">{room_title(room)} pukul {esc(start)} - {esc(end)} pada {short_date(d_pilih)}
        sudah ditandai terpakai. Teman-teman lain akan melihat kelas ini tercentang.</p>
    </div>
    <div class="modal-actions">
      <a class="btn btn-ghost" href="{esc(c.url("denah"))}">Tutup</a>
      <a class="btn btn-primary" id="seeMine" href="{esc(c.url(tab=1))}">Lihat Booking Saya</a>
    </div>"""


def modal_detail(c, room, si, status, infos):
    badge = {
        PAST: ("Sudah lewat", "var(--muted)", "#f1f5f9"),
        MINE: ("Ada booking kamu", "var(--primary)", "#eff6ff"),
        PARTIAL: ("Sebagian", "#d97706", "#fef3c7"),
        BOOKED: ("Terpakai", "var(--booked)", "#ffe4e6"),
    }[status]

    entries = ""
    for info in infos:
        mine = c.data.is_mine(info)
        actions = ""
        if info.get("phone") and not mine:
            actions += (
                f'<a class="btn btn-outline btn-sm" href="tel:{esc(info["phone"])}">{icon("phone")} Telepon</a>\n'
                f'                  <a class="btn btn-wa btn-sm" href="{esc(wa_url(info["phone"]))}" target="_blank" rel="noopener">{icon("chat")} WhatsApp</a>'
            )
        if mine and end_datetime(info["date"], info["end"]) > c.sekarang:
            actions += (
                f'<a class="btn btn-danger-outline btn-sm" href="{esc(c.url("denah", modal="batal", id=info["id"], room=room, slot=si))}">'
                f'{icon("trash")} Batalkan</a>'
            )
        reguler = info.get("regular")
        oleh = info["by_name"] if reguler else f'{info["by_name"]} ({info["by_nim"]})'
        entries += f"""<div class="occupant">
        {info_row("clock", "Jam", time_label(info))}
        {info_row("book", "Mata kuliah / kegiatan", info["course"])}
        {info_row("tag", "Keperluan", info["purpose"])}
        {info_row("person", "Dosen" if reguler else "Dipesan oleh", oleh)}
        {info_row("school", "Kelas", f'{info["kelas"]} • Angkatan {info["angkatan"]}') if info.get("kelas") else ""}
        {info_row("phone", "Nomor HP", info["phone"]) if info.get("phone") else ""}
        {f'<div class="actions">{actions}</div>' if actions else ""}
      </div>"""

    gap = None if status == PAST else c.data.free_gap(room, si)
    note = ROOM_NOTE.get(room)
    d_pilih = date.fromisoformat(c.tanggal)
    tombol_gap = (
        f'<a class="btn btn-primary" id="bookGap" href="{esc(c.url("denah", modal="form", room=room, start=gap[0], end=gap[1]))}">'
        f'{icon("plus")} Booking jam lain</a>'
        if gap else ""
    )
    return f"""
    <div style="display:flex;justify-content:space-between;align-items:center;gap:10px">
      <h3>{room_title(room)}</h3>
      <span class="status-badge" style="color:{badge[1]};background:{badge[2]}">{badge[0]}</span>
    </div>
    {info_row("door", "Ruang", f'{c.gedung}{" • " + note if note else ""}')}
    {info_row("calendar", "Tanggal", format_date(d_pilih))}
    <p style="font-weight:700;font-size:13px;margin-top:16px">Jadwal di jam {SLOTS[si][0]} - {SLOTS[si][1]}</p>
    {entries}
    <div class="modal-actions">
      <a class="btn btn-ghost" href="{esc(c.url("denah"))}">Tutup</a>
      {tombol_gap}
    </div>"""


def modal_batal(c, b, balik_frag="denah"):
    d = date.fromisoformat(b["date"])
    return f"""
    <h3>Batalkan booking?</h3>
    <p class="muted" style="margin-top:6px">{room_title(b["room"])} • {time_label(b)}<br/>{format_date(d)}</p>
    <form method="post" action="/batal" class="modal-actions">
      {c.hidden(id=b["id"])}
      <a class="btn btn-ghost" href="{esc(c.url(balik_frag))}">Tidak</a>
      <button class="btn btn-primary" id="doCancel" type="submit" style="background:var(--danger);box-shadow:none">Ya, batalkan</button>
    </form>"""


# ================= BOOKING SAYA =================
def bookings_view(c):
    list_ = sorted(
        [b for b in database.semua_booking() if b["by_nim"] == c.user["nim"]],
        key=lambda b: b["date"] + b["start"] + b["room"],
    )
    upcoming = [b for b in list_ if end_datetime(b["date"], b["end"]) > c.sekarang]
    history = [b for b in list_ if b not in upcoming][::-1]

    def ticket(b, active):
        d = date.fromisoformat(b["date"])
        tombol = (
            f'<a class="del" href="{esc(c.url(modal="batal", id=b["id"]))}" aria-label="Batalkan">{icon("trash")}</a>'
            if active else ""
        )
        return f"""<div class="ticket {"" if active else "done"}">
        <div class="stub"><small>{DAY_SHORT[hari_js(d)]}</small><b>{d.day}</b><small>{MONTHS[d.month - 1]}</small></div>
        <div class="body">
          <h4>{room_title(b["room"])} <span class="tag">{"Aktif" if active else "Selesai"}</span></h4>
          <p>🕒 {time_label(b)}</p>
          <p class="course">{esc(b["course"])}</p>
          <p class="purpose">{esc(b["purpose"])}</p>
        </div>
        {tombol}
      </div>"""

    if not list_:
        body = f"""<div class="card empty">
        <div class="circle">{icon("calendar")}</div>
        <h3>Belum ada booking</h3>
        <p>Buka tab Denah, ketuk kotak hijau, atur jam, lalu tekan Booking.</p>
        <a class="btn btn-primary" id="goDenah" href="{esc(c.url(tab=0))}">Cari Kelas Kosong</a>
      </div>"""
    else:
        body = ""
        if upcoming:
            body += f'<div class="section-title">{icon("upcoming")} Akan Datang ({len(upcoming)})</div>' + "".join(ticket(b, True) for b in upcoming)
        if history:
            body += f'<div class="section-title">{icon("history")} Riwayat ({len(history)})</div>' + "".join(ticket(b, False) for b in history)
    return f'<h1 class="page-title">Booking Saya</h1><p class="page-sub">Tiket ruang kelas yang sudah kamu pesan.</p>{body}'


# ================= PROFIL =================
def profile_view(c):
    u = c.user
    list_ = [b for b in database.semua_booking() if b["by_nim"] == u["nim"]]
    active = len([b for b in list_ if end_datetime(b["date"], b["end"]) > c.sekarang])
    initials = "".join(p[0] for p in u["name"].split()[:2]).upper()
    steps = [
        ("Pilih tanggal & gedung", "Lihat denah ruang seperti memilih kursi bioskop."),
        ("Cek warna kotak", "Hijau = kosong, kuning = sebagian terpakai, merah = sudah dipakai."),
        ("Ketuk & booking", "Atur jam mulai & selesai sendiri, isi mata kuliah dan nomor HP, lalu konfirmasi."),
    ]
    langkah = "".join(
        f'<div class="step"><span class="num">{i + 1}</span><div><b>{t}</b><p>{d}</p></div></div>'
        for i, (t, d) in enumerate(steps)
    )
    return f"""
    <div class="profile-card">
      <div class="avatar">{esc(initials)}</div>
      <div>
        <h2>{esc(u["name"])}</h2>
        <p>NIM {esc(u["nim"])}</p>
        {f'<p>HP {esc(u["phone"])}</p>' if u.get("phone") else ""}
        <span class="chip-light">🎓 Kelas {esc(u["kelas"])} • Angkatan {esc(u["angkatan"])}</span>
      </div>
    </div>
    <div class="two-col">
      <div class="card">{icon("ticket")}<b>{len(list_)}</b><span>Total booking</span></div>
      <div class="card">{icon("bookmark")}<b>{active}</b><span>Booking aktif</span></div>
    </div>
    <div class="card steps">
      <h3>Cara Pakai</h3>
      {langkah}
    </div>
    <form method="post" action="/keluar">
      <button class="btn btn-danger-outline btn-block" id="logout" type="submit" style="margin-top:16px">{icon("logout")} Keluar</button>
    </form>
    <p class="footer-note">FindRoom v1.0 • Python (Flask)</p>"""


# ================= KERANGKA UTAMA =================
def halaman_utama(c, modal=None, toast=None, segarkan_url=None, tanpa_animasi=False):
    """
    Membuat satu halaman penuh (isi tab + menu bawah + jendela jika ada).
    `modal` berupa kamus, contoh: {"jenis": "sel", "room": "202", "slot": 2}.
    """
    modal_html, tutup = "", c.url("denah")

    if modal:
        jenis = modal["jenis"]
        if jenis == "sel":                      # ketukan pada kotak denah
            room, si = modal["room"], modal["slot"]
            st, infos = c.data.status(room, si)
            if st == FREE:
                modal_html = modal_form_booking(c, room, *c.data.default_times(si))
            elif st == PAST and not infos:
                toast = ("Jam ini sudah lewat, pilih jam lain ya.", "var(--muted)")
            else:
                modal_html = modal_detail(c, room, si, st, infos)
        elif jenis == "form":                   # form booking (jam sudah ditentukan / ada pesan salah)
            modal_html = modal_form_booking(
                c, modal["room"], modal["start"], modal["end"],
                modal.get("nilai"), modal.get("errors"), modal.get("pesan", ""),
            )
        elif jenis == "sukses":
            modal_html = modal_sukses(c, modal["room"], modal["start"], modal["end"])
        elif jenis == "batal":
            b = next((x for x in c.data.booking + database.semua_booking() if x["id"] == modal["id"]), None)
            if b:
                modal_html = modal_batal(c, b, "denah" if c.tab == 0 else "")
                if c.tab != 0:
                    tutup = c.url()

    views = [home_view, bookings_view, profile_view]
    menu = [("grid", "Denah"), ("ticket", "Booking Saya"), ("person", "Profil")]
    nav = "".join(
        f"""
          <a class="{"active" if i == c.tab else ""}" href="{esc(c.url(tab=i))}">
            <span class="pill">{icon(ic)}</span>{label}
          </a>"""
        for i, (ic, label) in enumerate(menu)
    )
    isi = f"""
    <main class="screen" id="screen">{views[c.tab](c)}</main>
    <nav class="bottom-nav">
      {nav}
    </nav>"""
    return halaman(
        isi, modal_html=modal_html, tutup_url=tutup, toast=toast,
        segarkan_url=None if modal_html else segarkan_url, tanpa_animasi=tanpa_animasi,
    )

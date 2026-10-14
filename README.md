# ⚔️ Kelnara Bot CoC — Smart Farming, Easy Progress

**Kelnara Bot CoC** adalah aplikasi pendamping (*Game Assistant & Farming Manager*) Clash of Clans (CoC) terlengkap yang dirancang untuk platform **Android (Cloud Phone & Smartphone Fisik)** dan **PC (Windows)**.

---

## 🌟 Fitur Utama Kelnara Bot CoC

### 1. 🏰 Dashboard Monitoring Terpadu
- **Status Desa**: Menampilkan level TH13, profil akun, liga, dan status pelindung (*Shield*).
- **Builder & Lab Tracker**: Memantau waktu penyelesaian 5/5 Builder dan Laboratorium secara *real-time*.
- **Ringkasan Sumber Daya**: Membandingkan tabungan Gold, Elixir, dan Dark Elixir terhadap target farming yang ditetapkan.

### 2. 🎯 Farming Assistant & Auto Scouting
- **Target Farming**: Tetapkan target pencapaian Gold, Elixir, dan Dark Elixir.
- **Auto Next Threshold**: Bot otomatis menekan *Next* jika base musuh memiliki sumber daya di bawah batas yang Anda atur (misal: min 350.000 Gold / Elixir).
- **Auto Zoom-Out Layar 2x**: Gestur zoom-out otomatis sebelum menyebar pasukan agar seluruh perimeter dan kolektor luar musuh terlihat jelas.
- **Smart Collector Harvest**: Mengumpulkan hasil tambang emas dan elixir di desa secara berkala.

### 3. 👥 Troop Presets Manager
- **Barch Perimeter Striker**: 120 Barbarian & 140 Archer untuk menjarah desa mati (*dead base*) secara hemat dan efisien.
- **Sneaky Goblin Storage Snatcher**: Pasukan perampok kilat untuk menguras Dark Elixir dan Town Hall musuh.
- **Kalkulator Pasukan**: Menghitung kapasitas *housing space*, biaya elixir, dan waktu masak pasukan.

### 4. 🧱 Upgrade Manager & Wall Progress
- **Kalkulator Tembok TH13**: Pantau progres upgrade dinding level 13 ke level 14 beserta kalkulasi sisa gold/elixir yang dibutuhkan.
- **Pengingat Bangunan Selesai**: Notifikasi dan reminder saat upgrade bangunan pertahanan selesai.

### 5. ⚔️ Battle Tracker & Session Manager
- **Live Session Stopwatch**: Stopwatch durasi bermain dan pengingat waktu istirahat (*anti-burnout*).
- **Riwayat Serangan & Grafik**: Grafik visual hasil jarahan pertempuran dan rata-rata perolehan per jam.

---

## 📱 Panduan Menjalankan di Android & Cloud Phone (Redfinger / HP Fisik)

### Cara 1: Buka Kelnara Web App / PWA (Rekomendasi untuk Monitoring)
1. Buka folder `kelnara_app/index.html` di browser Chrome pada Cloud Phone atau Smartphone Anda.
2. Klik ikon titik tiga di Chrome dan pilih **"Tambahkan ke Layar Utama" (Add to Home Screen)**.
3. Aplikasi **Kelnara Bot CoC** akan terpasang di HP Anda layaknya aplikasi native mandiri!

### Cara 2: Menjalankan Floating Overlay Bot di AutoX.js
1. Buka aplikasi **AutoX.js** di Cloud Phone / Android.
2. Di halaman **Daftar File (管理)**, cari file `kelnara_bot.js` (atau `coc_bot.js`).
3. **PENTING**: Klik icon tombol **Play (▶)** di **sebelah kanan nama file** tersebut.  
   *(Jangan menekan tombol run di dalam editor teks Monaco agar tidak muncul notifikasi "暂不支持!").*
4. Izinkan *Floating Window* dan *Accessibility Service*.
5. Widget melayang **Kelnara Bot** akan muncul di atas game CoC, siap untuk start/stop farming dengan satu sentuhan!

---

## 🖥️ Panduan Menjalankan di PC (Windows + BlueStacks 5)

1. Pastikan Python 3.10+ terpasang di PC.
2. Jalankan aplikasi melalui shortcut desktop **CoC Bot Pro** atau double-click `run_app.bat`.
3. Atau via terminal:
   ```bash
   python app_gui.py
   ```

---

## 📦 Struktur Direktori Proyek

```
coc_farming_bot/
├── kelnara_app/            # Aplikasi Frontend Kelnara Bot CoC (HTML5 / PWA / JS)
│   ├── index.html          # Dashboard 5 Modul & Navigasi Mobile/PC
│   ├── app.js              # State Engine, LocalStorage, Chart.js & Session Timer
│   ├── manifest.json       # PWA Manifest (Add to Home Screen)
│   └── sw.js               # Service Worker Offline Caching
├── android/                # Modul Otomatisasi Android & Cloud Phone
│   ├── kelnara_bot.js      # Floating Overlay Script dengan Auto Zoom-Out & Perimeter Attack
│   └── coc_bot.js          # Skrip AutoX.js Standar
├── core/                   # Engine Otomatisasi Python untuk PC (ADB Bridge, Vision, Humanizer)
├── strategies/             # Algoritma Penyerangan (Barch Perimeter, dll)
├── app_gui.py              # Desktop GUI Dashboard (CustomTkinter)
└── run_app.bat             # 1-Click Runner untuk Windows
```

---

*Kelnara Bot CoC — Smart Farming, Easy Progress.*

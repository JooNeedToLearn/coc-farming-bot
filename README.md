# ⚔️ Clash of Clans Auto Farming Bot (Pro Edition)

Bot otomatisasi mandiri untuk game Clash of Clans (CoC) yang beroperasi di PC (BlueStacks 5) maupun Cloud Phone (Termux) menggunakan Computer Vision (OpenCV) dan simulasi input ADB non-intrusif.

---

## 🌟 Fitur Utama

- 🏰 **Farming Desa Utama (Home Village)**: Pencarian base otomatis (*Next* matchmaking loop) berdasarkan batas minimal Gold, Elixir, dan Dark Elixir.
- 🌙 **Farming Desa Malam (Builder Base)**: Otomatis menyeberang ke Desa Malam, menyerang lawan untuk bonus bintang harian, dan memanen *Gem Mine*.
- 🧱 **Auto Claim Collector & Auto Upgrade Wall**: Panen tambang otomatis setiap siklus dan belanja kelebihan loot ke tembok desa.
- 🎯 **Smart Auto-End Battle**: Otomatis menyerah saat seluruh kolektor luar musuh sudah habis terjarah.
- 🛡️ **Humanized Anti-Ban**: Menggunakan distribusi Gaussian jitter pada titik klik dan variasi delay acak untuk menyamarkan perilaku bot.
- 🖥️ **Desktop Dashboard GUI**: Antarmuka visual modern (*CustomTkinter*) dengan tombol Mulai/Jeda/Berhenti dan Live Console Log.

---

## 🚀 Panduan Menjalankan di PC (Windows + BlueStacks 5)

### 1. Prasyarat
- Python 3.10+ terpasang di sistem.
- BlueStacks 5 dengan resolusi layar **1280x720 (DPI 240)**.
- Fitur ADB diaktifkan di BlueStacks (**Settings → Advanced → Android Debug Bridge: ON**).

### 2. Instalasi Dependensi
```bash
pip install -r requirements.txt
```

### 3. Menjalankan Aplikasi
- **Cara Termudah (GUI)**: Cukup klik dua kali file `run_app.bat` atau shortcut `CoC Bot Pro` di Desktop.
- **Lewat Command Line (CLI)**:
  ```bash
  python app_gui.py
  # atau tanpa GUI:
  python main.py --run
  ```

---

## 📱 Panduan Menjalankan di Cloud Phone (Redfinger / LDCloud via Termux)

Bot ini dapat dijalankan langsung 24 jam nonstop di dalam Cloud Phone tanpa perlu menyalakan PC:

1. Buka Cloud Phone Anda dan pastikan fitur **Root** sudah aktif di pengaturan Cloud Phone.
2. Install aplikasi **Termux** di Cloud Phone.
3. Di dalam Termux, pasang dependensi:
   ```bash
   pkg update -y
   pkg install -y python opencv git
   ```
4. Clone repository ini:
   ```bash
   git clone https://github.com/JooNeedToLearn/coc-farming-bot.git
   cd coc-farming-bot
   pip install -r requirements.txt
   ```
5. Jalankan bot:
   ```bash
   python main.py --run
   ```

---

## ⚙️ Konfigurasi (`config/settings.yaml`)

Anda dapat menyesuaikan parameter bot secara langsung di dashboard GUI atau mengedit file `config/settings.yaml`:

```yaml
farming:
  min_gold: 250000
  min_elixir: 250000
  min_dark_elixir: 0
  max_search_count: 30
  max_attacks: 20
  enable_home_farming: true
  enable_builder_farming: false
  enable_auto_claim: true
  enable_auto_wall: false

humanizer:
  enable_jitter: true
  coordinate_variance: 5
  min_delay: 0.8
  max_delay: 1.6
```

---

## ⚠️ Disclaimer
Penggunaan bot atau perangkat lunak pihak ketiga melanggar Ketentuan Layanan (ToS) Supercell. Proyek ini dibuat untuk tujuan edukasi dan eksperimen otomasi. Gunakan dengan bijak, dan disarankan menggunakan akun sekunder.

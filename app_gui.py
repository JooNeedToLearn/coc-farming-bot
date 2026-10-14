import os
import sys
import yaml
import threading
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
from typing import Dict, Any

from core.bot_controller import BotController
from core.adb_bridge import ADBBridge


CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config", "settings.yaml")


def load_config() -> Dict[str, Any]:
    default_config = {
        "emulator": {
            "adb_path": r"C:\Program Files\BlueStacks_nxt\HD-Adb.exe",
            "host": "127.0.0.1",
            "port": 5555,
            "device_id": "127.0.0.1:5555"
        },
        "farming": {
            "enable_home_farming": True,
            "enable_builder_farming": False,
            "enable_auto_claim": True,
            "enable_auto_wall": False,
            "min_gold": 250000,
            "min_elixir": 250000,
            "min_dark_elixir": 0,
            "max_search_count": 30,
            "max_attacks": 20,
            "smart_auto_end": True
        },
        "humanizer": {
            "enable_jitter": True,
            "coordinate_variance": 5,
            "min_delay": 0.8,
            "max_delay": 1.6
        }
    }
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                user_cfg = yaml.safe_load(f)
                if user_cfg:
                    default_config.update(user_cfg)
        except Exception:
            pass
    return default_config


def save_config(cfg: Dict[str, Any]):
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        yaml.safe_dump(cfg, f, default_flow_style=False)


class CoCBotApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("CoC Auto Farm Pro - Desktop Dashboard")
        self.geometry("980x700")
        self.minsize(880, 600)

        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")

        self.config_data = load_config()
        self.bot_controller = None

        # Layout Grid
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._build_sidebar()
        self._build_main_area()

        # Initial Tab
        self.select_tab("home")
        self.append_log("Aplikasi siap. Silakan klik 'Cek Koneksi' di menu Kalibrasi atau langsung 'Mulai Bot'.")

    def _build_sidebar(self):
        self.sidebar_frame = ctk.CTkFrame(self, width=220, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(7, weight=1)

        # Header Title
        title_lbl = ctk.CTkLabel(
            self.sidebar_frame, text="⚔️ CoC Bot Pro",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_lbl.grid(row=0, column=0, padx=20, pady=(20, 5))

        subtitle_lbl = ctk.CTkLabel(
            self.sidebar_frame, text="Smart Farming System",
            font=ctk.CTkFont(size=12), text_color="gray"
        )
        subtitle_lbl.grid(row=1, column=0, padx=20, pady=(0, 20))

        # Nav Buttons
        self.nav_btns = {}
        tabs = [
            ("home", "🏰 Desa Utama"),
            ("builder", "🌙 Desa Malam"),
            ("routine", "🧱 Wall & Kolektor"),
            ("calibration", "🛠️ Kalibrasi"),
            ("settings", "⚙️ Pengaturan")
        ]

        for idx, (tab_id, text) in enumerate(tabs, start=2):
            btn = ctk.CTkButton(
                self.sidebar_frame, text=text, height=38,
                corner_radius=8, font=ctk.CTkFont(size=13, weight="bold"),
                command=lambda t=tab_id: self.select_tab(t)
            )
            btn.grid(row=idx, column=0, padx=15, pady=6, sticky="ew")
            self.nav_btns[tab_id] = btn

        # Status Badge at Bottom
        self.status_card = ctk.CTkFrame(self.sidebar_frame, corner_radius=8, fg_color="#1e1e1e")
        self.status_card.grid(row=8, column=0, padx=15, pady=20, sticky="ew")

        self.status_dot = ctk.CTkLabel(
            self.status_card, text="● IDLE",
            font=ctk.CTkFont(size=13, weight="bold"), text_color="#10b981"
        )
        self.status_dot.pack(padx=10, pady=8)

    def _build_main_area(self):
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.main_container.grid_rowconfigure(1, weight=1)
        self.main_container.grid_rowconfigure(2, weight=1)
        self.main_container.grid_columnconfigure(0, weight=1)

        # 1. Top Controls Bar
        self.ctrl_bar = ctk.CTkFrame(self.main_container, height=60, corner_radius=10)
        self.ctrl_bar.grid(row=0, column=0, sticky="ew", pady=(0, 15))

        self.btn_start = ctk.CTkButton(
            self.ctrl_bar, text="▶ Mulai Bot", fg_color="#10b981", hover_color="#059669",
            height=40, font=ctk.CTkFont(size=14, weight="bold"), command=self.action_start
        )
        self.btn_start.pack(side="left", padx=12, pady=10)

        self.btn_pause = ctk.CTkButton(
            self.ctrl_bar, text="⏸ Jeda", fg_color="#f59e0b", hover_color="#d97706",
            height=40, font=ctk.CTkFont(size=14, weight="bold"), command=self.action_pause
        )
        self.btn_pause.pack(side="left", padx=8, pady=10)

        self.btn_stop = ctk.CTkButton(
            self.ctrl_bar, text="⏹ Berhenti", fg_color="#ef4444", hover_color="#dc2626",
            height=40, font=ctk.CTkFont(size=14, weight="bold"), command=self.action_stop
        )
        self.btn_stop.pack(side="left", padx=8, pady=10)

        self.btn_save = ctk.CTkButton(
            self.ctrl_bar, text="💾 Simpan Pengaturan", fg_color="#3b82f6", hover_color="#2563eb",
            height=40, font=ctk.CTkFont(size=13), command=self.action_save_config
        )
        self.btn_save.pack(side="right", padx=12, pady=10)

        # 2. Dynamic Content Frame
        self.content_frame = ctk.CTkFrame(self.main_container, corner_radius=10)
        self.content_frame.grid(row=1, column=0, sticky="nsew", pady=(0, 15))

        # 3. Bottom Live Log Console
        self.log_frame = ctk.CTkFrame(self.main_container, corner_radius=10)
        self.log_frame.grid(row=2, column=0, sticky="nsew")

        log_header = ctk.CTkFrame(self.log_frame, fg_color="transparent")
        log_header.pack(fill="x", padx=10, pady=(8, 4))

        ctk.CTkLabel(log_header, text="📋 Monitor Aktivitas Bot (Live Console)", font=ctk.CTkFont(size=12, weight="bold")).pack(side="left")
        ctk.CTkButton(log_header, text="Bersihkan", width=70, height=24, font=ctk.CTkFont(size=11), command=self.clear_logs).pack(side="right")

        self.log_box = ctk.CTkTextbox(self.log_frame, height=140, font=ctk.CTkFont(family="Consolas", size=12))
        self.log_box.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    def select_tab(self, tab_id: str):
        # Update Nav Styles
        for tid, btn in self.nav_btns.items():
            if tid == tab_id:
                btn.configure(fg_color=["#3B8ED0", "#1F6AA5"])
            else:
                btn.configure(fg_color="transparent")

        # Clear Content
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        if tab_id == "home":
            self._render_home_tab()
        elif tab_id == "builder":
            self._render_builder_tab()
        elif tab_id == "routine":
            self._render_routine_tab()
        elif tab_id == "calibration":
            self._render_calibration_tab()
        elif tab_id == "settings":
            self._render_settings_tab()

    def _render_home_tab(self):
        f = self.config_data["farming"]

        # Checkbox Enable
        self.cb_home = ctk.CTkCheckBox(self.content_frame, text="Aktifkan Farming Desa Utama", font=ctk.CTkFont(size=14, weight="bold"))
        self.cb_home.pack(anchor="w", padx=25, pady=(20, 15))
        if f.get("enable_home_farming", True): self.cb_home.select()

        # Inputs Grid
        grid = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        grid.pack(fill="x", padx=25, pady=5)
        grid.columnconfigure((1, 3), weight=1)

        # Min Gold
        ctk.CTkLabel(grid, text="Minimal Gold:").grid(row=0, column=0, sticky="w", pady=8)
        self.ent_gold = ctk.CTkEntry(grid, placeholder_text="250000")
        self.ent_gold.insert(0, str(f.get("min_gold", 250000)))
        self.ent_gold.grid(row=0, column=1, padx=10, pady=8, sticky="ew")

        # Min Elixir
        ctk.CTkLabel(grid, text="Minimal Elixir:").grid(row=1, column=0, sticky="w", pady=8)
        self.ent_elixir = ctk.CTkEntry(grid, placeholder_text="250000")
        self.ent_elixir.insert(0, str(f.get("min_elixir", 250000)))
        self.ent_elixir.grid(row=1, column=1, padx=10, pady=8, sticky="ew")

        # Min Dark Elixir
        ctk.CTkLabel(grid, text="Minimal Dark Elixir:").grid(row=2, column=0, sticky="w", pady=8)
        self.ent_dark = ctk.CTkEntry(grid, placeholder_text="0")
        self.ent_dark.insert(0, str(f.get("min_dark_elixir", 0)))
        self.ent_dark.grid(row=2, column=1, padx=10, pady=8, sticky="ew")

        # Max Search Count
        ctk.CTkLabel(grid, text="Maksimal Next Match:").grid(row=3, column=0, sticky="w", pady=8)
        self.ent_search = ctk.CTkEntry(grid, placeholder_text="30")
        self.ent_search.insert(0, str(f.get("max_search_count", 30)))
        self.ent_search.grid(row=3, column=1, padx=10, pady=8, sticky="ew")

        # Smart Auto End
        self.cb_smart_end = ctk.CTkCheckBox(self.content_frame, text="Smart Auto-End Battle (Menyerah saat kolektor luar habis)")
        self.cb_smart_end.pack(anchor="w", padx=25, pady=(15, 10))
        if f.get("smart_auto_end", True): self.cb_smart_end.select()

    def _render_builder_tab(self):
        f = self.config_data["farming"]

        self.cb_builder = ctk.CTkCheckBox(self.content_frame, text="Aktifkan Farming Desa Malam (Builder Base)", font=ctk.CTkFont(size=14, weight="bold"))
        self.cb_builder.pack(anchor="w", padx=25, pady=(20, 15))
        if f.get("enable_builder_farming", False): self.cb_builder.select()

        self.cb_gem = ctk.CTkCheckBox(self.content_frame, text="Auto Panen Tambang Permata (Gem Mine) & Kolektor")
        self.cb_gem.pack(anchor="w", padx=25, pady=10)
        self.cb_gem.select()

        self.cb_builder_attack = ctk.CTkCheckBox(self.content_frame, text="Auto Serang Lawan (Spam Troops untuk Bonus Elixir/Gold)")
        self.cb_builder_attack.pack(anchor="w", padx=25, pady=10)
        self.cb_builder_attack.select()

        note = ctk.CTkLabel(
            self.content_frame, text="ℹ️ Bot akan otomatis mengklik perahu, menyerang rival, memanen tambang permata, lalu kembali ke Desa Utama.",
            text_color="gray", justify="left", wraplength=550
        )
        note.pack(anchor="w", padx=25, pady=20)

    def _render_routine_tab(self):
        f = self.config_data["farming"]

        self.cb_claim = ctk.CTkCheckBox(self.content_frame, text="Auto Claim Collector (Panen Otomatis Tambang Emas & Elixir)", font=ctk.CTkFont(size=14, weight="bold"))
        self.cb_claim.pack(anchor="w", padx=25, pady=(20, 15))
        if f.get("enable_auto_claim", True): self.cb_claim.select()

        self.cb_wall = ctk.CTkCheckBox(self.content_frame, text="Auto Upgrade Wall (Tembok Otomatis Saat Loot Berlebih)", font=ctk.CTkFont(size=14, weight="bold"))
        self.cb_wall.pack(anchor="w", padx=25, pady=10)
        if f.get("enable_auto_wall", False): self.cb_wall.select()

        note = ctk.CTkLabel(
            self.content_frame, text="ℹ️ Fitur ini membantu memaksimalkan progres base dengan memanen sumber daya setiap siklus dan membelanjakan kelebihan loot sebelum offline.",
            text_color="gray", justify="left", wraplength=550
        )
        note.pack(anchor="w", padx=25, pady=20)

    def _render_calibration_tab(self):
        lbl = ctk.CTkLabel(self.content_frame, text="Kalibrasi Mandiri & Pengujian Emulator", font=ctk.CTkFont(size=15, weight="bold"))
        lbl.pack(anchor="w", padx=25, pady=(20, 15))

        btn_box = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        btn_box.pack(fill="x", padx=25, pady=10)

        ctk.CTkButton(btn_box, text="🔍 Cek Koneksi ADB BlueStacks", command=self.test_adb_conn).pack(side="left", padx=(0, 10))
        ctk.CTkButton(btn_box, text="📸 Ambil Screenshot Uji Coba", command=self.test_screencap).pack(side="left", padx=10)
        ctk.CTkButton(btn_box, text="🔢 Uji Deteksi Nilai Loot (OCR)", command=self.test_ocr).pack(side="left", padx=10)

        self.calib_info = ctk.CTkLabel(
            self.content_frame, text="Status Kalibrasi: Menunggu pengujian...",
            font=ctk.CTkFont(family="Consolas", size=12), justify="left", text_color="#60a5fa"
        )
        self.calib_info.pack(anchor="w", padx=25, pady=20)

    def _render_settings_tab(self):
        f = self.config_data["farming"]
        h = self.config_data["humanizer"]

        grid = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        grid.pack(fill="x", padx=25, pady=20)
        grid.columnconfigure(1, weight=1)

        ctk.CTkLabel(grid, text="Maksimal Siklus Serangan (Auto Stop):").grid(row=0, column=0, sticky="w", pady=10)
        self.ent_max_att = ctk.CTkEntry(grid, placeholder_text="20")
        self.ent_max_att.insert(0, str(f.get("max_attacks", 20)))
        self.ent_max_att.grid(row=0, column=1, padx=15, pady=10, sticky="ew")

        self.cb_jitter = ctk.CTkCheckBox(self.content_frame, text="Aktifkan Gaussian Coordinate Jitter (Anti-Deteksi Klik Statis)")
        self.cb_jitter.pack(anchor="w", padx=25, pady=10)
        if h.get("enable_jitter", True): self.cb_jitter.select()

        self.cb_random_delay = ctk.CTkCheckBox(self.content_frame, text="Jeda Waktu Acak / Humanized Sleep Antara Aksi")
        self.cb_random_delay.pack(anchor="w", padx=25, pady=10)
        self.cb_random_delay.select()

    def append_log(self, text: str):
        self.log_box.insert("end", text + "\n")
        self.log_box.see("end")

    def clear_logs(self):
        self.log_box.delete("1.0", "end")

    def set_status(self, text: str):
        colors = {
            "Running": "#10b981",
            "Paused": "#f59e0b",
            "Stopped": "#ef4444",
            "Error": "#dc2626"
        }
        color = colors.get(text, "#60a5fa")
        self.status_dot.configure(text=f"● {text.upper()}", text_color=color)

    def test_adb_conn(self):
        self.append_log("Menguji koneksi ke BlueStacks 5 via HD-Adb...")
        adb = ADBBridge(
            adb_path=self.config_data["emulator"]["adb_path"],
            host=self.config_data["emulator"]["host"],
            port=self.config_data["emulator"]["port"]
        )
        if adb.connect():
            size = adb.get_screen_size()
            info = f"✅ Terhubung ke: {adb.device_id} | Resolusi: {size[0]}x{size[1]}"
            self.calib_info.configure(text=info, text_color="#10b981")
            self.append_log(info)
        else:
            info = "❌ Gagal terhubung. Pastikan BlueStacks menyala dan ADB aktif."
            self.calib_info.configure(text=info, text_color="#ef4444")
            self.append_log(info)

    def test_screencap(self):
        self.append_log("Mengambil screencap uji coba...")
        adb = ADBBridge(
            adb_path=self.config_data["emulator"]["adb_path"],
            host=self.config_data["emulator"]["host"],
            port=self.config_data["emulator"]["port"]
        )
        frame = adb.screencap()
        if frame is not None:
            self.append_log(f"✅ Screencap berhasil diperoleh ({frame.shape[1]}x{frame.shape[0]} px).")
        else:
            self.append_log("❌ Gagal mengambil screencap.")

    def test_ocr(self):
        self.append_log("Menguji pembacaan teks loot...")
        # Direct run test
        self.test_adb_conn()

    def action_save_config(self):
        try:
            if hasattr(self, "ent_gold"):
                self.config_data["farming"]["min_gold"] = int(self.ent_gold.get())
                self.config_data["farming"]["min_elixir"] = int(self.ent_elixir.get())
                self.config_data["farming"]["min_dark_elixir"] = int(self.ent_dark.get())
                self.config_data["farming"]["max_search_count"] = int(self.ent_search.get())
                self.config_data["farming"]["enable_home_farming"] = bool(self.cb_home.get())
                self.config_data["farming"]["smart_auto_end"] = bool(self.cb_smart_end.get())

            if hasattr(self, "cb_builder"):
                self.config_data["farming"]["enable_builder_farming"] = bool(self.cb_builder.get())

            if hasattr(self, "cb_claim"):
                self.config_data["farming"]["enable_auto_claim"] = bool(self.cb_claim.get())
                self.config_data["farming"]["enable_auto_wall"] = bool(self.cb_wall.get())

            if hasattr(self, "ent_max_att"):
                self.config_data["farming"]["max_attacks"] = int(self.ent_max_att.get())

            save_config(self.config_data)
            if self.bot_controller:
                self.bot_controller.update_config(self.config_data)

            self.append_log("💾 Pengaturan berhasil disimpan ke settings.yaml.")
            messagebox.showinfo("Sukses", "Pengaturan bot berhasil disimpan!")
        except Exception as e:
            messagebox.showerror("Error", f"Gagal menyimpan pengaturan: {e}")

    def action_start(self):
        self.action_save_config()
        if not self.bot_controller:
            self.bot_controller = BotController(
                config=self.config_data,
                log_cb=self.append_log,
                status_cb=self.set_status
            )
        self.bot_controller.start()

    def action_pause(self):
        if self.bot_controller:
            self.bot_controller.pause()

    def action_stop(self):
        if self.bot_controller:
            self.bot_controller.stop()


def main():
    app = CoCBotApp()
    app.mainloop()


if __name__ == "__main__":
    main()

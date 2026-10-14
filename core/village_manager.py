import time
from typing import Callable, Optional
from core.adb_bridge import ADBBridge
from core.humanizer import Humanizer


class VillageManager:
    """Handles routine tasks in Home Village: claiming collectors and auto-upgrading walls."""

    def __init__(self, adb: ADBBridge, humanizer: Humanizer, log_cb: Optional[Callable[[str], None]] = None):
        self.adb = adb
        self.humanizer = humanizer
        self.log_cb = log_cb or print

    def log(self, msg: str):
        self.log_cb(f"[Desa] {msg}")

    def claim_collectors(self):
        """Scans and clicks central and outer zones of the village to harvest resource collectors."""
        self.log("Memulai panen otomatis (Auto Claim Collector)...")

        # Kolektor biasanya tersebar di sekeliling base (koordinat 1280x720)
        collector_sample_points = [
            (500, 320), (550, 360), (620, 310), (680, 350), (740, 330),
            (440, 420), (520, 460), (640, 480), (760, 450), (840, 410),
            (640, 260), (640, 540), (380, 360), (900, 360)
        ]

        for pt in collector_sample_points:
            x, y = self.humanizer.jitter(pt[0], pt[1], radius=12)
            self.adb.tap(x, y)
            time.sleep(0.12)

        self.log("Panen sumber daya selesai.")

    def upgrade_wall(self, min_storage_gold: int = 1500000):
        """Attempts to select a wall piece and upgrade it with gold or elixir."""
        self.log("Mengecek kemungkinan Auto Upgrade Wall...")

        # Titik sampel tembok tengah (center wall)
        center_wall_pt = (640, 360)
        wx, wy = self.humanizer.jitter(center_wall_pt[0], center_wall_pt[1], radius=8)
        self.adb.tap(wx, wy)
        self.humanizer.sleep_random(0.6, 1.0)

        # Tombol upgrade biasanya muncul di panel bawah (koordinat ~720, 620)
        upgrade_btn_pt = (720, 620)
        ux, uy = self.humanizer.jitter(upgrade_btn_pt[0], upgrade_btn_pt[1], radius=6)
        self.adb.tap(ux, uy)
        self.humanizer.sleep_random(0.6, 1.0)

        # Konfirmasi upgrade dengan Gold / Elixir (koordinat ~640, 520)
        confirm_btn_pt = (640, 520)
        cx, cy = self.humanizer.jitter(confirm_btn_pt[0], confirm_btn_pt[1], radius=6)
        self.adb.tap(cx, cy)
        self.humanizer.sleep_random(0.8, 1.2)

        # Klik sembarang untuk membatalkan seleksi
        self.adb.tap(200, 200)
        self.log("Prosedur cek upgrade wall selesai.")

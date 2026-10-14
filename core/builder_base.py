import time
from typing import Callable, Optional
from core.adb_bridge import ADBBridge
from core.humanizer import Humanizer


class BuilderBaseManager:
    """Manages farming and routines in the Builder Base (Desa Malam)."""

    def __init__(self, adb: ADBBridge, humanizer: Humanizer, log_cb: Optional[Callable[[str], None]] = None):
        self.adb = adb
        self.humanizer = humanizer
        self.log_cb = log_cb or print

    def log(self, msg: str):
        self.log_cb(f"[Desa Malam] {msg}")

    def switch_to_builder_base(self):
        """Clicks the boat on the coast to sail to Builder Base."""
        self.log("Berlayar menuju Desa Malam (klik perahu)...")
        # Posisi perahu di tepi pantai kiri bawah (1280x720)
        bx, by = self.humanizer.jitter(310, 520, radius=15)
        self.adb.tap(bx, by)
        self.humanizer.sleep_random(3.0, 4.5)

    def switch_to_home_village(self):
        """Clicks the boat to sail back to Home Village."""
        self.log("Kembali berlayar ke Desa Utama...")
        bx, by = self.humanizer.jitter(960, 240, radius=15)
        self.adb.tap(bx, by)
        self.humanizer.sleep_random(3.0, 4.5)

    def claim_gem_mine(self):
        """Harvests the Gem Mine and collectors in Builder Base."""
        self.log("Memanen Tambang Permata (Gem Mine) & Kolektor...")
        sample_points = [(640, 260), (520, 340), (760, 340), (640, 420)]
        for pt in sample_points:
            x, y = self.humanizer.jitter(pt[0], pt[1], radius=10)
            self.adb.tap(x, y)
            time.sleep(0.15)

    def execute_builder_attack(self):
        """Initiates Builder Base battle and drops all troops."""
        self.log("Memulai penyerangan di Desa Malam...")

        # 1. Klik tombol Attack (kiri bawah)
        ax, ay = self.humanizer.jitter(75, 630, radius=5)
        self.adb.tap(ax, ay)
        self.humanizer.sleep_random(1.5, 2.0)

        # 2. Klik tombol Find Now (kanan bawah)
        fx, fy = self.humanizer.jitter(950, 520, radius=8)
        self.adb.tap(fx, fy)
        self.humanizer.sleep_random(4.0, 5.5)

        # 3. Deploy seluruh slot pasukan (Slot 1 s/d Slot 6)
        self.log("Menyebarkan pasukan Desa Malam...")
        slots = [(150, 650), (220, 650), (290, 650), (360, 650), (430, 650)]
        drop_zones = [(300, 360), (640, 200), (980, 360), (640, 520)]

        for slot in slots:
            # Pilih slot
            sx, sy = self.humanizer.jitter(slot[0], slot[1], radius=4)
            self.adb.tap(sx, sy)
            time.sleep(0.1)

            # Drop 3-4 kali di zona luar
            for zone in drop_zones:
                dx, dy = self.humanizer.jitter(zone[0], zone[1], radius=10)
                self.adb.tap(dx, dy)
                time.sleep(0.08)

        self.log("Semua pasukan telah diturunkan. Menunggu pertempuran selesai...")
        # Pasukan desa malam menyerang otomatis, tunggu 40-50 detik
        time.sleep(45)

        # 4. Selesai dan kembali
        self.log("Kembali ke Desa Malam...")
        # Tombol Return / Okay
        rx, ry = self.humanizer.jitter(640, 600, radius=10)
        self.adb.tap(rx, ry)
        self.humanizer.sleep_random(3.0, 4.0)

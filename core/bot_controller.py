import time
import threading
from enum import Enum, auto
from typing import Dict, Any, Callable, Optional

from core.adb_bridge import ADBBridge
from core.vision_engine import VisionEngine
from core.humanizer import Humanizer
from core.village_manager import VillageManager
from core.builder_base import BuilderBaseManager
from strategies.barch_perimeter import BarchPerimeterStrategy


class BotState(Enum):
    IDLE = auto()
    VILLAGE = auto()
    SCOUTING = auto()
    ATTACKING = auto()
    END_BATTLE = auto()
    BUILDER_BASE = auto()
    COOLDOWN = auto()


class BotController:
    def __init__(self, config: Dict[str, Any], log_cb: Optional[Callable[[str], None]] = None, status_cb: Optional[Callable[[str], None]] = None):
        self.config = config
        self.log_cb = log_cb or print
        self.status_cb = status_cb or (lambda s: None)

        self.adb = ADBBridge(
            adb_path=config["emulator"].get("adb_path"),
            host=config["emulator"].get("host", "127.0.0.1"),
            port=config["emulator"].get("port", 5555)
        )
        self.humanizer = Humanizer(
            variance=config["humanizer"].get("coordinate_variance", 5),
            min_delay=config["humanizer"].get("min_delay", 0.8),
            max_delay=config["humanizer"].get("max_delay", 1.6)
        )
        self.vision = VisionEngine()
        self.strategy = BarchPerimeterStrategy(self.adb, self.humanizer)
        self.village = VillageManager(self.adb, self.humanizer, self.log_cb)
        self.builder = BuilderBaseManager(self.adb, self.humanizer, self.log_cb)

        # Threading controls
        self.stop_event = threading.Event()
        self.pause_event = threading.Event()
        self.pause_event.set()

        self.thread: Optional[threading.Thread] = None
        self.current_state = BotState.IDLE
        self.total_attacks = 0

    def log(self, msg: str):
        self.log_cb(f"[{time.strftime('%H:%M:%S')}] {msg}")

    def update_config(self, new_config: Dict[str, Any]):
        self.config = new_config

    def tap_with_jitter(self, x: int, y: int, radius: int = 5):
        jx, jy = self.humanizer.jitter(x, y, radius)
        self.adb.tap(jx, jy)

    def is_interrupted(self) -> bool:
        if self.stop_event.is_set():
            return True
        while not self.pause_event.is_set():
            if self.stop_event.is_set():
                return True
            time.sleep(0.5)
        return False

    def train_army(self):
        self.log("Membuka menu pelatihan pasukan (Train Army)...")
        self.tap_with_jitter(60, 620)
        self.humanizer.sleep_random(1.0, 1.4)
        if self.is_interrupted(): return

        self.tap_with_jitter(1000, 120)
        self.humanizer.sleep_random(0.8, 1.1)
        if self.is_interrupted(): return

        self.tap_with_jitter(1100, 280)
        self.humanizer.sleep_random(0.8, 1.1)

        self.tap_with_jitter(1180, 80)
        self.humanizer.sleep_random(0.8, 1.2)

    def find_match(self):
        self.log("Membuka menu penyerangan (Attack)...")
        self.tap_with_jitter(75, 630)
        self.humanizer.sleep_random(1.2, 1.6)
        if self.is_interrupted(): return

        self.log("Mencari lawan...")
        self.tap_with_jitter(950, 520)
        self.humanizer.sleep_random(3.2, 4.2)
        self.current_state = BotState.SCOUTING

    def scout_base(self, min_gold: int, min_elixir: int, max_searches: int, search_idx: int) -> bool:
        screen = self.adb.screencap()
        if screen is None:
            return False

        rois = self.vision.extract_loot_roi(screen)
        gold = self.vision.parse_loot_digits(rois["gold"])
        elixir = self.vision.parse_loot_digits(rois["elixir"])

        self.log(f"Base #{search_idx} -> Terbaca Gold: {gold:,} | Elixir: {elixir:,}")

        if (gold >= min_gold and elixir >= min_elixir) or (search_idx >= max_searches):
            self.log(f"🎯 Target loot terpenuhi! Mempersiapkan penyerangan...")
            self.current_state = BotState.ATTACKING
            return True
        else:
            self.log("Loot di bawah target. Menekan tombol Next...")
            self.tap_with_jitter(1150, 580, radius=8)
            self.humanizer.sleep_random(2.4, 3.2)
            return False

    def finish_battle(self):
        self.log("Pertempuran selesai. Menyerah (Surrender) & Pulang...")
        self.tap_with_jitter(70, 560)
        self.humanizer.sleep_random(0.8, 1.2)

        self.tap_with_jitter(720, 440)
        self.humanizer.sleep_random(2.0, 2.8)

        self.tap_with_jitter(640, 600)
        self.humanizer.sleep_random(3.0, 4.0)
        self.current_state = BotState.VILLAGE

    def _worker_loop(self):
        """Main execution loop."""
        self.log("=== Bot Berjalan (Active) ===")
        self.status_cb("Running")

        farming_cfg = self.config.get("farming", {})
        min_gold = farming_cfg.get("min_gold", 200000)
        min_elixir = farming_cfg.get("min_elixir", 200000)
        max_searches = farming_cfg.get("max_search_count", 30)
        max_attacks = farming_cfg.get("max_attacks", 20)

        enable_home = farming_cfg.get("enable_home_farming", True)
        enable_builder = farming_cfg.get("enable_builder_farming", False)
        enable_claim = farming_cfg.get("enable_auto_claim", True)
        enable_wall = farming_cfg.get("enable_auto_wall", False)

        if not self.adb.connect():
            self.log("❌ Gagal terhubung ke emulator/device.")
            self.status_cb("Error")
            return

        while not self.stop_event.is_set():
            if self.is_interrupted(): break

            if enable_home:
                self.log(f"\n--- Memulai Siklus Penyerangan #{self.total_attacks + 1} ---")

                if enable_claim:
                    self.village.claim_collectors()
                    if self.is_interrupted(): break

                if enable_wall:
                    self.village.upgrade_wall()
                    if self.is_interrupted(): break

                self.train_army()
                if self.is_interrupted(): break

                self.find_match()
                if self.is_interrupted(): break

                search_idx = 1
                matched = False
                while not matched and search_idx <= max_searches and not self.is_interrupted():
                    matched = self.scout_base(min_gold, min_elixir, max_searches, search_idx)
                    search_idx += 1

                if matched and not self.is_interrupted():
                    self.strategy.execute_attack(cycles=2)
                    self.finish_battle()
                    self.total_attacks += 1
                    self.log(f"✅ Total serangan sukses: {self.total_attacks}/{max_attacks}")

            if enable_builder and not self.is_interrupted():
                self.log("\n--- Menjalankan Rutinitas Desa Malam ---")
                self.builder.switch_to_builder_base()
                if not self.is_interrupted():
                    self.builder.claim_gem_mine()
                    self.builder.execute_builder_attack()
                    self.builder.switch_to_home_village()

            if self.total_attacks >= max_attacks:
                self.log(f"🛑 Batas maksimum serangan ({max_attacks}) tercapai. Menghentikan bot secara otomatis.")
                break

            self.log("Menunggu istirahat antar siklus (cooldown)...")
            for _ in range(45):
                if self.is_interrupted(): break
                time.sleep(1)

        self.log("=== Bot Dihentikan (Stopped) ===")
        self.status_cb("Stopped")

    def run_one_cycle(self):
        """Runs the bot loop directly in CLI/Termux foreground."""
        try:
            self._worker_loop()
        except KeyboardInterrupt:
            self.stop()

    def start(self):
        if self.thread and self.thread.is_alive():
            return
        self.stop_event.clear()
        self.pause_event.set()
        self.thread = threading.Thread(target=self._worker_loop, daemon=True)
        self.thread.start()

    def pause(self):
        if self.pause_event.is_set():
            self.pause_event.clear()
            self.log("⏸ Bot dijeda (Paused).")
            self.status_cb("Paused")
        else:
            self.pause_event.set()
            self.log("▶ Bot dilanjutkan (Resumed).")
            self.status_cb("Running")

    def stop(self):
        self.stop_event.set()
        self.pause_event.set()
        self.log("Meminta penghentian bot...")
        self.status_cb("Stopping...")

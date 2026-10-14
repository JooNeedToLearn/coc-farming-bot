import time
from typing import List, Tuple
from core.adb_bridge import ADBBridge
from core.humanizer import Humanizer


class BarchPerimeterStrategy:
    """Strategy that drops troops along the outer map perimeter to snipe dead base collectors."""

    def __init__(self, adb: ADBBridge, humanizer: Humanizer):
        self.adb = adb
        self.humanizer = humanizer

        # Standard troop slots in battle bar (1280x720)
        # Slot 1: Barbarian, Slot 2: Archer
        self.slot_1_coords = (150, 650)
        self.slot_2_coords = (220, 650)

    def generate_perimeter_points(self, num_points: int = 16) -> List[Tuple[int, int]]:
        """Generates coordinate points along the outer diamond / perimeter of a 1280x720 canvas."""
        # Corner anchor points (just inside border)
        top = (640, 110)
        right = (1120, 360)
        bottom = (640, 590)
        left = (160, 360)

        corners = [top, right, bottom, left, top]
        points = []

        segments = len(corners) - 1
        pts_per_segment = max(1, num_points // segments)

        for i in range(segments):
            p1 = corners[i]
            p2 = corners[i + 1]
            for step in range(pts_per_segment):
                t = step / float(pts_per_segment)
                x = int(p1[0] + t * (p2[0] - p1[0]))
                y = int(p1[1] + t * (p2[1] - p1[1]))
                points.append((x, y))

        return points

    def execute_attack(self, cycles: int = 2):
        """Executes alternating wave deployment around perimeter."""
        print("[Strategy] Memulai penyebaran pasukan Barch di perimeter luar...")
        perimeter_points = self.generate_perimeter_points(num_points=12)

        for cycle in range(cycles):
            print(f"[Strategy] Gelombang serangan {cycle + 1}/{cycles}")

            # 1. Pilih Pasukan 1 (Barbarian)
            tap_x, tap_y = self.humanizer.jitter(self.slot_1_coords[0], self.slot_1_coords[1])
            self.adb.tap(tap_x, tap_y)
            self.humanizer.sleep_random(0.4, 0.7)

            # Deploy Barbarian di sekeliling base
            for pt in perimeter_points:
                px, py = self.humanizer.jitter(pt[0], pt[1], radius=8)
                self.adb.tap(px, py)
                time.sleep(0.08)

            self.humanizer.sleep_random(0.5, 0.9)

            # 2. Pilih Pasukan 2 (Archer)
            tap_x, tap_y = self.humanizer.jitter(self.slot_2_coords[0], self.slot_2_coords[1])
            self.adb.tap(tap_x, tap_y)
            self.humanizer.sleep_random(0.4, 0.7)

            # Deploy Archer di sekeliling base
            for pt in perimeter_points:
                px, py = self.humanizer.jitter(pt[0], pt[1], radius=8)
                self.adb.tap(px, py)
                time.sleep(0.08)

            self.humanizer.sleep_random(1.0, 2.0)

        print("[Strategy] Pasukan telah tersebar. Menunggu penjarahan kolektor...")
        # Waktu tunggu agar kolektor selesai diratakan
        time.sleep(25)

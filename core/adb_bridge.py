import subprocess
import cv2
import numpy as np
import time
from typing import Optional, Tuple, List


class ADBBridge:
    def __init__(self, adb_path: str = r"C:\Program Files\BlueStacks_nxt\HD-Adb.exe", host: str = "127.0.0.1", port: int = 5555):
        self.adb_path = adb_path
        self.host = host
        self.port = port
        self.device_id: Optional[str] = None

    def _get_attached_devices(self) -> List[str]:
        """Queries ADB for currently attached and ready devices."""
        try:
            result = subprocess.run([self.adb_path, "devices"],
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=3)
            lines = [line.strip() for line in result.stdout.strip().split("\n")[1:] if line.strip()]
            devices = []
            for line in lines:
                parts = line.split()
                if len(parts) >= 2 and parts[1] == "device":
                    devices.append(parts[0])
            return devices
        except Exception:
            return []

    def connect(self) -> bool:
        """Connects to BlueStacks ADB daemon and selects active device."""
        try:
            # 1. Cek apakah device sudah langsung terdaftar (misal: emulator-5554)
            devices = self._get_attached_devices()

            # 2. Jika belum ada, coba kirim perintah connect
            if not devices:
                target = f"{self.host}:{self.port}"
                try:
                    subprocess.run([self.adb_path, "connect", target],
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=2)
                except subprocess.TimeoutExpired:
                    pass
                devices = self._get_attached_devices()

            if not devices:
                print("[ADB] Tidak ada emulator yang terdeteksi.")
                print("[ADB] Pastikan BlueStacks 5 sedang berjalan dan setting ADB sudah aktif.")
                return False

            # Utamakan 127.0.0.1:5555 atau emulator-5554
            preferred = f"{self.host}:{self.port}"
            if preferred in devices:
                self.device_id = preferred
            else:
                self.device_id = devices[0]

            print(f"[ADB] ✅ Berhasil terhubung ke instance: {self.device_id}")
            return True
        except Exception as e:
            print(f"[ADB] Gagal menghubungkan ke ADB: {e}")
            return False

    def screencap(self) -> Optional[np.ndarray]:
        """Captures screen directly into memory as an OpenCV BGR image."""
        if not self.device_id:
            if not self.connect():
                return None

        cmd = [self.adb_path, "-s", self.device_id, "exec-out", "screencap", "-p"]
        try:
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            raw_png, _ = process.communicate(timeout=3)
            if not raw_png:
                return None

            img_array = np.frombuffer(raw_png, dtype=np.uint8)
            img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
            return img
        except Exception as e:
            print(f"[ADB] Error saat mengambil screencap: {e}")
            return None

    def tap(self, x: int, y: int) -> bool:
        """Sends tap touch event to device coordinates."""
        if not self.device_id:
            if not self.connect():
                return False

        cmd = [self.adb_path, "-s", self.device_id, "shell", "input", "tap", str(int(x)), str(int(y))]
        try:
            subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=3)
            return True
        except Exception as e:
            print(f"[ADB] Error saat tap({x}, {y}): {e}")
            return False

    def swipe(self, x1: int, y1: int, x2: int, y2: int, duration_ms: int = 300) -> bool:
        """Sends swipe touch event to device coordinates."""
        if not self.device_id:
            if not self.connect():
                return False

        cmd = [
            self.adb_path, "-s", self.device_id, "shell", "input", "swipe",
            str(int(x1)), str(int(y1)), str(int(x2)), str(int(y2)), str(int(duration_ms))
        ]
        try:
            subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=5)
            return True
        except Exception as e:
            print(f"[ADB] Error saat swipe: {e}")
            return False

    def get_screen_size(self) -> Optional[Tuple[int, int]]:
        """Returns (width, height) of current emulator screen."""
        if not self.device_id:
            if not self.connect():
                return None

        cmd = [self.adb_path, "-s", self.device_id, "shell", "wm", "size"]
        try:
            res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=3)
            for line in res.stdout.split("\n"):
                if "Physical size:" in line:
                    size_str = line.split(":")[1].strip()
                    w, h = map(int, size_str.split("x"))
                    return (w, h)
        except Exception as e:
            print(f"[ADB] Error membaca ukuran layar: {e}")
        return None

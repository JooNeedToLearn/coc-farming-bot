import subprocess
import time
import os
import sys
import shutil
import io
from typing import Optional, Tuple, List

try:
    import numpy as np
    HAS_NUMPY = True
except Exception:
    HAS_NUMPY = False
    np = None

try:
    import cv2
    HAS_CV2 = True and HAS_NUMPY
except Exception:
    HAS_CV2 = False

try:
    from PIL import Image
    HAS_PIL = True
except Exception:
    HAS_PIL = False


class ADBBridge:
    def __init__(self, adb_path: Optional[str] = None, host: str = "127.0.0.1", port: int = 5555):
        self.host = host
        self.port = port
        self.device_id: Optional[str] = None
        self.is_termux = "TERMUX_VERSION" in os.environ or os.path.exists("/data/data/com.termux")
        self.use_direct_root = False

        if adb_path and os.path.exists(adb_path):
            self.adb_path = adb_path
        elif sys.platform == "win32":
            default_bs = r"C:\Program Files\BlueStacks_nxt\HD-Adb.exe"
            self.adb_path = default_bs if os.path.exists(default_bs) else (shutil.which("adb") or "adb")
        else:
            self.adb_path = shutil.which("adb") or "adb"

    def _check_root(self) -> bool:
        """Checks if device has direct root execution available."""
        if not self.is_termux:
            return False
        try:
            res = subprocess.run(["su", "-c", "id"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=2)
            if res.returncode == 0 and b"uid=0" in res.stdout:
                self.use_direct_root = True
                return True
        except Exception:
            pass
        return False

    def _get_attached_devices(self) -> List[str]:
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
        if self._check_root():
            print("[ADB] ✅ Terdeteksi mode Root langsung di Termux (Cloud Phone).")
            self.device_id = "local_root"
            return True

        try:
            devices = self._get_attached_devices()
            if not devices:
                target = f"{self.host}:{self.port}"
                try:
                    subprocess.run([self.adb_path, "connect", target],
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=2)
                except subprocess.TimeoutExpired:
                    pass
                devices = self._get_attached_devices()

            if not devices:
                print("[ADB] Tidak ada device/emulator yang terdeteksi.")
                return False

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

    def screencap(self):
        """Captures screen directly into memory."""
        if not self.device_id:
            if not self.connect():
                return None

        if self.use_direct_root:
            cmd = ["su", "-c", "screencap -p"]
        else:
            cmd = [self.adb_path, "-s", self.device_id, "exec-out", "screencap", "-p"]

        try:
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            raw_png, _ = process.communicate(timeout=4)
            if not raw_png:
                return None

            if HAS_CV2 and HAS_NUMPY:
                img_array = np.frombuffer(raw_png, dtype=np.uint8)
                return cv2.imdecode(img_array, cv2.IMREAD_COLOR)
            elif HAS_PIL:
                pil_img = Image.open(io.BytesIO(raw_png)).convert("RGB")
                if HAS_NUMPY:
                    rgb_arr = np.array(pil_img)
                    return rgb_arr[:, :, ::-1]
                return pil_img
            return raw_png
        except Exception as e:
            print(f"[ADB] Error saat mengambil screencap: {e}")
            return None

    def tap(self, x: int, y: int) -> bool:
        if not self.device_id:
            if not self.connect():
                return False

        if self.use_direct_root:
            cmd = ["su", "-c", f"input tap {int(x)} {int(y)}"]
        else:
            cmd = [self.adb_path, "-s", self.device_id, "shell", "input", "tap", str(int(x)), str(int(y))]

        try:
            subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=3)
            return True
        except Exception as e:
            print(f"[ADB] Error saat tap({x}, {y}): {e}")
            return False

    def swipe(self, x1: int, y1: int, x2: int, y2: int, duration_ms: int = 300) -> bool:
        if not self.device_id:
            if not self.connect():
                return False

        if self.use_direct_root:
            cmd = ["su", "-c", f"input swipe {int(x1)} {int(y1)} {int(x2)} {int(y2)} {int(duration_ms)}"]
        else:
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
        if not self.device_id:
            if not self.connect():
                return None

        if self.use_direct_root:
            cmd = ["su", "-c", "wm size"]
        else:
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

    def pinch_zoom_out(self, times: int = 2) -> bool:
        """Simulates two-finger pinch inward gesture to zoom out the battlefield."""
        print(f"[ADB] Melakukan zoom-out kamera ({times}x pinch)...")
        w, h = self.get_screen_size() or (1280, 720)
        cx, cy = w // 2, h // 2

        for _ in range(times):
            # Swipe diagonal 1: sudut kiri atas ke tengah
            self.swipe(int(cx * 0.4), int(cy * 0.4), int(cx * 0.85), int(cy * 0.85), duration_ms=250)
            time.sleep(0.08)
            # Swipe diagonal 2: sudut kanan bawah ke tengah
            self.swipe(int(cx * 1.6), int(cy * 1.6), int(cx * 1.15), int(cy * 1.15), duration_ms=250)
            time.sleep(0.4)
        return True


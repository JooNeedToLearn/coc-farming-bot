import argparse
import yaml
import os
import sys

# Optional OpenCV with Pillow fallback
try:
    import cv2
    HAS_CV2 = True
except ImportError:
    HAS_CV2 = False

try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

from core.adb_bridge import ADBBridge
from core.bot_controller import BotController
from core.vision_engine import VisionEngine


def save_image(filepath: str, img_array):
    if HAS_CV2:
        cv2.imwrite(filepath, img_array)
    elif HAS_PIL:
        # img_array is in BGR format, convert to RGB for PIL
        rgb = img_array[:, :, ::-1] if len(img_array.shape) == 3 else img_array
        Image.fromarray(rgb).save(filepath)


def load_config(config_path: str = "config/settings.yaml"):
    if not os.path.exists(config_path):
        print(f"Error: Konfigurasi {config_path} tidak ditemukan.")
        sys.exit(1)
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def test_adb(config):
    print("\n--- [Uji Diagnostik ADB & Emulator/Device] ---")
    adb = ADBBridge(
        adb_path=config["emulator"].get("adb_path"),
        host=config["emulator"].get("host", "127.0.0.1"),
        port=config["emulator"].get("port", 5555)
    )

    if not adb.connect():
        print("❌ Gagal terhubung ke ADB atau Root.")
        return

    size = adb.get_screen_size()
    print(f"✅ Berhasil terhubung! Resolusi layar: {size}")

    print("Mengambil tangkapan layar (screencap)...")
    frame = adb.screencap()
    if frame is not None:
        out_path = "test_screen.png"
        save_image(out_path, frame)
        print(f"✅ Screencap berhasil disimpan ke: {out_path} ({frame.shape[1]}x{frame.shape[0]} px)")
    else:
        print("❌ Gagal mengambil screencap.")


def test_ocr(config):
    print("\n--- [Uji Ekstraksi Loot (Vision & OCR)] ---")
    adb = ADBBridge(
        adb_path=config["emulator"].get("adb_path"),
        host=config["emulator"].get("host", "127.0.0.1"),
        port=config["emulator"].get("port", 5555)
    )
    if not adb.connect():
        return

    screen = adb.screencap()
    if screen is None:
        print("❌ Tidak dapat mengambil tangkapan layar.")
        return

    vision = VisionEngine()
    rois = vision.extract_loot_roi(screen)

    save_image("roi_gold.png", rois["gold"])
    save_image("roi_elixir.png", rois["elixir"])
    save_image("roi_dark.png", rois["dark_elixir"])
    print("✅ ROI Gold, Elixir, dan Dark Elixir telah disimpan.")

    gold = vision.parse_loot_digits(rois["gold"])
    elixir = vision.parse_loot_digits(rois["elixir"])
    print(f"Hasil ekstraksi angka -> Gold: {gold:,} | Elixir: {elixir:,}")


def main():
    parser = argparse.ArgumentParser(description="Clash of Clans Auto Farming Bot - Multiplatform Edition")
    parser.add_argument("--test-adb", action="store_true", help="Tes koneksi ADB/Root dan ambil 1 screenshot uji coba")
    parser.add_argument("--test-ocr", action="store_true", help="Tes deteksi teks loot dari layar aktif")
    parser.add_argument("--dry-run", action="store_true", help="Jalankan pencarian musuh tanpa melakukan serangan")
    parser.add_argument("--run", action="store_true", help="Jalankan bot auto farming penuh")

    args = parser.parse_args()
    config = load_config()

    if args.test_adb:
        test_adb(config)
    elif args.test_ocr:
        test_ocr(config)
    elif args.run:
        bot = BotController(config)
        bot.run_one_cycle()
    else:
        test_adb(config)


if __name__ == "__main__":
    main()

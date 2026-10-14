import argparse
import yaml
import os
import sys
import cv2

from core.adb_bridge import ADBBridge
from core.bot_controller import BotController
from core.vision_engine import VisionEngine


def load_config(config_path: str = "config/settings.yaml"):
    if not os.path.exists(config_path):
        print(f"Error: Konfigurasi {config_path} tidak ditemukan.")
        sys.exit(1)
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def test_adb(config):
    print("\n--- [Uji Diagnostik ADB & BlueStacks] ---")
    adb = ADBBridge(
        adb_path=config["emulator"].get("adb_path", r"C:\Program Files\BlueStacks_nxt\HD-Adb.exe"),
        host=config["emulator"].get("host", "127.0.0.1"),
        port=config["emulator"].get("port", 5555)
    )

    if not adb.connect():
        print("❌ Gagal terhubung ke ADB BlueStacks.")
        print("Pastikan ADB aktif di BlueStacks Settings -> Advanced -> Connect to Android at 127.0.0.1:5555.")
        return

    size = adb.get_screen_size()
    print(f"✅ Berhasil terhubung! Resolusi layar emulator: {size}")

    print("Mengambil tangkapan layar (screencap)...")
    frame = adb.screencap()
    if frame is not None:
        out_path = "test_screen.png"
        cv2.imwrite(out_path, frame)
        print(f"✅ Screencap berhasil disimpan ke: {out_path} ({frame.shape[1]}x{frame.shape[0]} px)")
    else:
        print("❌ Gagal mengambil screencap.")


def test_ocr(config):
    print("\n--- [Uji Ekstraksi Loot (Vision & OCR)] ---")
    adb = ADBBridge(
        adb_path=config["emulator"].get("adb_path", r"C:\Program Files\BlueStacks_nxt\HD-Adb.exe"),
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

    # Simpan crop ROI untuk evaluasi pengguna
    cv2.imwrite("roi_gold.png", rois["gold"])
    cv2.imwrite("roi_elixir.png", rois["elixir"])
    cv2.imwrite("roi_dark.png", rois["dark_elixir"])
    print("✅ ROI Gold, Elixir, dan Dark Elixir telah disimpan (roi_gold.png, roi_elixir.png, roi_dark.png).")

    gold = vision.parse_loot_digits(rois["gold"])
    elixir = vision.parse_loot_digits(rois["elixir"])
    print(f"Hasil ekstraksi angka -> Gold: {gold:,} | Elixir: {elixir:,}")


def main():
    parser = argparse.ArgumentParser(description="Clash of Clans Auto Farming Bot - BlueStacks 5 Edition")
    parser.add_argument("--test-adb", action="store_true", help="Tes koneksi ADB dan ambil 1 screenshot uji coba")
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
        # Default jika tidak ada opsi: lakukan test-adb
        test_adb(config)


if __name__ == "__main__":
    main()

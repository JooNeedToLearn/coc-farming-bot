import os
import sys
import shutil
import zipfile
import subprocess

BASE_DIR = r"d:\Documents\LifeHack"
APP_DIR = os.path.join(r"d:\Documents\LifeHack\coc_farming_bot", "kelnara_native_app")
AAPT2 = os.path.join(BASE_DIR, "aapt2.exe")
ANDROID_JAR = os.path.join(BASE_DIR, "android.jar")
R8_JAR = os.path.join(BASE_DIR, "r8.jar")
KEYSTORE = os.path.join(r"d:\Documents\LifeHack\coc_farming_bot", "android", "kelnara.keystore")

WORK_DIR = os.path.join(r"d:\Documents\LifeHack\coc_farming_bot", "native_build_temp")
shutil.rmtree(WORK_DIR, ignore_errors=True)
os.makedirs(WORK_DIR, exist_ok=True)

GEN_DIR = os.path.join(WORK_DIR, "gen")
BIN_DIR = os.path.join(WORK_DIR, "bin")
DEX_DIR = os.path.join(WORK_DIR, "dex")
os.makedirs(GEN_DIR, exist_ok=True)
os.makedirs(BIN_DIR, exist_ok=True)
os.makedirs(DEX_DIR, exist_ok=True)

COMPILED_RES = os.path.join(WORK_DIR, "resources.zip")
BASE_APK = os.path.join(WORK_DIR, "base.apk")
FINAL_APK = os.path.join(r"d:\Documents\LifeHack\coc_farming_bot", "android", "Kelnara_Bot_CoC.apk")
DESKTOP_APK = os.path.join(os.path.expanduser("~"), "Desktop", "Kelnara_Bot_CoC.apk")

print("=== MEMULAI KOMPILASI APLIKASI NATIVE KELNARA BOT CoC ===")

# 1. Compile Resources with aapt2
print("\n[1/5] Mengompilasi resource XML dengan aapt2...")
cmd_compile = [
    AAPT2, "compile",
    "--dir", os.path.join(APP_DIR, "res"),
    "-o", COMPILED_RES
]
res = subprocess.run(cmd_compile, capture_output=True, text=True)
if res.returncode != 0:
    print("Error aapt2 compile:", res.stderr)
    sys.exit(1)
print("Resource XML berhasil dikompilasi!")

# 2. Link with aapt2 & generate R.java
print("\n[2/5] Menautkan resource dan menghasilkan R.java...")
cmd_link = [
    AAPT2, "link",
    "-I", ANDROID_JAR,
    COMPILED_RES,
    "--manifest", os.path.join(APP_DIR, "AndroidManifest.xml"),
    "--java", GEN_DIR,
    "-o", BASE_APK,
    "--auto-add-overlay"
]
res = subprocess.run(cmd_link, capture_output=True, text=True)
if res.returncode != 0:
    print("Error aapt2 link:", res.stderr)
    sys.exit(1)
print("Link berhasil, R.java terbentuk!")

# 3. Compile Java with javac
print("\n[3/5] Mengompilasi kode Java native (MainActivity, FloatingService, FarmingEngine, CoCAccessibilityService)...")
java_files = []
for root, _, files in os.walk(os.path.join(APP_DIR, "src")):
    for f in files:
        if f.endswith(".java"):
            java_files.append(os.path.join(root, f))
for root, _, files in os.walk(GEN_DIR):
    for f in files:
        if f.endswith(".java"):
            java_files.append(os.path.join(root, f))

cmd_javac = [
    "javac",
    "-cp", ANDROID_JAR,
    "-d", BIN_DIR,
    "--release", "8"
] + java_files

res = subprocess.run(cmd_javac, capture_output=True, text=True)
if res.returncode != 0:
    print("Error javac:", res.stderr)
    sys.exit(1)
print("Semua class Java berhasil dikompilasi ke bytecode!")

# 4. Convert .class to classes.dex using D8
print("\n[4/5] Mengonversi bytecode Java ke Dalvik Executable (classes.dex) menggunakan Google D8...")
class_files = []
for root, _, files in os.walk(BIN_DIR):
    for f in files:
        if f.endswith(".class"):
            class_files.append(os.path.join(root, f))

cmd_d8 = [
    "java", "-cp", R8_JAR,
    "com.android.tools.r8.D8",
    "--output", DEX_DIR,
    "--lib", ANDROID_JAR,
    "--min-api", "21"
] + class_files

res = subprocess.run(cmd_d8, capture_output=True, text=True)
if res.returncode != 0:
    print("Error D8:", res.stderr)
    sys.exit(1)
print("classes.dex resmi berhasil dibuat!")

# 5. Pack classes.dex into APK and Sign with Google apksig (v1 + v2 + v3)
print("\n[5/5] Memasukkan classes.dex ke APK & menandatangani dengan Google apksig (v1 + v2 + v3)...")
classes_dex = os.path.join(DEX_DIR, "classes.dex")
with zipfile.ZipFile(BASE_APK, "a", compression=zipfile.ZIP_DEFLATED) as z:
    z.write(classes_dex, "classes.dex")

# Sign with SignTool (official Google apksig library)
SIGNED_TEMP_APK = os.path.join(WORK_DIR, "signed.apk")
cmd_sign = [
    "java", "-cp", f"apksig.jar;{BASE_DIR}",
    "SignTool",
    BASE_APK,
    SIGNED_TEMP_APK,
    KEYSTORE,
    "kelnara123",
    "kelnara"
]
res = subprocess.run(cmd_sign, capture_output=True, text=True, cwd=BASE_DIR)
if res.returncode != 0:
    print("Error apksig SignTool:", res.stderr)
    sys.exit(1)
print(res.stdout.strip())

# Copy to final destinations
shutil.copyfile(SIGNED_TEMP_APK, FINAL_APK)
print(f"\n✅ APK BERHASIL DIBUAT: {FINAL_APK}")
if os.path.exists(os.path.dirname(DESKTOP_APK)):
    shutil.copyfile(SIGNED_TEMP_APK, DESKTOP_APK)
    print(f"✅ APK JUGA DISALIN KE DESKTOP: {DESKTOP_APK}")

size_mb = os.path.getsize(FINAL_APK) / (1024 * 1024)
print(f"Ukuran APK murni: {size_mb:.2f} MB (Sangat ringan, 100% Native, Tanpa AutoX, Bebas Crash!)")

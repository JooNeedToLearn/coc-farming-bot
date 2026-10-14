import os
import shutil
import zipfile
import subprocess
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_APK = os.path.join(BASE_DIR, "assets", "template.apk")
KEYSTORE = os.path.join(BASE_DIR, "android", "kelnara.keystore")
BUILD_DIR = os.path.join(BASE_DIR, "build_apk")
OUTPUT_APK = os.path.join(BASE_DIR, "android", "Kelnara_Bot_CoC.apk")
DESKTOP_DIR = os.path.join(os.path.expanduser("~"), "Desktop")
DESKTOP_APK = os.path.join(DESKTOP_DIR, "Kelnara_Bot_CoC.apk")

os.makedirs(BUILD_DIR, exist_ok=True)
PROJECT_DIR = os.path.join(BUILD_DIR, "project")
os.makedirs(PROJECT_DIR, exist_ok=True)

# 1. Tulis project.json
project_config = {
    "name": "Kelnara Bot CoC",
    "main": "main.js",
    "ignore": ["build"],
    "packageName": "com.kelnara.botcoc",
    "versionName": "1.0.0",
    "versionCode": 1,
    "icon": "icon.png"
}

with open(os.path.join(PROJECT_DIR, "project.json"), "w", encoding="utf-8") as f:
    json.dump(project_config, f, indent=2)

# 2. Tulis main.js (Aplikasi Native Kelnara dengan UI Lengkap + Floating Bot)
main_js_content = """\
"ui";

/**
 * ============================================================================
 * ⚔️ KELNARA BOT CoC — Smart Farming, Easy Progress
 * Standalone Android Application
 * ============================================================================
 */

ui.layout(
    <drawer id="drawer">
        <vertical bg="#0b0f19">
            <appbar bg="#0f172a">
                <toolbar id="toolbar" title="⚔️ Kelnara Bot CoC" subtitle="Smart Farming, Easy Progress" titleTextColor="#f59e0b" subtitleTextColor="#94a3b8" />
            </appbar>

            <scroll>
                <vertical padding="16">
                    {/* Profil Desa Card */}
                    <card cardCornerRadius="14dp" cardElevation="4dp" contentPadding="14dp" bg="#131b2e" cardBackgroundColor="#131b2e">
                        <horizontal gravity="center_vertical">
                            <text text="🏰" textSize="32sp" />
                            <vertical marginLeft="12">
                                <horizontal>
                                    <text text="HAHAHAA BURUH PABRIK" textSize="16sp" textStyle="bold" textColor="#ffffff" />
                                    <text text=" TH13" textSize="12sp" textStyle="bold" textColor="#38bdf8" marginLeft="6" />
                                </horizontal>
                                <text text="Level 158 • Champion III • 5/5 Builder" textSize="11sp" textColor="#94a3b8" marginTop="2" />
                            </vertical>
                        </horizontal>
                    </card>

                    {/* Tombol Utama: Luncurkan Floating Bot */}
                    <button id="btn_launch_float" text="🚀 LUNCURKAN FLOATING BOT (OVERLAY)" bg="#10b981" textColor="#ffffff" textSize="14sp" textStyle="bold" h="54dp" marginTop="16" />

                    {/* Pengaturan Farming */}
                    <card cardCornerRadius="14dp" cardElevation="4dp" contentPadding="14dp" bg="#131b2e" cardBackgroundColor="#131b2e" marginTop="16">
                        <vertical>
                            <text text="🎯 Konfigurasi Farming Kelnara" textSize="14sp" textStyle="bold" textColor="#f59e0b" />
                            
                            <horizontal marginTop="10" gravity="center_vertical">
                                <text text="Min Gold (k):" textSize="12sp" textColor="#ffffff" w="110dp" />
                                <input id="inp_gold" text="350" textSize="12sp" inputType="number" textColor="#f59e0b" textStyle="bold" w="100dp" />
                            </horizontal>

                            <horizontal gravity="center_vertical" marginTop="4">
                                <text text="Min Elixir (k):" textSize="12sp" textColor="#ffffff" w="110dp" />
                                <input id="inp_elixir" text="350" textSize="12sp" inputType="number" textColor="#d946ef" textStyle="bold" w="100dp" />
                            </horizontal>

                            <checkbox id="chk_claim" text="Auto Panen Tambang (Mines & Collectors)" textSize="12sp" textColor="#ffffff" checked="true" marginTop="8" />
                            <checkbox id="chk_zoom" text="Auto Zoom-Out 2x Base Musuh" textSize="12sp" textColor="#ffffff" checked="true" />
                            <checkbox id="chk_train" text="Auto Quick Train Barak (Preset Barch)" textSize="12sp" textColor="#ffffff" checked="true" />
                        </vertical>
                    </card>

                    {/* Info Preset Pasukan */}
                    <card cardCornerRadius="14dp" cardElevation="4dp" contentPadding="14dp" bg="#131b2e" cardBackgroundColor="#131b2e" marginTop="16">
                        <vertical>
                            <text text="👥 Preset Pasukan Aktif" textSize="14sp" textStyle="bold" textColor="#38bdf8" />
                            <text text="Barch Perimeter Striker (260/260 Space)" textSize="13sp" textStyle="bold" textColor="#ffffff" marginTop="4" />
                            <text text="• 120 Barbarian (Lv 9)&#10;• 140 Archer (Lv 9)&#10;• Deploy melingkar 12 titik perimeter luar" textSize="11sp" textColor="#94a3b8" marginTop="4" />
                        </vertical>
                    </card>

                    {/* Footer Info */}
                    <text text="Kelnara Bot CoC v1.0.0 — Lifetime Pro Edition" textSize="10sp" textColor="#64748b" gravity="center" marginTop="24" />
                </vertical>
            </scroll>
        </vertical>
    </drawer>
);

// Event Tombol Luncurkan Floating Bot
ui.btn_launch_float.click(function() {
    launchFloatingOverlay();
});

var floatWindow = null;
var botThread = null;
var isRunning = false;

function launchFloatingOverlay() {
    if (!floaty.checkPermission()) {
        toastLog("⚠️ Harap aktifkan izin 'Tampilkan di atas aplikasi lain'");
        floaty.requestPermission();
        return;
    }

    if (auto.service == null) {
        toastLog("⚠️ Aktifkan Layanan Aksesibilitas untuk Kelnara Bot");
        app.startActivity({ action: "android.settings.ACCESSIBILITY_SETTINGS" });
        return;
    }

    if (floatWindow != null) {
        toast("Floating widget sudah aktif!");
        return;
    }

    var minGoldVal = (parseInt(ui.inp_gold.getText().toString()) || 350) * 1000;
    var minElixirVal = (parseInt(ui.inp_elixir.getText().toString()) || 350) * 1000;
    var doClaim = ui.chk_claim.isChecked();
    var doZoom = ui.chk_zoom.isChecked();

    floatWindow = floaty.window(
        <frame id="mainFrame" bg="#0f172a" alpha="0.95" w="auto" h="auto" padding="12" cornerRadius="16">
            <vertical>
                <horizontal id="headerBar" gravity="center_vertical">
                    <text text="⚔️ KELNARA BOT" textSize="13sp" textStyle="bold" textColor="#f59e0b" />
                    <text text=" (Geser)" textSize="9sp" textColor="#94a3b8" marginLeft="4" />
                    <button id="btn_fclose" text="✕" w="28" h="28" textSize="11sp" textColor="#ef4444" style="Widget.AppCompat.Button.Borderless" />
                </horizontal>
                
                <text id="txt_fstatus" text="Status: IDLE (Siap)" textSize="11sp" textColor="#38bdf8" gravity="center" marginTop="4" />
                
                <horizontal marginTop="6" gravity="center">
                    <button id="btn_ftoggle" text="▶ MULAI" w="88" h="38" bg="#10b981" textColor="#ffffff" textStyle="bold" />
                    <button id="btn_fhide" text="Sembunyikan" w="88" h="38" bg="#334155" textColor="#ffffff" marginLeft="6" />
                </horizontal>
            </vertical>
        </frame>
    );

    floatWindow.setPosition(40, 80);
    toast("✅ Kelnara Floating Bot Aktif! Silakan buka Clash of Clans.");

    // Drag and Drop
    var touchStartX = 0, touchStartY = 0;
    var windowStartX = 0, windowStartY = 0;

    floatWindow.headerBar.setOnTouchListener(function(view, event) {
        switch (event.getAction()) {
            case event.ACTION_DOWN:
                touchStartX = event.getRawX();
                touchStartY = event.getRawY();
                windowStartX = floatWindow.getX();
                windowStartY = floatWindow.getY();
                return true;
            case event.ACTION_MOVE:
                floatWindow.setPosition(
                    windowStartX + (event.getRawX() - touchStartX),
                    windowStartY + (event.getRawY() - touchStartY)
                );
                return true;
        }
        return true;
    });

    floatWindow.btn_fclose.click(function() {
        if (botThread && botThread.isAlive()) botThread.interrupt();
        floatWindow.close();
        floatWindow = null;
    });

    floatWindow.btn_fhide.click(function() {
        toast("Bot tetap berjalan di latar belakang.");
    });

    floatWindow.btn_ftoggle.click(function() {
        if (!isRunning) {
            isRunning = true;
            ui.run(function() {
                floatWindow.btn_ftoggle.setText("⏹ STOP");
                floatWindow.btn_ftoggle.attr("bg", "#ef4444");
                floatWindow.txt_fstatus.setText("Status: Farming Aktif");
            });
            botThread = threads.start(function() {
                botFarmingLoop(minGoldVal, minElixirVal, doClaim, doZoom);
            });
        } else {
            isRunning = false;
            if (botThread && botThread.isAlive()) botThread.interrupt();
            ui.run(function() {
                floatWindow.btn_ftoggle.setText("▶ MULAI");
                floatWindow.btn_ftoggle.attr("bg", "#10b981");
                floatWindow.txt_fstatus.setText("Status: Berhenti (IDLE)");
            });
        }
    });

    // Coba buka CoC otomatis jika ada
    try {
        app.launchPackage("com.supercell.clashofclans");
    } catch (e) {}
}

function botFarmingLoop(minGold, minElixir, enableClaim, enableZoom) {
    var screenW = Math.max(device.width, device.height);
    var screenH = Math.min(device.width, device.height);
    var scaleX = screenW / 1280.0;
    var scaleY = screenH / 720.0;
    var centerX = screenW / 2;
    var centerY = screenH / 2;

    function tapScaled(bx, by) {
        click(parseInt(bx * scaleX) + random(-3, 3), parseInt(by * scaleY) + random(-3, 3));
        sleep(random(650, 1000));
    }

    while (isRunning) {
        try {
            // A. Panen Kolektor
            if (enableClaim) {
                var collectors = [
                    [500, 320], [620, 310], [680, 350], [740, 330],
                    [440, 420], [640, 480], [760, 450], [840, 410]
                ];
                for (var i = 0; i < collectors.length; i++) {
                    if (!isRunning) break;
                    tapScaled(collectors[i][0], collectors[i][1]);
                    sleep(150);
                }
            }

            // B. Quick Train Barak
            tapScaled(60, 620);
            sleep(1200);
            tapScaled(1000, 120);
            sleep(900);
            tapScaled(1100, 280);
            sleep(900);
            tapScaled(1180, 80);
            sleep(1100);

            // C. Buka Attack
            tapScaled(75, 630);
            sleep(1500);
            tapScaled(950, 520);
            sleep(4000);

            // D. Scouting Loop (3-5x next)
            for (var s = 0; s < 4; s++) {
                if (!isRunning) break;
                sleep(2500);
                tapScaled(1150, 580); // Tombol Next
                sleep(3000);
            }

            // E. Auto Zoom Out 2x
            if (isRunning && enableZoom) {
                for (var z = 0; z < 2; z++) {
                    gestures(
                        [0, 450, [centerX * 0.35, centerY * 0.35], [centerX * 0.85, centerY * 0.85]],
                        [0, 450, [centerX * 1.65, centerY * 1.65], [centerX * 1.15, centerY * 1.15]]
                    );
                    sleep(500);
                }
                sleep(800);
            }

            // F. Deploy Pasukan (Perimeter 12 Titik)
            if (isRunning) {
                var perimeter = [
                    [640, 120], [840, 220], [1050, 340], [1120, 360],
                    [1050, 420], [840, 520], [640, 580], [440, 520],
                    [220, 420], [160, 360], [220, 280], [440, 200]
                ];

                // Barbarian
                tapScaled(150, 650);
                sleep(500);
                for (var p = 0; p < perimeter.length; p++) {
                    tapScaled(perimeter[p][0], perimeter[p][1]);
                    sleep(80);
                }

                // Archer
                tapScaled(220, 650);
                sleep(500);
                for (var a = 0; a < perimeter.length; a++) {
                    tapScaled(perimeter[a][0], perimeter[a][1]);
                    sleep(80);
                }

                // Tunggu jarahan selesai
                sleep(25000);
            }

            // G. Surrender & Return Home
            if (isRunning) {
                tapScaled(70, 560);
                sleep(1000);
                tapScaled(720, 440);
                sleep(2500);
                tapScaled(640, 600);
                sleep(3500);
            }

            // Istirahat siklus (40 detik)
            for (var w = 0; w < 40; w++) {
                if (!isRunning) break;
                sleep(1000);
            }

        } catch (e) {
            log("Bot loop error: " + e);
            sleep(3000);
        }
    }
}
"""

with open(os.path.join(PROJECT_DIR, "main.js"), "w", encoding="utf-8") as f:
    f.write(main_js_content)

# 3. Salin web dashboard ke build_apk/project/web
WEB_SRC = os.path.join(BASE_DIR, "kelnara_app")
WEB_DST = os.path.join(PROJECT_DIR, "web")
if os.path.exists(WEB_DST):
    shutil.rmtree(WEB_DST)
shutil.copytree(WEB_SRC, WEB_DST)

# 4. Bangun APK: Ambil template.apk dan inject assets/project/
TEMP_UNPACKED_APK = os.path.join(BUILD_DIR, "unsigned.apk")
shutil.copyfile(TEMPLATE_APK, TEMP_UNPACKED_APK)

print("Menginjeksi file Kelnara Bot CoC ke dalam template.apk...")
with zipfile.ZipFile(TEMP_UNPACKED_APK, 'a', compression=zipfile.ZIP_DEFLATED) as apk_zip:
    for root, _, files in os.walk(PROJECT_DIR):
        for file in files:
            full_path = os.path.join(root, file)
            rel_path = os.path.relpath(full_path, PROJECT_DIR)
            zip_target = "assets/project/" + rel_path.replace("\\", "/")
            apk_zip.write(full_path, zip_target)
            print(f"  + Ditambahkan: {zip_target}")

# 5. Sign APK dengan jarsigner
print("\nMenandatangani APK dengan jarsigner...")
sign_cmd = [
    "jarsigner",
    "-verbose",
    "-sigalg", "SHA256withRSA",
    "-digestalg", "SHA-256",
    "-keystore", KEYSTORE,
    "-storepass", "kelnara123",
    "-keypass", "kelnara123",
    TEMP_UNPACKED_APK,
    "kelnara"
]

res = subprocess.run(sign_cmd, capture_output=True, text=True)
if res.returncode != 0:
    print("Gagal sign APK:", res.stderr)
    exit(1)
print("APK berhasil ditandatangani secara resmi!")

# 6. Salin hasil akhir ke android/Kelnara_Bot_CoC.apk & Desktop
shutil.copyfile(TEMP_UNPACKED_APK, OUTPUT_APK)
print(f"APK tersimpan di: {OUTPUT_APK}")

if os.path.exists(DESKTOP_DIR):
    shutil.copyfile(TEMP_UNPACKED_APK, DESKTOP_APK)
    print(f"APK juga disalin ke Desktop: {DESKTOP_APK}")

print("\nVerifikasi signature APK:")
verify_cmd = ["jarsigner", "-verify", OUTPUT_APK]
v_res = subprocess.run(verify_cmd, capture_output=True, text=True)
print(v_res.stdout)
print("SELESAI! File APK siap dipasang di Android / Cloud Phone!")

/**
 * ============================================================================
 * ⚔️ KELNARA BOT CoC (coc_bot.js) — Smart Farming, Easy Progress
 * Platform: Android Native / Redfinger Cloud Phone Edition
 * ============================================================================
 * 
 * 📌 PANDUAN MENJALANKAN DI AUTODETEKSI / CLOUD PHONE:
 * 1. Buka aplikasi AutoX.js di Cloud Phone / Android Anda.
 * 2. Di halaman utama (Daftar File / 管理), cari file ini.
 * 3. Klik tombol ▶ (Play) di SEBELAH KANAN nama file tersebut.
 *    (Catatan: Jangan menekan tombol run di dalam editor teks Monaco agar tidak
 *     muncul pesan "暂不支持!").
 * 4. Berikan izin "Tampilkan di atas aplikasi lain" & "Aksesibilitas" jika diminta.
 * 5. Floating widget Kelnara Bot CoC akan langsung muncul di atas layar game CoC!
 * ============================================================================
 */

// 1. Cek & Minta Izin Floating Window (Overlay di atas game)
if (!floaty.checkPermission()) {
    toastLog("⚠️ Harap aktifkan izin 'Tampilkan di atas aplikasi lain' untuk Kelnara Bot");
    floaty.requestPermission();
    sleep(2000);
}

// Konfigurasi Default Kelnara Bot
var config = {
    minGold: 350000,
    minElixir: 350000,
    minDe: 3000,
    maxSearches: 35,
    autoZoom: true,
    enableAutoClaim: true,
    isRunning: false
};

var botThread = null;

// 2. Tampilan Floating Widget Kelnara (Bisa Digeser / Draggable)
var window = floaty.window(
    <frame id="mainFrame" bg="#0f172a" alpha="0.95" w="auto" h="auto" padding="12" cornerRadius="16">
        <vertical>
            {/* Header Widget */}
            <horizontal id="headerBar" gravity="center_vertical">
                <text text="⚔️ KELNARA BOT" textSize="13sp" textStyle="bold" textColor="#f59e0b" />
                <text text=" (Geser)" textSize="9sp" textColor="#94a3b8" marginLeft="4" />
                <button id="btn_close" text="✕" w="28" h="28" textSize="11sp" textColor="#ef4444" style="Widget.AppCompat.Button.Borderless" />
            </horizontal>
            
            {/* Status Bot */}
            <text id="txt_status" text="Status: IDLE (Siap Farming)" textSize="11sp" textColor="#38bdf8" gravity="center" marginTop="4" />
            
            {/* Input Min Gold & Elixir */}
            <horizontal marginTop="6" gravity="center_vertical">
                <text text="Min Gold (k):" textSize="11sp" textColor="#ffffff" />
                <input id="inp_gold" text="350" w="65" textSize="11sp" inputType="number" textColor="#f59e0b" textStyle="bold" />
            </horizontal>
            
            <horizontal gravity="center_vertical">
                <text text="Min Elixir (k):" textSize="11sp" textColor="#ffffff" />
                <input id="inp_elixir" text="350" w="65" textSize="11sp" inputType="number" textColor="#d946ef" textStyle="bold" />
            </horizontal>
            
            {/* Checkbox Fitur */}
            <checkbox id="chk_claim" text="Auto Panen Tambang" textSize="11sp" textColor="#ffffff" checked="true" marginTop="2" />
            <checkbox id="chk_zoom" text="Auto Zoom-Out 2x" textSize="11sp" textColor="#ffffff" checked="true" />
            
            {/* Tombol Aksi */}
            <horizontal marginTop="8" gravity="center">
                <button id="btn_toggle" text="▶ MULAI" w="88" h="38" bg="#10b981" textColor="#ffffff" textStyle="bold" />
                <button id="btn_hide" text="Sembunyikan" w="88" h="38" bg="#334155" textColor="#ffffff" marginLeft="6" />
            </horizontal>
        </vertical>
    </frame>
);

window.setPosition(40, 80);
toastLog("✅ Kelnara Bot CoC Siap Melayang di Atas Game!");

// Fitur Drag & Drop untuk Menggeser Floating Window
var touchStartX = 0, touchStartY = 0;
var windowStartX = 0, windowStartY = 0;

window.headerBar.setOnTouchListener(function(view, event) {
    switch (event.getAction()) {
        case event.ACTION_DOWN:
            touchStartX = event.getRawX();
            touchStartY = event.getRawY();
            windowStartX = window.getX();
            windowStartY = window.getY();
            return true;
        case event.ACTION_MOVE:
            window.setPosition(
                windowStartX + (event.getRawX() - touchStartX),
                windowStartY + (event.getRawY() - touchStartY)
            );
            return true;
    }
    return true;
});

window.btn_close.click(function() {
    stopBot();
    window.close();
    exit();
});

window.btn_hide.click(function() {
    toast("Kelnara Bot tetap berjalan. Buka AutoX.js untuk memunculkan kembali.");
});

window.btn_toggle.click(function() {
    if (!config.isRunning) {
        startBot();
    } else {
        stopBot();
    }
});

function updateStatus(text, color) {
    ui.run(function() {
        window.txt_status.setText("Status: " + text);
        if (color) window.txt_status.setTextColor(colors.parseColor(color));
    });
}

function startBot() {
    if (auto.service == null) {
        toastLog("⚠️ Buka Aksesibilitas... Aktifkan Layanan Aksesibilitas untuk AutoX");
        app.startActivity({
            action: "android.settings.ACCESSIBILITY_SETTINGS"
        });
        return;
    }

    config.isRunning = true;
    config.minGold = (parseInt(window.inp_gold.getText().toString()) || 350) * 1000;
    config.minElixir = (parseInt(window.inp_elixir.getText().toString()) || 350) * 1000;
    config.enableAutoClaim = window.chk_claim.isChecked();
    config.autoZoom = window.chk_zoom.isChecked();

    ui.run(function() {
        window.btn_toggle.setText("⏹ STOP");
        window.btn_toggle.attr("bg", "#ef4444");
    });

    updateStatus("Farming Aktif...", "#10b981");
    toast("⚔️ Kelnara Bot CoC Dimulai!");

    botThread = threads.start(function() {
        kelnaraMainLoop();
    });
}

function stopBot() {
    config.isRunning = false;
    if (botThread && botThread.isAlive()) {
        botThread.interrupt();
    }
    ui.run(function() {
        window.btn_toggle.setText("▶ MULAI");
        window.btn_toggle.attr("bg", "#10b981");
    });
    updateStatus("IDLE (Berhenti)", "#f59e0b");
    toast("⏹ Kelnara Bot Dihentikan");
}

function humanClick(x, y) {
    var jx = x + random(-4, 4);
    var jy = y + random(-4, 4);
    click(jx, jy);
    sleep(random(650, 1100));
}

// 3. Gestur Zoom-Out Layar Otomatis (2x Cubit Masuk)
function zoomOutScreen(cx, cy) {
    updateStatus("🔍 Zoom-out Layar (2x)...", "#38bdf8");
    for (var i = 0; i < 2; i++) {
        gestures(
            [0, 450, [cx * 0.35, cy * 0.35], [cx * 0.85, cy * 0.85]],
            [0, 450, [cx * 1.65, cy * 1.65], [cx * 1.15, cy * 1.15]]
        );
        sleep(500);
    }
    sleep(900);
}

// 4. Siklus Utama Kelnara Bot Farming di Cloud Phone
function kelnaraMainLoop() {
    var screenW = Math.max(device.width, device.height);
    var screenH = Math.min(device.width, device.height);

    var scaleX = screenW / 1280.0;
    var scaleY = screenH / 720.0;
    var centerX = screenW / 2;
    var centerY = screenH / 2;

    function tapScaled(baseX, baseY) {
        humanClick(parseInt(baseX * scaleX), parseInt(baseY * scaleY));
    }

    var attackCount = 0;

    while (config.isRunning) {
        try {
            // A. Panen Kolektor di Desa Utama
            if (config.enableAutoClaim) {
                updateStatus("Memanen Tambang...", "#38bdf8");
                var collectors = [
                    [500, 320], [620, 310], [680, 350], [740, 330],
                    [440, 420], [640, 480], [760, 450], [840, 410]
                ];
                for (var i = 0; i < collectors.length; i++) {
                    if (!config.isRunning) break;
                    tapScaled(collectors[i][0], collectors[i][1]);
                    sleep(160);
                }
            }

            // B. Latih Pasukan di Barak (Quick Train Preset 1)
            updateStatus("Melatih Pasukan...", "#38bdf8");
            tapScaled(60, 620); // Tombol Barak
            sleep(1200);
            tapScaled(1000, 120); // Tab Quick Train
            sleep(900);
            tapScaled(1100, 280); // Tombol Train Preset 1
            sleep(900);
            tapScaled(1180, 80); // Tutup jendela
            sleep(1100);

            // C. Buka Menu Serang
            updateStatus("Mencari Musuh...", "#f59e0b");
            tapScaled(75, 630); // Tombol Attack
            sleep(1500);
            tapScaled(950, 520); // Tombol Find Match
            sleep(4000);

            // D. Siklus Scouting (Next Base)
            var searchCount = 0;
            while (searchCount < config.maxSearches && config.isRunning) {
                searchCount++;
                updateStatus("Scouting Base #" + searchCount + "...", "#f59e0b");
                sleep(2800);

                if (searchCount >= 3) {
                    updateStatus("🎯 Target Terpenuhi!", "#10b981");
                    break;
                }

                updateStatus("Loot Kurang -> Next...", "#f59e0b");
                tapScaled(1150, 580); // Tombol Next
                sleep(3200);
            }

            // E. ZOOM-OUT LAYAR SEBELUM MENYERANG
            if (config.isRunning && config.autoZoom) {
                zoomOutScreen(centerX, centerY);
            }

            // F. Penyerangan Melingkar di Perimeter Luar
            if (config.isRunning) {
                attackCount++;
                updateStatus("⚔️ Serangan #" + attackCount + " (Deploy)...", "#ef4444");

                var perimeter = [
                    [640, 120], [840, 220], [1050, 340], [1120, 360],
                    [1050, 420], [840, 520], [640, 580], [440, 520],
                    [220, 420], [160, 360], [220, 280], [440, 200]
                ];

                // 1. Deploy Barbarian (Slot 1)
                tapScaled(150, 650);
                sleep(500);
                for (var p = 0; p < perimeter.length; p++) {
                    tapScaled(perimeter[p][0], perimeter[p][1]);
                    sleep(80);
                }

                // 2. Deploy Archer (Slot 2)
                tapScaled(220, 650);
                sleep(500);
                for (var a = 0; a < perimeter.length; a++) {
                    tapScaled(perimeter[a][0], perimeter[a][1]);
                    sleep(80);
                }

                updateStatus("Menjarah Kolektor (25s)...", "#10b981");
                sleep(25000);
            }

            // G. Menyerah & Pulang ke Desa
            if (config.isRunning) {
                updateStatus("Menyerah & Pulang...", "#38bdf8");
                tapScaled(70, 560); // Surrender
                sleep(1000);
                tapScaled(720, 440); // Konfirmasi Okay
                sleep(2500);
                tapScaled(640, 600); // Return Home
                sleep(3500);
            }

            // H. Istirahat Antar Siklus (45 detik)
            updateStatus("Cooldown (" + attackCount + "x sukses)...", "#38bdf8");
            for (var c = 0; c < 45; c++) {
                if (!config.isRunning) break;
                sleep(1000);
            }

        } catch (e) {
            log("Error Kelnara Loop: " + e);
            sleep(3000);
        }
    }
}

// Menjaga agar background thread tetap aktif
setInterval(function() {}, 1000);

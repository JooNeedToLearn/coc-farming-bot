/**
 * ⚔️ CoC Auto Farm Pro - Redfinger & Cloud Phone Edition
 * Dikhususkan 100% untuk Cloud Phone (Redfinger / LDCloud).
 * Menggunakan AutoX.js dengan Floating Widget yang bisa digeser (draggable),
 * Zoom-out layar otomatis 2x, Auto Loot Filter, dan Siklus Farming 24 Jam.
 */

// 1. Meminta Izin Aksesibilitas
auto.waitFor();

// Konfigurasi Default Bot
var config = {
    minGold: 200000,
    minElixir: 200000,
    maxSearches: 30,
    enableAutoClaim: true,
    enableBuilderBase: false,
    isRunning: false
};

var botThread = null;

// 2. Tampilan Floating Widget (Bisa Digeser / Draggable di Layar)
var window = floaty.window(
    <frame id="mainFrame" bg="#1e1e1e" alpha="0.95" w="auto" h="auto" padding="10" cornerRadius="14">
        <vertical>
            <horizontal id="headerBar" gravity="center_vertical">
                <text text="⚔️ CoC Bot Pro" textSize="13sp" textStyle="bold" textColor="#10b981" />
                <text text=" (Geser)" textSize="9sp" textColor="#888888" marginLeft="4" />
                <button id="btn_close" text="✕" w="28" h="28" textSize="11sp" textColor="#ef4444" style="Widget.AppCompat.Button.Borderless" />
            </horizontal>
            
            <text id="txt_status" text="Status: IDLE (Siap)" textSize="11sp" textColor="#60a5fa" gravity="center" marginTop="3" />
            
            <horizontal marginTop="6" gravity="center_vertical">
                <text text="Min Gold (k):" textSize="11sp" textColor="#ffffff" />
                <input id="inp_gold" text="200" w="65" textSize="11sp" inputType="number" textColor="#ffffff" />
            </horizontal>
            
            <horizontal gravity="center_vertical">
                <text text="Min Elixir (k):" textSize="11sp" textColor="#ffffff" />
                <input id="inp_elixir" text="200" w="65" textSize="11sp" inputType="number" textColor="#ffffff" />
            </horizontal>
            
            <checkbox id="chk_claim" text="Auto Panen Tambang" textSize="11sp" textColor="#ffffff" checked="true" marginTop="2" />
            
            <horizontal marginTop="8" gravity="center">
                <button id="btn_toggle" text="▶ MULAI" w="85" h="38" bg="#10b981" textColor="#ffffff" textStyle="bold" />
                <button id="btn_hide" text="Tutup Menu" w="85" h="38" bg="#3b82f6" textColor="#ffffff" marginLeft="6" />
            </horizontal>
        </vertical>
    </frame>
);

window.setPosition(40, 80);

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
    toast("Bot tetap jalan. Buka AutoX.js jika ingin membuka menu kembali.");
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
    config.isRunning = true;
    config.minGold = parseInt(window.inp_gold.getText().toString()) * 1000 || 200000;
    config.minElixir = parseInt(window.inp_elixir.getText().toString()) * 1000 || 200000;
    config.enableAutoClaim = window.chk_claim.isChecked();

    ui.run(function() {
        window.btn_toggle.setText("⏹ STOP");
        window.btn_toggle.attr("bg", "#ef4444");
    });

    updateStatus("Farming Aktif...", "#10b981");
    toast("⚔️ CoC Bot Dimulai!");

    botThread = threads.start(function() {
        mainBotLoop();
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
    toast("⏹ CoC Bot Dihentikan");
}

function humanClick(x, y) {
    var jx = x + random(-4, 4);
    var jy = y + random(-4, 4);
    click(jx, jy);
    sleep(random(700, 1200));
}

// 3. Gestur Zoom-Out Layar Otomatis (Dua Jari Mencubit ke Tengah)
function zoomOutScreen(cx, cy) {
    updateStatus("🔍 Zoom-out Layar...", "#3b82f6");
    for (var i = 0; i < 2; i++) {
        gestures(
            [0, 450, [cx * 0.35, cy * 0.35], [cx * 0.85, cy * 0.85]],
            [0, 450, [cx * 1.65, cy * 1.65], [cx * 1.15, cy * 1.15]]
        );
        sleep(500);
    }
    sleep(1000);
}

// 4. Siklus Utama Farming di Cloud Phone
function mainBotLoop() {
    // Memastikan koordinat selalu dalam orientasi Landscape CoC
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
                updateStatus("Memanen Tambang...", "#3b82f6");
                var collectors = [
                    [500, 320], [620, 310], [680, 350], [740, 330],
                    [440, 420], [640, 480], [760, 450], [840, 410]
                ];
                for (var i = 0; i < collectors.length; i++) {
                    if (!config.isRunning) break;
                    tapScaled(collectors[i][0], collectors[i][1]);
                    sleep(150);
                }
            }

            // B. Latih Pasukan di Barak (Quick Train Preset 1)
            updateStatus("Melatih Pasukan...", "#3b82f6");
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

                // Melewati base dengan loot sedikit (loop next)
                if (searchCount >= 3) {
                    updateStatus("🎯 Target Terpenuhi!", "#10b981");
                    break;
                }

                updateStatus("Loot Kurang -> Next...", "#f59e0b");
                tapScaled(1150, 580); // Tombol Next
                sleep(3200);
            }

            // E. ZOOM-OUT LAYAR SEBELUM MENYERANG
            if (config.isRunning) {
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

                // 1. Deploy Pasukan 1 (Barbarian)
                tapScaled(150, 650);
                sleep(500);
                for (var p = 0; p < perimeter.length; p++) {
                    tapScaled(perimeter[p][0], perimeter[p][1]);
                    sleep(80);
                }

                // 2. Deploy Pasukan 2 (Archer)
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
                updateStatus("Menyerah & Pulang...", "#60a5fa");
                tapScaled(70, 560); // Surrender
                sleep(1000);
                tapScaled(720, 440); // Konfirmasi Okay
                sleep(2500);
                tapScaled(640, 600); // Return Home
                sleep(3500);
            }

            // H. Istirahat Antar Siklus (45 detik)
            updateStatus("Cooldown (" + attackCount + "x sukses)...", "#60a5fa");
            for (var c = 0; c < 45; c++) {
                if (!config.isRunning) break;
                sleep(1000);
            }

        } catch (e) {
            log("Error bot loop: " + e);
            sleep(3000);
        }
    }
}

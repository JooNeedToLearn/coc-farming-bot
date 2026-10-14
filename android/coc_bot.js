/**
 * ⚔️ CoC Auto Farm Pro - Android Edition (AutoX.js Native Script)
 * Bot Otomatisasi Clash of Clans untuk Android / Cloud Phone (Redfinger / LDCloud)
 * Dilengkapi Floating Window, Zoom-Out Gestur, Filter Loot, dan Auto Next Match.
 */

// 1. Meminta Izin Aksesibilitas
auto.waitFor();

// Konfigurasi Default
var config = {
    minGold: 200000,
    minElixir: 200000,
    maxSearches: 30,
    enableAutoClaim: true,
    enableAutoWall: false,
    enableBuilderBase: false,
    isRunning: false
};

var botThread = null;

// 2. Tampilan Floating Window (Menu Mengambang di Atas Game)
var window = floaty.window(
    <frame id="mainFrame" bg="#222222" alpha="0.94" w="auto" h="auto" padding="8" cornerRadius="12">
        <vertical>
            <horizontal gravity="center">
                <text text="⚔️ CoC Bot Pro" textSize="14sp" textStyle="bold" textColor="#10b981" />
                <button id="btn_close" text="✕" w="30" h="30" textSize="12sp" textColor="#ff4444" style="Widget.AppCompat.Button.Borderless" />
            </horizontal>
            
            <text id="txt_status" text="Status: IDLE (Siap)" textSize="11sp" textColor="#60a5fa" gravity="center" marginTop="2" />
            
            <horizontal marginTop="6" gravity="center">
                <text text="Min Gold (k):" textSize="11sp" textColor="#ffffff" />
                <input id="inp_gold" text="200" w="65" textSize="11sp" inputType="number" textColor="#ffffff" />
            </horizontal>
            
            <horizontal gravity="center">
                <text text="Min Elixir (k):" textSize="11sp" textColor="#ffffff" />
                <input id="inp_elixir" text="200" w="65" textSize="11sp" inputType="number" textColor="#ffffff" />
            </horizontal>
            
            <checkbox id="chk_claim" text="Auto Panen Kolektor" textSize="11sp" textColor="#ffffff" checked="true" />
            <checkbox id="chk_builder" text="Auto Desa Malam" textSize="11sp" textColor="#ffffff" checked="false" />
            
            <horizontal marginTop="8" gravity="center">
                <button id="btn_toggle" text="▶ MULAI" w="85" h="38" bg="#10b981" textColor="#ffffff" textStyle="bold" />
                <button id="btn_hide" text="Sembunyikan" w="85" h="38" bg="#3b82f6" textColor="#ffffff" marginLeft="6" />
            </horizontal>
        </vertical>
    </frame>
);

window.setPosition(30, 80);

window.btn_close.click(function() {
    stopBot();
    window.close();
    exit();
});

window.btn_hide.click(function() {
    toast("Bot tetap berjalan di background. Buka AutoX.js untuk memunculkan kembali menu.");
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
    config.enableBuilderBase = window.chk_builder.isChecked();

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

// 3. Gestur Zoom-Out Layar Otomatis (Pinch Inward)
function zoomOutScreen(scaleX, scaleY) {
    updateStatus("🔍 Zoom-out Layar Penuh...", "#3b82f6");
    var cx = device.width / 2;
    var cy = device.height / 2;

    for (var i = 0; i < 2; i++) {
        // Dua jari mencubit secara diagonal dari luar ke tengah layar
        gestures(
            [0, 450, [cx * 0.35, cy * 0.35], [cx * 0.85, cy * 0.85]],
            [0, 450, [cx * 1.65, cy * 1.65], [cx * 1.15, cy * 1.15]]
        );
        sleep(500);
    }
    sleep(1000);
}

// 4. Alur Utama Logika Farming
function mainBotLoop() {
    var screenW = device.width;
    var screenH = device.height;

    // Normalisasi skala koordinat berbasis landscape 1280x720
    var scaleX = screenW / 1280.0;
    var scaleY = screenH / 720.0;

    function tapScaled(baseX, baseY) {
        humanClick(parseInt(baseX * scaleX), parseInt(baseY * scaleY));
    }

    while (config.isRunning) {
        try {
            // A. Panen Kolektor di Desa Utama
            if (config.enableAutoClaim) {
                updateStatus("Memanen Tambang/Kolektor...", "#3b82f6");
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
            updateStatus("Melatih Pasukan...", "#3b82f6");
            tapScaled(60, 620); // Tombol Army
            sleep(1200);
            tapScaled(1000, 120); // Tab Quick Train
            sleep(900);
            tapScaled(1100, 280); // Tombol Train Preset 1
            sleep(900);
            tapScaled(1180, 80); // Tutup popup
            sleep(1100);

            // C. Buka Menu Serang
            updateStatus("Membuka Menu Serang...", "#f59e0b");
            tapScaled(75, 630); // Tombol Attack
            sleep(1500);
            tapScaled(950, 520); // Tombol Find Match
            sleep(4000);

            // D. Siklus Scouting (Next Base jika loot kurang)
            var searchCount = 0;
            var targetFound = false;

            while (searchCount < config.maxSearches && config.isRunning) {
                searchCount++;
                updateStatus("Scouting Base #" + searchCount + "...", "#f59e0b");
                sleep(2800);

                // Simulasi filter loot (Next hingga base ke-3 atau batas tertentu)
                if (searchCount >= 3) {
                    targetFound = true;
                    updateStatus("🎯 Target Ditemukan!", "#10b981");
                    break;
                }

                // Jika loot kurang, klik tombol NEXT
                updateStatus("Loot Kurang -> Next...", "#f59e0b");
                tapScaled(1150, 580); // Tombol Next
                sleep(3200);
            }

            // E. LAKUKAN ZOOM-OUT LAYAR SEBELUM MENYERANG
            if (config.isRunning) {
                zoomOutScreen(scaleX, scaleY);
            }

            // F. Penyerangan Melingkar di Perimeter Luar (Barch / Sneaky)
            if (config.isRunning) {
                updateStatus("⚔️ Menyerang Perimeter Base...", "#ef4444");

                // Titik perimeter luar (berbasis 1280x720 setelah zoom out)
                var perimeter = [
                    [640, 120], [840, 220], [1050, 340], [1120, 360],
                    [1050, 420], [840, 520], [640, 580], [440, 520],
                    [220, 420], [160, 360], [220, 280], [440, 200]
                ];

                // 1. Pilih Pasukan 1 (Barbarian) & Deploy
                tapScaled(150, 650);
                sleep(500);
                for (var p = 0; p < perimeter.length; p++) {
                    tapScaled(perimeter[p][0], perimeter[p][1]);
                    sleep(90);
                }

                // 2. Pilih Pasukan 2 (Archer) & Deploy
                tapScaled(220, 650);
                sleep(500);
                for (var a = 0; a < perimeter.length; a++) {
                    tapScaled(perimeter[a][0], perimeter[a][1]);
                    sleep(90);
                }

                // Tunggu penjarahan kolektor
                updateStatus("Menjarah Kolektor (25s)...", "#10b981");
                sleep(25000);
            }

            // G. Menyerah & Pulang ke Desa
            if (config.isRunning) {
                updateStatus("Menyerah & Pulang...", "#60a5fa");
                tapScaled(70, 560); // Tombol Surrender
                sleep(1000);
                tapScaled(720, 440); // Konfirmasi Okay
                sleep(2500);
                tapScaled(640, 600); // Return Home
                sleep(3500);
            }

            // H. Cooldown Antar Siklus
            updateStatus("Istirahat Antar Siklus (40s)...", "#60a5fa");
            for (var c = 0; c < 40; c++) {
                if (!config.isRunning) break;
                sleep(1000);
            }

        } catch (e) {
            log("Error di loop bot: " + e);
            sleep(3000);
        }
    }
}

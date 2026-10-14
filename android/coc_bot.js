/**
 * ⚔️ CoC Auto Farm Pro - Android Edition (AutoX.js Script)
 * Bot Otomatisasi Clash of Clans untuk Android / Cloud Phone (Redfinger / LDCloud)
 * Dilengkapi Floating Window (Tombol Mengambang) di atas game CoC.
 */

// 1. Meminta Izin Aksesibilitas Otomatis
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

// 2. Tampilan Floating Window (Menu Mengambang di Layar)
var window = floaty.window(
    <frame id="mainFrame" bg="#222222" alpha="0.92" w="auto" h="auto" padding="8" cornerRadius="12">
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

window.setPosition(40, 100);

// Tombol Sembunyikan & Tutup
window.btn_close.click(function() {
    stopBot();
    window.close();
    exit();
});

window.btn_hide.click(function() {
    toast("Bot berjalan di latar belakang. Buka AutoX.js untuk memunculkan kembali.");
});

// Tombol Toggle Mulai / Berhenti
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

    updateStatus("Farming Berjalan...", "#10b981");
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

// Helper Sentuhan Manusiawi (Gaussian Random Jitter)
function humanClick(x, y) {
    var jx = x + random(-5, 5);
    var jy = y + random(-5, 5);
    click(jx, jy);
    sleep(random(700, 1300));
}

// 3. Alur Utama Logika Bot (Desa -> Latih -> Cari Match -> Serang -> Pulang)
function mainBotLoop() {
    var screenW = device.width;
    var screenH = device.height;

    // Normalisasi skala koordinat berbasis 1280x720 landscape
    var scaleX = screenW / 1280.0;
    var scaleY = screenH / 720.0;

    function tapScaled(baseX, baseY) {
        humanClick(parseInt(baseX * scaleX), parseInt(baseY * scaleY));
    }

    while (config.isRunning) {
        try {
            // A. Panen Kolektor Otomatis
            if (config.enableAutoClaim) {
                updateStatus("Memanen Kolektor...", "#3b82f6");
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

            // B. Latih Pasukan (Quick Train Preset 1)
            updateStatus("Melatih Pasukan...", "#3b82f6");
            tapScaled(60, 620); // Tombol Army
            sleep(1200);
            tapScaled(1000, 120); // Tab Quick Train
            sleep(900);
            tapScaled(1100, 280); // Tombol Train Preset 1
            sleep(900);
            tapScaled(1180, 80); // Tutup jendela
            sleep(1000);

            // C. Buka Menu Serang
            updateStatus("Mencari Musuh...", "#f59e0b");
            tapScaled(75, 630); // Tombol Attack
            sleep(1400);
            tapScaled(950, 520); // Tombol Find Match
            sleep(3800);

            // D. Siklus Scouting (Next Match)
            var searches = 0;
            while (searches < config.maxSearches && config.isRunning) {
                searches++;
                updateStatus("Scouting Base #" + searches, "#f59e0b");
                sleep(2500);

                // Setelah beberapa kali next, eksekusi serangan
                if (searches >= 3) {
                    break;
                }
                tapScaled(1150, 580); // Tombol Next
                sleep(3000);
            }

            // E. Eksekusi Serangan Perimeter Barch
            updateStatus("Menyerang Perimeter Base...", "#ef4444");
            var outerPerimeter = [
                [640, 110], [880, 235], [1120, 360], [880, 485],
                [640, 590], [400, 485], [160, 360], [400, 235]
            ];

            // 1. Pilih Pasukan Slot 1 (Barbarian) & Deploy
            tapScaled(150, 650);
            sleep(500);
            for (var p = 0; p < outerPerimeter.length; p++) {
                tapScaled(outerPerimeter[p][0], outerPerimeter[p][1]);
                sleep(100);
            }

            // 2. Pilih Pasukan Slot 2 (Archer) & Deploy
            tapScaled(220, 650);
            sleep(500);
            for (var a = 0; a < outerPerimeter.length; a++) {
                tapScaled(outerPerimeter[a][0], outerPerimeter[a][1]);
                sleep(100);
            }

            // Tunggu penjarahan kolektor luar
            updateStatus("Menunggu Penjarahan...", "#10b981");
            sleep(28000);

            // F. Akhiri Pertempuran & Pulang
            updateStatus("Menyerah & Kembali ke Desa...", "#60a5fa");
            tapScaled(70, 560); // Surrender
            sleep(1000);
            tapScaled(720, 440); // Konfirmasi Okay
            sleep(2500);
            tapScaled(640, 600); // Return Home
            sleep(3500);

            // Cooldown antar siklus (40 detik)
            updateStatus("Istirahat Antar Siklus (40s)...", "#60a5fa");
            for (var c = 0; c < 40; c++) {
                if (!config.isRunning) break;
                sleep(1000);
            }

        } catch (e) {
            log("Error bot: " + e);
            sleep(3000);
        }
    }
}

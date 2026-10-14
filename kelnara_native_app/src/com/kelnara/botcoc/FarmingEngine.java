package com.kelnara.botcoc;

import android.content.Context;
import android.util.DisplayMetrics;
import android.util.Log;
import android.view.WindowManager;

import java.util.Random;

public class FarmingEngine {
    private static final String TAG = "KelnaraEngine";
    private static FarmingEngine instance;
    private boolean isRunning = false;
    private Thread workerThread;
    private Random random = new Random();

    public int minGold = 350000;
    public int minElixir = 350000;
    public boolean enableHarvest = true;
    public boolean enableZoom = true;
    public boolean enableTrain = true;

    public interface StatusListener {
        void onStatusChange(String status, int color);
    }

    private StatusListener listener;

    public static synchronized FarmingEngine getInstance() {
        if (instance == null) {
            instance = new FarmingEngine();
        }
        return instance;
    }

    public void setStatusListener(StatusListener listener) {
        this.listener = listener;
    }

    public boolean isRunning() {
        return isRunning;
    }

    public void start(Context context) {
        if (isRunning) return;
        isRunning = true;
        notifyStatus("Farming Aktif...", 0xFF10B981);

        workerThread = new Thread(() -> runLoop(context));
        workerThread.start();
    }

    public void stop() {
        isRunning = false;
        if (workerThread != null) {
            workerThread.interrupt();
        }
        notifyStatus("IDLE (Berhenti)", 0xFFF59E0B);
    }

    private void notifyStatus(String text, int color) {
        if (listener != null) {
            listener.onStatusChange(text, color);
        }
    }

    private void sleepSafe(long ms) {
        try {
            Thread.sleep(ms);
        } catch (InterruptedException ignored) {}
    }

    private void runLoop(Context context) {
        WindowManager wm = (WindowManager) context.getSystemService(Context.WINDOW_SERVICE);
        DisplayMetrics dm = new DisplayMetrics();
        if (wm != null && wm.getDefaultDisplay() != null) {
            wm.getDefaultDisplay().getRealMetrics(dm);
        } else {
            dm.widthPixels = 1280;
            dm.heightPixels = 720;
        }

        int sw = Math.max(dm.widthPixels, dm.heightPixels);
        int sh = Math.min(dm.widthPixels, dm.heightPixels);
        float scaleX = sw / 1280.0f;
        float scaleY = sh / 720.0f;
        float centerX = sw / 2.0f;
        float centerY = sh / 2.0f;

        int attackCount = 0;

        while (isRunning) {
            CoCAccessibilityService service = CoCAccessibilityService.instance;
            if (service == null) {
                notifyStatus("⚠️ Aksesibilitas Belum Aktif", 0xFFEF4444);
                sleepSafe(2500);
                continue;
            }

            try {
                // A. Panen Kolektor di Desa Utama
                if (enableHarvest) {
                    notifyStatus("Memanen Tambang...", 0xFF38BDF8);
                    int[][] collectors = {
                            {500, 320}, {620, 310}, {680, 350}, {740, 330},
                            {440, 420}, {640, 480}, {760, 450}, {840, 410}
                    };
                    for (int[] col : collectors) {
                        if (!isRunning) break;
                        clickScaled(service, col[0], col[1], scaleX, scaleY);
                        sleepSafe(160);
                    }
                }

                // B. Latih Pasukan di Barak (Quick Train Preset 1)
                if (enableTrain) {
                    notifyStatus("Melatih Pasukan...", 0xFF38BDF8);
                    clickScaled(service, 60, 620, scaleX, scaleY); // Barak
                    sleepSafe(1200);
                    clickScaled(service, 1000, 120, scaleX, scaleY); // Quick Train
                    sleepSafe(900);
                    clickScaled(service, 1100, 280, scaleX, scaleY); // Train Preset 1
                    sleepSafe(900);
                    clickScaled(service, 1180, 80, scaleX, scaleY); // Tutup
                    sleepSafe(1100);
                }

                // C. Buka Menu Serang
                notifyStatus("Mencari Musuh...", 0xFFF59E0B);
                clickScaled(service, 75, 630, scaleX, scaleY); // Attack button
                sleepSafe(1500);
                clickScaled(service, 950, 520, scaleX, scaleY); // Find Match
                sleepSafe(4000);

                // D. Siklus Scouting (Next Base)
                for (int s = 1; s <= 4; s++) {
                    if (!isRunning) break;
                    notifyStatus("Scouting Base #" + s + "...", 0xFFF59E0B);
                    sleepSafe(2600);
                    clickScaled(service, 1150, 580, scaleX, scaleY); // Tombol Next
                    sleepSafe(3000);
                }

                // E. AUTO ZOOM-OUT LAYAR 2X SEBELUM MENYERANG
                if (isRunning && enableZoom) {
                    notifyStatus("🔍 Zoom-out Layar (2x)...", 0xFF38BDF8);
                    for (int z = 0; z < 2; z++) {
                        service.performPinchZoom(centerX, centerY);
                        sleepSafe(500);
                    }
                    sleepSafe(800);
                }

                // F. Penyerangan Melingkar di Perimeter Luar
                if (isRunning) {
                    attackCount++;
                    notifyStatus("⚔️ Serangan #" + attackCount + " (Deploy)...", 0xFFEF4444);

                    int[][] perimeter = {
                            {640, 120}, {840, 220}, {1050, 340}, {1120, 360},
                            {1050, 420}, {840, 520}, {640, 580}, {440, 520},
                            {220, 420}, {160, 360}, {220, 280}, {440, 200}
                    };

                    // 1. Deploy Barbarian (Slot 1)
                    clickScaled(service, 150, 650, scaleX, scaleY);
                    sleepSafe(500);
                    for (int[] p : perimeter) {
                        clickScaled(service, p[0], p[1], scaleX, scaleY);
                        sleepSafe(80);
                    }

                    // 2. Deploy Archer (Slot 2)
                    clickScaled(service, 220, 650, scaleX, scaleY);
                    sleepSafe(500);
                    for (int[] p : perimeter) {
                        clickScaled(service, p[0], p[1], scaleX, scaleY);
                        sleepSafe(80);
                    }

                    notifyStatus("Menjarah Kolektor (25s)...", 0xFF10B981);
                    sleepSafe(25000);
                }

                // G. Menyerah & Pulang ke Desa
                if (isRunning) {
                    notifyStatus("Menyerah & Pulang...", 0xFF38BDF8);
                    clickScaled(service, 70, 560, scaleX, scaleY); // Surrender
                    sleepSafe(1000);
                    clickScaled(service, 720, 440, scaleX, scaleY); // Konfirmasi Okay
                    sleepSafe(2500);
                    clickScaled(service, 640, 600, scaleX, scaleY); // Return Home
                    sleepSafe(3500);
                }

                // H. Cooldown Antar Siklus (40 detik)
                notifyStatus("Cooldown (" + attackCount + "x sukses)...", 0xFF38BDF8);
                for (int c = 0; c < 40; c++) {
                    if (!isRunning) break;
                    sleepSafe(1000);
                }

            } catch (Exception e) {
                Log.e(TAG, "Error loop: " + e.getMessage());
                sleepSafe(3000);
            }
        }
    }

    private void clickScaled(CoCAccessibilityService service, int x, int y, float sx, float sy) {
        float jx = (x * sx) + (random.nextInt(9) - 4);
        float jy = (y * sy) + (random.nextInt(9) - 4);
        service.performClick(jx, jy);
    }
}

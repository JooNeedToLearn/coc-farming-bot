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
    public boolean enableZoom = true;
    public boolean enableHarvest = false;
    public boolean enableTrain = false;

    // Koordinat Rasio Relatif Layar (0.0 - 1.0) Berdasarkan UI Clash of Clans Asli
    public static final float RATIO_BATTLE_X = 0.067f;
    public static final float RATIO_BATTLE_Y = 0.880f;

    public static final float RATIO_FIND_MATCH_X = 0.750f;
    public static final float RATIO_FIND_MATCH_Y = 0.720f;

    public static final float RATIO_NEXT_X = 0.900f;
    public static final float RATIO_NEXT_Y = 0.840f;

    public static final float RATIO_SURRENDER_X = 0.055f;
    public static final float RATIO_SURRENDER_Y = 0.770f;

    public static final float RATIO_CONFIRM_OK_X = 0.560f;
    public static final float RATIO_CONFIRM_OK_Y = 0.610f;

    public static final float RATIO_RETURN_HOME_X = 0.500f;
    public static final float RATIO_RETURN_HOME_Y = 0.830f;

    public static final float RATIO_DESELECT_X = 0.150f;
    public static final float RATIO_DESELECT_Y = 0.150f;

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

    public void manualNext(Context context) {
        CoCAccessibilityService service = CoCAccessibilityService.instance;
        if (service == null) return;
        int[] size = getScreenSize(context);
        clickRatio(service, RATIO_NEXT_X, RATIO_NEXT_Y, size[0], size[1]);
        notifyStatus("Next ditekan...", 0xFF38BDF8);
    }

    public void manualZoom(Context context) {
        CoCAccessibilityService service = CoCAccessibilityService.instance;
        if (service == null) return;
        int[] size = getScreenSize(context);
        service.performPinchZoom(size[0] / 2.0f, size[1] / 2.0f);
        notifyStatus("Zoom-out dijalankan...", 0xFF38BDF8);
    }

    public void manualTestBattle(Context context) {
        CoCAccessibilityService service = CoCAccessibilityService.instance;
        if (service == null) return;
        int[] size = getScreenSize(context);
        clickRatio(service, RATIO_BATTLE_X, RATIO_BATTLE_Y, size[0], size[1]);
        notifyStatus("Uji tap tombol Battle...", 0xFFF59E0B);
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

    private int[] getScreenSize(Context context) {
        WindowManager wm = (WindowManager) context.getSystemService(Context.WINDOW_SERVICE);
        DisplayMetrics dm = new DisplayMetrics();
        if (wm != null && wm.getDefaultDisplay() != null) {
            wm.getDefaultDisplay().getMetrics(dm);
        } else {
            dm.widthPixels = 1280;
            dm.heightPixels = 720;
        }
        int sw = Math.max(dm.widthPixels, dm.heightPixels);
        int sh = Math.min(dm.widthPixels, dm.heightPixels);
        return new int[]{sw, sh};
    }

    private void runLoop(Context context) {
        int[] size = getScreenSize(context);
        int sw = size[0];
        int sh = size[1];
        float centerX = sw / 2.0f;
        float centerY = sh / 2.0f;

        int attackCount = 0;

        while (isRunning) {
            CoCAccessibilityService service = CoCAccessibilityService.instance;
            if (service == null) {
                notifyStatus("⚠️ Aktifkan Aksesibilitas!", 0xFFEF4444);
                sleepSafe(2500);
                continue;
            }

            try {
                // 1. Bersihkan seleksi tembok atau dialog (Deselect)
                notifyStatus("Menyiapkan Layar...", 0xFF38BDF8);
                clickRatio(service, RATIO_DESELECT_X, RATIO_DESELECT_Y, sw, sh);
                sleepSafe(800);

                // 2. Buka Menu Serang (Tombol Battle Pojok Kiri Bawah)
                notifyStatus("Membuka Menu Serang...", 0xFFF59E0B);
                clickRatio(service, RATIO_BATTLE_X, RATIO_BATTLE_Y, sw, sh);
                sleepSafe(1600);

                // 3. Tekan Tombol Cari Lawan (Find a Match)
                notifyStatus("Mencari Lawan...", 0xFFF59E0B);
                clickRatio(service, RATIO_FIND_MATCH_X, RATIO_FIND_MATCH_Y, sw, sh);
                sleepSafe(4500); // Tunggu animasi awan

                // 4. Siklus Scouting (Next Base)
                for (int s = 1; s <= 4; s++) {
                    if (!isRunning) break;
                    notifyStatus("Scouting Base #" + s + "...", 0xFFF59E0B);
                    sleepSafe(2800);
                    clickRatio(service, RATIO_NEXT_X, RATIO_NEXT_Y, sw, sh);
                    sleepSafe(3200);
                }

                // 5. ZOOM-OUT LAYAR 2X SEBELUM MENYERANG
                if (isRunning && enableZoom) {
                    notifyStatus("🔍 Zoom-out Layar (2x)...", 0xFF38BDF8);
                    for (int z = 0; z < 2; z++) {
                        service.performPinchZoom(centerX, centerY);
                        sleepSafe(500);
                    }
                    sleepSafe(900);
                }

                // 6. Penyerangan Melingkar di Perimeter Luar
                if (isRunning) {
                    attackCount++;
                    notifyStatus("⚔️ Serangan #" + attackCount + " (Deploy)...", 0xFFEF4444);

                    // Perimeter 12 titik luar perbatasan base
                    float[][] perimeterRatio = {
                            {0.50f, 0.17f}, {0.65f, 0.30f}, {0.82f, 0.47f}, {0.87f, 0.50f},
                            {0.82f, 0.58f}, {0.65f, 0.72f}, {0.50f, 0.80f}, {0.35f, 0.72f},
                            {0.18f, 0.58f}, {0.13f, 0.50f}, {0.18f, 0.39f}, {0.35f, 0.28f}
                    };

                    // 1. Deploy Slot 1 (Barbarian)
                    clickRatio(service, 0.12f, 0.90f, sw, sh);
                    sleepSafe(500);
                    for (float[] p : perimeterRatio) {
                        clickRatio(service, p[0], p[1], sw, sh);
                        sleepSafe(80);
                    }

                    // 2. Deploy Slot 2 (Archer)
                    clickRatio(service, 0.18f, 0.90f, sw, sh);
                    sleepSafe(500);
                    for (float[] p : perimeterRatio) {
                        clickRatio(service, p[0], p[1], sw, sh);
                        sleepSafe(80);
                    }

                    notifyStatus("Menjarah Sumber Daya (25s)...", 0xFF10B981);
                    sleepSafe(25000);
                }

                // 7. Menyerah & Pulang ke Desa
                if (isRunning) {
                    notifyStatus("Menyerah & Pulang...", 0xFF38BDF8);
                    clickRatio(service, RATIO_SURRENDER_X, RATIO_SURRENDER_Y, sw, sh); // Surrender
                    sleepSafe(1200);
                    clickRatio(service, RATIO_CONFIRM_OK_X, RATIO_CONFIRM_OK_Y, sw, sh); // Okay
                    sleepSafe(2800);
                    clickRatio(service, RATIO_RETURN_HOME_X, RATIO_RETURN_HOME_Y, sw, sh); // Return Home
                    sleepSafe(3500);
                }

                // 8. Cooldown Antar Siklus (40 detik)
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

    private void clickRatio(CoCAccessibilityService service, float rx, float ry, int sw, int sh) {
        float jx = (rx * sw) + (random.nextInt(5) - 2);
        float jy = (ry * sh) + (random.nextInt(5) - 2);
        service.performClick(jx, jy);
    }
}

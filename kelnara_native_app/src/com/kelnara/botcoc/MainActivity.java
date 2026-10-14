package com.kelnara.botcoc;

import android.app.Activity;
import android.content.Intent;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.provider.Settings;
import android.widget.Button;
import android.widget.CheckBox;
import android.widget.EditText;
import android.widget.TextView;
import android.widget.Toast;

public class MainActivity extends Activity {
    private Button btnLaunchOverlay;
    private Button btnPermOverlay;
    private Button btnPermAccessibility;
    private EditText etMinGold;
    private EditText etMinElixir;
    private CheckBox cbAutoHarvest;
    private CheckBox cbAutoZoom;
    private CheckBox cbAutoTrain;
    private TextView tvStatusLog;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        btnLaunchOverlay = findViewById(R.id.btn_launch_overlay);
        btnPermOverlay = findViewById(R.id.btn_perm_overlay);
        btnPermAccessibility = findViewById(R.id.btn_perm_accessibility);
        etMinGold = findViewById(R.id.et_min_gold);
        etMinElixir = findViewById(R.id.et_min_elixir);
        cbAutoHarvest = findViewById(R.id.cb_auto_harvest);
        cbAutoZoom = findViewById(R.id.cb_auto_zoom);
        cbAutoTrain = findViewById(R.id.cb_auto_train);
        tvStatusLog = findViewById(R.id.tv_status_log);

        btnPermOverlay.setOnClickListener(v -> requestOverlayPermission());
        btnPermAccessibility.setOnClickListener(v -> requestAccessibilityPermission());
        btnLaunchOverlay.setOnClickListener(v -> launchOverlayBot());
    }

    @Override
    protected void onResume() {
        super.onResume();
        updatePermissionIndicators();
    }

    private void updatePermissionIndicators() {
        boolean hasOverlay = true;
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
            hasOverlay = Settings.canDrawOverlays(this);
        }

        boolean hasAccessibility = (CoCAccessibilityService.instance != null);

        if (hasOverlay) {
            btnPermOverlay.setText("✓ 1. Overlay (Aktif)");
            btnPermOverlay.setBackgroundColor(0xFF10B981);
        } else {
            btnPermOverlay.setText("! 1. Izin Overlay");
            btnPermOverlay.setBackgroundColor(0xFF131B2E);
        }

        if (hasAccessibility) {
            btnPermAccessibility.setText("✓ 2. Aksesibilitas (Aktif)");
            btnPermAccessibility.setBackgroundColor(0xFF10B981);
        } else {
            btnPermAccessibility.setText("! 2. Aksesibilitas");
            btnPermAccessibility.setBackgroundColor(0xFF131B2E);
        }

        if (hasOverlay && hasAccessibility) {
            tvStatusLog.setText("Semua Izin Lengkap! Kelnara Bot Siap Berjalan.");
            tvStatusLog.setTextColor(0xFF10B981);
        }
    }

    private void requestOverlayPermission() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
            if (!Settings.canDrawOverlays(this)) {
                Intent intent = new Intent(Settings.ACTION_MANAGE_OVERLAY_PERMISSION,
                        Uri.parse("package:" + getPackageName()));
                startActivity(intent);
                return;
            }
        }
        Toast.makeText(this, "Izin Overlay sudah aktif!", Toast.LENGTH_SHORT).show();
    }

    private void requestAccessibilityPermission() {
        Intent intent = new Intent(Settings.ACTION_ACCESSIBILITY_SETTINGS);
        startActivity(intent);
        Toast.makeText(this, "Pilih 'Kelnara Bot CoC' lalu Aktifkan", Toast.LENGTH_LONG).show();
    }

    private void launchOverlayBot() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M && !Settings.canDrawOverlays(this)) {
            Toast.makeText(this, "Harap aktifkan Izin Overlay terlebih dahulu!", Toast.LENGTH_SHORT).show();
            requestOverlayPermission();
            return;
        }

        if (CoCAccessibilityService.instance == null) {
            Toast.makeText(this, "Harap aktifkan Layanan Aksesibilitas Kelnara Bot!", Toast.LENGTH_LONG).show();
            requestAccessibilityPermission();
            return;
        }

        // Simpan konfigurasi ke engine
        FarmingEngine engine = FarmingEngine.getInstance();
        try {
            engine.minGold = Integer.parseInt(etMinGold.getText().toString()) * 1000;
            engine.minElixir = Integer.parseInt(etMinElixir.getText().toString()) * 1000;
        } catch (Exception ignored) {}
        engine.enableHarvest = cbAutoHarvest.isChecked();
        engine.enableZoom = cbAutoZoom.isChecked();
        engine.enableTrain = cbAutoTrain.isChecked();

        // Mulai floating service
        Intent serviceIntent = new Intent(this, FloatingService.class);
        startService(serviceIntent);

        Toast.makeText(this, "⚔️ Floating Bot Kelnara Aktif!", Toast.LENGTH_SHORT).show();

        // Coba luncurkan CoC jika terpasang
        try {
            Intent launchIntent = getPackageManager().getLaunchIntentForPackage("com.supercell.clashofclans");
            if (launchIntent != null) {
                startActivity(launchIntent);
            }
        } catch (Exception ignored) {}

        finish(); // Tutup activity agar kembali ke game
    }
}

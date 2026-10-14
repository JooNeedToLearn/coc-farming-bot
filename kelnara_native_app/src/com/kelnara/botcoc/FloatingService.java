package com.kelnara.botcoc;

import android.app.Service;
import android.content.Context;
import android.content.Intent;
import android.graphics.PixelFormat;
import android.os.Build;
import android.os.Handler;
import android.os.IBinder;
import android.os.Looper;
import android.view.Gravity;
import android.view.LayoutInflater;
import android.view.MotionEvent;
import android.view.View;
import android.view.WindowManager;
import android.widget.Button;
import android.widget.TextView;
import android.widget.Toast;

public class FloatingService extends Service {
    private WindowManager windowManager;
    private View floatingView;
    private WindowManager.LayoutParams params;
    private Handler mainHandler = new Handler(Looper.getMainLooper());

    @Override
    public IBinder onBind(Intent intent) {
        return null;
    }

    @Override
    public void onCreate() {
        super.onCreate();

        floatingView = LayoutInflater.from(this).inflate(R.layout.floating_widget, null);

        int layoutType;
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            layoutType = WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY;
        } else {
            layoutType = WindowManager.LayoutParams.TYPE_PHONE;
        }

        params = new WindowManager.LayoutParams(
                WindowManager.LayoutParams.WRAP_CONTENT,
                WindowManager.LayoutParams.WRAP_CONTENT,
                layoutType,
                WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE,
                PixelFormat.TRANSLUCENT
        );

        params.gravity = Gravity.TOP | Gravity.START;
        params.x = 40;
        params.y = 80;

        windowManager = (WindowManager) getSystemService(WINDOW_SERVICE);
        if (windowManager != null) {
            windowManager.addView(floatingView, params);
        }

        setupWidgetViews();
    }

    private void setupWidgetViews() {
        View dragHeader = floatingView.findViewById(R.id.drag_header);
        TextView tvStatus = floatingView.findViewById(R.id.tv_float_status);
        Button btnToggle = floatingView.findViewById(R.id.btn_float_toggle);
        Button btnHide = floatingView.findViewById(R.id.btn_float_hide);
        TextView btnClose = floatingView.findViewById(R.id.btn_close_float);

        Button btnQuickBattle = floatingView.findViewById(R.id.btn_quick_battle);
        Button btnQuickNext = floatingView.findViewById(R.id.btn_quick_next);
        Button btnQuickZoom = floatingView.findViewById(R.id.btn_quick_zoom);

        // Dragging listener
        dragHeader.setOnTouchListener(new View.OnTouchListener() {
            private int initialX, initialY;
            private float initialTouchX, initialTouchY;

            @Override
            public boolean onTouch(View v, MotionEvent event) {
                switch (event.getAction()) {
                    case MotionEvent.ACTION_DOWN:
                        initialX = params.x;
                        initialY = params.y;
                        initialTouchX = event.getRawX();
                        initialTouchY = event.getRawY();
                        return true;
                    case MotionEvent.ACTION_MOVE:
                        params.x = initialX + (int) (event.getRawX() - initialTouchX);
                        params.y = initialY + (int) (event.getRawY() - initialTouchY);
                        if (windowManager != null) {
                            windowManager.updateViewLayout(floatingView, params);
                        }
                        return true;
                }
                return false;
            }
        });

        // Close
        btnClose.setOnClickListener(v -> {
            FarmingEngine.getInstance().stop();
            stopSelf();
        });

        // Hide
        btnHide.setOnClickListener(v -> {
            Toast.makeText(this, "Kelnara Bot berjalan di latar belakang.", Toast.LENGTH_SHORT).show();
        });

        // Start / Stop Bot
        btnToggle.setOnClickListener(v -> {
            FarmingEngine engine = FarmingEngine.getInstance();
            if (!engine.isRunning()) {
                engine.start(this);
                btnToggle.setText("⏹ STOP");
                btnToggle.setBackgroundColor(0xFFEF4444);
            } else {
                engine.stop();
                btnToggle.setText("▶ MULAI FARM");
                btnToggle.setBackgroundColor(0xFF10B981);
            }
        });

        // Quick Manual Actions
        btnQuickBattle.setOnClickListener(v -> {
            FarmingEngine.getInstance().manualTestBattle(this);
        });

        btnQuickNext.setOnClickListener(v -> {
            FarmingEngine.getInstance().manualNext(this);
        });

        btnQuickZoom.setOnClickListener(v -> {
            FarmingEngine.getInstance().manualZoom(this);
        });

        // Status listener
        FarmingEngine.getInstance().setStatusListener((status, color) -> {
            mainHandler.post(() -> {
                if (tvStatus != null) {
                    tvStatus.setText("Status: " + status);
                    tvStatus.setTextColor(color);
                }
            });
        });
    }

    @Override
    public void onDestroy() {
        super.onDestroy();
        if (floatingView != null && windowManager != null) {
            windowManager.removeView(floatingView);
        }
    }
}

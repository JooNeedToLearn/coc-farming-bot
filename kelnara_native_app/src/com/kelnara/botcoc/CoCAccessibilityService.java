package com.kelnara.botcoc;

import android.accessibilityservice.AccessibilityService;
import android.accessibilityservice.GestureDescription;
import android.graphics.Path;
import android.os.Build;
import android.util.Log;
import android.view.accessibility.AccessibilityEvent;

public class CoCAccessibilityService extends AccessibilityService {
    private static final String TAG = "KelnaraAccessibility";
    public static CoCAccessibilityService instance = null;

    @Override
    protected void onServiceConnected() {
        super.onServiceConnected();
        instance = this;
        Log.d(TAG, "Kelnara Accessibility Service Terhubung!");
    }

    @Override
    public void onAccessibilityEvent(AccessibilityEvent event) {}

    @Override
    public void onInterrupt() {
        Log.d(TAG, "Kelnara Accessibility Service Terputus");
    }

    @Override
    public void onDestroy() {
        super.onDestroy();
        if (instance == this) {
            instance = null;
        }
    }

    public boolean performClick(float x, float y) {
        if (Build.VERSION.SDK_INT < Build.VERSION_CODES.N) return false;
        Path clickPath = new Path();
        clickPath.moveTo(x, y);
        clickPath.lineTo(x + 1, y + 1); // Wajib agar Android mendaftarkan stroke gerakan

        GestureDescription.StrokeDescription stroke =
                new GestureDescription.StrokeDescription(clickPath, 0, 100); // 100ms untuk Supercell game engine
        GestureDescription.Builder builder = new GestureDescription.Builder();
        builder.addStroke(stroke);
        return dispatchGesture(builder.build(), null, null);
    }

    public boolean performPinchZoom(float cx, float cy) {
        if (Build.VERSION.SDK_INT < Build.VERSION_CODES.N) return false;
        // Gestur 2 jari mencubit ke dalam untuk zoom out
        Path finger1 = new Path();
        finger1.moveTo(cx * 0.35f, cy * 0.35f);
        finger1.lineTo(cx * 0.85f, cy * 0.85f);

        Path finger2 = new Path();
        finger2.moveTo(cx * 1.65f, cy * 1.65f);
        finger2.lineTo(cx * 1.15f, cy * 1.15f);

        GestureDescription.StrokeDescription stroke1 =
                new GestureDescription.StrokeDescription(finger1, 0, 450);
        GestureDescription.StrokeDescription stroke2 =
                new GestureDescription.StrokeDescription(finger2, 0, 450);

        GestureDescription.Builder builder = new GestureDescription.Builder();
        builder.addStroke(stroke1);
        builder.addStroke(stroke2);
        return dispatchGesture(builder.build(), null, null);
    }
}

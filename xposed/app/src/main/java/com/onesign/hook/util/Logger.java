package com.onesign.hook.util;

import android.util.Log;

import de.robv.android.xposed.XposedBridge;

/**
 * 统一日志输出：同时写入 LSPosed 日志（XposedBridge.log）与
 * 标准 logcat（android.util.Log），后者无需 root 即可用 adb logcat 读取。
 */
public final class Logger {

    private static final String TAG = "OneSignHook";

    private Logger() {
    }

    public static void d(String msg) {
        XposedBridge.log(TAG + " | " + msg);
        Log.d(TAG, msg);
    }

    public static void e(String msg) {
        XposedBridge.log(TAG + " [E] " + msg);
        Log.e(TAG, msg);
    }

    public static void e(String msg, Throwable t) {
        XposedBridge.log(TAG + " [E] " + msg + " -> " + t);
        Log.e(TAG, msg, t);
    }
}

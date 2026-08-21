package com.onesign.hook.apps.ximalaya;

import android.app.Activity;

import com.onesign.hook.base.BaseAppHook;
import com.onesign.hook.util.Logger;

import java.lang.reflect.Method;

import de.robv.android.xposed.XC_MethodHook;
import de.robv.android.xposed.XposedHelpers;

/**
 * 喜马拉雅（com.ximalaya.ting.android）金币任务「看广告领金币」Hook。
 *
 * 逆向闭环结论（2026-08-21，设备版 9.5.4.3 / versionCode 10762，jadx_full + smali 权威）：
 *
 * 金币任务有【两条并行发奖路径】，都需覆盖：
 *
 * ── 路径 A：激励视频/纯视频类 ──
 *   unlockpaid/c$4（implements videoad/h，三路广告 SDK 最终汇聚监听器）
 *     c()  = onRewardVerify（广告看完验证成功）→ 置 c.p=true
 *     a(Z) = onAdClose（广告关闭）
 *         ├─ p==true  → c.a(null,true) 发币
 *         └─ p==false → 不发币（用户"直接离开"）
 *   → hook：强制 c.p=true + 调 c.a(null,true) 发币  ✅（v2.1.0 已解决）
 *
 * ── 路径 B：点击浏览 / 跳转App 类 ──
 *   1. bi（RewardAgainAdManager）："点击并浏览N秒" / "点击并浏览界面"
 *      bi.b(IAdModel) → tipStayTime>0&&actualStayTime>0 时起倒计时，否则 i=true
 *      bi.e() onResume → h&&i ? i()发币 : "浏览时长未满足，请重试"
 *      → hook bi.b(IAdModel) 强制 i=true + hook bi.e() 兜底
 *   2. bo$6/bo$7（跳转App拉活/下载广告）：
 *      onAdReward(boolean z, ...) → z=false 提示"浏览未满X秒，任务失败"
 *      → hook 强制 z=true
 *
 * 【策略】不伪造网络，hook 宿主侧发奖回调强制成功，让客户端自行走发币流程。
 */
public class XimalayaHook extends BaseAppHook {

    private static final String PKG = "com.ximalaya.ting.android";

    // ---------- 路径 A：宿主激励视频汇聚点 ----------
    private static final String UNLOCKPAID_C4 = "com.ximalaya.ting.android.host.manager.ad.unlockpaid.c$4";

    // ---------- 路径 B：点击浏览 / 跳转App ----------
    /** bi（RewardAgainAdManager）：点击浏览类发奖管理器。 */
    private static final String BI = "com.ximalaya.ting.android.host.manager.ad.bi";
    /** bo$6（下载广告）/ bo$7（拉活广告）：跳转App类发奖回调。 */
    private static final String BO_DOWNLOAD = "com.ximalaya.ting.android.host.manager.ad.bo$6";
    private static final String BO_ACTIVE = "com.ximalaya.ting.android.host.manager.ad.bo$7";

    // ---------- SDK 兜底 ----------
    private static final String TME_BASE = "com.tencentmusic.ad.d6.o";
    private static final String GDT_LISTENER_1 = "com.ximalaya.ting.android.host.manager.ad.videoad.d$3";
    private static final String GDT_LISTENER_2 = "com.ximalaya.ting.android.host.manager.ad.videoad.d$8";
    private static final String CSJ_LISTENER = "com.ximalaya.ting.android.host.manager.ad.videoad.a$10";

    @Override
    public String targetPackage() {
        return PKG;
    }

    @Override
    protected void onHook() throws Throwable {
        // ===== 路径 A：宿主激励视频汇聚点 =====
        safeHook("宿主 c$4.onAdClose 强制发币", this::hookHostOnAdClose);
        safeHook("宿主 c$4.onRewardVerify 强制发币", this::hookHostOnRewardVerify);

        // ===== 路径 B：点击浏览 / 跳转App =====
        safeHook("bi.b 点击浏览跳过倒计时", this::hookBiClickBrowse);
        safeHook("bi.e onResume 兜底发币", this::hookBiResume);
        safeHook("bo$6 下载广告 onAdReward 强制 true", this::hookBoDownload);
        safeHook("bo$7 拉活广告 onAdReward 强制 true", this::hookBoActive);

        // ===== SDK 兜底 =====
        safeHook("TME d6/o.onResume 展示即发奖", this::hookTmeOnResume);
        safeHook("GDT d$3 onReward 主动发奖", () -> hookGdtReward(GDT_LISTENER_1, "d$3"));
        safeHook("GDT d$8 onReward 主动发奖", () -> hookGdtReward(GDT_LISTENER_2, "d$8"));
        safeHook("CSJ a$10 onRewardArrived 强制发奖", this::hookCsjRewardArrived);
        safeHook("CSJ a$10 onRewardVerify 强制发奖", this::hookCsjRewardVerify);
    }

    // ==================== 路径 A：宿主激励视频汇聚点 ====================

    private void hookHostOnAdClose() {
        Class<?> cls = findClass(UNLOCKPAID_C4);
        XposedHelpers.findAndHookMethod(cls, "a", boolean.class, new XC_MethodHook() {
            @Override
            protected void beforeHookedMethod(MethodHookParam param) {
                Logger.d("[Host] c$4.onAdClose 触发，强制发币");
                forceReward(param.thisObject, "[Host onAdClose]");
            }
        });
    }

    private void hookHostOnRewardVerify() {
        Class<?> cls = findClass(UNLOCKPAID_C4);
        XposedHelpers.findAndHookMethod(cls, "c", new XC_MethodHook() {
            @Override
            protected void afterHookedMethod(MethodHookParam param) {
                Logger.d("[Host] c$4.onRewardVerify 触发，强制发币");
                forceReward(param.thisObject, "[Host onRewardVerify]");
            }
        });
    }

    private void forceReward(Object c4Obj, String tag) {
        try {
            Object c = XposedHelpers.getObjectField(c4Obj, "b");
            if (c == null) {
                Logger.e(tag + " c 实例为空");
                return;
            }
            try {
                XposedHelpers.setBooleanField(c, "p", true);
            } catch (Throwable ignored) {
            }
            Method m = XposedHelpers.findMethodExact(c.getClass(), "a", Activity.class, boolean.class);
            m.setAccessible(true);
            m.invoke(c, null, true);
            Logger.d(tag + " 已调 c.a(null, true) 发币");
        } catch (Throwable t) {
            Logger.e(tag + " 发币失败：" + t.getMessage());
        }
    }

    // ==================== 路径 B：点击浏览（bi） ====================

    /**
     * bi.b(IAdModel)（private static）：点击广告按钮后判定停留时长。
     * before 里强制静态字段 i=true，跳过倒计时，使 bi.e() 直接走发币 i()。
     */
    private void hookBiClickBrowse() {
        Class<?> cls = findClass(BI);
        XposedHelpers.findAndHookMethod(cls, "b",
                "com.ximalaya.ting.android.adsdk.external.feedad.IAdModel",
                new XC_MethodHook() {
                    @Override
                    protected void afterHookedMethod(MethodHookParam param) {
                        Logger.d("[bi] b(IAdModel) 点击浏览触发，强制 i=true 跳过倒计时");
                        try {
                            XposedHelpers.setStaticBooleanField(findClass(BI), "i", true);
                        } catch (Throwable t) {
                            Logger.e("[bi] 置 i=true 失败：" + t.getMessage());
                        }
                    }
                });
    }

    /**
     * bi.e()（public static）：onResume 时判定发币。
     * after 兜底：确保 i=true，让发币逻辑 i() 一定走通。
     */
    private void hookBiResume() {
        Class<?> cls = findClass(BI);
        XposedHelpers.findAndHookMethod(cls, "e", new XC_MethodHook() {
            @Override
            protected void afterHookedMethod(MethodHookParam param) {
                Logger.d("[bi] e() onResume 触发，兜底强制 i=true");
                try {
                    XposedHelpers.setStaticBooleanField(findClass(BI), "i", true);
                } catch (Throwable t) {
                    Logger.e("[bi] 兜底置 i=true 失败：" + t.getMessage());
                }
            }
        });
    }

    // ==================== 路径 B：跳转App（bo$6/bo$7） ====================

    private void hookBoDownload() {
        Class<?> cls = findClass(BO_DOWNLOAD);
        XposedHelpers.findAndHookMethod(cls, "onAdReward",
                boolean.class, long.class, Integer.class, String.class,
                new XC_MethodHook() {
                    @Override
                    protected void beforeHookedMethod(MethodHookParam param) {
                        Logger.d("[bo$6] 下载广告 onAdReward 触发，强制 z=true");
                        param.args[0] = Boolean.TRUE;
                    }
                });
    }

    private void hookBoActive() {
        Class<?> cls = findClass(BO_ACTIVE);
        XposedHelpers.findAndHookMethod(cls, "onAdReward",
                boolean.class, long.class, Integer.class, String.class,
                new XC_MethodHook() {
                    @Override
                    protected void beforeHookedMethod(MethodHookParam param) {
                        Logger.d("[bo$7] 拉活广告 onAdReward 触发，强制 z=true");
                        param.args[0] = Boolean.TRUE;
                    }
                });
    }

    // ==================== SDK 兜底 ====================

    private void hookTmeOnResume() {
        Class<?> cls = findClass(TME_BASE);
        XposedHelpers.findAndHookMethod(cls, "onResume", new XC_MethodHook() {
            @Override
            protected void afterHookedMethod(MethodHookParam param) {
                final Object thisObj = param.thisObject;
                Logger.d("[TME] onResume 触发，延迟主动发奖");
                new android.os.Handler(android.os.Looper.getMainLooper()).postDelayed(new Runnable() {
                    @Override
                    public void run() {
                        try {
                            XposedHelpers.callMethod(thisObj, "a", 0);
                            Logger.d("[TME] 已主动调用 a(0) 发奖");
                        } catch (Throwable t) {
                            Logger.e("[TME] 发奖失败：" + t.getMessage());
                        }
                    }
                }, 500);
            }
        });
    }

    private void hookGdtReward(final String className, final String tag) {
        Class<?> cls = findClass(className);
        XposedHelpers.findAndHookMethod(cls, "onReward", java.util.Map.class, new XC_MethodHook() {
            @Override
            protected void beforeHookedMethod(MethodHookParam param) {
                Logger.d("[GDT " + tag + "] onReward 被调用（SDK 正常发奖路径）");
            }
        });
    }

    private void hookCsjRewardArrived() {
        Class<?> cls = findClass(CSJ_LISTENER);
        XposedHelpers.findAndHookMethod(cls, "onRewardArrived", boolean.class, int.class,
                android.os.Bundle.class, new XC_MethodHook() {
                    @Override
                    protected void beforeHookedMethod(MethodHookParam param) {
                        Logger.d("[CSJ] onRewardArrived 触发，强制 z=true");
                        param.args[0] = Boolean.TRUE;
                    }
                });
    }

    private void hookCsjRewardVerify() {
        Class<?> cls = findClass(CSJ_LISTENER);
        XposedHelpers.findAndHookMethod(cls, "onRewardVerify", boolean.class, int.class,
                String.class, int.class, String.class, new XC_MethodHook() {
                    @Override
                    protected void beforeHookedMethod(MethodHookParam param) {
                        Logger.d("[CSJ] onRewardVerify 触发，强制 z=true");
                        param.args[0] = Boolean.TRUE;
                    }
                });
    }
}

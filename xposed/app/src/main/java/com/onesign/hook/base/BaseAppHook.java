package com.onesign.hook.base;

import com.onesign.hook.util.Logger;

import de.robv.android.xposed.XposedHelpers;
import de.robv.android.xposed.callbacks.XC_LoadPackage;

/**
 * App Hook 实现基类：封装 ClassLoader 查找、异常兜底等通用逻辑。
 */
public abstract class BaseAppHook implements IAppHook {

    protected XC_LoadPackage.LoadPackageParam lpparam;
    protected ClassLoader classLoader;

    @Override
    public final void hook(XC_LoadPackage.LoadPackageParam lpparam) throws Throwable {
        this.lpparam = lpparam;
        this.classLoader = lpparam.classLoader;
        onHook();
        Logger.d("[" + targetPackage() + "] Hook 完成");
    }

    /** 子类在此实现具体 Hook 逻辑。 */
    protected abstract void onHook() throws Throwable;

    /** 按全限定名查找类（优先用目标 App 的 ClassLoader）。 */
    protected Class<?> findClass(String name) {
        return XposedHelpers.findClass(name, classLoader);
    }

    /** 安全 Hook 封装：单个 Hook 点失败不影响其它 Hook 点。 */
    protected void safeHook(String tag, Runnable runnable) {
        try {
            runnable.run();
            Logger.d("[" + targetPackage() + "] hook 点成功：" + tag);
        } catch (Throwable t) {
            Logger.e("[" + targetPackage() + "] hook 点失败：" + tag, t);
        }
    }
}

package com.onesign.hook.base;

import de.robv.android.xposed.callbacks.XC_LoadPackage;

/**
 * 单个 App 的 Hook 实现契约。
 */
public interface IAppHook {

    /** 目标 App 包名。 */
    String targetPackage();

    /** 执行 Hook。 */
    void hook(XC_LoadPackage.LoadPackageParam lpparam) throws Throwable;
}

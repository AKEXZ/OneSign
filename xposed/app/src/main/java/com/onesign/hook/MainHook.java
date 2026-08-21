package com.onesign.hook;

import com.onesign.hook.apps.ximalaya.XimalayaHook;
import com.onesign.hook.base.HookRegistry;
import com.onesign.hook.base.IAppHook;
import com.onesign.hook.util.Logger;

import de.robv.android.xposed.IXposedHookLoadPackage;
import de.robv.android.xposed.callbacks.XC_LoadPackage;

/**
 * OneSign Hook 模块入口。
 *
 * 通过 HookRegistry 按目标包名分发到各 App 的 Hook 实现。
 * 新增 App 支持时：实现 IAppHook，并在下方 static 块中 register 即可。
 */
public class MainHook implements IXposedHookLoadPackage {

    static {
        // 在此注册各 App 的 Hook 实现（包名 -> 实现）
        HookRegistry.register(new XimalayaHook());
    }

    @Override
    public void handleLoadPackage(XC_LoadPackage.LoadPackageParam lpparam) {
        IAppHook hook = HookRegistry.get(lpparam.packageName);
        if (hook == null) {
            return;
        }
        Logger.d("命中目标 App：" + lpparam.packageName);
        try {
            hook.hook(lpparam);
        } catch (Throwable t) {
            Logger.e("分发 Hook 失败：" + lpparam.packageName, t);
        }
    }
}

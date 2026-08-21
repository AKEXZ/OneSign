package com.onesign.hook.base;

import java.util.LinkedHashMap;
import java.util.Map;

/**
 * Hook 注册表：包名 -> IAppHook 实现。
 */
public final class HookRegistry {

    private static final Map<String, IAppHook> HOOKS = new LinkedHashMap<>();

    private HookRegistry() {
    }

    public static void register(IAppHook hook) {
        HOOKS.put(hook.targetPackage(), hook);
    }

    public static IAppHook get(String packageName) {
        return HOOKS.get(packageName);
    }
}

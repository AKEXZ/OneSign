# OneSign Xposed 模块 proguard 规则
# 模块默认不混淆；如启用混淆，需保留 Hook 入口与方法名。
-keep class com.onesign.hook.MainHook { *; }
-keep class com.onesign.hook.base.** { *; }
-keep class com.onesign.hook.apps.** { *; }

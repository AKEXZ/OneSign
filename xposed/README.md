# OneSign Xposed Hook 模块

可扩展的 Xposed / LSPosed Hook 模块框架，用于自动完成 App 内金币任务（跳过真实看广告）。

当前以 **喜马拉雅**（`com.ximalaya.ting.android`）为范例实现。

## 目录结构

```
xposed/
├── settings.gradle.kts          # 仓库配置（含 Xposed API 仓库）
├── build.gradle.kts             # 根构建脚本
├── gradle.properties            # 构建参数
├── gradle/wrapper/              # Gradle Wrapper
└── app/
    ├── build.gradle.kts         # 模块构建脚本
    ├── proguard-rules.pro
    └── src/main/
        ├── AndroidManifest.xml  # LSPosed 模块声明
        ├── java/com/onesign/hook/
        │   ├── MainHook.java            # 入口（注册分发）
        │   ├── base/                    # 框架基类
        │   │   ├── IAppHook.java        # App Hook 契约
        │   │   ├── BaseAppHook.java     # 基类（ClassLoader/兜底）
        │   │   └── HookRegistry.java    # 包名->实现注册表
        │   ├── apps/ximalaya/           # 喜马拉雅 Hook 实现
        │   │   └── XimalayaHook.java
        │   └── util/Logger.java
        └── res/values/strings.xml       # 模块名 + xposed scope
```

## 快速开始

```bash
cd xposed
./gradlew assembleDebug    # debug 版（测试签名，部分 LSPosed 不识别）
./gradlew assembleRelease  # release 版（正式签名 V1+V2+V3，推荐安装此版）
```

产物：
- `dist/OneSignHook-v1.0.0-release.apk`（推荐，正式签名）
- `dist/OneSignHook-v1.0.0-debug.apk`

## 安装与激活

1. `adb install dist/OneSignHook-v1.0.0-release.apk`（或直接传到手机安装）
2. 打开 LSPosed Manager → 模块，应能看到「OneSign Hook」
3. 点击模块 → 勾选作用域 `com.ximalaya.ting.android`（喜马拉雅）
4. 重启喜马拉雅 App（或重启设备）生效

> ⚠️ 若 LSPosed 不识别 debug 版，务必安装 **release 版**（正式签名）。
> 部分新版 LSPosed（如 v2.x Zygisk fork）不识别测试签名的 APK。

## LSPosed 识别模块所需的关键配置

| 项 | 位置 | 说明 |
|----|------|------|
| `xposedmodule=true` | AndroidManifest meta-data | 核心识别标记 |
| `xposedminversion=82` | AndroidManifest meta-data | 最低 Xposed API |
| `xposedscope` | AndroidManifest meta-data + res | 作用域包名列表 |
| `assets/xposed_init` | APK 资产 | 入口类全限定名 `com.onesign.hook.MainHook` |
| 正式签名 | build.gradle signingConfigs | V1+V2+V3（部分 LSPosed 硬性要求）|

## 新增 App 支持

1. 在 `apps/<name>/` 下新建类，继承 `BaseAppHook`，实现 `targetPackage()` 与 `onHook()`。
2. 在 `MainHook` 的 static 块中 `HookRegistry.register(new XxxHook());`。
3. 在 `strings.xml` 的 `xposed_scope` 数组追加目标包名。

## 逆向结论（喜马拉雅）

- 金币任务广告走「广告聚合 SDK 层」`RewardVideoAdManager`，所有广告类型
  （Xm 自营 / GDT / 穿山甲）奖励回调最终汇聚到内部类
  `VideoAdStatueCallBackWrapper`。
- 视频看完 -> `XmRewardVideoAdFragment.requestReward()` -> `onRewardSuccess(true)`
  -> 宿主 App 收到 `onReward` 发放金币。
- 关闭广告时若 `positionId==279` 且 `isRewardSuccess`，触发
  `hookRewardForRead` 补发接口（签名由客户端 native 自行生成，无需伪造）。

## Hook 策略

| Hook 点 | 作用 |
|---------|------|
| `XmRewardVideoAdFragment.onResume` | 广告页一显示立即 `requestReward()` 发奖 |
| `VideoAdStatueCallBackWrapper.onRewardSuccess` | 强制入参 `true` |
| `XmRewardVideoAdFragment.initUi` | 缩短倒计时为 1 秒，加速自动关闭 |

> 提示：以上为 Xm 自营广告的通用路径。若实际投放为 GDT / 穿山甲广告，
> 可扩展 hook `GDTRewardVideoAdUtil` / `CSJRewardVideoAdUtil` 的对应回调。

# OneSign - 呆呆面板适配版

基于 [Wenmoux/checkbox](https://github.com/Wenmoux/checkbox) 二改，精简保留常用签到脚本，支持**呆呆面板订阅模式**和**独立运行**两种方式。

## 支持的签到

| 脚本 | 站点 | Cron |
|------|------|------|
| duokan | 多看阅读 | `25 8 * * *` |
| cg163 | 网易云游戏 | `30 8 * * *` |
| nga | NGA论坛 | `20 8 * * *` |
| mt_sign | MT论坛 | `15 8 * * *` |
| hykb | 好游快爆 | `5 8 * * *` |
| quark | 夸克网盘 | `10 8 * * *` |
| gobing | Gobing | `35 8 * * *` |
| mcdonald | 麦当劳 | `0 9 * * *` |
| hykb_exchange_goods | 好游快爆抢兑 | `59 12 * * *` |

> 好游快爆的临时任务、游戏签到已合并至 `hykb.js`，无需额外配置。

---

## 方式一：呆呆面板订阅模式（推荐）

### 1. 一键订阅

在面板终端中执行：

```bash
ql repo https://github.com/AKEXZ/OneSign.git "scripts/" "" "" "main"
```

或手动添加：进入「订阅管理」→「新建订阅」，填入仓库地址，面板会自动拉取 `scripts/` 目录下所有脚本，识别 `cron` 和 `new Env()` 注解。

### 2. 配置环境变量

在呆呆面板的「环境变量」中，按需配置以下变量：

| 环境变量 | 对应站点 | 说明 |
|---------|---------|------|
| `ONESIGN_CG163_AUTHORIZATION` | 网易云游戏 | 请求头 Authorization |
| `ONESIGN_MT_COOKIE` | MT论坛 | 完整 Cookie |
| `ONESIGN_NGA_UID` | NGA论坛 | 用户 UID |
| `ONESIGN_NGA_ACCESSTOKEN` | NGA论坛 | Access Token |
| `ONESIGN_NGA_UA` | NGA论坛 | User-Agent（可选） |
| `ONESIGN_DUOKAN_COOKIE` | 多看阅读 | 完整 Cookie |
| `ONESIGN_QUARK_COOKIE` | 夸克网盘 | Cookie（支持多账号数组） |
| `ONESIGN_GOBING_ACCOUNT` | Gobing | 账号 |
| `ONESIGN_GOBING_PASSWORD` | Gobing | 密码 |
| `ONESIGN_MCDONALD_TOKEN` | 麦当劳 | Bearer Token |
| `ONESIGN_HYKB_SCOOKIE` | 好游快爆 | scookie |
| `ONESIGN_HYKB_QQ` | 好游快爆 | QQ号（可选） |
| `ONESIGN_HYKB_GID` | 好游快爆抢兑 | 商品 gid |
| `ONESIGN_HYKB_KEY` | 好游快爆抢兑 | 商品 key |
| `ONESIGN_UA` | 全局 | 自定义 UA（可选） |

---

## 方式二：config.yml 独立运行

### 1. 配置文件

```bash
cp config.yml.temple config.yml
```

编辑 `config.yml`，填写对应站点的 cookie / token。

### 2. 运行

```bash
# 统一调度（运行所有已配置的签到）
node checkbox.js

# 单独运行某个脚本
node scripts/cg163.js
node scripts/duokan.js
node scripts/nga.js
node scripts/hykb/hykb.js
```

---

## 配置优先级

**环境变量 > config.yml**

在呆呆面板中使用时，配置环境变量即可，无需 config.yml。独立运行时，二者可共存，环境变量优先。

---

## 原项目

https://github.com/Wenmoux/checkbox
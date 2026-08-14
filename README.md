# OneSign - 呆呆面板适配版

基于 [Wenmoux/checkbox](https://github.com/Wenmoux/checkbox) 二改，精简保留常用签到脚本，专为**呆呆面板订阅模式**设计。

## 支持的签到

| 脚本 | 站点 | Cron |
|------|------|------|
| cg163 | 网易云游戏 | `30 8 * * *` |
| nga | NGA论坛 | `20 8 * * *` |
| mt_sign | MT论坛 | `15 8 * * *` |
| hykb | 好游快爆 | `5 8 * * *` |
| quark | 夸克网盘 | `10 8 * * *` |
| csdn | CSDN | `25 8 * * *` |
| mcdonald | 麦当劳 | `0 9 * * *` |
| aliyun | 阿里云盘 | `30 8 * * *` |
| unicom | 中国联通 | `0 9 * * *` |
| hykb_exchange_goods | 好游快爆抢兑 | `59 12 * * *` |

> 好游快爆的临时任务、游戏签到已合并至 `hykb.js`，无需额外配置。

---

## 订阅

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
| `ONESIGN_CG163_AUTHORIZATION` | 网易云游戏 | 请求头 Authorization（不是 Cookie） |
| `ONESIGN_MT_COOKIE` | MT论坛 | 完整 Cookie |
| `ONESIGN_NGA_UID` | NGA论坛 | 用户 UID |
| `ONESIGN_NGA_ACCESSTOKEN` | NGA论坛 | Access Token |
| `ONESIGN_NGA_UA` | NGA论坛 | User-Agent（可选） |
| `ONESIGN_QUARK_COOKIE` | 夸克网盘 | 完整 Cookie |
| `ONESIGN_CSDN_COOKIE` | CSDN | 完整 Cookie |
| `ONESIGN_MCDONALD_TOKEN` | 麦当劳 | Bearer Token |
| `ONESIGN_HYKB_SCOOKIE` | 好游快爆 | scookie |
| `ONESIGN_HYKB_QQ` | 好游快爆 | QQ号（可选） |
| `ONESIGN_HYKB_GID` | 好游快爆抢兑 | 商品 gid |
| `ONESIGN_HYKB_KEY` | 好游快爆抢兑 | 商品 key |
| `ONESIGN_UA` | 全局 | 自定义 UA（可选） |
| `ONESIGN_ALIYUN_REFRESH_TOKEN` | 阿里云盘 | refresh_token |
| `ONESIGN_UNICOM_TOKEN_ONLINE` | 中国联通 | token_online（抓包获取） |
| `ONESIGN_UNICOM_PHONE` | 中国联通 | 手机号（可选） |
| `ONESIGN_UNICOM_DEVICEID` | 中国联通 | deviceId（可选） |
| `ONESIGN_UNICOM_APPID` | 中国联通 | appId（可选） |

## 原项目

https://github.com/Wenmoux/checkbox
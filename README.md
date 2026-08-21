# OneSign - 呆呆面板适配版

基于 [Wenmoux/checkbox](https://github.com/Wenmoux/checkbox) 二改，精简保留常用签到脚本，专为**呆呆面板订阅模式**设计。

## 支持的签到

| 脚本 | 站点 | Cron |
|------|------|------|
| acfun | ACFun签到 | `0 9 * * *` |
| aliyun | 阿里云盘 | `30 8 * * *` |
| iqiyi | 爱奇艺 | `25 6,12,18 * * *` |
| dbkd | 德邦快递 | `0 6 * * *` |
| ddai | 钉钉AI签到 | `10 0 16 * * *` |
| hdl | 海底捞 | `0 6 * * *` |
| hykb | 好游快爆 | `0 8,12,18 * * *` |
| hykb_exchange_goods | 好游快爆抢兑 | `59 12 * * *` |
| jtsd | 极兔速递 | `0 6 * * *` |
| jtc | 捷停车 | `15 9 * * *` |
| quark | 夸克网盘 | `0 2 * * *` |
| mcdonald | 麦当劳 | `0 9 * * *` |
| mt_sign | MT论坛 | `15 8 * * *` |
| nga | NGA论坛 | `20 8 * * *` |
| qmread | 七猫抽奖 | `0 9,21 * * *` |
| chery | 奇瑞汽车 | `9 7 * * *` |
| tuhu | 途虎养车 | `12 8 * * *` |
| cg163 | 网易云游戏 | `30 8 * * *` |
| xmly | 喜马拉雅 | `0 */2 * * *` |
| ydkd | 韵达快递 | `0 6 * * *` |
| unicom | 中国联通 | `0 9 * * *` |
| ztkd | 中通快递 | `0 6 * * *` |

> 好游快爆的临时任务、游戏签到已合并至 `hykb.js`，无需额外配置。

---

## 订阅

### 1. 一键订阅

在面板终端中执行：

\`\`\`bash
ql repo https://github.com/AKEXZ/OneSign.git "scripts/" "" "" "main"
\`\`\`

或手动添加：进入「订阅管理」→「新建订阅」，填入仓库地址。

### 2. 配置环境变量

| 环境变量 | 对应站点 | 说明 |
|---------|---------|------|
| `ONESIGN_ACFUN_COOKIE` | ACFun | Cookie（多账号用 @ 分隔） |
| `ONESIGN_ALIYUN_REFRESH_TOKEN` | 阿里云盘 | refresh_token |
| `ONESIGN_IQY_COOKIE` | 爱奇艺 | 完整 Cookie（多账号用 # 或 & 分隔） |
| `ONESIGN_DBKD_TOKEN` | 德邦快递 | ECO_TOKEN（多账号用 # 分隔） |
| `ONESIGN_DDAI_COOKIE` | 钉钉AI | Cookie（多账号用 @ 分隔） |
| `ONESIGN_HDL_TOKEN` | 海底捞 | _HAIDILAO_APP_TOKEN（多账号用 # 或 & 分隔） |
| `ONESIGN_HYKB_COOKIE` | 好游快爆 | scookie（多账号用 @ 分隔） |
| `ONESIGN_HYKB_GID` | 好游快爆抢兑 | 商品 gid |
| `ONESIGN_HYKB_KEY` | 好游快爆抢兑 | 商品 key |
| `ONESIGN_JTSD_TOKEN` | 极兔速递 | authtoken（多账号用 # 或 & 分隔） |
| `ONESIGN_JTC_TOKEN` | 捷停车 | userId,token（多账号用 @ 分隔） |
| `ONESIGN_KKYP_COOKIE` | 夸克网盘 | Cookie（多账号用 # 或 & 分隔） |
| `ONESIGN_MCDONALD_TOKEN` | 麦当劳 | Bearer Token |
| `ONESIGN_MT_COOKIE` | MT论坛 | 完整 Cookie |
| `ONESIGN_NGA_UID` | NGA论坛 | 用户 UID |
| `ONESIGN_NGA_ACCESSTOKEN` | NGA论坛 | Access Token |
| `ONESIGN_NGA_UA` | NGA论坛 | User-Agent（可选） |
| `ONESIGN_QMREAD_COOKIE` | 七猫抽奖 | authorization#qm-params（多账号用 @ 分隔） |
| `ONESIGN_CHERY_TOKEN` | 奇瑞汽车 | Authorization（多账号用 @ 分隔） |
| `ONESIGN_TUHU_TOKEN` | 途虎养车 | token |
| `ONESIGN_CG163_AUTHORIZATION` | 网易云游戏 | Authorization（不是 Cookie） |
| `ONESIGN_XMLY_COOKIE` | 喜马拉雅 | Cookie（多账号用 # 分隔） |
| `ONESIGN_YDKD_TOKEN` | 韵达快递 | Authorization（多账号用 # 或 & 分隔） |
| `ONESIGN_UNICOM_COOKIE` | 中国联通 | act.10010.com 的 Cookie（必填） |
| `ONESIGN_UNICOM_PHONE` | 中国联通 | 手机号（可选） |
| `ONESIGN_UNICOM_DEVICEID` | 中国联通 | deviceId（可选） |
| `ONESIGN_UNICOM_APPID` | 中国联通 | appId（可选） |
| `ONESIGN_ZTKD_TOKEN` | 中通快递 | x-token（多账号用 # 分隔） |
| `ONESIGN_UA` | 全局 | 自定义 UA（可选） |

## 原项目

https://github.com/Wenmoux/checkbox

# 新脚本/移植脚本规范

创建或移植签到脚本时必须遵守以下规范，专为呆呆面板设计。

---

## 1. 文件位置

脚本放在 `scripts/` 目录下，支持子目录（如 `scripts/hykb/hykb.js`）。文件名建议与站点英文名一致。

## 2. 文件头注释（必填）

必须包含 `cron` 和 `new Env()` 两行注解，呆呆面板据此识别调度信息和任务名称。

```js
/*
抓包：简要说明如何获取所需变量
变量：ONESIGN_XXX_YYY（说明） / ONESIGN_XXX_ZZZ（说明）

cron: 0 9 * * *
new Env('站点名签到');
*/
```

## 3. 环境变量命名

- 统一前缀 `ONESIGN_`，全大写，下划线分隔
- 示例：`ONESIGN_QUARK_COOKIE`、`ONESIGN_UNICOM_TOKEN_ONLINE`
- 同时支持 `jd_cookie` 模式（多个 cookie 用 `&` 分隔）

## 4. 配置读取

使用 `getConfig` 辅助函数，同时支持环境变量和 `config.yml`：

```js
const { getConfig } = (() => {
    const fs = require("fs");
    const path = require("path");
    function getConfig(key, envName) {
        if (process.env[envName]) return process.env[envName];
        try {
            const configPath = path.join(__dirname, "..", "config.yml");
            // 子目录脚本需调整：path.join(__dirname, "..", "..", "config.yml")
            if (fs.existsSync(configPath)) {
                const yaml = require("js-yaml");
                const config = yaml.load(fs.readFileSync(configPath, "utf8"));
                const keys = key.split(".");
                let val = config;
                for (const k of keys) {
                    if (val && typeof val === "object") val = val[k];
                    else return undefined;
                }
                return val;
            }
        } catch (e) {}
        return undefined;
    }
    return { getConfig };
})();
```

## 5. 脚本结构

纯面板模式，直接执行，不导出模块。用 `success` 标志位追踪状态。

```js
async function myTask() {
    let success = true;
    console.log("【站点名】：开始签到...");

    // 任务逻辑
    // 失败时：success = false;

    if (!success) process.exit(1);
}
myTask();
```

## 6. 退出码（必填！）

**呆呆面板根据退出码判断成功/失败：`0` = 成功，非 `0` = 失败。**

失败时必须 `process.exit(1)`，否则面板会误报成功。

## 7. 错误处理

- 所有 HTTP 请求必须 `try/catch`，catch 中打印错误日志
- 不要让未捕获的异常导致脚本崩溃
- axios 请求建议设置 `timeout` 避免长时间挂起

## 8. 日志输出

- 开头打印 `【站点名】：开始签到...` 标识开始
- 每个关键步骤打印结果（登录成功/失败、签到成功/失败等）
- 不要在正常流程中打印完整响应体（避免刷屏）

## 9. 多账号支持

```js
const cookie = getConfig("xxx.cookie", "ONESIGN_XXX_COOKIE");
const cookies = Array.isArray(cookie) ? cookie : [cookie];
for (let i = 0; i < cookies.length; i++) {
    // 逐个处理
}
```

## 10. README 同步

新增脚本后，必须在 `README.md` 中更新：
- "支持的签到" 表格添加一行
- "环境变量" 表格添加对应变量，标注必填/可选

## 11. 测试

```bash
# 执行脚本
node scripts/xxx.js

# 检查退出码（应非 0 表示失败）
echo $?
```
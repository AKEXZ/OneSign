/**
 * 抓包：钉钉 app → 个人空间 → AI签到 → 抓包 api-wolai.dingtalk.com 的 cookie
 * 变量：ONESIGN_DDAI_COOKIE（cookie 值，多账号用 @ 或换行分隔）
 *
 * cron: 10 0 16 * * *
 * new Env('钉钉AI签到领算粒');
 */

const axios = require("axios");
const SCRIPT_NAME = "钉钉AI";
const { getConfig } = (() => {
    const fs = require("fs");
    const path = require("path");
    function getConfig(key, envName) {
        if (process.env[envName]) return process.env[envName];
        try {
            const configPath = path.join(__dirname, "..", "config.yml");
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

async function ddai() {
    let success = true;
    console.log("【钉钉AI】：开始签到...");

    const cookie = getConfig("", "ONESIGN_DDAI_COOKIE");
    if (!cookie) {
        console.log("【钉钉AI】：未配置 ONESIGN_DDAI_COOKIE 变量");
        success = false;
    } else {
        const cookies = cookie.split(/[@\n]/).filter(t => t.trim());

        for (let i = 0; i < cookies.length; i++) {
            const idx = i + 1;
            const ck = cookies[i].trim();
            console.log(`----- 账号[${idx}]开始执行 -----`);

            const headers = {
                'Cookie': ck,
                'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_1 like Mac OS X) AppleWebKit/605.1.15',
                'Content-Type': 'application/json',
            };

            try {
                // 签到
                const signResult = await axios.post(
                    'https://api-wolai.dingtalk.com/v1/sign/in',
                    {},
                    { headers }
                );

                const data = signResult.data;
                if (data && data.code === 0) {
                    console.log(`签到成功！获得 ${data.data?.reward || 0} 算粒`);
                } else if (data && data.code === 1) {
                    console.log('今日已签到');
                } else {
                    console.log(`签到失败: ${JSON.stringify(data)}`);
                    success = false;
                }

                // 获取算粒余额
                const balanceResult = await axios.get(
                    'https://api-wolai.dingtalk.com/v1/user/balance',
                    { headers }
                );

                if (balanceResult.data && balanceResult.data.code === 0) {
                    console.log(`当前算粒: ${balanceResult.data.data?.balance || 0}`);
                }
            } catch (e) {
                console.log(`账号[${idx}] 请求异常: ${e.message}`);
                success = false;
            }

            await new Promise(r => setTimeout(r, 2000));
        }
    }

    if (!success) { process.exit(1); }
}

ddai();
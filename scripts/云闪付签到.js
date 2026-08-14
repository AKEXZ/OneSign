/**
 * 抓包：云闪付 app → 签到页面 → 抓包获取 Authorization 值（去掉 Bearer 前缀）
 * 变量：ONESIGN_YSFQD_TOKEN（Authorization 值，多账号用 @ 或换行分隔）
 *
 * cron: 5 8 * * *
 * new Env('云闪付签到');
 */

const axios = require("axios");
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

async function ysfqd() {
    let success = true;
    console.log("【云闪付】：开始签到...");

    const token = getConfig("", "ONESIGN_YSFQD_TOKEN");
    if (!token) {
        console.log("【云闪付】：未配置 ONESIGN_YSFQD_TOKEN 变量");
        success = false;
    } else {
        const tokens = token.split(/[@\n]/).filter(t => t.trim());

        for (let i = 0; i < tokens.length; i++) {
            const ck = tokens[i].trim();
            console.log(`账号[${i + 1}]开始执行`);

            try {
                const options = {
                    method: 'POST',
                    url: 'https://youhui.95516.com/newsign/api/daily_sign_in',
                    headers: {
                        'Accept': '*/*',
                        'Authorization': `Bearer ${ck}`,
                        'Accept-Encoding': 'gzip, deflate, br',
                        'Content-Type': 'application/json',
                        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148',
                        'Connection': 'keep-alive',
                    },
                };
                const response = await axios(options);
                const result = response.data;

                if ('signedIn' in result) {
                    const days = result.signInDays || {};
                    console.log(`账号[${i + 1}] 今天是第${days.current?.days || '?'}天签到，已连续签到${days.days || '?'}天`);
                } else {
                    console.log(`账号[${i + 1}] 签到失败，原因未知`);
                    console.log(JSON.stringify(result));
                    success = false;
                }
            } catch (e) {
                console.log(`账号[${i + 1}] 请求异常: ${e.message}`);
                success = false;
            }

            await new Promise(r => setTimeout(r, 1000));
        }
    }

    if (!success) process.exit(1);
}

ysfqd();
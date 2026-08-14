/**
 * 抓包：途虎养车小程序 → 积分页面 → 抓包获取 Authorization (去掉 Bearer)
 *      TUHU_BLACKBOX 同样抓包获取
 * 变量：ONESIGN_TUHU_TOKEN（token） / ONESIGN_TUHU_BLACKBOX（blackbox）
 *       多账号用 @ 分隔，token 和 blackbox 一一对应
 *
 * cron: 12 8 * * *
 * new Env('途虎养车签到');
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

async function httpRequest(options) {
    try {
        const response = await axios(options);
        return response.data;
    } catch (e) {
        if (e.response) return e.response.data;
        return null;
    }
}

function hideMobile(mobile) {
    if (!mobile) return '';
    return mobile.slice(0, 3) + '****' + mobile.slice(-4);
}

async function tuhu() {
    let success = true;
    console.log("【途虎养车】：开始签到...");

    const tokenStr = getConfig("", "ONESIGN_TUHU_TOKEN") || '';
    const blackboxStr = getConfig("", "ONESIGN_TUHU_BLACKBOX") || '';

    const tokenArr = tokenStr.split('@').filter(t => t.trim());
    const blackboxArr = blackboxStr.split('@').filter(t => t.trim());

    if (!tokenArr.length) {
        console.log("【途虎养车】：未配置 ONESIGN_TUHU_TOKEN 变量");
        success = false;
    } else {
        for (let i = 0; i < tokenArr.length; i++) {
            const idx = i + 1;
            const token = tokenArr[i].trim();

            const headers = {
                'Authorization': token.startsWith('Bearer ') ? token : 'Bearer ' + token,
                'authType': 'oauth',
                'Content-Type': 'application/json',
                'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_1 like Mac OS X) AppleWebKit/605.1.15',
            };

            console.log(`----- 账号[${idx}]开始执行 -----`);

            try {
                // 获取用户信息
                const userResult = await httpRequest({
                    method: 'POST',
                    url: 'https://cl-gateway.tuhu.cn/cl-user-info-site/userAccount/getCurrentUserInfo',
                    headers,
                    data: '{}',
                });

                if (userResult?.code === 10000 && userResult?.data) {
                    const { nickName, mobile } = userResult.data;
                    console.log(`用户: ${nickName} [${hideMobile(mobile)}]`);
                } else {
                    console.log(`账号[${idx}] 获取用户信息失败，token可能无效`);
                    success = false;
                    continue;
                }

                // 签到 (APP + 小程序)
                const tasks = [
                    { name: "APP", url: "" },
                    { name: "小程序", url: "?channel=wxapp" },
                ];

                for (const task of tasks) {
                    const signResult = await httpRequest({
                        method: 'POST',
                        url: `https://cl-gateway.tuhu.cn/cl-integral-repository/integral/signIn${task.url}`,
                        headers,
                        data: '{}',
                    });

                    if (signResult?.code === 10000) {
                        const { continuousSignDays, signDays, totalSignDays } = signResult.data || {};
                        console.log(`${task.name}签到成功，连续签到${continuousSignDays}天，本月${signDays}天，总计${totalSignDays}天`);
                    } else {
                        console.log(`${task.name}签到: ${signResult?.message || '已签到或失败'}`);
                    }
                }

                // 获取积分
                const integralResult = await httpRequest({
                    method: 'POST',
                    url: 'https://cl-gateway.tuhu.cn/cl-integral-repository/integral/getIntegral',
                    headers,
                    data: '{}',
                });

                if (integralResult?.code === 10000) {
                    console.log(`当前积分: ${integralResult.data?.integral || 0}`);
                }
            } catch (e) {
                console.log(`账号[${idx}] 请求异常: ${e.message}`);
                success = false;
            }

            await new Promise(r => setTimeout(r, 2000));
        }
    }

    if (!success) process.exit(1);
}

tuhu();
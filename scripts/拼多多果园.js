/**
 * 拼多多果园任务脚本
 * 抓包：小程序或APP → 进果园一圈 → 请求头中搜索 AccessToken
 * 变量：ONESIGN_PDDGY_COOKIE（格式：accessToken#anti-token，多账号用 @ 或换行分隔）
 *
 * cron: 30 1,8,12,17 * * *
 * new Env('拼多多果园');
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

async function pddRequest(method, url, data, headers) {
    try {
        const options = {
            method,
            url,
            headers: {
                'Content-Type': 'application/json',
                'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_1 like Mac OS X) AppleWebKit/605.1.15',
                'Referer': 'https://mobile.yangkeduo.com/',
                ...headers,
            },
        };
        if (data) options.data = data;
        const response = await axios(options);
        return response.data;
    } catch (e) {
        if (e.response) return e.response.data;
        return null;
    }
}

async function pdd() {
    let success = true;
    console.log("【拼多多果园】：开始签到...");

    const cookie = getConfig("", "ONESIGN_PDDGY_COOKIE");
    if (!cookie) {
        console.log("【拼多多果园】：未配置 ONESIGN_PDDGY_COOKIE 变量");
        success = false;
    } else {
        const accounts = cookie.split(/[@\n]/).filter(t => t.trim());

        for (let i = 0; i < accounts.length; i++) {
            const idx = i + 1;
            const parts = accounts[i].trim().split('#');
            if (parts.length < 2) {
                console.log(`账号[${idx}] 格式错误，需要 accessToken#anti-token`);
                success = false;
                continue;
            }

            const accessToken = parts[0];
            const antiToken = parts[1];
            const headers = {
                'accesstoken': accessToken,
                'anti-token': antiToken,
            };

            console.log(`----- 账号[${idx}]开始执行 -----`);

            try {
                // 获取果园信息
                const infoResult = await pddRequest('GET',
                    'https://mobile.yangkeduo.com/proxy/api/api/orchard/info',
                    null, headers);

                if (infoResult && infoResult.success) {
                    const orchardInfo = infoResult.result;
                    console.log(`果树名称: ${orchardInfo.treeName || '未知'}`);
                    console.log(`水滴: ${orchardInfo.waterDrop || 0}`);
                    console.log(`化肥: ${orchardInfo.fertilizer || 0}`);
                    console.log(`进度: ${orchardInfo.progress ? (orchardInfo.progress * 100).toFixed(2) + '%' : '未知'}`);

                    // 签到
                    const signResult = await pddRequest('POST',
                        'https://mobile.yangkeduo.com/proxy/api/api/orchard/sign',
                        {}, headers);

                    if (signResult && signResult.success) {
                        console.log(`签到成功，获得 ${signResult.result || 0} 水滴`);
                    } else {
                        console.log(`签到: ${signResult?.errorMsg || '已签到或失败'}`);
                    }

                    // 浏览任务
                    const taskResult = await pddRequest('GET',
                        'https://mobile.yangkeduo.com/proxy/api/api/orchard/task/list',
                        null, headers);

                    if (taskResult && taskResult.success) {
                        const tasks = taskResult.result;
                        for (const task of tasks) {
                            if (task.status === 1) {
                                console.log(`执行任务: ${task.taskName}`);
                                const doResult = await pddRequest('POST',
                                    'https://mobile.yangkeduo.com/proxy/api/api/orchard/task/do',
                                    { taskId: task.taskId },
                                    headers);

                                if (doResult && doResult.success) {
                                    console.log(`  任务完成，获得 ${doResult.result || 0} 水滴`);
                                }
                                await new Promise(r => setTimeout(r, 2000));
                            }
                        }
                    }

                    // 领取奖励
                    const rewardResult = await pddRequest('POST',
                        'https://mobile.yangkeduo.com/proxy/api/api/orchard/reward',
                        {}, headers);

                    if (rewardResult && rewardResult.success) {
                        console.log(`领取奖励成功，获得 ${rewardResult.result || 0} 水滴`);
                    }
                } else {
                    console.log(`获取果园信息失败: ${JSON.stringify(infoResult)}`);
                    success = false;
                }
            } catch (e) {
                console.log(`账号[${idx}] 请求异常: ${e.message}`);
                success = false;
            }

            await new Promise(r => setTimeout(r, 3000));
        }
    }

    if (!success) process.exit(1);
}

pdd();
/*
cron: 30 8 * * *
new Env('阿里云盘签到');
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

const refreshToken = getConfig("aliyun.refresh_token", "ONESIGN_ALIYUN_REFRESH_TOKEN");

async function getAccessToken() {
    try {
        const res = await axios.post(
            "https://auth.aliyundrive.com/v2/account/token",
            {
                grant_type: "refresh_token",
                app_id: "pJZInNHN2dZWk8qg",
                refresh_token: refreshToken,
            },
            { headers: { "Content-Type": "application/json; charset=UTF-8" } }
        );
        if (res.data.code === "InvalidParameter.RefreshToken" || res.data.code === "RefreshTokenExpired") {
            console.log(`token刷新失败,${res.data.message}`);
            return null;
        }
        console.log(`用户: ${res.data.nick_name}`);
        return { name: res.data.nick_name, token: res.data.access_token };
    } catch (err) {
        console.log("token接口请求失败");
        console.log(err);
        return null;
    }
}

async function sign(token, name) {
    try {
        const res = await axios.post(
            "https://member.aliyundrive.com/v1/activity/sign_in_list",
            { isReward: false },
            {
                headers: {
                    "Content-Type": "application/json",
                    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/20D5024e iOS16.3 (iPhone15,2;zh-Hans-CN) App/4.1.3 AliApp(yunpan/4.1.3) com.alicloud.smartdrive/28278449 Channel/201200 AliApp(AYSD/4.1.3) com.alicloud.smartdrive/4.1.3 Version/16.3 Channel/201200 Language/zh-Hans-CN /iOS Mobile/iPhone15,2 language/zh-Hans-CN",
                    Authorization: "Bearer " + token,
                },
            }
        );
        if (res.data.success) {
            console.log(`${name}，已连续签到${res.data.result.signInCount}天!`);
            return res.data.result.signInCount;
        } else {
            console.log(`${name}，签到失败，${res.data.message}!`);
            return -1;
        }
    } catch (err) {
        console.log("签到接口请求失败");
        console.log(err);
        return -1;
    }
}

async function reward(token, day) {
    try {
        const res = await axios.post(
            "https://member.aliyundrive.com/v1/activity/sign_in_reward",
            { signInDay: day },
            {
                headers: {
                    "Content-Type": "application/json",
                    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/20D5024e iOS16.3 (iPhone15,2;zh-Hans-CN) App/4.1.3 AliApp(yunpan/4.1.3) com.alicloud.smartdrive/28278449 Channel/201200 AliApp(AYSD/4.1.3) com.alicloud.smartdrive/4.1.3 Version/16.3 Channel/201200 Language/zh-Hans-CN /iOS Mobile/iPhone15,2 language/zh-Hans-CN",
                    Authorization: "Bearer " + token,
                },
            }
        );
        if (res.data.success) {
            const r = res.data.result;
            console.log(`奖励: ${r.name}, ${r.description}, ${r.notice}!`);
        } else {
            console.log(`奖励获取失败: ${res.data.message}!`);
        }
    } catch (err) {
        console.log("奖励接口请求失败");
        console.log(err);
    }
}

async function aliyun() {
    const auth = await getAccessToken();
    if (!auth) {
        console.log("【阿里云盘】：token刷新失败");
        return;
    }
    const day = await sign(auth.token, auth.name);
    if (day > 0) {
        await reward(auth.token, day);
    }
    console.log("【阿里云盘】：签到完成");
}

aliyun();
/*
抓包：中国联通 app 登录后，抓包工具 → 请求 m.client.10010.com/mobileService/onLine.htm
      找到请求体中的 token_online 字段，复制值
      手机号、deviceId、appId 为可选参数
变量：ONESIGN_UNICOM_TOKEN_ONLINE / ONESIGN_UNICOM_PHONE / ONESIGN_UNICOM_DEVICEID / ONESIGN_UNICOM_APPID

cron: 0 9 * * *
new Env('中国联通签到');
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

const tokenOnline = getConfig("unicom.token_online", "ONESIGN_UNICOM_TOKEN_ONLINE");
const phone = getConfig("unicom.phone", "ONESIGN_UNICOM_PHONE");
const deviceId = getConfig("unicom.deviceId", "ONESIGN_UNICOM_DEVICEID");
const appId = getConfig("unicom.appId", "ONESIGN_UNICOM_APPID");

const headers = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 10; Redmi K30) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Mobile Safari/537.36",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "Origin": "https://m.client.10010.com",
    "Referer": "https://m.client.10010.com/",
};

let cookie = "";

async function onlineLogin() {
    try {
        const res = await axios.post(
            "https://m.client.10010.com/mobileService/onLine.htm",
            `token_online=${encodeURIComponent(tokenOnline)}&phone=${phone}&deviceId=${deviceId || ""}&appId=${appId || ""}`,
            { headers }
        );
        if (res.headers && res.headers["set-cookie"]) {
            cookie = res.headers["set-cookie"].map((c) => c.split(";")[0]).join("; ");
        }
        console.log("登录成功");
        return true;
    } catch (err) {
        console.log("登录失败");
        console.log(err);
        return false;
    }
}

async function daySign() {
    try {
        const res = await axios.post(
            "https://act.10010.com/SigninApp/signin/daySign",
            "",
            {
                headers: {
                    ...headers,
                    Cookie: cookie,
                    "Content-Type": "application/json",
                    Origin: "https://act.10010.com",
                    Referer: "https://act.10010.com/SigninApp/signin/index",
                },
            }
        );
        if (res.data && res.data.code === "0000") {
            console.log("签到成功");
            return true;
        } else if (res.data && res.data.code === "0001") {
            console.log("今日已签到");
            return true;
        } else {
            console.log(`签到失败: ${res.data && res.data.msg || "未知错误"}`);
            return false;
        }
    } catch (err) {
        console.log("签到接口请求失败");
        console.log(err);
        return false;
    }
}

async function unicom() {
    console.log("【中国联通】：开始签到...");
    const loginOk = await onlineLogin();
    if (!loginOk) {
        console.log("【中国联通】：登录失败，请检查token");
        return;
    }
    await daySign();
    console.log("【中国联通】：签到完成");
}

unicom();
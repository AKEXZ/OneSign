/*
抓包：1. 请求 m.client.10010.com/mobileService/onLine.htm → 请求体中的 token_online 字段
      2. 任意 act.10010.com 的请求 → Request Headers → 完整 Cookie 值
必填：ONESIGN_UNICOM_TOKEN_ONLINE（token_online） / ONESIGN_UNICOM_COOKIE（act.10010.com 的 Cookie）
可选：ONESIGN_UNICOM_PHONE（手机号） / ONESIGN_UNICOM_DEVICEID / ONESIGN_UNICOM_APPID

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
const sessionCookie = getConfig("unicom.cookie", "ONESIGN_UNICOM_COOKIE");

const ua = "Mozilla/5.0 (Linux; Android 15; RMX5062 Build/UKQ1.231108.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/130.0.6723.58 Mobile Safari/537.36; unicom{version:android@12.1500,desmobile:0};devicetype{deviceBrand:realme,deviceModel:RMX5062};OSVersion/15;ltst;";

const loginHeaders = {
    "User-Agent": ua,
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
};

const signHeaders = {
    "User-Agent": ua,
    "Content-Type": "application/x-www-form-urlencoded",
    "Origin": "https://img.client.10010.com",
    "Referer": "https://img.client.10010.com/SigininApp/index.html?cdncachetime=2977809&channel=shouye&webViewNavIsHidden=webViewNavIsHidden",
    "X-Requested-With": "com.sinovatech.unicom.ui",
};

let cookie = "";

async function onlineLogin() {
    try {
        const res = await axios.post(
            "https://m.client.10010.com/mobileService/onLine.htm",
            `token_online=${encodeURIComponent(tokenOnline)}&phone=${phone}&deviceId=${deviceId || ""}&appId=${appId || ""}`,
            { headers: loginHeaders }
        );
        if (res.headers && res.headers["set-cookie"]) {
            cookie = res.headers["set-cookie"].map((c) => c.split(";")[0]).join("; ");
        }
        if (sessionCookie) {
            cookie = cookie + "; " + sessionCookie;
        }
        console.log("登录成功");
        return true;
    } catch (err) {
        console.log("登录接口请求失败");
        return false;
    }
}

async function checkStatus() {
    try {
        const res = await axios.get(
            `https://activity.10010.com/sixPalaceGridTurntableLottery/signin/getContinuous?taskId=&channel=shouye&imei=${deviceId || ""}`,
            { headers: { ...signHeaders, Cookie: cookie } }
        );
        if (res.data && res.data.code === "0000" && res.data.data) {
            return res.data.data;
        }
        return null;
    } catch (err) {
        return null;
    }
}

async function signboard() {
    try {
        const res = await axios.post(
            "https://act.10010.com/SigninApp/convert/signboard",
            "",
            { headers: { ...signHeaders, Cookie: cookie } }
        );
        if (res.data && res.data.status === "0000") {
            console.log("签到成功");
            return true;
        }
        const msg = res.data && res.data.msg || "未知错误";
        if (msg.indexOf("已经签到") > -1 || msg.indexOf("已签到") > -1 || msg.indexOf("重复") > -1) {
            console.log("今日已签到");
            return true;
        }
        console.log(`签到失败: ${msg}`);
        return false;
    } catch (err) {
        console.log("签到接口请求失败");
        return false;
    }
}

async function unicom() {
    let success = true;
    console.log("【中国联通】：开始签到...");
    const loginOk = await onlineLogin();
    if (!loginOk) {
        console.log("【中国联通】：登录失败，请检查token");
        success = false;
    } else {
        const status = await checkStatus();
        if (status && status.todayIsSignIn === "y") {
            console.log(`今日已签到，连续${status.continueCount || "?"}天`);
            console.log("【中国联通】：签到完成");
        } else {
            const signOk = await signboard();
            if (signOk) {
                console.log("【中国联通】：签到完成");
            } else {
                console.log("【中国联通】：签到失败");
                success = false;
            }
        }
    }
    if (!success) process.exit(1);
}

unicom();
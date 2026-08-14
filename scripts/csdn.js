/*
cron: 25 8 * * *
new Env('CSDN签到');
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

const cookie = getConfig("csdn.cookie", "ONESIGN_CSDN_COOKIE");

function csdn() {
    return new Promise(async (resolve) => {
        let msg = "";
        const headers = {
            cookie: cookie,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
            "Referer": "https://www.csdn.net/",
        };
        try {
            const res = await axios.get("https://me.csdn.net/api/v2/sign/in", { headers });
            const data = res.data;
            if (data.code === 200) {
                msg = `签到成功! 连续签到${data.data?.continuousDays || "?"}天`;
            } else if (data.code === 400 && data.msg && data.msg.includes("已签到")) {
                msg = "今日已签到，无需重复签到";
            } else {
                msg = `签到失败: ${data.msg || "未知错误"}`;
            }
        } catch (err) {
            const status = err.response && err.response.status;
            if (status === 400 && err.response.data && err.response.data.msg && err.response.data.msg.includes("已签到")) {
                msg = "今日已签到，无需重复签到";
            } else if (status === 401 || status === 403) {
                console.log(err);
                msg = "cookie已失效，请重新获取";
            } else if (status === 404) {
                console.log(err);
                msg = "签到接口返回404，cookie可能已失效或接口已变更，请重新获取cookie";
            } else {
                console.log(err);
                msg = "签到接口请求出错";
            }
        }
        console.log(msg);
        resolve("【CSDN】: " + msg);
    });
}

module.exports = csdn;

if (require.main === module) {
    csdn().then(console.log);
}
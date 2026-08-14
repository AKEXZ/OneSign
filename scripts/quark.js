/*
抓包：浏览器打开 pan.quark.cn 登录后，F12 → Network → 任意请求
      找到 Request Headers 中的 Cookie 字段，整段复制
变量：ONESIGN_QUARK_COOKIE

cron: 10 8 * * *
new Env('夸克网盘签到');
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

const cookie = getConfig("quark.cookie", "ONESIGN_QUARK_COOKIE");

const headers = {
    "Content-Type": "application/json",
    Cookie: cookie,
};

async function qd_check() {
    return new Promise(async (resolve) => {
        try {
            const url = "https://drive-m.quark.cn/1/clouddrive/capacity/growth/info";
            const params = {
                pr: "ucpro",
                fr: "pc",
                uc_param_str: "",
            };
            const res = await axios.get(url, { headers, params });
            let msg;
            if (res.data.data.cap_sign.sign_daily) {
                const sign = res.data.data.cap_sign;
                const number = sign.sign_daily_reward / 1048576;
                const progress = Math.round(
                    (sign.sign_progress / sign.sign_target) * 100
                );
                console.log(`今日已签到,获取${number}MB，进度${progress}%`);
                msg = `今日已签到,获取${number}MB，进度${progress}%`;
            } else {
                msg = await qd();
            }
            resolve("【夸克网盘】：" + (msg || "正常运行了"));
        } catch (error) {
            console.log("签到接口请求失败");
            resolve("【夸克网盘】：签到接口请求失败");
        }
    });
}

function qd() {
    return new Promise(async (resolve) => {
        try {
            const url = "https://drive-m.quark.cn/1/clouddrive/capacity/growth/sign";
            const params = {
                pr: "ucpro",
                fr: "pc",
                uc_param_str: "",
            };
            const res = await axios.post(
                url,
                { sign_cyclic: true },
                { headers, params }
            );
            let msg;
            if (res.data.status == 200) {
                const sign = res.data.data;
                const number = sign.sign_daily_reward / 1048576;
                console.log(`签到成功,本次签到领取${number}MB`);
                msg = `签到成功,本次签到领取${number}MB`;
            } else {
                console.log(`签到失败，${res.data.message}!`);
                msg = "签到失败";
            }
            resolve(msg);
        } catch (error) {
            console.log("签到接口请求失败");
            resolve("签到接口请求失败");
        }
    });
}

async function quark() {
    if (!cookie) {
        return { success: false, msg: "【夸克网盘】：未配置cookie" };
    }
    const cookies = Array.isArray(cookie) ? cookie : [cookie];
    let allOk = true;
    for (let index = 0; index < cookies.length; index++) {
        headers["Cookie"] = cookies[index];
        const msg = await qd_check();
        if (msg.indexOf("失败") > -1) allOk = false;
    }
    return { success: allOk };
}

module.exports = quark;

if (require.main === module) {
    quark().then((result) => {
        if (result && !result.success) {
            process.exit(1);
        }
    });
}
/*
cron: 35 8 * * *
new Env('Gobing签到');
*/

const $http = require("axios");
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

const account = getConfig("gobing.account", "ONESIGN_GOBING_ACCOUNT");
const password = getConfig("gobing.password", "ONESIGN_GOBING_PASSWORD");

let result = "";
const headers = {
    "Content-Type": "application/json",
    Accept: "application/json, text/plain, */*",
    Origin: "https://www.gobing.cn",
    Referer: "https://www.gobing.cn/",
    "sec-ch-ua": '"Chromium";v="9", "Not?A_Brand";v="8"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-site",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "User-Agent":
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36 SLBrowser/9.0.3.1311 SLBChan/105",
    token: "",
};

function _log(msg) {
    console.log(msg);
    result += `${msg}\n`;
}

function getToken(account, password) {
    const data = {
        account: account,
        password: password,
    };
    return new Promise(async (resolve) => {
        let token;
        try {
            const response = await $http.post(
                "https://api.gobing.cn/v1/user/login",
                data
            );
            token = response.data.data?.token;
            resolve(token);
        } catch (err) {
            console.log(err.response);
        }
        resolve();
    });
}

function addsign(token) {
    return new Promise(async (resolve) => {
        try {
            headers["token"] = token;
            const url = "https://api.gobing.cn/v1/signin/signin";
            const res = await $http.post(url, {}, { headers });
            _log(`签到成功: ${res.data?.msg}`);
        } catch (err) {
            if (
                err.response.status == 400 &&
                err.response.data.msg.includes("成功签到")
            ) {
                _log(err.response.data?.msg);
            } else {
                console.error(
                    "Error sending GET request:",
                    err.response.data.msg
                );
                _log(`签到失败 ${err.response.status}`);
            }
        }
        resolve();
    });
}

async function gobing() {
    _log("【Gobing每日签到】:");
    const token = await getToken(account, password);

    if (token) {
        _log("获取token成功");
        await addsign(token);
    } else {
        _log("获取token失败");
    }

    return result;
}

module.exports = gobing;

if (require.main === module) {
    gobing().then(console.log);
}
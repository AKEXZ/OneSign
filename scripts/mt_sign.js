/*
cron: 15 8 * * *
new Env('MT论坛签到');
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

const cookie = getConfig("mt.cookie", "ONESIGN_MT_COOKIE");

function mt() {
    return new Promise(async (resolve) => {
        try {
            const header = {
                headers: {
                    cookie: cookie || "wenmoux",
                    "Referer": "https://bbs.binmt.cc/member.php?mod=logging&action=login&mobile=2"
                }
            };
            const res = await axios.get("https://bbs.binmt.cc/k_misign-sign.html", header);
            const formhash = res.data.match(/formhash=(.+?)&/);
            let msg;
            if (formhash && !res.data.match(/登录/)) {
                const signurl = `https://bbs.binmt.cc/k_misign-sign.html?operation=qiandao&format=button&formhash=${formhash[1]}&inajax=1&ajaxtarget=midaben_sign`;
                const res2 = await axios.get(signurl, header);
                if (res2.data.match(/今日已签/)) {
                    msg = "今天已经签到过啦";
                } else if (res2.data.match(/签到成功/)) {
                    const msg1 = res2.data.match(/获得随机奖励.+?金币/);
                    const msg2 = res2.data.match(/已累计签到 \d+ 天/);
                    msg = "签到成功\n" + msg1 + "\n" + msg2;
                } else {
                    msg = "签到失败!原因未知";
                    console.log(res2.data);
                }
            } else {
                msg = "cookie失效";
            }
            console.log(msg);
            resolve("【MT论坛】: " + msg);
        } catch (err) {
            console.log(err);
            resolve("【MT论坛】: 签到接口请求出错");
        }
    });
}

module.exports = mt;

if (require.main === module) {
    mt().then(console.log);
}
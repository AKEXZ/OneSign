/*
抓包：浏览器打开 bbs.binmt.cc 登录后，F12 → Network → 任意请求
      找到 Request Headers 中的 Cookie 字段，整段复制
变量：ONESIGN_MT_COOKIE

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
        let success = true;
        console.log("【MT论坛】：开始签到...");
        try {
            const header = {
                headers: {
                    cookie: cookie || "wenmoux",
                    "Referer": "https://bbs.binmt.cc/member.php?mod=logging&action=login&mobile=2"
                }
            };
            const res = await axios.get("https://bbs.binmt.cc/k_misign-sign.html", header);
            const formhash = res.data.match(/formhash=(.+?)&/);
            if (formhash && !res.data.match(/登录/)) {
                const signurl = `https://bbs.binmt.cc/k_misign-sign.html?operation=qiandao&format=button&formhash=${formhash[1]}&inajax=1&ajaxtarget=midaben_sign`;
                const res2 = await axios.get(signurl, header);
                if (res2.data.match(/今日已签/)) {
                    console.log("今天已经签到过啦");
                } else if (res2.data.match(/签到成功/)) {
                    const msg1 = res2.data.match(/获得随机奖励.+?金币/);
                    const msg2 = res2.data.match(/已累计签到 \d+ 天/);
                    console.log("签到成功\n" + msg1 + "\n" + msg2);
                } else {
                    console.log("签到失败!原因未知");
                    success = false;
                }
            } else {
                console.log("cookie失效");
                success = false;
            }
        } catch (err) {
            console.log("签到接口请求出错");
            success = false;
        }
        if (!success) process.exit(1);
        resolve();
    });
}

mt();
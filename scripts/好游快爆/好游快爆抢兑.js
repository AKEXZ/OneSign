/**
 * 好游快爆爆米花商城抢兑
 * 抓包：好游快爆 app → 爆米花商城 → 选择商品 → 分享给好友
 *      链接如 https://huodong3.3839.com/n/hykb/bmhstore2/inc/libao/index.php?gid=6237
 *      gid=6237 → 填 ONESIGN_HYKB_GID，key=libao → 填 ONESIGN_HYKB_KEY
 *      scookie 同好游快爆.js
 * 变量：ONESIGN_HYKB_COOKIE / ONESIGN_HYKB_GID / ONESIGN_HYKB_KEY
 *
 * cron: 59 12 * * *
 * new Env('好游快爆抢兑');
 */

const { getConfig } = (() => {
    const fs = require("fs");
    const path = require("path");
    function getConfig(key, envName) {
        if (process.env[envName]) return process.env[envName];
        try {
            const configPath = path.join(__dirname, "..", "..", "config.yml");
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

const axios = require("axios");
const hyck = getConfig("", "ONESIGN_HYKB_COOKIE");
const gid = getConfig("", "ONESIGN_HYKB_GID");
const key = getConfig("", "ONESIGN_HYKB_KEY");
const scookie = hyck && hyck.includes("|") ? encodeURIComponent(hyck) : hyck;

const UA = "Mozilla/5.0 (Linux; Android 8.0.0; FRD-AL10 Build/HUAWEIFRD-AL10; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/77.0.3865.120 MQQBrowser/6.2 TBS/045224 Mobile Safari/537.36";

async function post(a, b, key) {
    return new Promise(async (resolve) => {
        let back = null;
        try {
            const encodedKey = encodeURIComponent(key);
            const capitalizedKey = encodeURIComponent(key.slice(0, 1).toUpperCase() + key.slice(1));
            const res = await axios.post(
                `https://huodong3.3839.com/n/hykb/bmhstore2/inc/${encodedKey}/ajax${capitalizedKey}.php`,
                `ac=${a}&r=0.9948423196524376&${b}&scookie=${scookie}`,
                { headers: { "User-Agent": UA } }
            );
            back = res.data;
            console.log(JSON.stringify(res.data));
        } catch (err) {
            console.log(err.message);
        }
        resolve(back);
    });
}

async function exchange() {
    let success = true;
    console.log("【好游快爆抢兑】：开始抢兑...");

    if (!hyck) {
        console.log("【好游快爆抢兑】：未配置 ONESIGN_HYKB_COOKIE 变量");
        success = false;
    } else if (!gid) {
        console.log("【好游快爆抢兑】：未配置 ONESIGN_HYKB_GID 变量");
        success = false;
    } else if (!key) {
        console.log("【好游快爆抢兑】：未配置 ONESIGN_HYKB_KEY 变量");
        success = false;
    } else {
        let done = false;
        await post("checkExchange", `gid=${gid}`, key);
        for (let i = 0; i < 100; i++) {
            const res = await post("exchange", `goodsid=${gid}`, key);
            if (res && res.key === "ok") {
                console.log("抢兑成功！");
                done = true;
                break;
            }
        }
        if (!done) {
            console.log("抢兑失败，未抢到商品");
            success = false;
        }
    }

    if (!success) process.exit(1);
}

exchange();
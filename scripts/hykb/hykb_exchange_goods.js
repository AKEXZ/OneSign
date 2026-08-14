/*
抓包：好游快爆 app → 我的 → 爆米花商城 → 选择商品 → 分享给好友
      链接如 https://huodong3.3839.com/n/hykb/bmhstore2/inc/libao/index.php?gid=6237
      gid=6237 → 填 ONESIGN_HYKB_GID，key=libao → 填 ONESIGN_HYKB_KEY
      scookie 同 hykb.js
变量：ONESIGN_HYKB_SCOOKIE / ONESIGN_HYKB_GID / ONESIGN_HYKB_KEY

cron: 59 12 * * *
new Env('好游快爆抢兑');
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
const hyck = getConfig("hykb.scookie", "ONESIGN_HYKB_SCOOKIE");
const gid = getConfig("hykb.gid", "ONESIGN_HYKB_GID");
const key = getConfig("hykb.key", "ONESIGN_HYKB_KEY");
const scookie = hyck && hyck.match(/\|/) ? encodeURIComponent(hyck) : hyck;

async function get(a, b, key) {
    return new Promise(async (resolve) => {
        try {
            const encodedKey = encodeURIComponent(key);
            const capitalizedKey = encodeURIComponent(key.slice(0, 1).toUpperCase() + key.slice(1));
            const res = await axios.post(`https://huodong3.3839.com/n/hykb/bmhstore2/inc/${encodedKey}/ajax${capitalizedKey}.php`, `ac=${a}&r=0.9948423196524376&${b}&scookie=${scookie}`, {
                headers: {
                    "User-Agent": "Mozilla/5.0 (Linux; Android 8.0.0; FRD-AL10 Build/HUAWEIFRD-AL10; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/77.0.3865.120 MQQBrowser/6.2 TBS/045224 Mobile Safari/537.36 V1_AND_SQ_7.1.0_0_TIM_D TIM/3.0.0.2860 QQ/6.5.5  NetType/WIFI WebP/0.3.0 Pixel/1080"
                }
            });
            console.log(res.data);
        } catch (err) {
            console.log(err);
        }
        resolve();
    });
}

async function exchange() {
    console.log("【好游快爆】：抢兑物品...");
    let success = false;
    await get("checkExchange", `gid=${gid}`, key);
    for (let i = 0; i < 100; i++) {
        const res = await get("exchange", `goodsid=${gid}`, key);
        if (res && res.key === "ok") {
            console.log("抢兑成功");
            success = true;
            break;
        }
    }
    if (!success) process.exit(1);
}

exchange();
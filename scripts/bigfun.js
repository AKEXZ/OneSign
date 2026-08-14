/*
cron: 0 9 * * *
new Env('BigFun签到');
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

const token = getConfig("bigfun.token", "ONESIGN_BIGFUN_TOKEN");
const cookie = getConfig("bigfun.cookie", "ONESIGN_BIGFUN_COOKIE");
const comment = ["早", "路过", "哦哈呦", "每日打卡", "<p>[大黄脸_妙啊]</p>"];
const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
let loginStatus = true;

async function bget(method, data, postMethod) {
    try {
        const headers = {
            "x-csrf-token": token,
            "referer": "https://bigfun.bilibili.com/",
            "cookie": cookie,
            "User-Agent": "Mozilla/5.0 (Linux; Android 11; Redmi K30) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Mobile Safari/537.36",
        };
        let res;
        if (postMethod) {
            res = await axios.get(`https://bigfun.bilibili.com/api/client/web?method=${method}`, { headers });
        } else {
            res = await axios.post(`https://bigfun.bilibili.com/api/client/web?method=${method}`, data, { headers });
            console.log(JSON.stringify(res.data));
        }
        return res.data;
    } catch (err) {
        if (err.response && err.response.data && err.response.data.errors && err.response.data.errors.code === 403) {
            loginStatus = false;
            console.log("cookie或token已失效,结束任务");
        } else {
            console.log(err);
        }
        return null;
    }
}

async function bigfun() {
    await bget("checkIn", "");

    if (!loginStatus) {
        console.log("【BigFun】：token或cookie已失效");
        return;
    }

    await bget("like", { type: 1, action: 1, id: 1175302 });
    await bget("follow", { type: 1, to_user_id: "17995983" });

    const formData = await bget("getForumPostList&forum_id=1&page=1&limit=25&sort=time&get_sub_forum_posts=1", "", "get");
    if (formData && formData.data) {
        const ForumPostList = formData.data;
        for (let i = 0; i < Math.min(5, ForumPostList.length); i++) {
            const formId = ForumPostList[i].id;
            console.log(`第${i + 1}次点赞 ${formId}`);
            await bget("like", { type: 1, action: 1, id: formId });
            await sleep(1000);
        }
    }

    const myInfo = await bget("getUserProfile", "", "get");
    if (myInfo && myInfo.data && myInfo.data[0]) {
        const Info = myInfo.data[0];
        const msg = `【BigFun】：\n昵称：${Info.nickname}\n等级：Lv${Info.level}\n签到：连签${Info.continued_check_in_days}天/共签${Info.check_in_days}天\n经验值：${Info.current_exp}/${Info.upgrade_exp}`;
        console.log(msg);
    }
}

bigfun();
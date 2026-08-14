/**
 * 好游快爆爆米花任务，可兑换激活码、实物周边等
 * 抓包：好游快爆 app → 爆米花页面 → 抓包获取 scookie（完整的 cookie 值）
 * 变量：ONESIGN_HYKB_COOKIE（scookie 值，多账号用 @ 或换行分隔）
 *
 * cron: 0 8,12,18 * * *
 * new Env('好游快爆');
 */

const axios = require("axios");
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

// 照料好友 id 列表
const buid = [
    21039293, 48653684, 44191145, 54216701, 54184381, 38442812, 34977383,
    54099572, 54060137, 18344113, 53334988, 49100316, 24158995, 53043395,
    53746196, 7495782, 53752398, 13268805, 53540861, 53169378, 53481728,
    53480955, 53236037, 5015419, 17998323, 142234, 53043027, 53022651,
    52883552, 52919017, 52883915, 2987459, 52863870,
];

const UA = "Mozilla/5.0 (Linux; Android 8.0.0; FRD-AL10 Build/HUAWEIFRD-AL10; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/77.0.3865.120 MQQBrowser/6.2 TBS/045224 Mobile Safari/537.36";

function hykbGet(scookie, a, b) {
    return new Promise(async (resolve) => {
        let back = null;
        try {
            let res = await axios.post(
                `https://huodong3.3839.com/n/hykb/${a}/ajax.php`,
                `ac=${b}&r=0.${Math.round(Math.random() * 8999999999999999) + 1000000000000000}&scookie=${scookie}`,
                { headers: { "User-Agent": UA } }
            );

            const data = typeof res.data === "string" ? JSON.parse(res.data) : res.data;

            if (JSON.stringify(data).includes("玉米成熟度已经达到100")) {
                await hykbGet(scookie, "grow", "PlantRipe");
                await hykbGet(scookie, "grow", "PlantSow");
                await hykbGet(scookie, a, b);
            }
            if (JSON.stringify(data).includes("还没有播种玉米")) {
                let bzs = await hykbGet(scookie, "grow", "PlantSow");
                if (bzs && bzs.seed === 0) {
                    await hykbGet(scookie, "grow", "GouMai&resure=1&gmmode=seed&tmpNum=10");
                    await hykbGet(scookie, "grow", "PlantSow");
                }
                await hykbGet(scookie, a, b);
            }

            back = data;
        } catch (err) {
            console.log(err.message);
        }
        resolve(back);
    });
}

async function getTaskIds() {
    let ids = [];
    try {
        let res = await axios.get("https://huodong3.3839.com/n/hykb/gs/index.php");
        let str = res.data.match(/HdmodelUser\.Ling\((.+?)\)/g);
        if (str) ids = str;

        let res2 = await axios.get("https://huodong3.3839.com/n/hykb/grow/daily.php");
        let str2 = res2.data.match(/ACT\.Daily[a-z,A-Z]+(Share|Ling|JiaoHu){1,}\(\d+\)/g);
        if (str2) ids = ids.concat(str2);
    } catch (err) {
        console.log("获取任务id失败: " + err.message);
    }
    return ids;
}

async function getGameSignIds() {
    let items = [];
    try {
        let cheerio;
        try { cheerio = require("cheerio"); } catch (e) {
            console.log("缺少 cheerio 依赖，跳过游戏签到");
            return items;
        }
        let res = await axios.get("https://huodong3.3839.com/n/hykb/qdjh/index.php");
        const $ = cheerio.load(res.data);
        $(".glist>li").each((index, li) => {
            if (!$(".btn", li).attr("onclick")?.match(/已结束/)) {
                let str = $(".btn", li).attr("onclick").replace(/每日签到领/, "").split("'");
                items.push({
                    title: str[3],
                    id: str[1].match(/hd_id=(.+)/)[1],
                });
            }
        });
    } catch (err) {
        console.log("获取游戏签到列表失败: " + err.message);
    }
    return items;
}

async function gameSignIn(scookie, items) {
    let gameCount = 0;
    for (const item of items) {
        try {
            await axios.post(
                "https://huodong3.3839.com/n/hykb/signcard/ajax.php",
                `ac=login&t=2020-08-3+11%3A14%3A48&r=0.9948423196524376&hd_id=${item.id}&hd_id2=${item.id}&scookie=${scookie}`,
                { headers: { "User-Agent": UA } }
            );

            let dataRes = await axios.post(
                "https://huodong3.3839.com/n/hykb/signcard/ajax.php",
                `ac=signToday&t=2020-08-3+11%3A14%3A48&r=0.9948423196524376&hd_id=${item.id}&hd_id2=${item.id}&scookie=${scookie}`,
                { headers: { "User-Agent": UA } }
            );

            const key = dataRes.data?.key;
            if (key === "-1005") {
                console.log(`${item.title} 体验游戏中,请一分钟后再刷新领取`);
                await axios.post(
                    "https://huodong3.3839.com/n/hykb/signcard/ajax.php",
                    `ac=tiyan&t=2020-08-3+11%3A14%3A48&r=0.9948423196524376&hd_id=${item.id}&hd_id2=${item.id}&scookie=${scookie}`,
                    { headers: { "User-Agent": UA } }
                );
                gameCount++;
            } else if (key === "-1007") {
                await axios.post(
                    "https://huodong3.3839.com/n/hykb/signcard/ajax.php",
                    `ac=sharelimit&t=2020-08-3+11%3A14%3A48&r=0.9948423196524376&hd_id=${item.id}&hd_id2=${item.id}&scookie=${scookie}`,
                    { headers: { "User-Agent": UA } }
                );
                console.log(`${item.title} 分享成功`);
                gameCount++;
            } else if (key === "-1002") {
                console.log(`${item.title} 今日已签`);
                gameCount++;
            } else if (key === "200") {
                gameCount++;
                console.log(`${item.title} 签到成功 已签到${dataRes.data.signnum}天`);
            } else if (key === "no_login") {
                console.log("scookie失效,请重新配置");
                break;
            } else {
                console.log(`${item.title}: ${JSON.stringify(dataRes.data)}`);
            }
        } catch (err) {
            console.log(`游戏签到 ${item.title} 失败: ${err.message}`);
        }
    }
    console.log(`游戏签到完成: ${gameCount}个`);
}

async function runOneAccount(scookie, idx) {
    console.log(`----- 账号[${idx}]开始执行 -----`);

    let loginData = await hykbGet(scookie, "grow", "Dailylogin&id=174");
    if (!loginData || loginData.key !== "ok") {
        if (typeof loginData === "string" && loginData.indexOf("<!DOCTYPE") > -1) {
            console.log(`账号[${idx}] scookie已失效，请重新抓包获取`);
        } else {
            console.log(`账号[${idx}] 登录失败: ${loginData?.key || "未知错误"}`);
        }
        return false;
    }

    let exData = await hykbGet(scookie, "kbexam", "login");
    if (!exData || exData.config?.lyks !== 1) {
        console.log("请先完成礼仪考试,再运行脚本");
        return false;
    }

    console.log(`用户: ${loginData.name || "未知"}`);

    try {
        let mres = await axios.get("https://ghproxy.com/https://raw.githubusercontent.com/Wenmoux/sources/master/other/miling.json");
        if (mres.data?.miling) {
            await hykbGet(scookie, "friend", `Secretorder&miling=${mres.data.miling}`);
        }
        if (mres.data?.egg) {
            await hykbGet(scookie, "wxsph", `send_egg&egg_data=${mres.data.egg}`);
        }
    } catch (e) {
        console.log("获取密令失败, 跳过: " + e.message);
    }

    await hykbGet(scookie, "grow", "GuanZhu&singleUid=21039293");
    await hykbGet(scookie, "signhelp", "useCode&code=21039293");
    await hykbGet(scookie, "friend", "LingXinrenFuli");
    await hykbGet(scookie, "grow", "shareEwai");
    await hykbGet(scookie, "grow", "Watering&id=6");

    let canCare = true;
    let mode = 0;
    for (const uid of buid) {
        if (mode !== 2) {
            if (canCare) {
                let zlres = await hykbGet(scookie, "grow", `gamehander&buid=${uid}&icon_id=58`);
                if (zlres) {
                    mode = zlres.mode;
                    if (zlres.sy_day_shijian_corn_max_num === 0) canCare = false;
                }
            }
            if (uid !== 21039293) {
                let stealRes = await hykbGet(scookie, "grow", `gamehander&buid=${uid}&icon_id=888888`);
                if (stealRes) console.log(`偷 ${uid} 玉米: ${stealRes.msg}`);
            }
        }
        await new Promise(r => setTimeout(r, 1000));
    }

    let taskIds = await getTaskIds();
    for (let task of taskIds) {
        let match = task.match(/\.(.+)\((\d+)\)/);
        if (!match) continue;
        let taskType = match[1];
        let taskId = match[2];

        try {
            switch (taskType) {
                case "Ling":
                    await hykbGet(scookie, "gs", `recordshare&gameid=${taskId}`);
                    await hykbGet(scookie, "gs", `ling&gameid=${taskId}`);
                    break;
                case "DailyShare":
                    await hykbGet(scookie, "grow", `DailyShare&id=${taskId}`);
                    await hykbGet(scookie, "grow", `DailyShareCallb&id=${taskId}`);
                    await hykbGet(scookie, "grow", `DailyShare&id=${taskId}`);
                    break;
                case "DailyAppLing":
                    await hykbGet(scookie, "grow", `DailyAppJump&id=${taskId}`);
                    await hykbGet(scookie, "grow", `DailyAppLing&id=${taskId}`);
                    break;
                case "DailyGameCateLing":
                    await hykbGet(scookie, "grow", `DailyGameCateJump&id=${taskId}`);
                    await hykbGet(scookie, "grow", `DailyGameCateLing&id=${taskId}`);
                    break;
                case "DailyGameLing":
                    await hykbGet(scookie, "grow", `DailyGamePlay&id=${taskId}`);
                    await hykbGet(scookie, "grow", `DailyGameLing&id=${taskId}`);
                    break;
                case "DailyYuyueLing":
                    await hykbGet(scookie, "grow", `DailyYuyueLing&id=${taskId}`);
                    break;
                case "DailyDouyinLing":
                    await hykbGet(scookie, "grow", "DailyDouyinCheck", taskId);
                    await hykbGet(scookie, "grow", "DailyDouyinPlay", taskId);
                    await hykbGet(scookie, "grow", "DailyDouyinLing", taskId);
                    break;
                case "DailyVideoLing":
                    await hykbGet(scookie, "grow", `DailyVideoGuanzhu&id=${taskId}`);
                    await hykbGet(scookie, "grow", `DailyVideoShare&id=${taskId}`);
                    await hykbGet(scookie, "wxsph", "share&mode=qq");
                    await hykbGet(scookie, "grow", `DailyVideoLing&id=${taskId}`);
                    break;
                case "DailyJiaoHu":
                    await hykbGet(scookie, "grow", `DailyJiaoHu&id=${taskId}`);
                    break;
                case "DailyDati":
                    let qData = await hykbGet(scookie, "grow", "DailyDati&id=4");
                    if (qData && qData.option1 && qData.expand) {
                        let yxid = qData.expand.split("##")[1] || "16876";
                        try {
                            let url = `https://api.3839app.com/cdn/android/gameintro-home-1546-id-${yxid}-packag--level-2.htm`;
                            let answerRes = await axios.get(url);
                            if (answerRes.data?.result) {
                                let strr = JSON.stringify(answerRes.data.result.data.downinfo.appinfo)
                                    .replace(/&nbsp;/g, "").replace(/ /g, "");
                                let isReverse = /错误|不属于|不是|不存在|没有|不需要|不能|不可以/.test(qData.title);
                                let kw = 1;
                                for (let k = 1; k < 5; k++) {
                                    let opt = (qData["option" + k] || "").replace(/ /g, "");
                                    if (isReverse ? !strr.includes(opt) : strr.includes(opt)) {
                                        kw = k;
                                        break;
                                    }
                                }
                                console.log("正确答案: " + qData["option" + kw]);
                                await hykbGet(scookie, "grow", `DailyDatiAnswer&option=${qData["option" + kw]}&id=4`);
                            }
                        } catch (e) {
                            console.log("找不到答案,请自行去app答题");
                        }
                    } else {
                        console.log("找不到答案,请自行去app答题");
                    }
                    break;
                case "DailyFriendLing":
                    await hykbGet(scookie, "grow", `DailyFriendLing&id=${taskId}`);
                    break;
                case "DailyInviteLing":
                    await hykbGet(scookie, "grow", `DailyInviteLing&id=${taskId}`);
                    break;
                default:
                    console.log(`未知任务类型: ${taskType}`);
            }
        } catch (e) {
            console.log(`任务 ${taskType}(${taskId}) 执行失败: ${e.message}`);
        }
    }

    try {
        let actRes = await axios.get("https://ghproxy.com/https://raw.githubusercontent.com/Wenmoux/sources/master/other/activities.js");
        if (actRes.data) {
            if (typeof eval("typeof task1") === "undefined") {
                eval(actRes.data);
            }
            if (typeof task1 === "function") {
                await task1();
            }
        }
    } catch (e) {
        console.log("获取额外活动失败: " + e.message);
    }

    let csData = await hykbGet(scookie, "grow", "Dailylogin&id=174");
    if (csData && csData.key === "ok" && csData.config) {
        let info = csData.config;
        let exInfo = exData.config;
        console.log(`昵称: ${info.name}`);
        console.log(`种子: ${info.seed} 爆米花: ${info.baomihua} 成熟度: ${info.chengshoudu}`);
        console.log(`荣誉等级: ${exInfo.tag_title}`);

        if (info.chengshoudu == 100) {
            await hykbGet(scookie, "grow", "PlantRipe");
            await hykbGet(scookie, "grow", "PlantSow");
        }
    }

    let gameItems = await getGameSignIds();
    if (gameItems.length > 0) {
        await gameSignIn(scookie, gameItems);
    }

    console.log(`----- 账号[${idx}]执行完成 -----`);
    return true;
}

async function hykb() {
    let success = true;
    console.log("【好游快爆】：开始执行...");

    const cookie = getConfig("", "ONESIGN_HYKB_COOKIE");
    if (!cookie) {
        console.log("【好游快爆】：未配置 ONESIGN_HYKB_COOKIE 变量");
        success = false;
    } else {
        const cookies = cookie.split(/[@\n]/).filter(t => t.trim());

        for (let i = 0; i < cookies.length; i++) {
            let scookie = cookies[i].trim();
            scookie = scookie.includes("|") ? encodeURIComponent(scookie) : scookie;
            const ok = await runOneAccount(scookie, i + 1);
            if (!ok) success = false;
            if (i < cookies.length - 1) await new Promise(r => setTimeout(r, 3000));
        }
    }

    if (!success) process.exit(1);
}

hykb();
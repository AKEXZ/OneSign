/*
抓包：好游快爆 app → 我的 → 赚爆米花 → 任务，抓任意 POST 请求
      请求体中的 scookie 字段，复制整段值
      请求头中的 User-Agent 复制整段（可选）
变量：ONESIGN_HYKB_SCOOKIE / ONESIGN_HYKB_QQ / ONESIGN_UA

cron: 5 8 * * *
new Env('好游快爆签到');
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

//好游快爆爆米花任务,可兑换激活码、实物周边等
//我的邀请码 sdvf180uscf3
let result = "【好游快爆】：";
const $http = axios = require("axios");
const hyck = getConfig("hykb.scookie", "ONESIGN_HYKB_SCOOKIE");
const qq = getConfig("hykb.qq", "ONESIGN_HYKB_QQ") || null;
const globalUA = getConfig("hykb.UA", "ONESIGN_UA");
//照料id 我没加好友所以随机取得 第一个是我,不建议改ヽ(*´з｀*)ﾉ
//   const moment=require("moment")
var uid = ""
//照料id 我没加好友所以随机取得 第一个是我,不建议改ヽ(*´з｀*)ﾉ
buid = [21039293,48653684,44191145,54216701,54184381,38442812,34977383,54099572,54060137,18344113,53950826,53334988,49100316,24158995,53043395,53746196,7495782,53752398,13268805,53540861,53169378,53481728,53480955,53236037,5015419,17998323,142234,53043027,53022651,52883552,52919017,52883915,2987459,52863870]
scookie = hyck.match(/\|/)?encodeURIComponent(hyck):hyck
function get(a, b) {
  return new Promise(async (resolve) => {
    try {
      let res = await axios.post(
        `https://huodong3.3839.com/n/hykb/${a}/ajax.php`,
        `ac=${b}&r=0.${Math.round(Math.random() * 8999999999999999) + 1000000000000000}&scookie=${scookie}`,
        {
          headers: {
            "User-Agent":
              globalUA || "Mozilla/5.0 (Linux; Android 8.0.0; FRD-AL10 Build/HUAWEIFRD-AL10; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/77.0.3865.120 MQQBrowser/6.2 TBS/045224 Mobile Safari/537.36 V1_AND_SQ_7.1.0_0_TIM_D TIM/3.0.0.2860 QQ/6.5.5  NetType/WIFI WebP/0.3.0 Pixel/1080",
          },
        }
      );

      if (JSON.stringify(res.data).match(/玉米成熟度已经达到100/)) {
        await get("grow", "PlantRipe"); //收获
        await get("grow", "PlantSow"); //播种
        await get(a, b); //播种        
      }
      if (JSON.stringify(res.data).match(/还没有播种玉米/)) {
          let bzs = await get("grow", "PlantSow"); //播种
          if (bzs.seed && bzs.seed == 0) {
            //    console.log("莫得种子了")
            await get("grow", "GouMai&resure=1&gmmode=seed&tmpNum=10"); //购买种子*10
            await get("grow", "PlantSow"); //播种
          }
          await get(a, b);
        }

        back = res.data;      
    } catch (err) {
      console.log(err);
    }
    resolve(back);
  });
}

function getid() {
  return new Promise(async (resolve) => {
    try {
      let res = await axios.get(
        "https://huodong3.3839.com/n/hykb/gs/index.php"
      );
      //预约游戏id
      str = res.data.match(/HdmodelUser\.Ling\((.+?)\)/g);
      let res2 = await axios.get(
        "https://huodong3.3839.com/n/hykb/grow/daily.php"
      );
      //任务id
      str2 = res2.data.match(
        /ACT\.Daily[a-z,A-Z]+(Share||Ling||JiaoHu){1,}\(\d+\)/g
      );
      id = str.concat(str2);
    } catch (err) {
      console.log(err);
    }
    resolve();
  });
}
async function task() {
    let success = true;
    console.log("【好游快爆】：开始签到...");
    let logindata = await get("grow", "Dailylogin&id=174");
    if (logindata.key == "ok") {
        exdata = await get("kbexam", "login");
        if (exdata.config.lyks == 1) {
            var mres = await axios.get(
                "https://ghproxy.com/https://raw.githubusercontent.com/Wenmoux/sources/master/other/miling.json"
            );
            await get("friend", `Secretorder&miling=${mres.data.miling}`);
            await get("wxsph", `send_egg&egg_data=${mres.data.egg}`);
            await get("grow", "GuanZhu&singleUid=21039293");
            await get("signhelp", "useCode&code=21039293");
            await get("friend", "LingXinrenFuli");
            await get("grow", "shareEwai");
            await getid();
            await get("grow", "Watering&id=6");
            let canzl = true;
            let mode = 0;
            for (i of buid) {
                if (mode != 2) {
                    if (canzl) {
                        let zlres = await get("grow", `gamehander&buid=${i}&icon_id=58`);
                        mode = zlres.mode;
                        if (zlres.sy_day_shijian_corn_max_num == 0) canzl = false;
                    }
                    if (i != 21039293) {
                        let stealres = await get("grow", `gamehander&buid=${i}&icon_id=888888`, true);
                        console.log(`偷 ${i}玉米 ${stealres.msg}`);
                    }
                }
            }
            for (i of id) {
                i = i.match(/\.(.+)\((\d+)\)/);
                if (!i) continue;
                switch (i[1]) {
                    case "Ling":
                        await get("gs", `recordshare&gameid=${i[2]}`);
                        await get("gs", `ling&gameid=${i[2]}`);
                        break;
                    case "DailyShare":
                        await get("grow", `DailyShare&id=${i[2]}`);
                        await get("grow", `DailyShareCallb&id=${i[2]}`);
                        await get("grow", `DailyShare&id=${i[2]}`);
                        break;
                    case "DailyAppLing":
                        await get("grow", `DailyAppJump&id=${i[2]}`);
                        await get("grow", `DailyAppLing&id=${i[2]}`);
                        break;
                    case "DailyGameCateLing":
                        await get("grow", `DailyGameCateJump&id=${i[2]}`);
                        await get("grow", `DailyGameCateLing&id=${i[2]}`);
                        break;
                    case "DailyGameLing":
                        await get("grow", `DailyGamePlay&id=${i[2]}`);
                        await get("grow", `DailyGameLing&id=${i[2]}`);
                        break;
                    case "DailyYuyueLing":
                        await get("grow", `DailyYuyueLing&id=${i[2]}`);
                        break;
                    case "DailyDouyinLing":
                        await get("grow", "DailyDouyinCheck", i[2]);
                        await get("grow", "DailyDouyinPlay", i[2]);
                        await get("grow", "DailyDouyinLing", i[2]);
                        break;
                    case "DailyVideoLing":
                        await get("grow", `DailyVideoGuanzhu&id=${i[2]}`);
                        await get("grow", `DailyVideoShare&id=${i[2]}`);
                        await get("wxsph", "share&mode=qq");
                        await get("grow", `DailyVideoLing&id=${i[2]}`);
                    case "DailyJiaoHu":
                        await get("grow", `DailyJiaoHu&id=${i[2]}`);
                        break;
                    case "DailyDati":
                        let ress = await get("grow", "DailyDati&id=4");
                        if (ress.option1 && ress.expand) {
                            let kw = 1;
                            let yxid = ress.expand.split("##")[1] || "16876";
                            let urll = `https://api.3839app.com/cdn/android/gameintro-home-1546-id-${yxid}-packag--level-2.htm`;
                            let resss = await axios.get(urll);
                            if (resss.data.result) {
                                let strr = JSON.stringify(resss.data.result.data.downinfo.appinfo)
                                    .replace(/&nbsp;/g, "")
                                    .replace(/ /g, "");
                                let reg = /错误|不属于|不是|不存在|没有|不需要|不能|不可以/;
                                if (reg.test(ress.title)) {
                                    for (let j = 1; j < 5; j++) {
                                        let strrr = ress["option" + j].replace(/ /g, "");
                                        if (!strr.match(strrr)) kw = j;
                                    }
                                } else {
                                    for (let j = 1; j < 5; j++) {
                                        let strrr = ress["option" + j].replace(/ /g, "");
                                        if (strr.match(strrr)) kw = j;
                                    }
                                }
                            }
                            console.log("正确答案: " + ress["option" + kw]);
                            await get("grow", `DailyDatiAnswer&option=${ress["option" + kw]}&id=4`);
                        }
                        break;
                    case "DailyFriendLing":
                        await get("grow", `DailyFriendLing&id=${i[2]}`);
                        break;
                    case "DailyInviteLing":
                        await get("grow", `DailyInviteLing&id=${i[2]}`);
                        break;
                }
            }
            try {
                let tasl1data = await axios.get(
                    "https://ghproxy.com/https://raw.githubusercontent.com/Wenmoux/sources/master/other/activities.js"
                );
                eval(tasl1data.data);
                await task1();
            } catch (e) {}
            let csdata = await get("grow", `Dailylogin&id=174`);
            if (csdata.key == "ok" && csdata.config) {
                let csinfo = csdata.config;
                let exinfo = exdata.config;
                console.log(`昵称：${csinfo.name}`);
                console.log(`种子：${csinfo.seed} 爆米花：${csinfo.baomihua}`);
                console.log(`成熟度：${csinfo.chengshoudu}  荣誉等级：${exinfo.tag_title}`);
                if (csinfo.chengshoudu == 100) {
                    await get("grow", "PlantRipe");
                    await get("grow", "PlantSow");
                }
            }
        } else {
            console.log("请先进行礼仪考试,再运行脚本");
        }
    } else {
        if (typeof logindata === "string" && logindata.indexOf("<!DOCTYPE") > -1) {
            console.log("scookie已失效，请重新抓包获取");
        } else {
            console.log(logindata.key || "登录失败，请检查scookie");
        }
        success = false;
    }
    if (!success) process.exit(1);
}

task();
/*
cron: 28 8 * * *
new Env('OneSign');
*/
const yaml = require("js-yaml");
const fs = require('fs');
const yargsModule = require('yargs/yargs');
const yargs = yargsModule.default || yargsModule;
const { hideBin } = require('yargs/helpers');
var argv = yargs(hideBin(process.argv)).argv;
const axios = require('axios');

var config = null, sendmsg = null, signlist = [], logs = "", needPush = false, signList = [];

if (fs.existsSync("./sendNotify.js")) var notify = require('./sendNotify');

async function go() {
    let ycurl = process.env.ycurl;
    if (ycurl) {
        await getCF(ycurl);
    } else {
        if (fs.existsSync("./config.yml")) {
            config = yaml.load(fs.readFileSync('./config.yml', 'utf8'));
        } else {
            console.log("配置文件 config.yml 不存在，请复制 config.yml.temple 并改名为 config.yml 后填写配置");
            return;
        }
    }

    if (config && config.Push) sendmsg = require("./sendmsg");
    if (config) signlist = config.cbList.split("&");
    if (config && config.needPush) needPush = true;
    signList = (argv._.length) > 0 ? argv._ : signlist;
    start(signList);
}

function start(taskList) {
    return new Promise(async (resolve) => {
        try {
            console.log("任务个数  " + taskList.length);
            console.log("------------开始签到任务------------");
            for (let i = 0; i < taskList.length; i++) {
                console.log(`任务${i + 1}执行中`);
                let exists = fs.existsSync(`./scripts/${taskList[i]}.js`);
                if (exists) {
                    const task = require(`./scripts/${taskList[i]}.js`);
                    let taskResult = await task();
                    if (taskResult && taskResult.match(/单独通知|cookie|失效|失败|出错|重新登录/)) {
                        if (sendmsg) await sendmsg(taskResult);
                    } else {
                        logs += taskResult + "    \n\n";
                    }
                } else {
                    logs += `${taskList[i]}  不存在该脚本文件,请确认输入是否有误\n\n`;
                    console.log("不存在该脚本文件,请确认输入是否有误");
                }
            }
            console.log("------------任务执行完毕------------\n");

            let hasCustomPushChannel = false;
            if (config && config.Push) {
                hasCustomPushChannel =
                    config.Push.sckey ||
                    (config.Push.qywx && config.Push.qywx.corpsecret) ||
                    (config.Push.tgpushkey && config.Push.tgpushkey.tgbotoken) ||
                    config.Push.qmsgkey ||
                    config.Push.pushplustoken ||
                    (config.Push.vocechat && config.Push.vocechat.key);
            }

            if (needPush) {
                if (sendmsg) {
                    let fullLogs = logs + "\n\n吹水群：https://t.me/htuoypa";
                    await sendmsg(fullLogs);
                }
                if (!hasCustomPushChannel && notify) {
                    await notify.sendNotify("OneSign", `${logs}\n\n吹水群：https://t.me/htuoypa`);
                }
            } else {
                console.log(logs);
            }
        } catch (err) {
            console.log(err);
        }
        resolve();
    });
}

function getCF(ycurl) {
    return new Promise(async (resolve) => {
        try {
            console.log("------------开始获取远程配置文件------------");
            let rr = await axios.get(ycurl);
            if (rr && rr.data) var rconfig = rr.data;
            if (rconfig.match(/cbList/)) {
                console.log("------------获取远程配置文件成功------------");
                config = yaml.load(rconfig);
            } else {
                console.log("远程配置文件有误");
                return;
            }
        } catch (err) {
            console.log(err);
            console.log("远程配置文件有误");
        }
        resolve();
    });
}

go();
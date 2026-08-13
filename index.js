// 呆呆面板入口

const yaml = require("js-yaml");
const fs = require('fs');
const yargs = require('yargs');
var argv = yargs.argv;

var config = null, signlist = [], logs = "";

if (fs.existsSync("./config.yml")) config = yaml.load(fs.readFileSync('./config.yml', 'utf8'));

if (config) signlist = config.cbList.split("&");

var signList = (argv._.length) > 0 ? argv._ : signlist;

function start(taskList) {
    return new Promise(async (resolve) => {
        try {
            console.log("任务个数  " + signList.length);
            console.log("------------开始签到任务------------");
            for (let i = 0; i < taskList.length; i++) {
                console.log(`任务${i + 1}执行中`);
                let exists = fs.existsSync(`./scripts/${taskList[i]}.js`);
                if (exists) {
                    const task = require(`./scripts/${taskList[i]}.js`);
                    logs += await task() + "    \n\n";
                } else {
                    logs += `${taskList[i]}  不存在该脚本文件,请确认输入是否有误\n\n`;
                    console.log("不存在该脚本文件,请确认输入是否有误");
                }
            }
            console.log("------------任务执行完毕------------\n");
        } catch (err) {
            console.log(err);
        }
        resolve();
    });
}

start(signList);
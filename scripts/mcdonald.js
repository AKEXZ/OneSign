/*
抓包：麦当劳 app 登录后，抓包工具 → 任意 API 请求
      找到 Request Headers 中的 Authorization 字段（Bearer xxx），复制整段
变量：ONESIGN_MCDONALD_TOKEN

cron: 0 9 * * *
new Env('麦当劳MCP领券');
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

const token = getConfig("mcdonald.token", "ONESIGN_MCDONALD_TOKEN");
const baseURL = "https://mcp.mcd.cn/mcp-servers/mcd-mcp";

let result = "【麦当劳MCP】：";

function request(toolName, args = {}) {
    return new Promise(async (resolve, reject) => {
        try {
            const headers = {
                "Authorization": `Bearer ${token}`,
                "Content-Type": "application/json"
            };

            const requestBody = {
                jsonrpc: "2.0",
                id: Date.now(),
                method: "tools/call",
                params: {
                    name: toolName,
                    arguments: args
                }
            };

            const res = await axios.post(baseURL, requestBody, { headers });

            if (res.data && res.data.result) {
                resolve(res.data.result);
            } else if (res.data && res.data.error) {
                reject(new Error(res.data.error.message || "请求失败"));
            } else {
                resolve(res.data);
            }
        } catch (err) {
            console.error("请求失败:", err.message);
            reject(err);
        }
    });
}

async function getAvailableCoupons() {
    try {
        const res = await request("available-coupons");
        return res;
    } catch (err) {
        result += "查询优惠券列表失败: " + err.message + "  ";
        return null;
    }
}

async function autoBindCoupons() {
    try {
        const res = await request("auto-bind-coupons");
        return res;
    } catch (err) {
        result += "一键领券失败: " + err.message + "  ";
        return null;
    }
}

async function getMyCoupons() {
    try {
        const res = await request("my-coupons");
        return res;
    } catch (err) {
        result += "查询我的优惠券失败: " + err.message + "  ";
        return null;
    }
}

async function getCampaignCalendar(specifiedDate = null) {
    try {
        const args = specifiedDate ? { specifiedDate } : {};
        const res = await request("campaign-calender", args);
        return res;
    } catch (err) {
        result += "查询活动日历失败: " + err.message + "  ";
        return null;
    }
}

function parseTextContent(toolResult) {
    if (!toolResult || !toolResult.content) return "";

    const textContent = toolResult.content.find(item => item.type === "text");
    return textContent ? textContent.text : "";
}

async function mcdonald() {
    return new Promise(async (resolve) => {
        try {
            console.log("正在查询可领取的优惠券...");
            const availableCoupons = await getAvailableCoupons();
            if (availableCoupons) {
                const availableText = parseTextContent(availableCoupons);
                console.log(availableText);

                const unreceivedMatches = availableText.match(/状态：未领取/g);
                const unreceivedCount = unreceivedMatches ? unreceivedMatches.length : 0;

                if (unreceivedCount > 0) {
                    result += `发现${unreceivedCount}张可领取优惠券  `;

                    console.log("正在一键领取优惠券...");
                    const bindResult = await autoBindCoupons();
                    if (bindResult) {
                        const bindText = parseTextContent(bindResult);
                        console.log(bindText);

                        const successMatch = bindText.match(/成功.*?(\d+).*?张/s);
                        if (successMatch) {
                            result += `成功领取${successMatch[1]}张  `;
                        }

                        const couponNameMatches = bindText.match(/✅.*?\*\*(.+?)\*\*/g);
                        if (couponNameMatches) {
                            const couponNames = couponNameMatches.map(match => {
                                const nameMatch = match.match(/\*\*(.+?)\*\*/);
                                return nameMatch ? nameMatch[1] : "";
                            }).filter(name => name);

                            if (couponNames.length > 0) {
                                result += `[${couponNames.join(", ")}]  `;
                            }
                        }
                    }
                } else {
                    result += "暂无可领取的新优惠券  ";
                }
            }

            console.log("正在查询我的优惠券...");
            const myCoupons = await getMyCoupons();
            if (myCoupons) {
                const myText = parseTextContent(myCoupons);
                console.log(myText);

                const totalMatch = myText.match(/共.*?(\d+).*?张/);
                if (totalMatch) {
                    result += `当前共有${totalMatch[1]}张优惠券可用`;
                }
            }

        } catch (err) {
            console.error(err);
            result += "执行失败: " + err.message;
        }

        console.log(result);
        resolve(result);
    });
}

module.exports = mcdonald;

if (require.main === module) {
    mcdonald().then(console.log);
}
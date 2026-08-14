/**
 * 抓包：麦当劳 app → MCP 接口 → 抓包获取 token（Authorization Bearer）
 * 变量：ONESIGN_MCDONALD_TOKEN（Bearer token 值）
 *
 * cron: 0 10 * * *
 * new Env('麦当劳领券');
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

const baseURL = "https://mcp.mcd.cn/mcp-servers/mcd-mcp";

function request(token, toolName, args = {}) {
    return new Promise(async (resolve, reject) => {
        try {
            const headers = {
                "Authorization": `Bearer ${token}`,
                "Content-Type": "application/json",
            };

            const requestBody = {
                jsonrpc: "2.0",
                id: Date.now(),
                method: "tools/call",
                params: {
                    name: toolName,
                    arguments: args,
                },
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
            reject(err);
        }
    });
}

function parseTextContent(toolResult) {
    if (!toolResult || !toolResult.content) return "";
    const textContent = toolResult.content.find((item) => item.type === "text");
    return textContent ? textContent.text : "";
}

async function mcdonald() {
    let success = true;
    console.log("【麦当劳】：开始领券...");

    const token = getConfig("", "ONESIGN_MCDONALD_TOKEN");
    if (!token) {
        console.log("【麦当劳】：未配置 ONESIGN_MCDONALD_TOKEN 变量");
        success = false;
    } else {
        try {
            // 查询可领取的优惠券
            console.log("正在查询可领取的优惠券...");
            const availableCoupons = await request(token, "available-coupons");
            const availableText = parseTextContent(availableCoupons);
            console.log(availableText);

            const unreceivedMatches = availableText.match(/状态：未领取/g);
            const unreceivedCount = unreceivedMatches ? unreceivedMatches.length : 0;

            if (unreceivedCount > 0) {
                console.log(`发现 ${unreceivedCount} 张可领取优惠券`);

                // 一键领取所有优惠券
                console.log("正在一键领取优惠券...");
                const bindResult = await request(token, "auto-bind-coupons");
                const bindText = parseTextContent(bindResult);
                console.log(bindText);

                const successMatch = bindText.match(/成功.*?(\d+).*?张/s);
                if (successMatch) {
                    console.log(`成功领取 ${successMatch[1]} 张`);
                }
            } else {
                console.log("暂无可领取的新优惠券");
            }

            // 查询我的优惠券统计
            const myCoupons = await request(token, "my-coupons");
            const myText = parseTextContent(myCoupons);
            console.log(myText);

            const totalMatch = myText.match(/共.*?(\d+).*?张/);
            if (totalMatch) {
                console.log(`当前共有 ${totalMatch[1]} 张优惠券可用`);
            }
        } catch (e) {
            console.log(`执行失败: ${e.message}`);
            success = false;
        }
    }

    if (!success) process.exit(1);
}

mcdonald();
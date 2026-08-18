#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
抓包：蜜雪冰城小程序 → 进入每日抽奖活动（抽新款雪王挂件）
      抓取 76177-activity.dexfu.cn 域名的完整 Cookie
      从 ProxyPin 中复制请求头里的 Cookie 完整值
变量：ONESIGN_MXBC_COOKIE（Cookie 完整字符串，多账号用 # 或 & 分隔）

依赖：pip install requests
需要 Node.js 环境来解析动态 token（brew install node）

cron: 30 9 * * *
new Env('蜜雪冰城小程序每日抽奖')
"""
import os
import sys
import json
import time
import base64
import subprocess
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

success = True


class RUN:
    def __init__(self, info, index):
        self.cookie = info.strip()
        self.index = index + 1
        self.s = requests.session()
        self.s.verify = False
        self.headers = {
            'Host': '76177-activity.dexfu.cn',
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-Requested-With': 'XMLHttpRequest',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 15; RMX5062 Build/UKQ1.231108.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/150.0.7871.181 Mobile Safari/537.36 XWEB/1500047 MMWEBSDK/20260502 MMWEBID/784 MicroMessenger/8.0.76.3141(0x28004C50) WeChat/arm64 Weixin NetType/WIFI Language/zh_CN ABI/arm64 miniProgram/wx7696c66d2245d107',
            'Accept': 'application/json',
            'Origin': 'https://76177-activity.dexfu.cn',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty',
            'Referer': 'https://76177-activity.dexfu.cn/hdtool/index?id=337532939599501&dbnewopen',
            'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7'
        }
        self.base_url = 'https://76177-activity.dexfu.cn'
        self.activityId = '337532939599501'
        self.consumerId = self._extract_consumer_id()

    def _extract_consumer_id(self):
        try:
            for part in self.cookie.split(';'):
                part = part.strip()
                if part.startswith('_ac='):
                    ac_value = part[4:]
                    padding = 4 - len(ac_value) % 4
                    if padding != 4:
                        ac_value += '=' * padding
                    decoded = base64.b64decode(ac_value).decode()
                    ac_json = json.loads(decoded)
                    return str(ac_json.get('cid', ''))
        except Exception:
            pass
        return ''

    def _get_headers_with_cookie(self):
        headers = self.headers.copy()
        headers['Cookie'] = self.cookie
        return headers

    def get_token(self):
        print('获取抽奖token----->>>')
        timestamp = int(time.time() * 1000)
        data = {
            'timestamp': timestamp,
            'activityId': self.activityId,
            'activityType': 'hdtool',
            'consumerId': self.consumerId
        }
        try:
            response = self.s.post(
                f'{self.base_url}/hdtool/ctoken/getTokenNew',
                headers=self._get_headers_with_cookie(),
                data=data
            )
            if response.status_code == 200:
                res_json = response.json()
                if res_json.get('success'):
                    js_code = res_json.get('token', '')
                    if js_code:
                        token = self._execute_js_token(js_code)
                        if token:
                            print(f'token获取成功: {token}')
                            return token
                        print('token解析失败')
                        return None
                    print('未获取到token')
                    return None
                print(f'获取token失败: {res_json}')
                return None
            print(f'获取token请求失败，状态码：{response.status_code}')
            return None
        except Exception as e:
            print(f'获取token异常：{e}')
            return None

    def _execute_js_token(self, js_code):
        try:
            wrapper = (
                'const _eval=eval;'
                'let _tr=null;'
                'eval=function(c){_tr=_eval(c);return _tr};'
                + js_code +
                ';console.log("TOKEN:"+(_tr||""))'
            )
            result = subprocess.run(
                ['node', '-e', wrapper],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                for line in result.stdout.strip().split('\n'):
                    if line.startswith('TOKEN:') and len(line) > 6:
                        token = line[6:].strip()
                        if token:
                            return token
                if result.stdout.strip():
                    print(f'JS执行输出: {result.stdout.strip()[:200]}')
            if result.stderr:
                print(f'JS执行错误: {result.stderr.strip()[:200]}')
            return None
        except FileNotFoundError:
            print('未找到 Node.js 环境，请安装: brew install node')
            return None
        except subprocess.TimeoutExpired:
            print('JS执行超时')
            return None
        except Exception as e:
            print(f'JS执行异常: {e}')
            return None

    def check_free_draw(self):
        print('检查免费抽奖资格----->>>')
        ts = int(time.time() * 1000)
        data = {
            'hdType': 'dev',
            'hdToolId': '',
            'preview': 'false',
            'actId': self.activityId,
            'adslotId': ''
        }
        try:
            response = self.s.post(
                f'{self.base_url}/hdtool/ajaxElement?_={ts}',
                headers=self._get_headers_with_cookie(),
                data=data
            )
            if response.status_code == 200:
                res_json = response.json()
                if res_json.get('success'):
                    element = res_json.get('element', {})
                    free_empty = element.get('freeEmpty', True)
                    my_credits = element.get('myCredits', '0')
                    status = element.get('status', 0)
                    if free_empty:
                        print(f'今日免费抽奖次数已用完 (status={status})')
                        print(f'当前雪王币: {my_credits} (不消耗雪王币抽奖)')
                        return False
                    print(f'免费抽奖可用 (status={status}, 雪王币: {my_credits})')
                    return True
                print(f'查询抽奖资格失败: {res_json}')
                return False
            print(f'查询抽奖资格请求失败，状态码：{response.status_code}')
            return False
        except Exception as e:
            print(f'查询抽奖资格异常：{e}')
            return False

    def do_join(self, token):
        print('执行抽奖----->>>')
        ts = int(time.time() * 1000)
        data = {
            'actId': self.activityId,
            'oaId': self.activityId,
            'activityType': 'hdtool',
            'consumerId': self.consumerId,
            'token': token
        }
        try:
            url = f'{self.base_url}/hdtool/doJoin?dpm=76177.3.1.0&activityId={self.activityId}&_={ts}'
            response = self.s.post(
                url,
                headers=self._get_headers_with_cookie(),
                data=data
            )
            if response.status_code == 200:
                res_json = response.json()
                if res_json.get('success'):
                    order_id = res_json.get('orderId', '')
                    need_credits = res_json.get('needCredits', 0)
                    print(f'抽奖请求成功，订单号: {order_id}')
                    if need_credits > 0:
                        print(f'注意: 本次消耗了 {need_credits} 雪王币')
                    return order_id
                status = res_json.get('status', '')
                message = res_json.get('message', '')
                if status == 24:
                    print(f'未中奖，明天再来吧~ ({message})')
                    return '__NOT_WON__'
                print(f'抽奖失败: {res_json}')
                return None
            print(f'抽奖请求失败，状态码：{response.status_code}')
            return None
        except Exception as e:
            print(f'抽奖异常：{e}')
            return None

    def get_order_status(self, order_id):
        print('查询抽奖结果----->>>')
        ts = int(time.time() * 1000)
        data = {
            'orderId': order_id,
            'adslotId': ''
        }
        try:
            response = self.s.post(
                f'{self.base_url}/hdtool/getOrderStatus?_={ts}',
                headers=self._get_headers_with_cookie(),
                data=data
            )
            if response.status_code == 200:
                res_json = response.json()
                if res_json.get('success'):
                    result = res_json.get('result', -1)
                    if result == 2:
                        lottery = res_json.get('lottery', {})
                        title = lottery.get('title', '未知')
                        type_name = lottery.get('type', '')
                        element = res_json.get('element', {})
                        my_credits = element.get('myCredits', '')
                        print(f'抽奖结果: 【{title}】({type_name})')
                        if my_credits:
                            print(f'当前雪王币: {my_credits}')
                        return True
                    elif result == 0:
                        print('抽奖处理中，稍后重试...')
                        return False
                    else:
                        print(f'未知结果状态: result={result}')
                        return False
                print(f'查询结果失败: {res_json}')
                return False
            print(f'查询结果请求失败，状态码：{response.status_code}')
            return False
        except Exception as e:
            print(f'查询结果异常：{e}')
            return False

    def main(self):
        global success
        print(f"\n---------开始执行第{self.index}个账号>>>>>")

        if not self.consumerId:
            print('未能从 Cookie 中解析到 consumerId，请检查 Cookie 是否完整')
            success = False
            return False

        if not self.check_free_draw():
            print('今日免费抽奖次数已用完，跳过')
            return True

        token = self.get_token()
        if not token:
            success = False
            return False

        order_id = self.do_join(token)
        if order_id == '__NOT_WON__':
            return True
        if not order_id:
            success = False
            return False

        for i in range(5):
            if self.get_order_status(order_id):
                return True
            time.sleep(2)

        print('查询抽奖结果超时')
        success = False
        return False


if __name__ == '__main__':
    cookie = os.environ.get('ONESIGN_MXBC_COOKIE', '')
    if not cookie:
        print("未配置 ONESIGN_MXBC_COOKIE 变量")
        print("请从抓包中复制 76177-activity.dexfu.cn 域名的完整 Cookie")
        sys.exit(1)
    cookies = cookie.split('#')
    cookies = [c for c in cookies if c.strip()]
    print(f"共获取到{len(cookies)}个账号")
    for idx, info in enumerate(cookies):
        RUN(info, idx).main()
    if not success:
        sys.exit(1)
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
抓包：喜马拉雅 app → 我的 → 签到 → 抓包获取 cookie
变量：ONESIGN_XMLY_COOKIE（cookie 值，多账号用 # 或 & 分隔）

cron: 10 9 * * *
new Env('喜马拉雅签到')
"""
import os
import sys
import json
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

success = True


class RUN:
    def __init__(self, info, index):
        self.cookie = info
        self.index = index + 1

    def sign(self):
        url = 'https://m.ximalaya.com/web-activity/signIn/v2/signIn?v=new'
        headers = {
            'Host': 'm.ximalaya.com',
            'Content-Type': 'application/json',
            'Accept': '*/*',
            'X-Xuid-Fp': 'FISDYy0YZLgYhwIObU0_rmpz5ZIWc2doY1AQZ8xlyQk8pafpgABxMiE5LjAuNDMh',
            'Connection': 'keep-alive',
            'Cookie': self.cookie,
            'User-Agent': 'ting_v9.0.87_c5(CFNetwork, iOS 15.6, iPhone14,5)',
            'Accept-Language': 'zh-CN,zh-Hans;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
        }
        data = '{"aid":87}'
        try:
            response = requests.post(url=url, headers=headers, data=data)
            result = response.json().get('data', {})
            msg = result.get('msg', '')
            code = result.get('code', -1)
            if code == 0 or code == -2:
                print(f"打卡成功: {msg}")
                return True
            else:
                print(f"打卡失败: {msg}")
                return False
        except Exception as e:
            print(f"打卡异常: {e}")
            return False

    def get_user_info(self):
        m_url = 'https://m.ximalaya.com/business-vip-presale-mobile-web/page/ts-1671779856199?version=9.0.87'
        m_headers = {
            'Host': 'm.ximalaya.com',
            'Accept': 'application/json, text/plain, */*',
            'Connection': 'keep-alive',
            'Cookie': self.cookie,
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 iting/9.0.87 kdtunion_iting/1.0 iting(main)/9.0.87/ios_1 ;xmly(main)/9.0.87/iOS_1',
            'Accept-Language': 'zh-CN,zh-Hans;q=0.9',
            'Referer': 'https://m.ximalaya.com/gatekeeper/business-xmvip/main?app=iting&version=9.0.87&impl=com.gemd.iting&orderSource=app_Other_MyPage_VipCard',
            'Accept-Encoding': 'gzip, deflate, br',
        }
        try:
            response = requests.get(url=m_url, headers=m_headers)
            user_info = response.json().get('data', {}).get('modules', [{}])[0].get('userInfo', {})
            userId = user_info.get('userId', '')
            nickName = user_info.get('nickName', '')
            subtitle = user_info.get('subtitle', '')
            print(f"ID: {userId} 用户名: {nickName} VIP到期日期: {subtitle}")
            return True
        except Exception as e:
            print(f"获取用户信息异常: {e}")
            return False

    def main(self):
        global success
        print(f"\n---------开始执行第{self.index}个账号>>>>>")
        if not self.sign():
            success = False
        self.get_user_info()
        return True


if __name__ == '__main__':
    token = os.environ.get('ONESIGN_XMLY_COOKIE', '')
    if not token:
        print("未配置 ONESIGN_XMLY_COOKIE 变量")
        sys.exit(1)
    tokens = token.replace('&', '#').split('#')
    tokens = [t for t in tokens if t]
    print(f"共获取到{len(tokens)}个账号")
    for idx, info in enumerate(tokens):
        RUN(info, idx).main()
    if not success:
        sys.exit(1)
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
抓包：海底捞小程序 → 授权登录 → 找请求头带 openId 和 uid 的 URL
      复制 openId 和 uid，格式：openId@uid
变量：ONESIGN_HDL_TOKEN（openId@uid，多账号用 # 或 & 分隔）

cron: 0 6 * * *
new Env('海底捞小程序签到')
"""
import os
import sys
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

success = True


class RUN:
    def __init__(self, info, index):
        split_info = info.split('@')
        self.openId = split_info[0]
        self.uid = split_info[1] if len(split_info) > 1 else ''
        self.index = index + 1
        self.s = requests.session()
        self.s.verify = False
        self.haidilao_app_token = ''
        self.headers = {
            'Host': 'superapp-public.kiwa-tech.com',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 14; Mi14 Pro Build/RKQ1.200826.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/116.0.0.0 Mobile Safari/537.36 XWEB/1160065 MMWEBSDK/20230701 MMWEBID/8701 MicroMessenger/8.0.40.2420(0x28002858) WeChat/arm64 Weixin NetType/WIFI Language/zh_CN ABI/arm64 miniProgram/wx1ddeb67115f30d1a',
            "_haidilao_app_token": "",
            "content-type": "application/json",
            "xweb_xhr": "1",
            "appid": "15",
            "appversion": "3.67.0",
            "accept": "*/*",
            "sec-fetch-site": "cross-site",
            "sec-fetch-mode": "cors",
            "sec-fetch-dest": "empty",
            "referer": "https://servicewechat.com/wx1ddeb67115f30d1a/121/page-frame.html",
            "accept-language": "zh-CN,zh;q=0.9"
        }

    def do_request(self, url, method='POST', data=None):
        try:
            if method == 'POST':
                response = self.s.post(url, json=data, headers=self.headers)
            else:
                response = self.s.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"请求错误: {e}")
            return None

    def wechatLogin(self):
        print('>>>>>>登录获取token')
        try:
            data = {"type": 1, "country": "CN", "codeType": 1, "business": "登录",
                    "terminal": "会员小程序", "openId": self.openId, "uid": self.uid}
            response = self.do_request(
                'https://superapp-public.kiwa-tech.com/api/gateway/login/center/login/wechatLogin', data=data)
            if response and response.get('success'):
                data = response.get('data', {})
                self.haidilao_app_token = data.get('token', '')
                self.headers['_haidilao_app_token'] = self.haidilao_app_token
                print(f"ID：【{data.get('id', '')}】")
                return True
            else:
                print(f"登录失败: {response}")
                return False
        except Exception as e:
            print(f"登录异常: {e}")
            return False

    def queryMemberCacheInfo(self):
        print('>>>>>>获取用户信息')
        try:
            data = {"type": 1}
            response = self.do_request(
                'https://superapp-public.kiwa-tech.com/activity/wxapp/applet/queryMemberCacheInfo', data=data)
            if response and response.get('success'):
                data = response.get('data', {})
                customerName = data.get('customerName', '')
                mobile = data.get('mobile', '')
                mobile = mobile[:3] + "*" * 4 + mobile[7:]
                coinNum = data.get('coinNum', '')
                print(f"用户名：【{customerName}】\n手机号：【{mobile}】\n捞币：【{coinNum}】")
                return True
            return False
        except Exception as e:
            print(f"获取用户信息异常: {e}")
            return False

    def sign_in(self):
        try:
            data = {"signinSource": "MiniApp"}
            self.headers['referer'] = f"https://superapp-public.kiwa-tech.com/app-sign-in/?SignInToken={self.haidilao_app_token}&source=MiniApp"
            response = self.do_request(
                'https://superapp-public.kiwa-tech.com/activity/wxapp/signin/signin', data=data)
            if response and response.get('success'):
                print("签到成功！")
                return True
            else:
                print(f"签到失败: {response}")
                return False
        except Exception as e:
            print(f"签到异常: {e}")
            return False

    def signin_query(self):
        global success
        print('>>>>>>开始签到')
        try:
            self.headers['referer'] = f"https://superapp-public.kiwa-tech.com/app-sign-in/?SignInToken={self.haidilao_app_token}&source=MiniApp"
            response = self.do_request(
                'https://superapp-public.kiwa-tech.com/activity/wxapp/signin/query')
            if response and response.get('success'):
                data = response.get('data', {})
                signinOr = data.get('signinOr', 0)
                signinQueryDetailList = data.get('signinQueryDetailList', [{}])
                daycount = sum(1 for day in signinQueryDetailList if day.get('dailySigninStatus', 1) == 2)
                if signinOr != 0:
                    print(f"已签到,本期累计签到【{daycount}】天")
                else:
                    print(f"未签到,本期累计签到【{daycount}】天")
                    self.sign_in()
                return True
            else:
                print(f"查询签到失败: {response}")
                success = False
                return False
        except Exception as e:
            print(f"查询签到异常: {e}")
            success = False
            return False

    def main(self):
        global success
        print(f"\n---------开始执行第{self.index}个账号>>>>>")
        if self.wechatLogin():
            self.queryMemberCacheInfo()
            self.signin_query()
            return True
        else:
            success = False
            return False


if __name__ == '__main__':
    token = os.environ.get('ONESIGN_HDL_TOKEN', '')
    if not token:
        print("未配置 ONESIGN_HDL_TOKEN 变量")
        sys.exit(1)
    tokens = token.replace('&', '#').split('#')
    tokens = [t for t in tokens if t]
    print(f"共获取到{len(tokens)}个账号")
    for idx, info in enumerate(tokens):
        RUN(info, idx).main()
    if not success:
        sys.exit(1)
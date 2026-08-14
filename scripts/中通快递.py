#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
抓包：中通快递小程序 → 授权登录 → 找请求头带 token 的 URL
      复制里面的 token 参数值
变量：ONESIGN_ZTKD_TOKEN（token 值，多账号用 # 或 & 分隔）

cron: 0 6 * * *
new Env('中通快递小程序签到')
"""
import os
import sys
import time
from datetime import date, datetime
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

success = True


class RUN:
    def __init__(self, info, index):
        self.token = info
        self.index = index + 1
        self.headers = {
            'Host': 'api.ztomember.com',
            'Accept': 'application/json, text/plain, */*',
            'token': self.token,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF XWEB/8259',
            'Content-Type': 'application/json; charset=UTF-8',
            'Referer': 'https://servicewechat.com/wx63df5458e2e2afb7/189/page-frame.html',
        }
        self.baseUrl = 'https://api.ztomember.com/api/'

    def do_request(self, url, data=None):
        try:
            s = requests.session()
            s.verify = False
            response = s.post(url, headers=self.headers, json=data or {})
            return response.json()
        except Exception as e:
            print(f"请求错误: {e}")
            return None

    def get_point(self, end=False):
        global success
        response = self.do_request(f'{self.baseUrl}user/point/get')
        if response and response.get('success') and response.get('code') == 10000:
            data = response.get('data', {})
            point = data.get('point', 0)
            mobile = data.get('mobile', '')
            mobile = mobile[:3] + "*" * 4 + mobile[7:]
            if end:
                print(f'执行后积分：【{point}】')
            else:
                print(f'当前用户：【{mobile}】\n当前积分：【{point}】')
            return True
        else:
            print('获取积分信息失败，可能token已失效')
            success = False
            return False

    def Check_sign(self):
        print('>>>>>>查询签到')
        json_data = {"calendarType": 0}
        response = self.do_request(f'{self.baseUrl}member/sign/v2/calendar', json_data)
        if response and response.get('success') and response.get('data'):
            data = response.get('data', {})
            dayList = data.get('dayList', [])
            signDays = data.get('signDays', 0)
            current_date = date.today()
            for day in dayList:
                dates = day.get('date', '')
                point = day.get('point', '')
                signFlag = day.get('signFlag', '')
                parsed_date = datetime.strptime(dates, '%Y-%m-%d').date()
                if parsed_date == current_date:
                    if signFlag == 1:
                        print(f'今日已签到,连续签到【{signDays}】天,获得【{point}】积分')
                    else:
                        self.sign()
        else:
            print(f"查询签到失败: {response.get('msg', '') if response else '无响应'}")

    def sign(self):
        print('>>>签到')
        response = self.do_request(f'{self.baseUrl}member/sign/v2/userSignIn')
        if response and response.get('success') and response.get('code') == 10000:
            point = response.get('data', {}).get('point', '')
            print(f'签到成功获得：【{point}】积分')
        else:
            print(f"签到失败: {response.get('msg', '') if response else '无响应'}")

    def main(self):
        global success
        print(f"\n---------开始执行第{self.index}个账号>>>>>")
        if self.get_point():
            self.Check_sign()
            self.get_point(end=True)
            return True
        return False


if __name__ == '__main__':
    token = os.environ.get('ONESIGN_ZTKD_TOKEN', '')
    if not token:
        print("未配置 ONESIGN_ZTKD_TOKEN 变量")
        sys.exit(1)
    tokens = token.replace('&', '#').split('#')
    tokens = [t for t in tokens if t]
    print(f"共获取到{len(tokens)}个账号")
    for idx, info in enumerate(tokens):
        RUN(info, idx).main()
    if not success:
        sys.exit(1)
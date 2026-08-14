#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
依赖：pip install pycryptodome
抓包：蜜雪冰城小程序 → 我的 → 授权登录
      找 loginByUnionid 请求的 unionid 参数值
变量：ONESIGN_MXBC_TOKEN（unionid 值，多账号用 # 或 & 分隔）

cron: 30 9 * * *
new Env('蜜雪冰城小程序签到')
"""
import os
import sys
import json
import base64
import time
import requests
from urllib.parse import quote_plus
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA256
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

success = True

PRIVATE_KEY = '''-----BEGIN PRIVATE KEY-----
MIIEvwIBADANBgkqhkiG9w0BAQEFAASCBKkwggSlAgEAAoIBAQCtypUdHZJKlQ9L
L6lIJSphnhqjke7HclgWuWDRWvzov30du235cCm13mqJ3zziqLCwstdQkuXo9sOP
Ih94t6nzBHTuqYA1whrUnQrKfv9X4/h3QVkzwT+xWflE+KubJZoe+daLKkDeZjVW
nUku8ov0E5vwADACfntEhAwiSZUALX9UgNDTPbj5ESeII+VztZ/KOFsRHMTfDb1G
-----END PRIVATE KEY-----'''


class RUN:
    def __init__(self, info, index):
        self.unionid = info
        self.index = index + 1
        self.s = requests.session()
        self.s.verify = False
        self.accessToken = ''
        self.headers = {
            'Host': 'mxsa.mxbc.net',
            'Content-Type': 'application/json',
            'xweb_xhr': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x6309080f) XWEB/9105',
            'version': '2.2.5',
            'Accept': '*/*',
            'Sec-Fetch-Site': 'cross-site',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty',
            'Referer': 'https://servicewechat.com/wx7696c66d2245d107/105/page-frame.html',
            'Accept-Language': 'zh-CN,zh;q=0.9'
        }
        self.base_url = 'https://mxsa.mxbc.net'

    def getSign(self, params):
        sorted_params = sorted(params.items())
        param_str = "&".join(
            f"{k}={quote_plus(json.dumps(v)) if isinstance(v, dict) else quote_plus(str(v))}" for k, v in sorted_params)
        key = RSA.importKey(PRIVATE_KEY)
        hash_obj = SHA256.new(param_str.encode())
        signer = PKCS1_v1_5.new(key)
        signature = signer.sign(hash_obj)
        signature = base64.b64encode(signature).decode()
        signature = signature.replace("/", "_").replace("+", "-")
        return signature

    def login(self):
        global success
        print('开始登录----->>>')
        params = {
            'third': 'wxmini',
            'unionid': self.unionid,
            't': int(time.time() * 1000),
            'appId': 'd82be6bbc1da11eb9dd000163e122ecb'
        }
        sign = self.getSign(params)
        params['sign'] = sign
        try:
            response = self.s.post(f'{self.base_url}/api/v1/app/loginByUnionid', headers=self.headers, json=params)
            if response.status_code == 200:
                res_json = response.json()
                if res_json.get('code') == 0:
                    self.accessToken = res_json.get('data', {}).get('accessToken', '')
                    if self.accessToken:
                        self.headers['Access-Token'] = self.accessToken
                        print('登录成功')
                        return True
                print('登录失败')
                return False
            print(f'登录请求失败，状态码：{response.status_code}')
            return False
        except Exception as e:
            print(f'登录异常：{e}')
            success = False
            return False

    def get_userInfo(self, end=False):
        params = {
            't': int(time.time() * 1000),
            'appId': 'd82be6bbc1da11eb9dd000163e122ecb'
        }
        sign = self.getSign(params)
        params['sign'] = sign
        try:
            response = self.s.get(f'{self.base_url}/api/v1/customer/info', headers=self.headers, params=params)
            if response.status_code == 200:
                res_json = response.json()
                if res_json.get('code') == 0:
                    data = res_json.get('data', {})
                    mobilePhone = data.get('mobilePhone', '')
                    customerPoint = data.get('customerPoint', '')
                    isSignin = data.get('isSignin', 0)
                    if end:
                        print(f'[执行后]雪王币：【{customerPoint}】')
                        return
                    print(f"手机号：【{mobilePhone}】\n[执行前]雪王币：【{customerPoint}】")
                    if isSignin == 0:
                        print('今日未签到')
                        self.signin()
                    else:
                        print('今日已签到')
                return True
            return False
        except Exception as e:
            print(f'获取用户信息异常：{e}')
            return False

    def signin(self):
        print('签到----->>>')
        params = {
            't': int(time.time() * 1000),
            'appId': 'd82be6bbc1da11eb9dd000163e122ecb'
        }
        sign = self.getSign(params)
        params['sign'] = sign
        try:
            response = self.s.get(f'{self.base_url}/api/v1/customer/signin', headers=self.headers, params=params)
            if response.status_code == 200:
                res_json = response.json()
                if res_json.get('code') == 0:
                    data = res_json.get('data', {})
                    ruleValuePoint = data.get('ruleValuePoint', '')
                    print(f"签到成功！获得：【{ruleValuePoint}】雪王币")
                elif res_json.get('code') == 5020:
                    print('今日已签到')
                else:
                    print('签到失败')
            return True
        except Exception as e:
            print(f'签到异常：{e}')
            return False

    def main(self):
        global success
        print(f"\n---------开始执行第{self.index}个账号>>>>>")
        if self.login():
            self.get_userInfo()
            self.get_userInfo(True)
            return True
        success = False
        return False


if __name__ == '__main__':
    token = os.environ.get('ONESIGN_MXBC_TOKEN', '')
    if not token:
        print("未配置 ONESIGN_MXBC_TOKEN 变量")
        print("依赖：pip install pycryptodome")
        sys.exit(1)
    tokens = token.replace('&', '#').split('#')
    tokens = [t for t in tokens if t]
    print(f"共获取到{len(tokens)}个账号")
    for idx, info in enumerate(tokens):
        RUN(info, idx).main()
    if not success:
        sys.exit(1)
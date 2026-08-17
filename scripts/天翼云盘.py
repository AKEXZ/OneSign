#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
依赖：pip install rsa
抓包：天翼云盘 app → 签到页面 → 抓包获取 accessToken
变量：ONESIGN_TYYP_TOKEN（accessToken 值，多账号用 # 或 & 分隔）

cron: 0 0 * * *
new Env('天翼云盘签到')
"""
import os
import sys
import json
import time
import base64
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

try:
    import rsa
except ImportError:
    print("缺少依赖，请运行: pip install rsa")
    sys.exit(1)

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

success = True


class RUN:
    def __init__(self, info, index):
        self.accessToken = info
        self.index = index + 1
        self.s = requests.session()
        self.s.verify = False
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 14; Mi14 Pro Build/RKQ1.200826.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/116.0.0.0 Mobile Safari/537.36',
            'accessToken': self.accessToken,
            'Content-Type': 'application/json;charset=UTF-8',
        }

    def encrypt_password(self, password):
        """RSA 加密密码"""
        public_key = """-----BEGIN RSA PUBLIC KEY-----
        MIGJAoGBALJQ3B3GqsVx9EUx9s2DpBxYdH6VqEbQxn1mJqHq5SX5LqHq5SX5LqHq
        5SX5LqHq5SX5LqHq5SX5LqHq5SX5LqHq5SX5LqHq5SX5LqHq5SX5LqHq5SX5LqHq
        5SX5LqHq5SX5LqHq5SX5LqHq5SX5LqHq5SX5LqHq5SX5LqHq5SX5LqHq5SX5LqHq
        AgMBAAE=
        -----END RSA PUBLIC KEY-----"""
        try:
            pub_key = rsa.PublicKey.load_pkcs1_openssl_pem(public_key.encode())
            encrypted = rsa.encrypt(password.encode(), pub_key)
            return base64.b64encode(encrypted).decode()
        except Exception as e:
            print(f"加密失败: {e}")
            return None

    def login(self):
        global success
        print('>>>>>>获取用户信息')
        try:
            response = self.s.get('https://api.cloud.189.cn/open/user/getUserInfoForPortal.action',
                                  headers=self.headers)
            result = response.json()
            if result.get('res_code') == 0:
                data = result.get('data', {})
                phone = data.get('phone', '')
                phone = phone[:3] + "*" * 4 + phone[7:]
                print(f"手机号：【{phone}】")
                return True
            else:
                print(f"获取用户信息失败: {result.get('res_message', '')}")
                success = False
                return False
        except Exception as e:
            print(f"获取用户信息异常: {e}")
            success = False
            return False

    def userSign(self):
        print('>>>>>>开始签到')
        try:
            response = self.s.get('https://api.cloud.189.cn/mkt/userSign.action',
                                  headers=self.headers)
            result = response.json()
            if result.get('res_code') == 0:
                print(f"签到成功！累计签到【{result.get('data', {}).get('signDay', '')}】天")
                return True
            elif result.get('res_code') == 1001:
                print('今日已签到')
                return True
            else:
                print(f"签到失败: {result.get('res_message', '')}")
                return False
        except Exception as e:
            print(f"签到异常: {e}")
            return False

    def main(self):
        global success
        print(f"\n---------开始执行第{self.index}个账号>>>>>")
        if self.login():
            self.userSign()
            return True
        return False


if __name__ == '__main__':
    token = os.environ.get('ONESIGN_TYYP_TOKEN', '')
    if not token:
        print("未配置 ONESIGN_TYYP_TOKEN 变量")
        print("依赖：pip install rsa")
        sys.exit(1)
    tokens = token.split('#')
    tokens = [t for t in tokens if t]
    print(f"共获取到{len(tokens)}个账号")
    for idx, info in enumerate(tokens):
        RUN(info, idx).main()
    if not success:
        sys.exit(1)
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
抓包：顺丰速运小程序 → 授权登录 → 复制整个请求 URL
变量：ONESIGN_SFSY_TOKEN（完整 URL，多账号用 # 或 & 分隔）

cron: 5 5,17 * * *
new Env('顺丰速运小程序签到')
"""
import os
import sys
import hashlib
import json
import random
import time
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

success = True


class RUN:
    def __init__(self, info, index):
        self.index = index + 1
        print(f"\n---------开始执行第{self.index}个账号>>>>>")
        self.s = requests.session()
        self.s.verify = False
        self.headers = {
            'Host': 'mcs-mimp-web.sf-express.com',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36 NetType/WIFI MicroMessenger/7.0.20.1781(0x6700143B) WindowsWechat(0x63090551) XWEB/6945 Flue',
            'accept': 'application/json, text/plain, */*',
            'content-type': 'application/json;charset=UTF-8',
            'platform': 'MINI_PROGRAM',
        }
        self.taskId = ''
        self.taskCode = ''
        self.strategyId = ''
        self.title = ''
        self.login_res = self.login(info)

    def get_deviceId(self):
        chars = 'abcdef0123456789'
        result = ''.join(random.choice(chars) if c == 'x' else random.choice(chars).upper() if c == 'X' else c for c in 'xxxxxxxx-xxxx-xxxx')
        return result

    def login(self, sfurl):
        global success
        try:
            ress = self.s.get(sfurl, headers=self.headers)
            phone = self.s.cookies.get_dict().get('_login_mobile_', '')
            if phone:
                mobile = phone[:3] + "*" * 4 + phone[7:]
                print(f'用户:【{mobile}】登录成功')
                return True
            else:
                print('获取用户信息失败')
                success = False
                return False
        except Exception as e:
            print(f'登录异常: {e}')
            success = False
            return False

    def getSign(self):
        timestamp = str(int(round(time.time() * 1000)))
        token = 'wwesldfs29aniversaryvdld29'
        sysCode = 'MCS-MIMP-CORE'
        data = f'token={token}&timestamp={timestamp}&sysCode={sysCode}'
        signature = hashlib.md5(data.encode()).hexdigest()
        self.headers.update({'sysCode': sysCode, 'timestamp': timestamp, 'signature': signature})

    def do_request(self, url, data=None, req_type='post'):
        self.getSign()
        try:
            if req_type == 'get':
                response = self.s.get(url, headers=self.headers)
            else:
                response = self.s.post(url, headers=self.headers, json=data or {})
            return response.json()
        except Exception as e:
            print(f'请求失败: {e}')
            return None

    def sign(self):
        print('>>>>>>开始执行签到')
        json_data = {"comeFrom": "vioin", "channelFrom": "WEIXIN"}
        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~integralTaskSignPlusService~automaticSignFetchPackage'
        response = self.do_request(url, data=json_data)
        if response and response.get('success'):
            obj = response.get('obj', {})
            count_day = obj.get('countDay', 0)
            packets = obj.get('integralTaskSignPackageVOList', [])
            if packets:
                packet_name = packets[0].get("packetName", "")
                print(f'签到成功，获得【{packet_name}】，本周累计签到【{count_day + 1}】天')
            else:
                print(f'今日已签到，本周累计签到【{count_day + 1}】天')
        else:
            print(f'签到失败: {response.get("errorMessage") if response else "无响应"}')

    def superWelfare(self):
        print('>>>>>>超值福利签到')
        json_data = {'channel': 'czflqdlhbxcx'}
        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberActLengthy~redPacketActivityService~superWelfare~receiveRedPacket'
        response = self.do_request(url, data=json_data)
        if response and response.get('success'):
            obj = response.get('obj', {})
            gift_list = obj.get('giftList', [])
            if obj.get('extraGiftList'):
                gift_list.extend(obj['extraGiftList'])
            gift_names = ', '.join([g.get('giftName', '') for g in gift_list])
            status = '领取成功' if obj.get('receiveStatus') == 1 else '已领取过'
            print(f'超值福利签到[{status}]: {gift_names}')
        else:
            print(f'超值福利签到失败: {response.get("errorMessage") if response else "无响应"}')

    def get_SignTaskList(self, end=False):
        if not end:
            print('>>>开始获取签到任务列表')
        json_data = {'channelType': '3', 'deviceId': self.get_deviceId()}
        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~integralTaskStrategyService~queryPointTaskAndSignFromES'
        response = self.do_request(url, data=json_data)
        if response and response.get('success') and response.get('obj'):
            totalPoint = response["obj"]["totalPoint"]
            if end:
                print(f'当前积分：【{totalPoint}】')
                return
            print(f'执行前积分：【{totalPoint}】')
            for task in response["obj"].get("taskTitleLevels", []):
                self.taskId = task["taskId"]
                self.taskCode = task["taskCode"]
                self.strategyId = task["strategyId"]
                self.title = task["title"]
                status = task["status"]
                skip_titles = ['用行业模板寄件下单', '去新增一个收件偏好', '参与积分活动']
                if status == 3:
                    print(f'>{self.title}-已完成')
                    continue
                if self.title in skip_titles:
                    print(f'>{self.title}-跳过')
                    continue
                self.doTask()
                time.sleep(1)
                self.receiveTask()
        else:
            if not end:
                print('获取任务列表失败')

    def doTask(self):
        print(f'>>>开始去完成【{self.title}】任务')
        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonRoutePost/memberEs/taskRecord/finishTask'
        response = self.do_request(url, data={'taskCode': self.taskCode})
        if response and response.get('success'):
            print(f'>【{self.title}】任务-已完成')
        else:
            print(f'>【{self.title}】任务-{response.get("errorMessage") if response else "无响应"}')

    def receiveTask(self):
        print(f'>>>开始领取【{self.title}】任务奖励')
        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~integralTaskStrategyService~fetchIntegral'
        json_data = {"strategyId": self.strategyId, "taskId": self.taskId, "taskCode": self.taskCode, "deviceId": self.get_deviceId()}
        response = self.do_request(url, data=json_data)
        if response and response.get('success'):
            print(f'>【{self.title}】任务奖励领取成功！')
        else:
            print(f'>【{self.title}】任务-{response.get("errorMessage") if response else "无响应"}')

    def main(self):
        global success
        if not self.login_res:
            return False
        self.sign()
        time.sleep(1)
        self.superWelfare()
        time.sleep(1)
        self.get_SignTaskList()
        self.get_SignTaskList(end=True)
        return True


if __name__ == '__main__':
    token = os.environ.get('ONESIGN_SFSY_TOKEN', '')
    if not token:
        print("未配置 ONESIGN_SFSY_TOKEN 变量")
        sys.exit(1)
    tokens = token.replace('&', '#').split('#')
    tokens = [t for t in tokens if t]
    print(f"共获取到{len(tokens)}个账号")
    for idx, info in enumerate(tokens):
        RUN(info, idx).main()
    if not success:
        sys.exit(1)
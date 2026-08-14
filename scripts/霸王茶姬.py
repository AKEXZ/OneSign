#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
抓包：霸王茶姬小程序 → 我的 → 授权登录
      找请求头带 qm-user-token 的 URL，复制参数值
变量：ONESIGN_BWCJ_TOKEN（qm-user-token 值，多账号用 @ 分隔）

cron: 5 8 * * *
new Env('霸王茶姬小程序签到')
"""
import os
import sys
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

success = True


def log(msg):
    global success
    print(msg)


class RUN:
    def __init__(self, info, index):
        self.token = info
        self.index = index + 1
        self.s = requests.session()
        self.s.verify = False
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x6309080f) XWEB/8555',
            'Qm-User-Token': self.token,
            'Qm-From': 'wechat',
            'store-id': '49006',
            'Qm-From-Type': 'catering',
            'Accept': 'v=1.0',
            'Accept-Encoding': 'gzip,compress,br,deflate',
            'Referer': 'https://servicewechat.com/wxafec6f8422cb357b/87/page-frame.html'
        }
        self.s.headers.update(self.headers)
        self.appid = 'wxafec6f8422cb357b'
        self.activity_id = '947079313798000641'

    def personal_info(self):
        try:
            params = {'appid': self.appid}
            response = self.s.get('https://webapi.qmai.cn/web/catering/crm/personal-info', json=params)
            result = response.json()
            if result.get('code', '-1') == '0':
                mobile_phone = result.get('data', {}).get('mobilePhone', '')
                name = result.get('data', {}).get('name', '')
                phone = mobile_phone[:3] + "*" * 4 + mobile_phone[7:]
                log(f"账号[{self.index}]登录成功！\n用户名：【{name}】\n手机号：【{phone}】")
                return True
            else:
                log(f'登录失败: {result.get("message", "")}')
                return False
        except Exception as e:
            print(e)
            return False

    def user_sign_statistics(self):
        try:
            json_data = {'activityId': self.activity_id, 'appid': self.appid}
            response = self.s.post('https://webapi.qmai.cn/web/cmk-center/sign/userSignStatistics', json=json_data)
            result = response.json()
            if result.get('code', -1) == 0:
                data = result.get('data', {})
                sign_days = data.get('signDays', '')
                sign_status = data.get('signStatus', 0) == 1
                log(f"今天{'已' if sign_status else '未'}签到, 已连续签到{sign_days}天")
                if not sign_status:
                    self.take_part_in_sign()
                return sign_status, sign_days
            else:
                log(f'查询签到失败: {result.get("message", "")}')
                return False, 0
        except Exception as e:
            print(e)
            return False, 0

    def take_part_in_sign(self):
        try:
            json_data = {'activityId': self.activity_id, 'appid': self.appid}
            response = self.s.post('https://webapi.qmai.cn/web/cmk-center/sign/takePartInSign', json=json_data)
            result = response.json()
            if result.get('code', -1) == 0:
                data = result.get('data', {})
                rewardDetailList = data.get('rewardDetailList', [{}])
                if rewardDetailList:
                    rewardName = rewardDetailList[0].get('rewardName', '')
                    sendNum = rewardDetailList[0].get('sendNum', '')
                    log(f"签到成功，获得【{sendNum}】{rewardName}")
                    return True
                else:
                    log(f"签到失败：【{result.get('message', '')}】")
                    return False
            else:
                log(f'签到失败: {result.get("message", "")}')
                return False
        except Exception as e:
            print(e)
            return False

    def points_info(self):
        try:
            json_data = {'appid': self.appid}
            response = self.s.post('https://webapi.qmai.cn/web/catering/crm/points-info', json=json_data)
            result = response.json()
            if result.get('code', -1) == '0':
                data = result.get('data', {})
                soon_expired_points = data.get('soonExpiredPoints', 0)
                total_points = data.get('totalPoints', 0)
                expired_time = data.get('expiredTime', '')
                if soon_expired_points:
                    log(f"有【{soon_expired_points}】积分将于（{expired_time}）过期")
                log(f"当前积分: 【{total_points}】")
                return True
            else:
                log(f'查询积分失败: {result.get("message", "")}')
                return False
        except Exception as e:
            print(e)
            return False

    def main(self):
        global success
        log(f"\n---------开始执行第{self.index}个账号>>>>>")
        if not self.personal_info():
            log("用户信息无效，请更新token")
            success = False
            return False
        self.user_sign_statistics()
        self.points_info()
        return True


if __name__ == '__main__':
    token = os.environ.get('ONESIGN_BWCJ_TOKEN', '')
    if not token:
        print("未配置 ONESIGN_BWCJ_TOKEN 变量")
        sys.exit(1)
    tokens = token.replace('&', '#').split('#')
    tokens = [t for t in tokens if t]
    print(f"共获取到{len(tokens)}个账号")
    for idx, info in enumerate(tokens):
        RUN(info, idx).main()
    if not success:
        sys.exit(1)
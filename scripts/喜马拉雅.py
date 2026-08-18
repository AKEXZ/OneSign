#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
抓包：喜马拉雅 app → 我的 → 福利中心 → 抓包获取 cookie
变量：ONESIGN_XMLY_COOKIE（cookie 值，多账号用 # 分隔）

cron: 10 9 * * *
new Env('喜马拉雅签到')
"""
import os
import sys
import re
import time
import uuid
import json
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

success = True


class RUN:
    def __init__(self, info, index):
        self.cookie = info
        self.index = index + 1
        self.uid = self._extract_uid()
        self.device_id = self._extract_device_id()

    def _extract_uid(self):
        """从 cookie 中提取用户 uid"""
        m = re.search(r'_token=(\d+)', self.cookie)
        if m:
            return m.group(1)
        return ''

    def _extract_device_id(self):
        """从 cookie 中提取设备 ID (imei)"""
        m = re.search(r'_device=android&([^&]+)&', self.cookie)
        if m:
            return m.group(1)
        return ''

    def _get_base_headers(self):
        return {
            'Accept': '*/*',
            'Connection': 'keep-alive',
            'Cookie': self.cookie,
            'User-Agent': 'ting_9.5.1(RMX5062,Android35)',
            'Accept-Encoding': 'gzip, deflate',
        }

    def _reward_gold_coin(self, source_name, reward_type, coins=0, extra_body=None):
        """通用金币领取方法"""
        ts = int(time.time() * 1000)
        url = f'https://adse.ximalaya.com/incentive/ting/welfare/rewardGoldCoin/ts-{ts}?rn-credit-bundle-version=0.0.1125'
        headers = self._get_base_headers()
        headers.update({
            'Host': 'adse.ximalaya.com',
            'Content-Type': 'application/json; charset=utf-8',
        })

        body = {
            "requestId": str(uuid.uuid4()),
            "ts": ts,
            "coins": coins,
            "sourceName": source_name,
            "rewardType": reward_type,
            "retry": 0,
            "fallbackReq": 0,
            "index": 0,
            "startSource": "mine_page",
            "adId": 0,
            "adResponseId": 0,
            "ecpm": "",
            "encryptType": "",
        }

        if extra_body:
            body.update(extra_body)

        try:
            response = requests.post(url=url, headers=headers, json=body, timeout=15)
            result = response.json()
            data_info = result.get('data', {})
            toast = data_info.get('toast', '')
            coins_got = data_info.get('coins', 0)
            balance = data_info.get('balance', 0)
            is_success = data_info.get('success', False)
            code = data_info.get('code', 0)
            return is_success, toast, coins_got, balance, code
        except Exception as e:
            return False, str(e), 0, 0, -1

    def query_water_info(self):
        """查询喝水打卡状态，返回可领取的时段列表"""
        ts = int(time.time() * 1000)
        url = f'https://adse.ximalaya.com/incentive/ting/welfare/queryWaterInfo/ts-{ts}?rn-credit-bundle-version=0.0.1125'
        headers = self._get_base_headers()
        headers['Host'] = 'adse.ximalaya.com'
        try:
            response = requests.get(url=url, headers=headers, timeout=15)
            data = response.json()
            if data.get('ret') == 0:
                info = data.get('data', {})
                water_list = info.get('waterInfo', [])
                available = []
                completed = []
                for w in water_list:
                    idx = w.get('index', 0)
                    status = w.get('status', 0)
                    title = w.get('title', '')
                    coins = w.get('coins', 0)
                    time_area = w.get('timeArea', '')
                    if status == 3:
                        available.append({'index': idx, 'title': title, 'coins': coins, 'timeArea': time_area})
                    elif status == 4:
                        completed.append({'index': idx, 'title': title, 'coins': coins, 'timeArea': time_area})

                week_info = info.get('waterWeek', {})
                full_week_info = info.get('waterFullWeek', {})
                continue_day = week_info.get('continueDrinkDay', 0)
                week_coins = week_info.get('coins', 0)

                print(f"\n--- 喝水打卡 ---")
                print(f"  连续打卡: {continue_day}天 (周奖励{week_coins}金币)")
                if completed:
                    cups_str = ' '.join([f"✅{c['title']}" for c in completed])
                    print(f"  已完成: {cups_str}")
                if available:
                    cups_str = ' '.join([f"🔔{c['title']}({c['timeArea']},{c['coins']}金币)" for c in available])
                    print(f"  可领取: {cups_str}")
                if not available and not completed:
                    print(f"  暂无可用时段")
                return available, completed, week_info, full_week_info
            return [], [], {}, {}
        except Exception as e:
            print(f"查询喝水状态异常: {e}")
            return [], [], {}, {}

    def _claim_drink_water(self, water_index, coins):
        """领取单杯喝水奖励 (使用正确的 DRINK_WATER_NORMAL 参数)"""
        ts = int(time.time() * 1000)
        url = f'https://adse.ximalaya.com/incentive/ting/welfare/rewardGoldCoin/ts-{ts}?rn-credit-bundle-version=0.0.1125'
        headers = self._get_base_headers()
        headers.update({
            'Host': 'adse.ximalaya.com',
            'Content-Type': 'application/json; charset=utf-8',
        })

        body = {
            "requestId": str(uuid.uuid4()),
            "ts": ts,
            "coins": coins,
            "sourceName": "DRINK_WATER_NORMAL",
            "rewardType": 16,
            "retry": 0,
            "fallbackReq": 0,
            "index": water_index,
            "startSource": "mine_page",
            "adId": 0,
            "adResponseId": 0,
            "ecpm": "",
            "encryptType": "",
        }

        try:
            response = requests.post(url=url, headers=headers, json=body, timeout=15)
            result = response.json()
            data_info = result.get('data', {})
            toast = data_info.get('toast', '')
            coins_got = data_info.get('coins', 0)
            balance = data_info.get('balance', 0)
            is_success = data_info.get('success', False)
            code = data_info.get('code', 0)
            return is_success, toast, coins_got, balance, code
        except Exception as e:
            return False, str(e), 0, 0, -1

    # yyz 每日打卡签到 (yyz-api.nwiztech.com)
    # 已移除。原因: 接口需要动态签名验证，签名算法存在于混淆后的 JS 文件中
    # (Object(k["v"]) 函数)，涉及 sorter/stringify 等辅助函数，无法从 minified JS
    # 中提取完整算法逻辑。已知密钥 "ppjV09hq&oU]sYz" 和 caller "hbt4gkIUh5"，
    # 但 MD5 拼接方式与实际签名不匹配，且 JS 中未找到 md5 关键字，签名可能由
    # native 层计算。该签到需在 app 内手动完成。

    def query_gold_sign_in(self):
        """查询金币系统签到状态"""
        ts = int(time.time() * 1000)
        url = f'https://adse.ximalaya.com/incentive/ting/welfare/querySignInInfo/ts-{ts}?rn-credit-bundle-version=0.0.1125'
        headers = self._get_base_headers()
        headers['Host'] = 'adse.ximalaya.com'
        try:
            response = requests.get(url=url, headers=headers, timeout=15)
            data = response.json()
            if data.get('ret') == 0:
                info = data.get('data', {})
                title = info.get('title', '')
                awards = info.get('awardInfo', [])
                today_info = None
                for a in awards:
                    if a.get('today'):
                        today_info = a
                        break
                if today_info:
                    status = today_info.get('status', 0)
                    already = today_info.get('alreadyAward', 0)
                    award = today_info.get('award', 0)
                    if status == 1 or already > 0:
                        print(f"签到: 今日已签到 获得{already}金币 ({title})")
                        return True, already
                    else:
                        print(f"签到: 今日未签到 可领{award}金币 ({title})")
                        return False, award
            return None, 0
        except Exception as e:
            print(f"查询签到状态异常: {e}")
            return None, 0

    def do_sign_in(self):
        """执行签到"""
        is_success, toast, coins, balance, code = self._reward_gold_coin(
            source_name="SIGN_IN_WAKE_UP",
            reward_type=1,
            coins=8,
        )
        if is_success:
            print(f"签到成功: {toast} (获得{coins}金币, 余额{balance})")
            return True
        elif code == 10067:
            print(f"签到: {toast}")
            return True
        else:
            print(f"签到失败: {toast} (code={code})")
            return False

    def query_gold_coin_page(self):
        """查询金币中心主页数据（含余额、兑换项）"""
        ts = int(time.time() * 1000)
        url = f'https://adse.ximalaya.com/incentive/ting/welfare/queryGoldCoinPage/ts-{ts}?transactionType=1&requestVersion=20250520&rn-credit-bundle-version=0.0.1125'
        headers = self._get_base_headers()
        headers['Host'] = 'adse.ximalaya.com'
        try:
            response = requests.get(url=url, headers=headers, timeout=15)
            data = response.json()
            if data.get('ret') == 0:
                info = data.get('data', {})
                coins = info.get('coins', 0)
                enable_withdraw = info.get('enableWithDraw', False)
                print(f"金币余额: {coins}" + (" (可提现)" if enable_withdraw else ""))
                return coins
            return None
        except Exception as e:
            print(f"查询金币余额异常: {e}")
            return None

    def query_composite_tasks(self):
        """查询所有任务状态（compositeQuery 无 ticket 版）"""
        ts = int(time.time() * 1000)
        uid = self.uid or '0'
        url = (
            f'https://adse.ximalaya.com/incentive/ting/compositeQuery/ts-{ts}'
            f'?uid={uid}&drinkwater=1&exchange=1&loadingClick=1&luckyCard=1'
            f'&joyEarning=1&srcChannel=mine_page&newPage=true'
            f'&rn-credit-bundle-version=0.0.1125'
        )
        headers = self._get_base_headers()
        headers.update({
            'Host': 'adse.ximalaya.com',
            'Content-Type': 'application/json; charset=utf-8',
        })
        body = {
            "keys": [
                "carveUp", "listenTaskInfo", "freeGift", "adTask",
                "tmeDownloadTaskAdView", "cardFlipInfo", "rotaryTableInfo", "dailyTask"
            ],
        }
        try:
            response = requests.post(url=url, headers=headers, json=body, timeout=15)
            data = response.json()
            if data.get('ret') == 0:
                return data.get('data', {}).get('results', {})
            return None
        except Exception as e:
            print(f"查询任务列表异常: {e}")
            return None

    def process_daily_tasks(self, tasks_result):
        """处理每日任务列表"""
        if not tasks_result:
            return

        daily_task = tasks_result.get('dailyTask', {})
        if daily_task.get('ret') != 0:
            return

        task_list = daily_task.get('data', {}).get('list', [])
        print(f"\n--- 每日任务 ---")

        # 可自动领取的任务类型 (DRINK_WATER 单独处理，不走通用领取)
        auto_claim_types = {'JOYFUL_EAENING', 'RED_PACKET_RAIN'}
        claimable = []
        incomplete = []
        need_interact = []
        done = []
        drink_water_task = None

        for task in task_list:
            task_type = task.get('type', '')
            title = task.get('title', '')
            coins = task.get('coins', 0)
            status = task.get('status', 0)
            ext_map_str = task.get('extMap', '{}')
            try:
                ext_map = json.loads(ext_map_str)
            except (json.JSONDecodeError, TypeError):
                ext_map = {}
            task_id = ext_map.get('taskId', task.get('taskId', ''))

            entry = (task_type, title, coins, status, task_id)

            if task_type == 'DRINK_WATER':
                drink_water_task = entry
            elif task_type == 'EXCHANGE':
                need_interact.append(entry)
            elif status == 2:
                done.append(entry)
            elif task_type in auto_claim_types:
                if status == 1:
                    claimable.append(entry)
                else:
                    incomplete.append(entry)
            else:
                need_interact.append(entry)

        # 处理喝水补贴 (通过 queryWaterInfo + 正确参数领取)
        if drink_water_task:
            task_type, title, coins, status, task_id = drink_water_task
            if status == 2:
                print(f"  [{task_type}] {title} - 已领取")
            else:
                self._process_drink_water(title, coins)

        # 展示可领取任务
        for task_type, title, coins, status, task_id in claimable:
            print(f"  [{task_type}] {title} (可领取) {coins}金币")
            self._try_claim_daily_task(task_type, task_id, coins, title)

        # 展示未完成任务
        for task_type, title, coins, status, task_id in incomplete:
            if task_type == 'JOYFUL_EAENING':
                print(f"  [{task_type}] {title} (未完成) {coins}金币 - 需在app内打开yyz页面完成签到后领取")
            else:
                print(f"  [{task_type}] {title} (未完成) {coins}金币 - 需在app内完成交互后领取")

        # 展示需交互任务
        for task_type, title, coins, status, task_id in need_interact:
            if task_type == 'EXCHANGE':
                print(f"  [{task_type}] {title} - 需跳转外部app")
            else:
                print(f"  [{task_type}] {title} ({coins}金币) - 需app内交互")

        # 展示已领取
        for task_type, title, coins, status, task_id in done:
            print(f"  [{task_type}] {title} - 已领取")

    def _process_drink_water(self, title, _daily_coins):
        """处理喝水补贴：查询可领取时段并逐个领取"""
        available, completed, week_info, _full_week_info = self.query_water_info()

        if not available:
            if not completed:
                print(f"  [DRINK_WATER] {title} - 暂无可用时段，需等待到对应时间")
            return

        print(f"\n  [DRINK_WATER] 开始领取喝水补贴...")
        for cup in available:
            idx = cup['index']
            cup_title = cup['title']
            coins = cup['coins']
            time_area = cup['timeArea']
            print(f"    领取 {cup_title}({time_area}, {coins}金币)...", end=' ')

            is_success, toast, _got_coins, balance, code = self._claim_drink_water(idx, coins)
            if is_success:
                print(f"✅ {toast} (余额{balance})")
            elif code in (10067, 10003):
                print(f"⚠️ {toast}")
            else:
                print(f"❌ {toast} (code={code})")

        # 检查是否有周奖励
        if week_info.get('status') == 1:
            week_coins = week_info.get('coins', 0)
            print(f"    周奖励可领取: {week_coins}金币 - 需在app内手动领取")

    def _try_claim_daily_task(self, task_type, _task_id, coins, _title):
        """尝试领取每日任务奖励"""
        reward_type_map = {
            'JOYFUL_EAENING': 1,
            'RED_PACKET_RAIN': 1,
        }

        if task_type not in reward_type_map:
            return

        reward_type = reward_type_map[task_type]
        is_success, toast, got_coins, balance, code = self._reward_gold_coin(
            source_name=task_type,
            reward_type=reward_type,
            coins=coins,
        )

        if is_success:
            print(f"    ✅ 领取成功: {toast} (获得{got_coins}金币, 余额{balance})")
            return True
        elif code in (10067, 10003):
            print(f"    ⚠️ {toast}")
            return True
        else:
            print(f"    ❌ 领取失败: {toast} (code={code})")
            return False

    def _try_spinning_wheel_draw(self, draw_type):
        """尝试幸运大转盘首次免费抽奖"""
        print(f"    尝试免费抽奖...", end=' ')
        is_success, toast, coins_got, balance, code = self._reward_gold_coin(
            source_name="SPINNING_WHEEL",
            reward_type=draw_type,
            coins=0,
        )
        if is_success:
            print(f"✅ {toast} (获得{coins_got}金币, 余额{balance})")
            return True
        elif code in (10067, 10003):
            print(f"⚠️ {toast}")
            return True
        else:
            print(f"❌ {toast} (code={code})")
            return False

    def show_other_tasks(self, tasks_result):
        """展示其他任务状态"""
        if not tasks_result:
            return

        print(f"\n--- 其他任务 ---")

        # 瓜分任务
        carve_up = tasks_result.get('carveUp', {})
        if carve_up.get('ret') == 0:
            data = carve_up.get('data', {})
            done = data.get('alreadyRewardTimes', 0)
            total = data.get('maxRewardTimes', 0)
            progress = data.get('progress', 0)
            pct = f" ({progress}%)" if progress else ""
            print(f"  瓜分百亿金币: {done}/{total}次广告{pct} - 需看广告")

        # 翻卡任务
        card_flip = tasks_result.get('cardFlipInfo', {})
        if card_flip.get('ret') == 0:
            data = card_flip.get('data', {})
            done = data.get('alreadyRewardTimes', 0)
            total = data.get('maxRewardTimes', 0)
            print(f"  翻卡赢金币: {done}/{total}次 - 需看广告")

        # 免费礼物
        free_gift = tasks_result.get('freeGift', {})
        if free_gift.get('ret') == 0:
            data = free_gift.get('data', {})
            done = data.get('finishedAdCount', 0)
            total = data.get('allAdCount', 0)
            print(f"  免费礼物: {done}/{total}个广告 - 需看广告")

        # 听书任务 (需要真实听书行为，无法自动化)
        listen_task = tasks_result.get('listenTaskInfo', {})
        if listen_task.get('ret') == 0:
            data = listen_task.get('data', {})
            step_info = data.get('stepInfo', [])
            if step_info:
                parts = []
                for s in step_info:
                    status = s.get('status', 0)
                    coins = s.get('amount', 0)
                    condition = s.get('condition', 0)
                    if status == 1:
                        parts.append(f"✅{condition}分钟{coins}金币")
                    else:
                        parts.append(f"⬜{condition}分钟{coins}金币")
                print(f"  听书任务: {' | '.join(parts)} - 需真实听书，无法自动化")
            else:
                print(f"  听书任务: 无数据 - 需真实听书，无法自动化")

        # 幸运大转盘
        rotary = tasks_result.get('rotaryTableInfo', {})
        if rotary.get('ret') == 0:
            data = rotary.get('data', {})
            first_free = data.get('firstFree', False)
            today = data.get('todayCount', 0)
            max_today = data.get('todayCountMax', 0)
            cost = data.get('costCoins', 0)
            button_text = data.get('buttonText', '')
            draw_type = data.get('drawType', 3)
            if first_free:
                print(f"  幸运大转盘: 🎁 首次免费可抽! {today}/{max_today}次")
                self._try_spinning_wheel_draw(draw_type)
            else:
                print(f"  幸运大转盘: {cost}金币/次 或 {button_text} {today}/{max_today}次 - 需看广告，无法自动化")

        # 广告任务
        ad_task = tasks_result.get('adTask', {})
        if ad_task.get('ret') == 0:
            data = ad_task.get('data', {})
            task_list = data.get('list', [])
            if task_list:
                done_count = sum(1 for t in task_list if t.get('awardText') != '待解锁')
                total_count = len(task_list)
                print(f"  广告任务: {done_count}/{total_count}个已完成 - 需看广告，无法自动化")

    def get_user_info(self):
        m_url = 'https://m.ximalaya.com/business-vip-presale-mobile-web/page/ts-1671779856199?version=9.5.1'
        m_headers = {
            'Host': 'm.ximalaya.com',
            'Accept': 'application/json, text/plain, */*',
            'Connection': 'keep-alive',
            'Cookie': self.cookie,
            'User-Agent': 'ting_9.5.1(RMX5062,Android35)',
            'Accept-Encoding': 'gzip, deflate',
        }
        try:
            response = requests.get(url=m_url, headers=m_headers, timeout=15)
            user_info = response.json().get('data', {}).get('modules', [{}])[0].get('userInfo', {})
            userId = user_info.get('userId', '') or self.uid or ''
            nickName = user_info.get('nickName', '')
            subtitle = user_info.get('subtitle', '')
            print(f"\nID: {userId} 用户名: {nickName} VIP到期日期: {subtitle}")
            return True
        except Exception as e:
            print(f"获取用户信息异常: {e}")
            return False

    def main(self):
        global success
        print(f"\n---------开始执行第{self.index}个账号>>>>>")

        sign_ok = False

        # 1. 查询签到状态
        already_signed, _ = self.query_gold_sign_in()

        if already_signed is True:
            sign_ok = True
        elif already_signed is False:
            sign_ok = self.do_sign_in()
        elif already_signed is None:
            sign_ok = self.do_sign_in()

        if not sign_ok:
            print("签到失败，请检查 cookie 是否有效")
            success = False

        # 2. 查询金币余额
        self.query_gold_coin_page()

        # 3. 查询并处理任务 (含喝水补贴自动领取)
        tasks_result = self.query_composite_tasks()
        if tasks_result:
            self.process_daily_tasks(tasks_result)
            self.show_other_tasks(tasks_result)

        self.get_user_info()
        return True


if __name__ == '__main__':
    token = os.environ.get('ONESIGN_XMLY_COOKIE', '')
    if not token:
        print("未配置 ONESIGN_XMLY_COOKIE 变量")
        sys.exit(1)
    tokens = token.split('#')
    tokens = [t for t in tokens if t]
    print(f"共获取到{len(tokens)}个账号")
    for idx, info in enumerate(tokens):
        RUN(info, idx).main()
    if not success:
        sys.exit(1)
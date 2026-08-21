#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
抓包：喜马拉雅 app → 我的 → 福利中心 → 抓包获取 cookie
变量：ONESIGN_XMLY_COOKIE（cookie 值，多账号用 # 分隔）

cron: 0 */2 * * *
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

SCRIPT_NAME = "喜马拉雅"
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
            'User-Agent': 'ting_9.5.4(RMX5062,Android35)',
            'Accept-Encoding': 'gzip, deflate',
        }

    _last_reward_time = 0
    _reward_cooldown = 3  # 两次 rewardGoldCoin 请求之间的最小间隔(秒)

    # 广告位标识 (从抓包提取，所有请求共用)
    _AD_PI = "7_3_96_35_172_2_1029_86_1053_97_124_33_22"
    _AD_PN = "500_1067_312_1040_121_1165_592_284_1027_866_201_442_8_178_942_61_543_864_976_1097_1047_879_9_463_1187_449_514_271_1058_1138_1194_475_245_538_177_132_404_345_276_1180_1128_1010_402_544_341_205_29_998_101_286_852_123_411_440_25_355_620_1099_551_554_504_1078_1162_896_242_460_859_602_948_934_835_119_882_1188_215_454_1170_958_362_20_418_512_527_1045_162_156_114_180_477_256_1126_1114_407_388_860_340_1008_1171_363_16_618_251_145_1164_989_977_261_233_1175_397_995_1155_1136_1163_888_289_169_185_1005_1181_1134_932_305_601_1182_139_262_153_903_1006_1177_1020_409_1089_122_371_878_589_898_1061_936_1159_887_182_978_329_586_949_487_943_547_963_1028_568_196_200_1139_152_1143_1092_1043_72_1056_243_1189_507_844_390_972_207_1038_996_938_571_557_319_840_899_886_577_444_956_158_293_1030_513_349_291_1130_1150_473_1036_23_842_435_597_337_979_890_590_250_894_501_1157_298_386_127_147_1124_519_373_358_502_255_492_1168_1021_906_259_75_494_85_576_466_118_617_905_532_563_599_204_1044_608_985_845_238_964_987_1137_489_176_190_297_884_283_311_993_900_136_239_511_135_387_288_433_961_1093_910_1069_991_333_851_202_249_885_479_580_549_357_389_375_456_24_1064_166_465_834_952_1087_548_1111_626_1185_1147_596_194_383_483_78_622_254_459_19_517_616_52_342_1190_534_546_883_159_1031_263_1110_603_614_146_377_965_545_384_1002_858_1039_1121_1102_615_199_982_974_574_1077_1167_1148_874_113_350_935_1094_992_871_1023_21_195_299_432_31_438_1001_434_955_99_959_403_907_423_225_64_837_981_1096_247_290_593_1140_1026_65_314_893_572_41_530_1079_573_490_1054_1199_624_518_833_1070_227_986_408_967_32_584_1071_1018_142_1082_1141_398_1055_287_47_983_313_1145_1191_90_265_55_839_1133_120_843_183_578_1123_1098_997_623_1074_495_836_352_889_189_484_607_1017_1035_510_133_137_1022_1117_498_1066_369_480_937_1160_144_550_1115_1042_876_394_901_130_868_457_1032_1000_448_464_908_1052_469_975_1049_1129_850_1125_1050_1037_891_58_115_410_1090_980_353_134_944_94_441_366_559_116_1057_1034_1085_486_1184_206_48_619_17_611_322_458_54_857_582_1025_173_193_292_945_308_508_1172_1075_1151_268_339_1192_336_1153_385_1103_213_587_1195_111_223_44_326_417_450_370_413_579_954_203_88_970_302_1193_447_875_849_170_11_100_93_1095_80_368_400_841_92_1012_467_1059_621_1062_470_523_867_266_1011_160_1073_237_220_443_405_939_165_1100_491_1024_971_1135_399_569_1149_1144_560_496_1106_476_226_401_367_984_1014_1120_315_241_198_1152_951_946_892_109_98_1104_274_880_610_1091_253_865_881_509_988_306_1197_46_462_1174_1112_529_846_1086_149_216_26_264_15_1132_393_62_613_1176_909_343_962_392_848_181_1083_556_869_863_258_257_581_344_231_1065_57_990_323_461_872_1068_174_968_1046_63_605_567_999_565_950_1105_212_1041_521_481_347_1108_969_1_151_525_583_493_853_275_154_316_895_539_218_629_1156_260_541_1113_191_360_171_186_585_526_163_269_1178_1033_604_208_321_280_282_131_1009_126_598_112_1088_515_1072_482_240_1048_966_1016_210_953_141_627_455_51_1173_252_506_328_1015_30_570_1158_1119_1200_497_39_278_870_1169_856_994_232_524_378_187_351_235_591_296_1109_499_228_248_536_1013_1084_1101_902_277_957_304_566_1051_540_1154_12_873_40_973_320_437_453_861_91_110_564_904_1183_53_452_1063_83_1116_5_1060_222_1198_217_219_1076_947_1019_854_138_346_1131_855_940_1146_419_595_600_1179_332_1080_960_157_184_10_471_897_1118_847_214_1142_505_330_451_552_334_528_445_361_488_561_273_862_230_140_143_324_612_128_406_436_356_244_439_272_281_575_382_338_474_150_270_478_838_625_1007_877_359_167_1196_503_1166_317_148_14_533_246_933_520_1081_535_609_1161_175_197_542_1186"
    _BUNDLE_VERSION = "0.0.1142"

    # 广告验证参数 (从抓包成功请求提取，用于绕过广告观看验证)
    # 注意: ticket/signature 可能有时效性，如果失效需重新抓包获取
    _AD_TICKET = "TACaoav6TNJWSQ-gj9xuovybE7bQSrOW66oVJJzSCUigYZC2k-JYS2uQqamX1XzLS46wH4-G6UZnvdKkkrjQAblYjzfcedjb20ueGltYWxheWEudGluZy5hbmRyb2lkITEuMy4yNyE5LjUuNC4zIWI9aW5jZW50aXZlcyZzPWdvbGRfcmV3YXJkJnU9OTM0MDQ4NDI"
    _AD_SIGNATURE = "dfc7cea6266aa8006747ea60c16e68aa"
    _AD_ID = "246993186"
    _AD_RESPONSE_ID = "22844414336433"
    _AD_ECPM = "Z8LGKspRdNuY+7JmFzhJ8obxWil0UwoI1u6p+eSlsIKGRj8Wv/3P3yKBPSiCsPB6OSpW2ggodBlb\nG9qEZBRtZg==\n"
    _AD_ENCRYPT_TYPE = 1

    def _reward_gold_coin(self, source_name, reward_type, coins=0, extra_body=None, ad_data=None):
        """通用金币领取方法。ad_data 为广告验证参数，非广告任务可为 None"""
        elapsed = time.time() - self._last_reward_time
        if elapsed < self._reward_cooldown:
            wait = self._reward_cooldown - elapsed
            time.sleep(wait)
        self._last_reward_time = time.time()

        ts = int(time.time() * 1000)
        url = f'https://adse.ximalaya.com/incentive/ting/welfare/rewardGoldCoin/ts-{ts}?rn-credit-bundle-version={self._BUNDLE_VERSION}'
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
            "startSource": "home_page_price_sensitive",
            "adId": 0,
            "adResponseId": 0,
            "ecpm": "",
            "encryptType": "",
            "adPI": self._AD_PI,
            "adPN": self._AD_PN,
        }

        if ad_data:
            body.update(ad_data)

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
        """领取单杯喝水奖励（复用 _reward_gold_coin 的冷却机制）"""
        return self._reward_gold_coin(
            source_name="DRINK_WATER_NORMAL",
            reward_type=16,
            coins=coins,
            extra_body={"index": water_index, "startSource": "mine_page"},
        )

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
        elif code in (10067, 10003, 10001):
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
            elif code in (10067, 10003, 10001):
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
        elif code in (10067, 10003, 10001):
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
        elif code in (10067, 10003, 10001):
            print(f"⚠️ {toast}")
            return True
        else:
            print(f"❌ {toast} (code={code})")
            return False

    def _try_claim_ad_reward(self, source_name, reward_type, coins, task_name):
        """尝试领取广告类任务奖励（使用抓包获取的广告验证参数模拟广告观看完成）"""
        print(f"    尝试领取 {task_name}...", end=' ')
        ad_data = {
            "adId": self._AD_ID,
            "adResponseId": self._AD_RESPONSE_ID,
            "ecpm": self._AD_ECPM,
            "encryptType": self._AD_ENCRYPT_TYPE,
        }
        extra_body = {
            "ticket": self._AD_TICKET,
            "signature": self._AD_SIGNATURE,
            "isSecondPhaseCompleted": False,
            "secondPhaseType": 0,
            "isUnisdk": True,
            "verify_str": "",
        }
        is_success, toast, got_coins, balance, code = self._reward_gold_coin(
            source_name=source_name,
            reward_type=reward_type,
            coins=coins,
            ad_data=ad_data,
            extra_body=extra_body,
        )
        if is_success:
            print(f"✅ {toast} (获得{got_coins}金币, 余额{balance})")
            return True
        elif code in (10067, 10003, 10001):
            print(f"⚠️ {toast}")
            return True
        else:
            print(f"❌ {toast} (code={code})")
            return False

    def show_other_tasks(self, tasks_result):
        """展示其他任务状态，每轮只尝试领取一个广告奖励"""
        if not tasks_result:
            return

        print(f"\n--- 其他任务 ---")

        # DEBUG: 打印各任务类型的完整数据（用于分析 sourceName/rewardType）
        for key in ['carveUp', 'cardFlipInfo', 'freeGift', 'adTask', 'rotaryTableInfo']:
            task_data = tasks_result.get(key, {})
            if task_data.get('ret') == 0:
                data = task_data.get('data', {})
                print(f"  [DEBUG] {key}: {json.dumps(data, ensure_ascii=False)}")

        claimed_this_round = False

        # 幸运大转盘 (优先级最高，首次免费)
        rotary = tasks_result.get('rotaryTableInfo', {})
        if not claimed_this_round and rotary.get('ret') == 0:
            data = rotary.get('data', {})
            first_free = data.get('firstFree', False)
            today = data.get('todayCount', 0)
            max_today = data.get('todayCountMax', 0)
            cost = data.get('costCoins', 0)
            button_text = data.get('buttonText', '')
            draw_type = data.get('drawType', 3)
            if first_free and today < max_today:
                print(f"  幸运大转盘: 🎁 首次免费可抽! {today}/{max_today}次")
                self._try_spinning_wheel_draw(draw_type)
                claimed_this_round = True
            elif first_free:
                print(f"  幸运大转盘: 🎁 首次免费已用完 {today}/{max_today}次")
            else:
                print(f"  幸运大转盘: {cost}金币/次 或 {button_text} {today}/{max_today}次 - 需看广告")

        # 瓜分百亿金币
        carve_up = tasks_result.get('carveUp', {})
        if not claimed_this_round and carve_up.get('ret') == 0:
            data = carve_up.get('data', {})
            done = data.get('alreadyRewardTimes', 0)
            total = data.get('maxRewardTimes', 0)
            progress = data.get('progress', 0)
            pct = f" ({progress}%)" if progress else ""
            remaining = total - done
            if remaining > 0:
                print(f"  瓜分百亿金币: {done}/{total}次广告{pct}")
                self._try_claim_ad_reward("CARVE_UP", 1, 0, f"瓜分第{done + 1}次")
                claimed_this_round = True
            else:
                print(f"  瓜分百亿金币: {done}/{total}次广告{pct} - 已完成")

        # 翻卡赢金币
        card_flip = tasks_result.get('cardFlipInfo', {})
        if not claimed_this_round and card_flip.get('ret') == 0:
            data = card_flip.get('data', {})
            done = data.get('alreadyRewardTimes', 0)
            total = data.get('maxRewardTimes', 0)
            remaining = total - done
            if remaining > 0:
                print(f"  翻卡赢金币: {done}/{total}次")
                self._try_claim_ad_reward("CARD_FLIP", 1, 0, f"翻卡第{done + 1}次")
                claimed_this_round = True
            else:
                print(f"  翻卡赢金币: {done}/{total}次 - 已完成")

        # 免费礼物
        free_gift = tasks_result.get('freeGift', {})
        if not claimed_this_round and free_gift.get('ret') == 0:
            data = free_gift.get('data', {})
            done = data.get('finishedAdCount', 0)
            total = data.get('allAdCount', 0)
            remaining = total - done
            if remaining > 0:
                print(f"  免费礼物: {done}/{total}个广告")
                self._try_claim_ad_reward("FREE_GIFT", 1, 0, f"免费礼物第{done + 1}次")
                claimed_this_round = True
            else:
                print(f"  免费礼物: {done}/{total}个广告 - 已完成")

        # 广告任务
        ad_task = tasks_result.get('adTask', {})
        if not claimed_this_round and ad_task.get('ret') == 0:
            data = ad_task.get('data', {})
            task_list = data.get('list', [])
            if task_list:
                done_count = sum(1 for t in task_list if t.get('awardText') != '待解锁')
                total_count = len(task_list)
                remaining = total_count - done_count
                if remaining > 0:
                    print(f"  广告任务: {done_count}/{total_count}个已完成")
                    self._try_claim_ad_reward("AD_TASK", 1, 0, f"广告任务第{done_count + 1}个")
                    claimed_this_round = True
                else:
                    print(f"  广告任务: {done_count}/{total_count}个已完成")

        if claimed_this_round:
            print(f"  💡 本轮已领取1个奖励，剩余奖励下次执行时继续")

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
        notify_failure(SCRIPT_NAME, success)
        sys.exit(1)
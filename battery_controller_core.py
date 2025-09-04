#!/usr/bin/env python3
import subprocess
import re
import time
import asyncio
import sys
from datetime import datetime

# Tapo P110M制御用ライブラリのインポート（インストール必要）
try:
    from tapo import ApiClient
    TAPO_AVAILABLE = True
except ImportError:
    TAPO_AVAILABLE = False
    print("警告: tapoライブラリがインストールされていません")
    print("インストール方法: pip install tapo")

class BatteryChargeController:
    def __init__(self, tapo_username=None, tapo_password=None, device_ip=None):
        self.tapo_username = tapo_username
        self.tapo_password = tapo_password
        self.device_ip = device_ip
        self.client = None
        self.device = None
        
        # 充電制御の閾値
        self.charge_start_threshold = 30  # 30%以下で充電開始
        self.charge_stop_threshold = 78   # 78%以上で充電停止
        
        # 状態管理
        self.last_action = None
        self.last_battery_level = None
        
    async def init_tapo_device(self):
        """Tapo P110Mデバイスを初期化"""
        if not TAPO_AVAILABLE:
            print("Tapoライブラリが利用できません")
            return False
            
        if not all([self.tapo_username, self.tapo_password, self.device_ip]):
            print("Tapo設定が不完全です")
            return False
            
        try:
            self.client = ApiClient(self.tapo_username, self.tapo_password)
            self.device = await self.client.p110(self.device_ip)
            print("Tapo P110M接続成功")
            return True
        except Exception as e:
            print(f"Tapo P110M接続エラー: {e}")
            return False
    
    async def turn_on_charger(self):
        """充電器をONにする"""
        if self.device:
            try:
                await self.device.on()
                print("充電器をONにしました")
                self.last_action = "ON"
                return True
            except Exception as e:
                print(f"充電器ON エラー: {e}")
                return False
        else:
            print("シミュレーション: 充電器をONにしました")
            self.last_action = "ON"
            return True
    
    async def turn_off_charger(self):
        """充電器をOFFにする"""
        if self.device:
            try:
                await self.device.off()
                print("充電器をOFFにしました")
                self.last_action = "OFF"
                return True
            except Exception as e:
                print(f"充電器OFF エラー: {e}")
                return False
        else:
            print("シミュレーション: 充電器をOFFにしました")
            self.last_action = "OFF"
            return True
    
    def get_battery_percentage(self):
        """macOSのバッテリー残量を取得"""
        try:
            result = subprocess.run(['pmset', '-g', 'batt'], capture_output=True, text=True)
            output = result.stdout
            
            match = re.search(r'(\d+)%', output)
            if match:
                return int(match.group(1))
            else:
                return None
        except Exception as e:
            print(f"バッテリー情報の取得エラー: {e}")
            return None

    def is_charging(self):
        """充電中かどうかを確認"""
        try:
            result = subprocess.run(['pmset', '-g', 'batt'], capture_output=True, text=True)
            output = result.stdout.lower()
            
            # より正確な判定: 'charging' があり、かつ 'not charging' がない
            if 'charging' in output and 'not charging' not in output:
                return True
            else:
                return False
        except Exception as e:
            print(f"充電状態の確認エラー: {e}")
            return False

    async def control_charging(self):
        """充電制御のメインロジック"""
        battery_level = self.get_battery_percentage()
        is_charging_now = self.is_charging()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if battery_level is None:
            print(f"[{timestamp}] バッテリー情報を取得できませんでした")
            return
        
        # 状態表示
        charging_status = "充電中" if is_charging_now else "放電中"
        print(f"[{timestamp}] バッテリー: {battery_level}% ({charging_status})")
        
        # 充電制御ロジック
        action_taken = False
        
        # 30%以下で充電開始
        if battery_level <= self.charge_start_threshold:
            if self.last_action != "ON":
                print(f"  → バッテリーが{self.charge_start_threshold}%以下になりました。充電を開始します。")
                await self.turn_on_charger()
                action_taken = True
        
        # 78%以上で充電停止
        elif battery_level >= self.charge_stop_threshold:
            if self.last_action != "OFF":
                print(f"  → バッテリーが{self.charge_stop_threshold}%以上になりました。充電を停止します。")
                await self.turn_off_charger()
                action_taken = True
        
        # 状態変化がない場合の情報表示
        if not action_taken and self.last_battery_level != battery_level:
            if battery_level < self.charge_start_threshold:
                print(f"  → 充電中: 次の停止は{self.charge_stop_threshold}%")
            elif battery_level > self.charge_stop_threshold:
                print(f"  → 放電中: 次の開始は{self.charge_start_threshold}%")
            else:
                print(f"  → 通常範囲: {self.charge_start_threshold}%-{self.charge_stop_threshold}%")
        
        self.last_battery_level = battery_level

    async def run_monitor(self, check_interval=60):
        """バッテリー監視と充電制御を実行"""
        print("バッテリー充電制御を開始します...")
        print(f"充電開始閾値: {self.charge_start_threshold}%")
        print(f"充電停止閾値: {self.charge_stop_threshold}%")
        print(f"チェック間隔: {check_interval}秒")
        print("Ctrl+C で終了")
        print("-" * 50)
        
        # Tapoデバイス初期化
        await self.init_tapo_device()
        
        try:
            while True:
                await self.control_charging()
                await asyncio.sleep(check_interval)
                
        except KeyboardInterrupt:
            print("\nバッテリー充電制御を終了しました")

def main():
    """メイン関数"""
    print("バッテリー充電制御アプリ")
    print("=" * 50)
    
    # 設定ファイルから読み込み
    try:
        from config import (
            TAPO_USERNAME, TAPO_PASSWORD, DEVICE_IP,
            CHARGE_START_THRESHOLD, CHARGE_STOP_THRESHOLD,
            CHECK_INTERVAL, SIMULATION_MODE
        )
    except ImportError:
        print("警告: config.pyが見つかりません。デフォルト設定を使用します。")
        TAPO_USERNAME = None
        TAPO_PASSWORD = None  
        DEVICE_IP = None
        CHARGE_START_THRESHOLD = 30
        CHARGE_STOP_THRESHOLD = 78
        CHECK_INTERVAL = 60
        SIMULATION_MODE = True
    
    # コントローラーを初期化
    controller = BatteryChargeController(
        tapo_username=TAPO_USERNAME,
        tapo_password=TAPO_PASSWORD,
        device_ip=DEVICE_IP
    )
    
    # 閾値設定を更新
    controller.charge_start_threshold = CHARGE_START_THRESHOLD
    controller.charge_stop_threshold = CHARGE_STOP_THRESHOLD
    
    if SIMULATION_MODE:
        print("シミュレーションモードで動作します（実際のTapoデバイス制御は行いません）")
    
    # 非同期実行
    try:
        asyncio.run(controller.run_monitor(check_interval=CHECK_INTERVAL))
    except KeyboardInterrupt:
        print("\nプログラムを終了しました")

if __name__ == "__main__":
    main()
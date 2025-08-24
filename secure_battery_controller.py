#!/usr/bin/env python3
import subprocess
import re
import time
import asyncio
import sys
import os
from datetime import datetime
from security import SecureConfig, SecurityLogger, cleanup_sensitive_data

try:
    from tapo import ApiClient
    TAPO_AVAILABLE = True
except ImportError:
    TAPO_AVAILABLE = False
    print("警告: tapoライブラリがインストールされていません")

class SecureBatteryChargeController:
    def __init__(self, use_secure_config=True):
        self.use_secure_config = use_secure_config
        self.secure_config = SecureConfig() if use_secure_config else None
        self.security_logger = SecurityLogger()
        
        self.client = None
        self.device = None
        
        # デフォルト設定
        self.charge_start_threshold = 30
        self.charge_stop_threshold = 78
        self.check_interval = 60
        self.debug_mode = True
        self.simulation_mode = True
        
        # 認証情報（メモリ上でのみ保持）
        self.tapo_username = None
        self.tapo_password = None
        self.device_ip = None
        
        # 状態管理
        self.last_action = None
        self.last_battery_level = None
        
        # セキュリティログ初期化
        self.security_logger.log_event("INIT", "セキュアバッテリーコントローラー初期化")
    
    def load_configuration(self, password=None):
        """設定を読み込み（セキュア/通常）"""
        try:
            if self.use_secure_config and self.secure_config:
                # セキュアな設定ファイルから読み込み
                config_data = self.secure_config.decrypt_config(password)
                if not config_data:
                    self.security_logger.log_event("ERROR", "セキュア設定の読み込み失敗")
                    return False
                
                self.tapo_username = config_data.get('TAPO_USERNAME')
                self.tapo_password = config_data.get('TAPO_PASSWORD')
                self.device_ip = config_data.get('DEVICE_IP')
                self.charge_start_threshold = config_data.get('CHARGE_START_THRESHOLD', 30)
                self.charge_stop_threshold = config_data.get('CHARGE_STOP_THRESHOLD', 78)
                self.check_interval = config_data.get('CHECK_INTERVAL', 60)
                self.debug_mode = config_data.get('DEBUG_MODE', True)
                self.simulation_mode = config_data.get('SIMULATION_MODE', True)
                
                self.security_logger.log_event("CONFIG", "セキュア設定読み込み成功")
                
            else:
                # 従来のconfig.pyから読み込み
                try:
                    from config import (
                        TAPO_USERNAME, TAPO_PASSWORD, DEVICE_IP,
                        CHARGE_START_THRESHOLD, CHARGE_STOP_THRESHOLD,
                        CHECK_INTERVAL, SIMULATION_MODE, DEBUG_MODE
                    )
                    
                    self.tapo_username = TAPO_USERNAME
                    self.tapo_password = TAPO_PASSWORD
                    self.device_ip = DEVICE_IP
                    self.charge_start_threshold = CHARGE_START_THRESHOLD
                    self.charge_stop_threshold = CHARGE_STOP_THRESHOLD
                    self.check_interval = CHECK_INTERVAL
                    self.simulation_mode = SIMULATION_MODE
                    self.debug_mode = DEBUG_MODE
                    
                    self.security_logger.log_event("CONFIG", "通常設定読み込み成功")
                    
                except ImportError:
                    self.security_logger.log_event("ERROR", "設定ファイルが見つかりません")
                    return False
            
            return True
            
        except Exception as e:
            self.security_logger.log_event("ERROR", f"設定読み込みエラー: {str(e)}")
            return False
    
    async def init_tapo_device(self):
        """Tapo P110Mデバイスを初期化"""
        if not TAPO_AVAILABLE:
            self.security_logger.log_event("WARNING", "Tapoライブラリが利用できません")
            return False
            
        if not all([self.tapo_username, self.tapo_password, self.device_ip]):
            self.security_logger.log_event("ERROR", "Tapo設定が不完全です")
            return False
        
        try:
            self.client = ApiClient(self.tapo_username, self.tapo_password)
            self.device = await self.client.p110(self.device_ip)
            
            # 接続テスト
            device_info = await self.device.get_device_info()
            device_model = device_info.model if hasattr(device_info, 'model') else 'Unknown'
            
            self.security_logger.log_event("CONNECT", f"Tapo接続成功: {device_model}")
            if self.debug_mode:
                print("✅ Tapo P110M接続成功")
            
            return True
            
        except Exception as e:
            self.security_logger.log_event("ERROR", f"Tapo接続エラー: {str(e)}")
            if self.debug_mode:
                print(f"❌ Tapo P110M接続エラー: {e}")
            return False
        finally:
            # 認証情報をメモリからクリア
            cleanup_sensitive_data()
    
    async def turn_on_charger(self):
        """充電器をONにする"""
        try:
            if self.device and not self.simulation_mode:
                await self.device.on()
                self.security_logger.log_event("ACTION", "充電器ON")
                if self.debug_mode:
                    print("🔌 充電器をONにしました")
            else:
                self.security_logger.log_event("SIMULATION", "充電器ON（シミュレーション）")
                if self.debug_mode:
                    print("🔌 シミュレーション: 充電器をONにしました")
            
            self.last_action = "ON"
            return True
            
        except Exception as e:
            self.security_logger.log_event("ERROR", f"充電器ON失敗: {str(e)}")
            if self.debug_mode:
                print(f"❌ 充電器ON エラー: {e}")
            return False
    
    async def turn_off_charger(self):
        """充電器をOFFにする"""
        try:
            if self.device and not self.simulation_mode:
                await self.device.off()
                self.security_logger.log_event("ACTION", "充電器OFF")
                if self.debug_mode:
                    print("🔌 充電器をOFFにしました")
            else:
                self.security_logger.log_event("SIMULATION", "充電器OFF（シミュレーション）")
                if self.debug_mode:
                    print("🔌 シミュレーション: 充電器をOFFにしました")
            
            self.last_action = "OFF"
            return True
            
        except Exception as e:
            self.security_logger.log_event("ERROR", f"充電器OFF失敗: {str(e)}")
            if self.debug_mode:
                print(f"❌ 充電器OFF エラー: {e}")
            return False
    
    def get_battery_percentage(self):
        """macOSのバッテリー残量を取得"""
        try:
            result = subprocess.run(['pmset', '-g', 'batt'], 
                                  capture_output=True, text=True, timeout=10)
            output = result.stdout
            
            match = re.search(r'(\d+)%', output)
            if match:
                return int(match.group(1))
            else:
                self.security_logger.log_event("WARNING", "バッテリー情報のパース失敗")
                return None
                
        except subprocess.TimeoutExpired:
            self.security_logger.log_event("ERROR", "バッテリー情報取得タイムアウト")
            return None
        except Exception as e:
            self.security_logger.log_event("ERROR", f"バッテリー情報取得エラー: {str(e)}")
            return None

    def is_charging(self):
        """充電中かどうかを確認"""
        try:
            result = subprocess.run(['pmset', '-g', 'batt'], 
                                  capture_output=True, text=True, timeout=10)
            output = result.stdout
            return 'charging' in output.lower()
        except Exception as e:
            self.security_logger.log_event("ERROR", f"充電状態確認エラー: {str(e)}")
            return False

    async def control_charging(self):
        """充電制御のメインロジック"""
        battery_level = self.get_battery_percentage()
        is_charging_now = self.is_charging()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if battery_level is None:
            if self.debug_mode:
                print(f"[{timestamp}] ❌ バッテリー情報を取得できませんでした")
            return
        
        # 状態表示
        charging_status = "充電中" if is_charging_now else "放電中"
        status_message = f"バッテリー: {battery_level}% ({charging_status})"
        
        if self.debug_mode:
            print(f"[{timestamp}] 🔋 {status_message}")
        
        # セキュリティログに記録（バッテリーレベルは非機密情報として記録）
        self.security_logger.log_event("STATUS", status_message)
        
        # 充電制御ロジック
        action_taken = False
        
        # 30%以下で充電開始
        if battery_level <= self.charge_start_threshold:
            if self.last_action != "ON":
                if self.debug_mode:
                    print(f"  → バッテリーが{self.charge_start_threshold}%以下になりました。充電を開始します。")
                await self.turn_on_charger()
                action_taken = True
        
        # 78%以上で充電停止
        elif battery_level >= self.charge_stop_threshold:
            if self.last_action != "OFF":
                if self.debug_mode:
                    print(f"  → バッテリーが{self.charge_stop_threshold}%以上になりました。充電を停止します。")
                await self.turn_off_charger()
                action_taken = True
        
        # 状態変化がない場合の情報表示
        if not action_taken and self.last_battery_level != battery_level and self.debug_mode:
            if battery_level < self.charge_start_threshold:
                print(f"  → 充電中: 次の停止は{self.charge_stop_threshold}%")
            elif battery_level > self.charge_stop_threshold:
                print(f"  → 放電中: 次の開始は{self.charge_start_threshold}%")
            else:
                print(f"  → 通常範囲: {self.charge_start_threshold}%-{self.charge_stop_threshold}%")
        
        self.last_battery_level = battery_level

    async def run_monitor(self):
        """バッテリー監視と充電制御を実行"""
        print("🔒 セキュアバッテリー充電制御を開始します...")
        print(f"充電開始閾値: {self.charge_start_threshold}%")
        print(f"充電停止閾値: {self.charge_stop_threshold}%")
        print(f"チェック間隔: {self.check_interval}秒")
        print(f"シミュレーションモード: {self.simulation_mode}")
        print("Ctrl+C で終了")
        print("-" * 50)
        
        self.security_logger.log_event("START", "監視開始")
        
        # Tapoデバイス初期化
        if not self.simulation_mode:
            await self.init_tapo_device()
        
        try:
            while True:
                await self.control_charging()
                await asyncio.sleep(self.check_interval)
                
        except KeyboardInterrupt:
            self.security_logger.log_event("STOP", "ユーザーによる停止")
            print("\n🔒 セキュアバッテリー充電制御を終了しました")
        except Exception as e:
            self.security_logger.log_event("ERROR", f"予期しないエラー: {str(e)}")
            print(f"\n❌ エラーが発生しました: {e}")
        finally:
            cleanup_sensitive_data()

def main():
    """メイン関数"""
    print("🔒 セキュアバッテリー充電制御アプリ")
    print("=" * 50)
    
    # セキュア設定を使用するかの確認
    use_secure = True
    if os.path.exists("secure_config.enc"):
        print("✅ セキュア設定ファイルが見つかりました")
    elif os.path.exists("config.py"):
        print("⚠️  従来の設定ファイル(config.py)が見つかりました")
        choice = input("セキュア設定に移行しますか？ (Y/n): ").lower()
        if choice != 'n':
            print("setup_secure_config.py を実行してセキュア設定を作成してください")
            return
        use_secure = False
    else:
        print("❌ 設定ファイルが見つかりません")
        print("setup_secure_config.py を実行して設定を作成してください")
        return
    
    # コントローラーを初期化
    controller = SecureBatteryChargeController(use_secure_config=use_secure)
    
    # 設定を読み込み
    if not controller.load_configuration():
        print("❌ 設定の読み込みに失敗しました")
        return
    
    # 非同期実行
    try:
        asyncio.run(controller.run_monitor())
    except KeyboardInterrupt:
        print("\nプログラムを終了しました")
    except Exception as e:
        print(f"エラー: {e}")

if __name__ == "__main__":
    main()
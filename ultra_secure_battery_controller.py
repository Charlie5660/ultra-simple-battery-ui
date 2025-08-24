#!/usr/bin/env python3
import subprocess
import re
import time
import asyncio
import sys
import os
from datetime import datetime
from security import SecureConfig, SecurityLogger, cleanup_sensitive_data
from auth_security import SecureAuthManager, SecureNetworkMonitor

try:
    from tapo import ApiClient
    TAPO_AVAILABLE = True
except ImportError:
    TAPO_AVAILABLE = False
    print("警告: tapoライブラリがインストールされていません")

class UltraSecureBatteryChargeController:
    """最高レベルセキュリティのバッテリー充電制御"""
    
    def __init__(self, use_secure_config=True):
        self.use_secure_config = use_secure_config
        self.secure_config = SecureConfig() if use_secure_config else None
        self.security_logger = SecurityLogger()
        self.auth_manager = SecureAuthManager()
        self.network_monitor = SecureNetworkMonitor()
        
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
        
        # セッション管理
        self.session_id = None
        self.last_auth_time = None
        self.auth_token_cache = None
        
        # 状態管理
        self.last_action = None
        self.last_battery_level = None
        
        # セキュリティログ初期化
        self.security_logger.log_event("INIT", "ウルトラセキュアバッテリーコントローラー初期化")
    
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
            
            # ネットワークセキュリティ検証
            if self.device_ip and not self.simulation_mode:
                if not self.auth_manager.validate_network_security(self.device_ip):
                    self.security_logger.log_event("WARNING", f"ネットワークセキュリティ警告: {self.device_ip}")
                    if not self.debug_mode:
                        return False
            
            return True
            
        except Exception as e:
            self.security_logger.log_event("ERROR", f"設定読み込みエラー: {str(e)}")
            return False
    
    async def init_tapo_device_secure(self):
        """セキュア強化されたTapoデバイス初期化"""
        if not TAPO_AVAILABLE:
            self.security_logger.log_event("WARNING", "Tapoライブラリが利用できません")
            return False
            
        if not all([self.tapo_username, self.tapo_password, self.device_ip]):
            self.security_logger.log_event("ERROR", "Tapo設定が不完全です")
            return False
        
        # IPロックアウトチェック
        if self.auth_manager.is_ip_locked(self.device_ip):
            self.security_logger.log_event("SECURITY", f"IP {self.device_ip} はロックアウト中")
            return False
        
        # キャッシュされた認証トークンをチェック
        cached_token = self.auth_manager.get_cached_auth_token(self.tapo_username, self.device_ip)
        if cached_token:
            self.security_logger.log_event("AUTH", "キャッシュされたトークンを使用")
            self.auth_token_cache = cached_token
        
        try:
            start_time = time.time()
            
            # セキュアな接続パラメータを使用
            secure_params = self.auth_manager.secure_connection_params()
            
            self.client = ApiClient(self.tapo_username, self.tapo_password)
            self.device = await self.client.p110(self.device_ip)
            
            # 接続テスト
            device_info = await self.device.get_device_info()
            device_model = device_info.model if hasattr(device_info, 'model') else 'Unknown'
            
            response_time = time.time() - start_time
            
            # ネットワーク監視に記録
            self.network_monitor.log_connection_attempt(self.device_ip, True, response_time)
            
            # 認証成功を記録
            self.auth_manager.record_auth_success(self.device_ip)
            self.last_auth_time = datetime.now()
            
            # 新しい認証情報をキャッシュ（実際のトークンがある場合）
            if hasattr(self.client, '_session_token'):
                token_data = {'session_token': getattr(self.client, '_session_token', '')}
                self.auth_manager.cache_auth_token(self.tapo_username, self.device_ip, token_data)
            
            self.security_logger.log_event("CONNECT", f"Tapo接続成功: {device_model} (応答時間: {response_time:.2f}秒)")
            if self.debug_mode:
                print(f"🔒 Tapo P110M セキュア接続成功 ({response_time:.2f}秒)")
            
            return True
            
        except Exception as e:
            response_time = time.time() - start_time
            
            # ネットワーク監視に失敗を記録
            self.network_monitor.log_connection_attempt(self.device_ip, False, response_time)
            
            # 認証失敗を記録
            self.auth_manager.record_auth_failure(self.device_ip)
            
            # ログから機密情報を除去
            sanitized_error = self.auth_manager.sanitize_auth_logs(str(e))
            
            self.security_logger.log_event("ERROR", f"Tapo接続エラー: {sanitized_error}")
            if self.debug_mode:
                print(f"❌ Tapo P110M接続エラー: {sanitized_error}")
            
            return False
        finally:
            # 認証情報をメモリからクリア
            cleanup_sensitive_data()
    
    async def secure_device_operation(self, operation: str):
        """セキュアなデバイス操作"""
        if not self.device or self.simulation_mode:
            self.security_logger.log_event("SIMULATION", f"デバイス操作（シミュレーション）: {operation}")
            if self.debug_mode:
                print(f"🔒 シミュレーション: {operation}")
            return True
        
        try:
            start_time = time.time()
            
            if operation == "ON":
                await self.device.on()
                action_msg = "充電器ON"
            elif operation == "OFF":
                await self.device.off()
                action_msg = "充電器OFF"
            else:
                raise ValueError(f"無効な操作: {operation}")
            
            response_time = time.time() - start_time
            
            # ネットワーク監視に記録
            self.network_monitor.log_connection_attempt(self.device_ip, True, response_time)
            
            self.security_logger.log_event("ACTION", f"{action_msg} (応答時間: {response_time:.2f}秒)")
            if self.debug_mode:
                print(f"🔌 {action_msg}")
            
            self.last_action = operation
            return True
            
        except Exception as e:
            response_time = time.time() - start_time
            
            # ネットワーク監視に失敗を記録
            self.network_monitor.log_connection_attempt(self.device_ip, False, response_time)
            
            sanitized_error = self.auth_manager.sanitize_auth_logs(str(e))
            self.security_logger.log_event("ERROR", f"デバイス操作失敗 {operation}: {sanitized_error}")
            
            if self.debug_mode:
                print(f"❌ デバイス操作エラー {operation}: {sanitized_error}")
            
            return False
    
    async def turn_on_charger(self):
        """セキュア充電器ON"""
        return await self.secure_device_operation("ON")
    
    async def turn_off_charger(self):
        """セキュア充電器OFF"""
        return await self.secure_device_operation("OFF")
    
    def get_battery_percentage(self):
        """バッテリー残量取得（セキュア）"""
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
            sanitized_error = self.auth_manager.sanitize_auth_logs(str(e))
            self.security_logger.log_event("ERROR", f"バッテリー情報取得エラー: {sanitized_error}")
            return None

    def is_charging(self):
        """充電中かどうかを確認（セキュア）"""
        try:
            result = subprocess.run(['pmset', '-g', 'batt'], 
                                  capture_output=True, text=True, timeout=10)
            output = result.stdout
            return 'charging' in output.lower()
        except Exception as e:
            sanitized_error = self.auth_manager.sanitize_auth_logs(str(e))
            self.security_logger.log_event("ERROR", f"充電状態確認エラー: {sanitized_error}")
            return False

    async def control_charging(self):
        """充電制御のメインロジック（セキュア強化版）"""
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
        
        # セキュリティログに記録
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
        """バッテリー監視実行（ウルトラセキュア版）"""
        print("🔒 ウルトラセキュアバッテリー充電制御を開始します...")
        print(f"充電開始閾値: {self.charge_start_threshold}%")
        print(f"充電停止閾値: {self.charge_stop_threshold}%")
        print(f"チェック間隔: {self.check_interval}秒")
        print(f"シミュレーションモード: {self.simulation_mode}")
        print("Ctrl+C で終了")
        print("-" * 50)
        
        self.security_logger.log_event("START", "ウルトラセキュア監視開始")
        
        # Tapoデバイス初期化（セキュア強化版）
        if not self.simulation_mode:
            if not await self.init_tapo_device_secure():
                print("❌ Tapoデバイスの初期化に失敗しました")
                return
        
        try:
            while True:
                await self.control_charging()
                
                # 定期的なセキュリティレポート
                if hasattr(self, '_report_counter'):
                    self._report_counter += 1
                else:
                    self._report_counter = 1
                
                # 100回に1回セキュリティレポートを出力
                if self._report_counter % 100 == 0:
                    security_report = self.network_monitor.get_security_report()
                    self.security_logger.log_event("SECURITY_REPORT", 
                        f"接続成功率: {security_report['success_rate']:.2%}, "
                        f"疑わしいパターン: {security_report['suspicious_patterns']}件")
                
                await asyncio.sleep(self.check_interval)
                
        except KeyboardInterrupt:
            self.security_logger.log_event("STOP", "ユーザーによる停止")
            print("\n🔒 ウルトラセキュアバッテリー充電制御を終了しました")
        except Exception as e:
            sanitized_error = self.auth_manager.sanitize_auth_logs(str(e))
            self.security_logger.log_event("ERROR", f"予期しないエラー: {sanitized_error}")
            print(f"\n❌ エラーが発生しました: {sanitized_error}")
        finally:
            # セキュリティクリーンアップ
            self.auth_manager.clear_auth_cache()
            cleanup_sensitive_data()
            
            # 最終セキュリティレポート
            final_report = self.network_monitor.get_security_report()
            self.security_logger.log_event("FINAL_REPORT", 
                f"総接続回数: {final_report['total_connections']}, "
                f"成功率: {final_report['success_rate']:.2%}")

def main():
    """メイン関数"""
    print("🔒 ウルトラセキュアバッテリー充電制御アプリ")
    print("=" * 60)
    
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
    controller = UltraSecureBatteryChargeController(use_secure_config=use_secure)
    
    # 設定を読み込み
    if not controller.load_configuration():
        print("❌ 設定の読み込みに失敗しました")
        return
    
    print("🔒 ウルトラセキュリティ機能:")
    print("  - AES-256暗号化設定")
    print("  - 認証トークンキャッシュ")
    print("  - ブルートフォース攻撃対策")
    print("  - ネットワーク通信監視")
    print("  - 機密データ自動除去")
    print("  - リアルタイムセキュリティログ")
    print()
    
    # 非同期実行
    try:
        asyncio.run(controller.run_monitor())
    except KeyboardInterrupt:
        print("\nプログラムを終了しました")
    except Exception as e:
        print(f"エラー: {e}")

if __name__ == "__main__":
    main()
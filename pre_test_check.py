#!/usr/bin/env python3
"""
実機テスト前チェックスクリプト
Tapo P110Mデバイスの接続性と基本機能を確認
"""

import os
import sys
import asyncio
import subprocess
import socket
from datetime import datetime

# セキュリティモジュールをインポート
try:
    from security import SecureConfig, SecurityLogger
    from auth_security import SecureAuthManager
    SECURITY_AVAILABLE = True
except ImportError:
    print("⚠️  セキュリティモジュールが見つかりません")
    SECURITY_AVAILABLE = False

# Tapoライブラリをインポート
try:
    from tapo import ApiClient
    TAPO_AVAILABLE = True
except ImportError:
    print("⚠️  tapoライブラリがインストールされていません")
    print("   インストール: pip install tapo")
    TAPO_AVAILABLE = False

class PreTestChecker:
    def __init__(self):
        self.results = {}
        self.warnings = []
        self.errors = []
        
    def log_result(self, test_name, success, message=""):
        """テスト結果を記録"""
        self.results[test_name] = {
            'success': success,
            'message': message,
            'timestamp': datetime.now().isoformat()
        }
        
        status = "✅" if success else "❌"
        print(f"{status} {test_name}: {message}")
        
        if not success:
            self.errors.append(f"{test_name}: {message}")
    
    def log_warning(self, message):
        """警告を記録"""
        self.warnings.append(message)
        print(f"⚠️  {message}")
    
    def check_file_permissions(self):
        """ファイル権限をチェック"""
        print("\n📁 ファイル権限チェック")
        print("-" * 30)
        
        security_files = [
            'security.py',
            'auth_security.py', 
            'secure_config.enc',
            '.salt'
        ]
        
        for file_path in security_files:
            if os.path.exists(file_path):
                stat = os.stat(file_path)
                mode = oct(stat.st_mode)[-3:]
                
                if file_path.endswith('.py'):
                    expected = '700'
                else:
                    expected = '600'
                
                if mode == expected:
                    self.log_result(f"権限_{file_path}", True, f"権限OK ({mode})")
                else:
                    self.log_result(f"権限_{file_path}", False, f"権限要修正 ({mode} → {expected})")
            else:
                if file_path in ['secure_config.enc', '.salt']:
                    self.log_warning(f"{file_path} が見つかりません（初回セットアップが必要）")
                else:
                    self.log_result(f"ファイル_{file_path}", False, "ファイルが見つかりません")
    
    def check_network_connectivity(self, device_ip):
        """ネットワーク接続性をチェック"""
        print("\n🌐 ネットワーク接続チェック")
        print("-" * 30)
        
        if not device_ip:
            self.log_result("ネットワーク", False, "デバイスIPが設定されていません")
            return False
        
        # IPアドレスの妥当性チェック
        try:
            import ipaddress
            ip = ipaddress.ip_address(device_ip)
            
            if ip.is_private:
                self.log_result("IPアドレス", True, f"プライベートIP ({device_ip})")
            else:
                self.log_result("IPアドレス", False, f"パブリックIP使用は非推奨 ({device_ip})")
        except ValueError:
            self.log_result("IPアドレス", False, f"無効なIPアドレス ({device_ip})")
            return False
        
        # ping テスト
        try:
            result = subprocess.run(
                ['ping', '-c', '3', '-W', '3000', device_ip],
                capture_output=True, text=True, timeout=10
            )
            
            if result.returncode == 0:
                self.log_result("Ping", True, f"デバイスに到達可能 ({device_ip})")
                return True
            else:
                self.log_result("Ping", False, f"デバイスに到達できません ({device_ip})")
                return False
                
        except subprocess.TimeoutExpired:
            self.log_result("Ping", False, "Pingタイムアウト")
            return False
        except Exception as e:
            self.log_result("Ping", False, f"Pingエラー: {str(e)}")
            return False
    
    async def check_tapo_connection(self, username, password, device_ip):
        """Tapo P110M接続をチェック"""
        print("\n🔌 Tapoデバイス接続チェック")
        print("-" * 30)
        
        if not TAPO_AVAILABLE:
            self.log_result("Tapoライブラリ", False, "tapoライブラリがインストールされていません")
            return False
        
        if not all([username, password, device_ip]):
            self.log_result("Tapo認証", False, "認証情報が不完全です")
            return False
        
        try:
            # API接続テスト
            client = ApiClient(username, password)
            device = await client.p110(device_ip)
            
            # デバイス情報取得
            device_info = await device.get_device_info()
            
            self.log_result("Tapo接続", True, f"接続成功 ({device_info.model if hasattr(device_info, 'model') else 'P110M'})")
            
            # 現在の状態取得
            try:
                is_on = device_info.device_on if hasattr(device_info, 'device_on') else 'Unknown'
                self.log_result("デバイス状態", True, f"現在の状態: {'ON' if is_on else 'OFF' if is_on is False else 'Unknown'}")
            except:
                self.log_warning("デバイス状態を取得できませんでした")
            
            return True
            
        except Exception as e:
            self.log_result("Tapo接続", False, f"接続失敗: {str(e)}")
            return False
    
    def check_battery_monitoring(self):
        """バッテリー監視機能をチェック"""
        print("\n🔋 バッテリー監視チェック")
        print("-" * 30)
        
        try:
            result = subprocess.run(['pmset', '-g', 'batt'], 
                                  capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0:
                output = result.stdout
                import re
                match = re.search(r'(\d+)%', output)
                
                if match:
                    battery_level = int(match.group(1))
                    charging = 'charging' in output.lower()
                    
                    self.log_result("バッテリー情報", True, 
                                  f"残量: {battery_level}%, {'充電中' if charging else '放電中'}")
                    
                    # バッテリー健康状態の確認
                    if 'condition' in output.lower():
                        if 'normal' in output.lower():
                            self.log_result("バッテリー健康", True, "バッテリー状態: 正常")
                        else:
                            self.log_warning("バッテリー状態に注意が必要かもしれません")
                    
                    return True
                else:
                    self.log_result("バッテリー情報", False, "バッテリー残量を解析できません")
                    return False
            else:
                self.log_result("バッテリー情報", False, "pmsetコマンドが失敗しました")
                return False
                
        except subprocess.TimeoutExpired:
            self.log_result("バッテリー情報", False, "バッテリー情報取得タイムアウト")
            return False
        except Exception as e:
            self.log_result("バッテリー情報", False, f"エラー: {str(e)}")
            return False
    
    def check_security_configuration(self):
        """セキュリティ設定をチェック"""
        print("\n🔒 セキュリティ設定チェック")
        print("-" * 30)
        
        if not SECURITY_AVAILABLE:
            self.log_result("セキュリティモジュール", False, "セキュリティモジュールが利用できません")
            return False
        
        # セキュア設定ファイルの存在確認
        if os.path.exists('secure_config.enc'):
            self.log_result("暗号化設定", True, "セキュア設定ファイルが存在します")
            
            if os.path.exists('.salt'):
                self.log_result("ソルトファイル", True, "ソルトファイルが存在します")
            else:
                self.log_result("ソルトファイル", False, "ソルトファイルが見つかりません")
                
        elif os.path.exists('config.py'):
            self.log_warning("従来の設定ファイル(config.py)を使用中です")
            self.log_result("設定ファイル", True, "config.py を検出")
        else:
            self.log_result("設定ファイル", False, "設定ファイルが見つかりません")
            return False
        
        return True
    
    def generate_report(self):
        """最終レポートを生成"""
        print("\n" + "=" * 50)
        print("📊 実機テスト前チェック結果")
        print("=" * 50)
        
        total_tests = len(self.results)
        passed_tests = sum(1 for result in self.results.values() if result['success'])
        
        print(f"実行テスト数: {total_tests}")
        print(f"成功: {passed_tests}")
        print(f"失敗: {total_tests - passed_tests}")
        print(f"警告: {len(self.warnings)}")
        
        if self.errors:
            print(f"\n❌ 修正が必要な項目:")
            for error in self.errors:
                print(f"   - {error}")
        
        if self.warnings:
            print(f"\n⚠️  警告項目:")
            for warning in self.warnings:
                print(f"   - {warning}")
        
        print(f"\n🎯 実機テスト推奨度:")
        if len(self.errors) == 0:
            print("   🟢 実機テスト実行可能")
            print("   👍 全ての基本チェックが完了しています")
        elif len(self.errors) <= 2:
            print("   🟡 注意して実機テスト可能")
            print("   ⚠️  上記のエラーを修正することを推奨します")
        else:
            print("   🔴 実機テスト非推奨")
            print("   ❌ 重要なエラーが複数あります。修正後に再チェックしてください")
        
        print(f"\n📝 詳細情報は PRE_TEST_CHECKLIST.md を確認してください")

async def main():
    """メイン実行関数"""
    print("🔍 バッテリー充電制御アプリ - 実機テスト前チェック")
    print("=" * 60)
    
    checker = PreTestChecker()
    
    # 1. ファイル権限チェック
    checker.check_file_permissions()
    
    # 2. セキュリティ設定チェック
    checker.check_security_configuration()
    
    # 3. バッテリー監視チェック
    checker.check_battery_monitoring()
    
    # 4. 設定情報を取得してネットワーク・Tapoチェック
    device_ip = None
    username = None
    password = None
    
    # 設定ファイルから情報を取得
    try:
        if os.path.exists('secure_config.enc') and SECURITY_AVAILABLE:
            print("\n🔑 暗号化設定からの情報取得をスキップ（パスワード入力が必要）")
            print("   手動でネットワーク設定を確認してください")
        elif os.path.exists('config.py'):
            from config import TAPO_USERNAME, TAPO_PASSWORD, DEVICE_IP
            username = TAPO_USERNAME
            password = TAPO_PASSWORD
            device_ip = DEVICE_IP
        
        if device_ip:
            # 5. ネットワーク接続チェック
            checker.check_network_connectivity(device_ip)
            
            # 6. Tapo接続チェック
            if username and password:
                await checker.check_tapo_connection(username, password, device_ip)
            else:
                checker.log_warning("Tapo認証情報が不足しているため接続テストをスキップ")
        else:
            checker.log_warning("デバイスIPが設定されていないためネットワークテストをスキップ")
            
    except ImportError:
        checker.log_warning("設定ファイルの読み込みに失敗しました")
    except Exception as e:
        checker.log_result("設定読み込み", False, f"エラー: {str(e)}")
    
    # 7. 最終レポート生成
    checker.generate_report()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⚠️  チェックが中断されました")
    except Exception as e:
        print(f"\n❌ 予期しないエラーが発生しました: {e}")
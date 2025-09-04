#!/usr/bin/env python3
"""
Integration Test for Battery Manager
Phase 3 安全性テスト - バッテリー情報取得のみテスト
実際の充電制御は行わない
"""

import sys
import subprocess
import re
from datetime import datetime

# 親ディレクトリからインポート
sys.path.append('..')

def test_battery_info_only():
    """バッテリー情報取得のみテスト"""
    print("🧪 Integration Test: バッテリー情報取得テスト")
    print("=" * 50)
    
    try:
        # Step 1: pmset直接実行テスト
        print("\n1. pmset直接実行テスト:")
        result = subprocess.run(['pmset', '-g', 'batt'], 
                              capture_output=True, text=True, timeout=5)
        
        if result.returncode == 0:
            print("✅ pmset実行成功")
            
            output = result.stdout.lower()
            print(f"📄 出力:\n{result.stdout}")
            
            # バッテリーレベル抽出テスト
            match = re.search(r'(\d+)%', output)
            if match:
                battery_level = int(match.group(1))
                print(f"🔋 バッテリー残量: {battery_level}%")
                
                # 充電状態確認テスト
                is_ac_power = 'now drawing from \'ac power\'' in output
                is_charging_status = 'charging' in output
                is_charging = is_ac_power and is_charging_status
                
                print(f"⚡ AC電源: {is_ac_power}")
                print(f"🔌 充電ステータス: {is_charging_status}")
                print(f"📊 最終充電判定: {is_charging}")
            else:
                print("❌ バッテリー残量の抽出に失敗")
        else:
            print(f"❌ pmset実行失敗: {result.stderr}")
            
    except Exception as e:
        print(f"❌ pmsetテストエラー: {e}")
    
    # Step 2: コア機能インポートテスト
    print("\n2. コア機能インポートテスト:")
    try:
        from battery_controller_core import BatteryChargeController
        from app_config import TAPO_SETTINGS, CHARGE_SETTINGS
        print("✅ インポート成功")
        
        # Controller初期化テスト
        controller = BatteryChargeController()
        print("✅ Controller初期化成功")
        
        # バッテリー情報取得テスト
        battery_level = controller.get_battery_percentage()
        is_charging = controller.is_charging()
        
        if battery_level is not None:
            print(f"🔋 Controller取得バッテリー: {battery_level}%")
            print(f"⚡ Controller取得充電状態: {is_charging}")
        else:
            print("❌ Controller経由バッテリー情報取得失敗")
            
        # 設定情報確認
        print(f"⚙️ 開始閾値: {CHARGE_SETTINGS.get('start_threshold', 30)}%")
        print(f"⚙️ 停止閾値: {CHARGE_SETTINGS.get('stop_threshold', 78)}%")
        print(f"🛡️ シミュレーションモード: {controller.device is None}")
        
    except Exception as e:
        print(f"❌ コア機能テストエラー: {e}")
        import traceback
        traceback.print_exc()
    
    # Step 3: CustomTkinter可用性テスト
    print("\n3. CustomTkinter可用性テスト:")
    try:
        import customtkinter as ctk
        print(f"✅ CustomTkinter利用可能: {ctk.__version__}")
    except Exception as e:
        print(f"❌ CustomTkinterエラー: {e}")
    
    print("\n" + "=" * 50)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"🧪 Integration Test完了: {timestamp}")

def test_connection_status():
    """接続状態の確認のみ"""
    print("\n🔌 接続状態確認テスト:")
    try:
        from app_config import TAPO_SETTINGS
        
        # 設定値確認（パスワードは隠す）
        username = TAPO_SETTINGS.get('username', '')
        device_ip = TAPO_SETTINGS.get('device_ip', '')
        has_password = bool(TAPO_SETTINGS.get('password', ''))
        
        print(f"📧 Tapoユーザー名: {'設定済み' if username else '未設定'}")
        print(f"🔑 Tapoパスワード: {'設定済み' if has_password else '未設定'}")
        print(f"🌐 デバイスIP: {'設定済み' if device_ip else '未設定'}")
        
        # 🚨 実際の接続テストは行わない（安全のため）
        print("🚨 安全モード: 実際の接続テストはスキップ")
        
    except Exception as e:
        print(f"❌ 接続状態確認エラー: {e}")

if __name__ == "__main__":
    test_battery_info_only()
    test_connection_status()
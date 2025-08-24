#!/usr/bin/env python3
"""
バッテリーコントローラーのテスト実行（60秒間）
"""

import asyncio
import sys
from battery_charge_controller import BatteryChargeController
import config

async def test_controller():
    print("🔍 バッテリーコントローラーのテスト開始")
    print("=" * 50)
    
    try:
        # 設定読み込み
        controller = BatteryChargeController(
            tapo_username=config.TAPO_SETTINGS['username'],
            tapo_password=config.TAPO_SETTINGS['password'],
            device_ip=config.TAPO_SETTINGS['device_ip']
        )
        
        controller.charge_start_threshold = config.CHARGE_SETTINGS['start_threshold']
        controller.charge_stop_threshold = config.CHARGE_SETTINGS['stop_threshold']
        
        print(f"📊 設定確認:")
        print(f"  充電開始閾値: {controller.charge_start_threshold}%")
        print(f"  充電停止閾値: {controller.charge_stop_threshold}%")
        print(f"  デバイスIP: {controller.device_ip}")
        print()
        
        # Tapoデバイス初期化
        print("🔌 Tapoデバイス初期化...")
        if await controller.init_tapo_device():
            print("✅ Tapoデバイス接続成功")
        else:
            print("❌ Tapoデバイス接続失敗")
            return
        
        print()
        print("🔋 バッテリー監視開始 (60秒間)...")
        
        # 60秒間監視
        for i in range(12):  # 5秒間隔で12回 = 60秒
            try:
                # バッテリー状態取得
                battery_level = controller.get_battery_percentage()
                charging_status = controller.is_charging()
                
                print(f"[{i+1:2d}/12] バッテリー: {battery_level}% ({'充電中' if charging_status else '放電中'})")
                
                # 制御ロジックテスト
                if battery_level is not None:
                    if battery_level <= controller.charge_start_threshold and not charging_status:
                        print(f"    🔋 充電開始条件に達しました ({battery_level}% <= {controller.charge_start_threshold}%)")
                        # 充電開始テスト
                        result = await controller.turn_on_charging()
                        if result:
                            print("    ✅ 充電開始コマンド送信成功")
                        else:
                            print("    ❌ 充電開始コマンド失敗")
                    
                    elif battery_level >= controller.charge_stop_threshold and charging_status:
                        print(f"    🛑 充電停止条件に達しました ({battery_level}% >= {controller.charge_stop_threshold}%)")
                        # 充電停止テスト
                        result = await controller.turn_off_charging()
                        if result:
                            print("    ✅ 充電停止コマンド送信成功")
                        else:
                            print("    ❌ 充電停止コマンド失敗")
                    
                    else:
                        print(f"    ⏸️  制御不要 (現在: {battery_level}%, 範囲: {controller.charge_start_threshold}%-{controller.charge_stop_threshold}%)")
                
                await asyncio.sleep(5)  # 5秒待機
                
            except Exception as e:
                print(f"    ❌ エラー: {e}")
                await asyncio.sleep(5)
        
        print("\n✅ テスト完了")
        
    except Exception as e:
        print(f"❌ テスト実行エラー: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_controller())
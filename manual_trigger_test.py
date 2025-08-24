#!/usr/bin/env python3
"""
手動トリガーテスト - 29%のバッテリーで充電開始を確認
"""

import asyncio
import config
from battery_charge_controller import BatteryChargeController

async def manual_trigger_test():
    print("🔋 手動トリガーテスト - 充電開始確認")
    print("=" * 50)
    
    # コントローラー初期化
    controller = BatteryChargeController(
        tapo_username=config.TAPO_SETTINGS['username'],
        tapo_password=config.TAPO_SETTINGS['password'],
        device_ip=config.TAPO_SETTINGS['device_ip']
    )
    
    controller.charge_start_threshold = config.CHARGE_SETTINGS['start_threshold']
    controller.charge_stop_threshold = config.CHARGE_SETTINGS['stop_threshold']
    
    print(f"📊 制御設定:")
    print(f"  充電開始閾値: {controller.charge_start_threshold}%")
    print(f"  充電停止閾値: {controller.charge_stop_threshold}%")
    print()
    
    # Tapo接続
    print("🔌 Tapoデバイス接続中...")
    if not await controller.init_tapo_device():
        print("❌ 接続失敗")
        return False
    
    print("✅ 接続成功")
    print()
    
    # 現在状態確認
    print("📊 現在の状態確認:")
    battery_level = controller.get_battery_percentage()
    is_charging = controller.is_charging()
    print(f"  バッテリーレベル: {battery_level}%")
    print(f"  充電状態: {'充電中' if is_charging else '放電中'}")
    print()
    
    # 制御ロジック実行
    print("⚡ 制御ロジック実行:")
    if battery_level <= controller.charge_start_threshold:
        if not is_charging:
            print(f"  🔋 充電開始条件に該当: {battery_level}% <= {controller.charge_start_threshold}%")
            print("  📤 充電開始コマンドを送信します...")
            
            result = await controller.turn_on_charger()
            if result:
                print("  ✅ 充電開始コマンド送信成功")
                
                # 5秒後に状態確認
                print("  ⏳ 5秒後に状態を確認します...")
                await asyncio.sleep(5)
                
                new_battery = controller.get_battery_percentage()
                new_charging = controller.is_charging()
                print(f"  📊 更新後の状態:")
                print(f"    バッテリーレベル: {new_battery}%")
                print(f"    充電状態: {'充電中' if new_charging else '放電中'}")
                
                if new_charging and not is_charging:
                    print("  🎉 充電開始成功!")
                    return True
                elif new_charging and is_charging:
                    print("  ✅ 充電継続中")
                    return True
                else:
                    print("  ⚠️  充電状態が変わりませんでした")
                    return False
            else:
                print("  ❌ 充電開始コマンド送信失敗")
                return False
        else:
            print(f"  ✅ 既に充電中です ({battery_level}%)")
            return True
    else:
        print(f"  ⏸️  充電開始条件に該当しません ({battery_level}% > {controller.charge_start_threshold}%)")
        return True

if __name__ == "__main__":
    success = asyncio.run(manual_trigger_test())
    if success:
        print("\n🎉 テスト成功 - バッテリー制御が正常に動作しています")
    else:
        print("\n❌ テスト失敗 - 問題があります")
#!/usr/bin/env python3
"""
Tapo接続問題の診断と修正テスト
"""

import asyncio
import sys
import time
import config

# 複数のTapoライブラリ接続方式をテスト
async def test_tapo_connection():
    print("🔍 Tapo P110M接続診断開始")
    print("=" * 50)
    
    # 設定確認
    username = config.TAPO_SETTINGS['username']
    password = config.TAPO_SETTINGS['password']
    device_ip = config.TAPO_SETTINGS['device_ip']
    
    print(f"📊 設定情報:")
    print(f"  ユーザー名: {username}")
    print(f"  デバイスIP: {device_ip}")
    print()
    
    # 方式1: 通常のApiClient
    print("🔌 方式1: 標準ApiClient接続テスト")
    try:
        from tapo import ApiClient
        client = ApiClient(username, password)
        device = await client.p110(device_ip)
        
        print("✅ 接続成功!")
        
        # デバイス情報取得
        try:
            device_info = await device.get_device_info()
            print(f"📄 デバイス情報: {device_info.nickname}")
            print(f"🔋 電源状態: {'ON' if device_info.device_on else 'OFF'}")
            return device, True
        except Exception as e:
            print(f"⚠️  デバイス情報取得エラー: {e}")
            return device, True
            
    except Exception as e:
        print(f"❌ 方式1失敗: {e}")
    
    # 方式2: タイムアウト付きApiClient
    print("\n🔌 方式2: タイムアウト付き接続テスト")
    try:
        from tapo import ApiClient
        import aiohttp
        
        timeout = aiohttp.ClientTimeout(total=10, connect=5)
        client = ApiClient(username, password, timeout=timeout)
        device = await client.p110(device_ip)
        
        print("✅ タイムアウト付き接続成功!")
        return device, True
        
    except Exception as e:
        print(f"❌ 方式2失敗: {e}")
    
    # 方式3: 複数回リトライ
    print("\n🔌 方式3: リトライ接続テスト")
    for retry in range(3):
        try:
            print(f"  🔄 試行 {retry + 1}/3...")
            from tapo import ApiClient
            client = ApiClient(username, password)
            device = await client.p110(device_ip)
            
            # 短時間待機してから再接続
            await asyncio.sleep(2)
            device_info = await device.get_device_info()
            
            print("✅ リトライ接続成功!")
            return device, True
            
        except Exception as e:
            print(f"  ❌ 試行 {retry + 1} 失敗: {e}")
            if retry < 2:
                await asyncio.sleep(3)  # 3秒待機
    
    print("\n❌ すべての接続方式が失敗しました")
    return None, False

async def test_device_control(device):
    """デバイス制御テスト"""
    if not device:
        print("⚠️  デバイスが利用できないため制御テストをスキップ")
        return False
    
    print("\n⚡ デバイス制御テスト")
    print("-" * 30)
    
    try:
        # 現在の状態確認
        print("📊 現在の状態確認...")
        device_info = await device.get_device_info()
        current_state = device_info.device_on
        print(f"  現在の電源状態: {'ON' if current_state else 'OFF'}")
        
        # テスト用の状態変更（現在の状態と逆にしてすぐ戻す）
        if current_state:
            print("  🔄 OFF → ON テスト")
            await device.off()
            await asyncio.sleep(2)
            await device.on()
            print("  ✅ ON/OFF制御成功")
        else:
            print("  🔄 ON → OFF テスト")
            await device.on()
            await asyncio.sleep(2)
            await device.off()
            print("  ✅ ON/OFF制御成功")
        
        return True
        
    except Exception as e:
        print(f"  ❌ 制御テスト失敗: {e}")
        return False

async def main():
    """メイン診断関数"""
    # 接続テスト
    device, connection_ok = await test_tapo_connection()
    
    if connection_ok:
        # 制御テスト
        control_ok = await test_device_control(device)
        
        print("\n" + "=" * 50)
        print("📊 診断結果サマリー")
        print("=" * 50)
        print(f"🔌 Tapo接続: {'✅ 成功' if connection_ok else '❌ 失敗'}")
        print(f"⚡ デバイス制御: {'✅ 成功' if control_ok else '❌ 失敗'}")
        
        if connection_ok and control_ok:
            print("\n🎉 Tapo P110Mとの通信が正常に確立されました！")
            print("💡 バッテリー制御アプリを再起動してください")
            return True
        else:
            print("\n⚠️  一部の機能に問題があります")
            return False
    else:
        print("\n❌ Tapo P110Mへの接続に失敗しました")
        print("🔧 推奨解決方法:")
        print("  1. Tapoアプリでデバイスがオンラインか確認")
        print("  2. Wi-Fiルーターの再起動")
        print("  3. Tapo P110Mの電源入れ直し")
        print("  4. MacのWi-Fi再接続")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
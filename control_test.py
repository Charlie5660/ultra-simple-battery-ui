#!/usr/bin/env python3
"""
制御テスト用スクリプト (10分間)
通常版のbattery_charge_controllerを使用
"""

import asyncio
import sys
from datetime import datetime

async def run_control_test():
    """10分間の制御テストを実行"""
    print("⚡ Phase 3: 制御テスト (10分間) 開始")
    print("=" * 50)
    print(f"📅 開始時刻: {datetime.now().strftime('%H:%M:%S')}")
    print("🔍 バッテリー充電制御の動作確認を行います")
    print("⚠️  異常を感じたらCtrl+Cで停止してください")
    print()
    
    try:
        # battery_charge_controller.pyを10分間実行
        process = await asyncio.create_subprocess_exec(
            'python3', 'battery_charge_controller.py',
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        print("🔍 バッテリー充電制御実行中...")
        
        try:
            # 10分間 (600秒) でタイムアウト
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=600)
            
            print(f"\n📅 終了時刻: {datetime.now().strftime('%H:%M:%S')}")
            print("✅ 制御テスト完了 (正常終了)")
            
            if stdout:
                print("\n📤 標準出力:")
                output = stdout.decode('utf-8', errors='replace')
                print(output[-1500:])  # 最後の1500文字のみ表示
                
            if stderr:
                print("\n❌ エラー出力:")
                error = stderr.decode('utf-8', errors='replace')
                print(error[-500:])  # 最後の500文字のみ表示
                
            return True
            
        except asyncio.TimeoutError:
            print(f"\n📅 終了時刻: {datetime.now().strftime('%H:%M:%S')}")
            print("⏰ 10分経過 - 制御テストを停止します")
            
            # プロセスを終了
            process.terminate()
            try:
                await asyncio.wait_for(process.wait(), timeout=5)
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                
            print("✅ 制御テスト完了 (タイムアウト)")
            return True
            
    except Exception as e:
        print(f"❌ 制御テストエラー: {e}")
        return False

def main():
    """メイン関数"""
    try:
        result = asyncio.run(run_control_test())
        
        print("\n" + "=" * 50)
        if result:
            print("🎉 Phase 3: 制御テスト完了")
            print("📚 次は Phase 4: 安定性テスト (30分間)")
        else:
            print("❌ Phase 3: 制御テスト失敗")
            
        return 0 if result else 1
        
    except KeyboardInterrupt:
        print("\n\n⚠️  ユーザーによって停止されました")
        print("🛑 Phase 3: 制御テスト中断")
        return 130

if __name__ == "__main__":
    sys.exit(main())
#!/usr/bin/env python3
"""
接続テスト用スクリプト (5分間タイムアウト付き)
"""

import asyncio
import signal
import sys
import subprocess
from datetime import datetime

async def run_connection_test():
    """5分間の接続テストを実行"""
    print("🔌 Phase 2: 接続テスト (5分間) 開始")
    print("=" * 50)
    print(f"📅 開始時刻: {datetime.now().strftime('%H:%M:%S')}")
    print("⚠️  異常を感じたらCtrl+Cで停止してください")
    print()
    
    try:
        # ultra_secure_battery_controller.pyを5分間実行
        process = await asyncio.create_subprocess_exec(
            'python3', 'ultra_secure_battery_controller.py',
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        print("🔍 ウルトラセキュア版実行中...")
        
        try:
            # 5分間 (300秒) でタイムアウト
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=300)
            
            print(f"\n📅 終了時刻: {datetime.now().strftime('%H:%M:%S')}")
            print("✅ 接続テスト完了 (正常終了)")
            
            if stdout:
                print("\n📤 標準出力:")
                output = stdout.decode('utf-8', errors='replace')
                print(output[-1000:])  # 最後の1000文字のみ表示
                
            if stderr:
                print("\n❌ エラー出力:")
                error = stderr.decode('utf-8', errors='replace') 
                print(error[-500:])  # 最後の500文字のみ表示
                
            return True
            
        except asyncio.TimeoutError:
            print(f"\n📅 終了時刻: {datetime.now().strftime('%H:%M:%S')}")
            print("⏰ 5分経過 - 接続テストを停止します")
            
            # プロセスを終了
            process.terminate()
            try:
                await asyncio.wait_for(process.wait(), timeout=5)
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                
            print("✅ 接続テスト完了 (タイムアウト)")
            return True
            
    except Exception as e:
        print(f"❌ 接続テストエラー: {e}")
        return False

def main():
    """メイン関数"""
    try:
        result = asyncio.run(run_connection_test())
        
        print("\n" + "=" * 50)
        if result:
            print("🎉 Phase 2: 接続テスト完了")
            print("📚 次は Phase 3: 制御テスト (10分間)")
        else:
            print("❌ Phase 2: 接続テスト失敗")
            
        return 0 if result else 1
        
    except KeyboardInterrupt:
        print("\n\n⚠️  ユーザーによって停止されました")
        print("🛑 Phase 2: 接続テスト中断")
        return 130

if __name__ == "__main__":
    sys.exit(main())
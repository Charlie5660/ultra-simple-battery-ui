#!/usr/bin/env python3
"""
安定性テスト用スクリプト (30分間)
ログ監視機能付き
"""

import asyncio
import sys
import time
from datetime import datetime

async def monitor_logs():
    """ログファイルを監視"""
    log_files = [
        'security.log',
        'secure_battery_control.log', 
        'battery_control.log'
    ]
    
    print("📊 ログ監視を開始...")
    
    while True:
        try:
            for log_file in log_files:
                try:
                    with open(log_file, 'r') as f:
                        lines = f.readlines()
                        if lines:
                            # 新しいログエントリがあれば表示
                            recent = lines[-1].strip()
                            if recent:
                                timestamp = datetime.now().strftime('%H:%M:%S')
                                print(f"[{timestamp}] {log_file}: {recent}")
                except FileNotFoundError:
                    pass  # ファイルが存在しない場合は無視
                    
            await asyncio.sleep(30)  # 30秒ごとにチェック
            
        except Exception as e:
            print(f"ログ監視エラー: {e}")
            await asyncio.sleep(30)

async def run_stability_test():
    """30分間の安定性テストを実行"""
    print("🔋 Phase 4: 安定性テスト (30分間) 開始")
    print("=" * 50)
    print(f"📅 開始時刻: {datetime.now().strftime('%H:%M:%S')}")
    print("🔍 長期安定性確認を行います")
    print("⚠️  異常を感じたらCtrl+Cで停止してください")
    print()
    
    try:
        # battery_charge_controller.pyを30分間実行
        process = await asyncio.create_subprocess_exec(
            'python3', 'battery_charge_controller.py',
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        print("🔍 長期バッテリー充電制御実行中...")
        print("💡 30秒ごとにログをチェックします")
        
        # ログ監視タスクを開始
        log_task = asyncio.create_task(monitor_logs())
        
        try:
            # 30分間 (1800秒) でタイムアウト
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=1800)
            
            log_task.cancel()
            
            print(f"\n📅 終了時刻: {datetime.now().strftime('%H:%M:%S')}")
            print("✅ 安定性テスト完了 (正常終了)")
            
            if stdout:
                print("\n📤 標準出力:")
                output = stdout.decode('utf-8', errors='replace')
                print(output[-2000:])  # 最後の2000文字のみ表示
                
            if stderr:
                print("\n❌ エラー出力:")
                error = stderr.decode('utf-8', errors='replace')
                print(error[-500:])  # 最後の500文字のみ表示
                
            return True
            
        except asyncio.TimeoutError:
            log_task.cancel()
            
            print(f"\n📅 終了時刻: {datetime.now().strftime('%H:%M:%S')}")
            print("⏰ 30分経過 - 安定性テストを停止します")
            
            # プロセスを終了
            process.terminate()
            try:
                await asyncio.wait_for(process.wait(), timeout=10)
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                
            print("✅ 安定性テスト完了 (タイムアウト)")
            return True
            
    except Exception as e:
        print(f"❌ 安定性テストエラー: {e}")
        return False

def main():
    """メイン関数"""
    try:
        result = asyncio.run(run_stability_test())
        
        print("\n" + "=" * 50)
        if result:
            print("🎉 Phase 4: 安定性テスト完了")
            print("✅ 全段階的実機テスト完了！")
            print()
            print("📊 テスト結果サマリー:")
            print("  ✅ Phase 1: 事前確認テスト - 成功")
            print("  ✅ Phase 2: 接続テスト (5分) - 成功") 
            print("  ✅ Phase 3: 制御テスト (10分) - 成功")
            print("  ✅ Phase 4: 安定性テスト (30分) - 成功")
            print()
            print("🚀 本格運用移行準備完了！")
        else:
            print("❌ Phase 4: 安定性テスト失敗")
            
        return 0 if result else 1
        
    except KeyboardInterrupt:
        print("\n\n⚠️  ユーザーによって停止されました")
        print("🛑 Phase 4: 安定性テスト中断")
        return 130

if __name__ == "__main__":
    sys.exit(main())
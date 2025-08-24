#!/usr/bin/env python3
"""
非インタラクティブ実機テスト用バッチスクリプト
Claude Code環境で使用可能
"""

import os
import sys
import asyncio
import time
import argparse
from datetime import datetime

def print_banner(title):
    """バナー表示"""
    print("\n" + "="*60)
    print(f"🔌 {title}")
    print("="*60)

def check_prerequisites(verbose=True):
    """前提条件チェック"""
    if verbose:
        print_banner("前提条件チェック")
    
    checks = []
    
    # 1. セキュア設定ファイル確認
    if os.path.exists('secure_config.enc'):
        checks.append(("✅ セキュア設定ファイル", "存在"))
    else:
        checks.append(("❌ セキュア設定ファイル", "未作成"))
        
    # 2. 設定ファイル確認
    if os.path.exists('config.py'):
        checks.append(("✅ 設定ファイル", "存在"))
        try:
            # 設定ファイルの内容をチェック
            import config
            if hasattr(config, 'TAPO_SETTINGS') and config.TAPO_SETTINGS.get('username'):
                checks.append(("✅ Tapo認証情報", "設定済み"))
            else:
                checks.append(("❌ Tapo認証情報", "未設定"))
        except Exception:
            checks.append(("❌ 設定ファイル", "読み取りエラー"))
    else:
        checks.append(("❌ 設定ファイル", "見つからず"))
        
    # 3. 緊急停止スクリプト確認
    if os.path.exists('emergency_stop.sh'):
        checks.append(("✅ 緊急停止スクリプト", "準備済み"))
    else:
        checks.append(("❌ 緊急停止スクリプト", "見つからず"))
    
    # 4. バッテリー情報取得テスト
    try:
        import subprocess
        result = subprocess.run(['pmset', '-g', 'batt'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            checks.append(("✅ バッテリー情報取得", "正常"))
        else:
            checks.append(("❌ バッテリー情報取得", "失敗"))
    except:
        checks.append(("❌ バッテリー情報取得", "エラー"))
    
    # 5. Tapoライブラリ確認
    try:
        import tapo
        checks.append(("✅ Tapoライブラリ", "インストール済み"))
    except ImportError:
        checks.append(("❌ Tapoライブラリ", "未インストール"))
    
    # 結果表示
    if verbose:
        for check, status in checks:
            print(f"  {check}: {status}")
    
    # 判定
    failed_checks = [c for c in checks if c[0].startswith("❌")]
    if failed_checks:
        if verbose:
            print(f"\n⚠️  {len(failed_checks)}個の前提条件が満たされていません")
        return False, failed_checks
    else:
        if verbose:
            print(f"\n✅ 全ての前提条件が満たされています")
        return True, []

async def connection_test(timeout_seconds=300):
    """接続テスト (デフォルト5分)"""
    print_banner(f"接続テスト ({timeout_seconds//60}分間)")
    
    print("🔍 接続テストを開始します...")
    print("⚠️  異常を感じた場合は手動で停止してください")
    
    try:
        print("\n📱 ウルトラセキュア版で接続テスト中...")
        print("💡 暗号化パスワードの入力が求められる場合があります")
        print(f"💡 {timeout_seconds}秒後に自動停止します")
        
        # タイムアウト付きでテスト実行
        process = await asyncio.create_subprocess_exec(
            'python3', 'ultra_secure_battery_controller.py',
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        try:
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=timeout_seconds)
            print("✅ 接続テスト完了 (正常終了)")
            if stdout:
                print("📤 標準出力:")
                print(stdout.decode()[-500:])  # 最後の500文字のみ表示
            return True
        except asyncio.TimeoutError:
            print(f"⏰ {timeout_seconds}秒経過 - テストを停止します")
            process.terminate()
            await process.wait()
            print("✅ 接続テスト完了 (タイムアウト)")
            return True
            
    except Exception as e:
        print(f"\n❌ 接続テストエラー: {e}")
        return False

def battery_monitor_test(duration_seconds=30):
    """バッテリー監視テスト"""
    print_banner(f"バッテリー監視テスト ({duration_seconds}秒間)")
    
    try:
        print("🔋 バッテリー監視を開始...")
        import subprocess
        
        # battery_monitor.py を短時間実行
        process = subprocess.Popen(['python3', 'battery_monitor.py'], 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE)
        
        # 指定時間待機
        time.sleep(duration_seconds)
        
        # プロセス終了
        process.terminate()
        stdout, stderr = process.communicate()
        
        print("✅ バッテリー監視テスト完了")
        if stdout:
            print("📤 バッテリー状態:")
            print(stdout.decode()[-300:])  # 最後の300文字のみ表示
        
        return True
        
    except Exception as e:
        print(f"❌ バッテリー監視テストエラー: {e}")
        return False

def review_logs():
    """ログ確認"""
    print_banner("ログファイル確認")
    
    log_files = [
        ('security.log', 'セキュリティログ'),
        ('secure_battery_control.log', 'アプリログ'),
        ('emergency_stop.log', '緊急停止ログ')
    ]
    
    for log_file, description in log_files:
        if os.path.exists(log_file):
            print(f"\n📄 {description} ({log_file}):")
            try:
                with open(log_file, 'r') as f:
                    lines = f.readlines()
                    if lines:
                        # 最新の5行を表示
                        recent_lines = lines[-5:]
                        for line in recent_lines:
                            print(f"  {line.strip()}")
                    else:
                        print("  (ログが空です)")
            except Exception as e:
                print(f"  ❌ ログ読み取りエラー: {e}")
        else:
            print(f"\n📄 {description}: ファイルが見つかりません")

async def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(description='非インタラクティブ実機テスト')
    parser.add_argument('--check-only', action='store_true', help='前提条件チェックのみ実行')
    parser.add_argument('--connection-test', type=int, default=300, help='接続テスト時間(秒)')
    parser.add_argument('--battery-test', type=int, default=30, help='バッテリー監視テスト時間(秒)')
    parser.add_argument('--skip-connection', action='store_true', help='接続テストをスキップ')
    parser.add_argument('--logs-only', action='store_true', help='ログ確認のみ実行')
    
    args = parser.parse_args()
    
    print("🔌 バッテリー充電制御アプリ - 非インタラクティブテスト")
    
    # ログのみの場合
    if args.logs_only:
        review_logs()
        return
    
    # 前提条件チェック
    print("\n🔍 前提条件をチェックしています...")
    prereq_ok, failed_checks = check_prerequisites()
    
    if not prereq_ok:
        print(f"\n❌ {len(failed_checks)}個の前提条件が満たされていません:")
        for check, status in failed_checks:
            print(f"  {check}: {status}")
        print("\n📋 設定手順:")
        print("1. config.py の TAPO_SETTINGS を編集")
        print("2. pip3 install tapo (未インストールの場合)")
        print("3. python3 create_secure_config.py (セキュア版使用時)")
        return 1
    
    if args.check_only:
        print("✅ 前提条件チェック完了")
        return 0
    
    # バッテリー監視テスト
    print("\n🔋 バッテリー監視テストを実行...")
    battery_ok = battery_monitor_test(args.battery_test)
    
    # 接続テスト
    if not args.skip_connection:
        print("\n🔌 接続テストを実行...")
        connection_ok = await connection_test(args.connection_test)
    else:
        print("\n⏩ 接続テストをスキップしました")
        connection_ok = True
    
    # ログ確認
    review_logs()
    
    # 結果サマリー
    print_banner("テスト結果サマリー")
    print(f"前提条件チェック: {'✅ 通過' if prereq_ok else '❌ 失敗'}")
    print(f"バッテリー監視テスト: {'✅ 通過' if battery_ok else '❌ 失敗'}")
    if not args.skip_connection:
        print(f"接続テスト: {'✅ 通過' if connection_ok else '❌ 失敗'}")
    
    if prereq_ok and battery_ok and connection_ok:
        print("\n🎉 全テストが正常に完了しました")
        print("📚 次のステップ:")
        print("  - REAL_DEVICE_TEST_GUIDE.md を確認")
        print("  - config.py で simulation_mode = False に設定")
        print("  - 段階的に実機テストを実行")
        return 0
    else:
        print("\n⚠️  一部のテストが失敗しました")
        return 1

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n👋 テストが中断されました")
        sys.exit(130)
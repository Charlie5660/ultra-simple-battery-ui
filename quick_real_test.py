#!/usr/bin/env python3
"""
実機テスト用クイックスタートスクリプト
段階的に安全な実機テストを実行
"""

import os
import sys
import asyncio
import time
from datetime import datetime

def print_banner(title):
    """バナー表示"""
    print("\n" + "="*60)
    print(f"🔌 {title}")
    print("="*60)

def check_prerequisites():
    """前提条件チェック"""
    print_banner("前提条件チェック")
    
    checks = []
    
    # 1. セキュア設定ファイル確認
    if os.path.exists('secure_config.enc'):
        checks.append(("✅ セキュア設定ファイル", "存在"))
    else:
        checks.append(("❌ セキュア設定ファイル", "未作成"))
        
    # 2. 緊急停止スクリプト確認
    if os.path.exists('emergency_stop.sh'):
        checks.append(("✅ 緊急停止スクリプト", "準備済み"))
    else:
        checks.append(("❌ 緊急停止スクリプト", "見つからず"))
    
    # 3. バッテリー情報取得テスト
    try:
        import subprocess
        result = subprocess.run(['pmset', '-g', 'batt'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            checks.append(("✅ バッテリー情報取得", "正常"))
        else:
            checks.append(("❌ バッテリー情報取得", "失敗"))
    except:
        checks.append(("❌ バッテリー情報取得", "エラー"))
    
    # 4. Tapoライブラリ確認
    try:
        import tapo
        checks.append(("✅ Tapoライブラリ", "インストール済み"))
    except ImportError:
        checks.append(("❌ Tapoライブラリ", "未インストール"))
    
    # 結果表示
    for check, status in checks:
        print(f"  {check}: {status}")
    
    # 判定
    failed_checks = [c for c in checks if c[0].startswith("❌")]
    if failed_checks:
        print(f"\n⚠️  {len(failed_checks)}個の前提条件が満たされていません")
        print("先に解決してから実機テストを実行してください")
        return False
    else:
        print(f"\n✅ 全ての前提条件が満たされています")
        return True

def get_user_confirmation(message):
    """ユーザー確認"""
    while True:
        response = input(f"\n{message} (y/N): ").lower().strip()
        if response in ['y', 'yes']:
            return True
        elif response in ['n', 'no', '']:
            return False
        else:
            print("❌ 'y' または 'n' で答えてください")

async def test_stage_1_connection():
    """Stage 1: 接続テスト"""
    print_banner("Stage 1: Tapo P110M接続テスト (5分間)")
    
    print("🔍 接続テストを開始します...")
    print("⚠️  異常を感じたらCtrl+Cで即座停止してください")
    
    if not get_user_confirmation("接続テストを開始しますか？"):
        print("❌ テストを中止しました")
        return False
    
    try:
        # ウルトラセキュア版を短時間実行
        print("\n📱 ウルトラセキュア版で接続テスト中...")
        print("💡 暗号化パスワードの入力が求められたら入力してください")
        print("💡 5分後に自動停止します")
        
        # タイムアウト付きでテスト実行
        process = await asyncio.create_subprocess_exec(
            'python3', 'ultra_secure_battery_controller.py',
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        # 5分間 (300秒) 実行
        try:
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=300)
            print("✅ 接続テスト完了 (正常終了)")
            return True
        except asyncio.TimeoutError:
            print("⏰ 5分経過 - テストを停止します")
            process.terminate()
            await process.wait()
            print("✅ 接続テスト完了 (タイムアウト)")
            return True
            
    except KeyboardInterrupt:
        print("\n⚠️  ユーザーによって停止されました")
        return False
    except Exception as e:
        print(f"\n❌ 接続テストエラー: {e}")
        return False

def manual_control_test():
    """手動制御テスト"""
    print_banner("Stage 2: 手動制御確認")
    
    print("📋 以下の手順で手動制御を確認してください:")
    print()
    print("1. 📱 Tapoアプリを開く")
    print("2. 🔌 P110Mデバイスを選択")
    print("3. ⚡ 手動でON/OFF切り替えテスト")
    print("4. ⏱️  応答時間を確認 (3秒以内が理想)")
    print("5. 🔄 3回連続で成功することを確認")
    
    return get_user_confirmation("手動制御テストは正常に完了しましたか？")

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
                        print("  " + "  ".join(lines[-5:]).replace('\n', '\n  '))
                    else:
                        print("  (ログが空です)")
            except Exception as e:
                print(f"  ❌ ログ読み取りエラー: {e}")
        else:
            print(f"\n📄 {description}: ファイルが見つかりません")

def real_test_guidance():
    """実機テストガイダンス"""
    print_banner("実機テスト実行ガイダンス")
    
    print("📚 実機テストの詳細手順:")
    print("1. 📖 REAL_DEVICE_TEST_GUIDE.md を確認")
    print("2. ⚙️  config_template.py で実際のTapo情報を設定")
    print("3. 🔐 python3 create_secure_config.py で実機用設定作成")
    print("4. 🧪 段階的テスト実行 (接続→制御→安定性)")
    print("5. 📊 結果評価と本格運用移行判定")
    
    print("\n⚠️  重要な安全ガイドライン:")
    print("- 💀 初回は必ず短時間 (30分以内) で実行")
    print("- 👀 テスト中は常時監視")
    print("- 🚨 異常時は./emergency_stop.sh で即座停止")
    print("- 🔋 バッテリーの発熱・膨張がないか確認")
    
    if get_user_confirmation("詳細ガイドを開きますか？"):
        os.system("open REAL_DEVICE_TEST_GUIDE.md")

def main():
    """メイン関数"""
    print("🔌 バッテリー充電制御アプリ - 実機テスト支援ツール")
    
    # 前提条件チェック
    if not check_prerequisites():
        print("\n❌ 前提条件を満たしていないため終了します")
        return
    
    print("\n🎯 実機テストの段階:")
    print("1. 💻 シミュレーションテスト (現在完了)")
    print("2. 🔌 実機接続テスト")
    print("3. ⚡ 実機制御テスト")
    print("4. 🚀 本格運用移行")
    
    # テスト選択
    print("\n📋 実行可能なテスト:")
    print("1. Stage 1: 接続テスト (5分間)")
    print("2. Stage 2: 手動制御確認")
    print("3. ログファイル確認")
    print("4. 実機テスト詳細ガイド")
    print("5. 終了")
    
    while True:
        try:
            choice = input("\n選択してください (1-5): ").strip()
            
            if choice == "1":
                if asyncio.run(test_stage_1_connection()):
                    print("✅ Stage 1 完了 - 次は手動制御確認を実行してください")
                break
            elif choice == "2":
                if manual_control_test():
                    print("✅ Stage 2 完了 - 次は実機テスト詳細ガイドを確認してください")
                break
            elif choice == "3":
                review_logs()
            elif choice == "4":
                real_test_guidance()
            elif choice == "5":
                print("👋 実機テスト支援ツールを終了します")
                break
            else:
                print("❌ 1-5の数字を選択してください")
                
        except KeyboardInterrupt:
            print("\n\n👋 実機テスト支援ツールを終了します")
            break
        except Exception as e:
            print(f"\n❌ エラーが発生しました: {e}")

if __name__ == "__main__":
    main()
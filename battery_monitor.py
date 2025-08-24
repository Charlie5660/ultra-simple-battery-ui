#!/usr/bin/env python3
import subprocess
import re
import time
import argparse
from datetime import datetime

def get_battery_percentage():
    """macOSのバッテリー残量を取得"""
    try:
        result = subprocess.run(['pmset', '-g', 'batt'], capture_output=True, text=True)
        output = result.stdout
        
        # バッテリー残量のパーセンテージを正規表現で抽出
        match = re.search(r'(\d+)%', output)
        if match:
            return int(match.group(1))
        else:
            return None
    except Exception as e:
        print(f"バッテリー情報の取得エラー: {e}")
        return None

def is_charging():
    """充電中かどうかを確認"""
    try:
        result = subprocess.run(['pmset', '-g', 'batt'], capture_output=True, text=True)
        output = result.stdout
        return 'charging' in output.lower()
    except Exception as e:
        print(f"充電状態の確認エラー: {e}")
        return False

def log_battery_status():
    """バッテリーの状態をログ出力"""
    battery_level = get_battery_percentage()
    charging_status = is_charging()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    if battery_level is not None:
        status = "充電中" if charging_status else "放電中"
        print(f"[{timestamp}] バッテリー: {battery_level}% ({status})")
        return battery_level, charging_status
    else:
        print(f"[{timestamp}] バッテリー情報を取得できませんでした")
        return None, False

def main():
    """メイン関数 - バッテリー監視のテスト"""
    parser = argparse.ArgumentParser(description='バッテリー監視ツール')
    parser.add_argument('--test', type=int, metavar='SECONDS', 
                       help='テストモード: 指定秒数後に自動終了')
    parser.add_argument('--interval', type=int, default=30, metavar='SECONDS',
                       help='監視間隔(秒) デフォルト: 30')
    
    args = parser.parse_args()
    
    if args.test:
        print(f"バッテリー監視テストを開始します ({args.test}秒間)...")
        end_time = time.time() + args.test
    else:
        print("バッテリー監視を開始します...")
        print("Ctrl+C で終了")
        end_time = None
    
    try:
        while True:
            battery_level, is_charging_now = log_battery_status()
            
            if battery_level is not None:
                # 将来の制御ロジック用のテスト出力
                if battery_level <= 30:
                    print("  → 充電開始の条件に達しました (30%以下)")
                elif battery_level >= 78:
                    print("  → 充電停止の条件に達しました (78%以上)")
            
            # テストモードの終了条件チェック
            if end_time and time.time() >= end_time:
                print(f"\n⏰ {args.test}秒経過 - テスト終了")
                break
            
            # 指定間隔で監視
            time.sleep(args.interval)
            
    except KeyboardInterrupt:
        print("\nバッテリー監視を終了しました")

if __name__ == "__main__":
    main()
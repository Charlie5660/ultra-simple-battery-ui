#!/bin/bash

# 🚨 緊急停止スクリプト
# バッテリー充電制御アプリを即座に停止します

echo "🚨 緊急停止処理を開始します..."
echo "=================================="

# 現在時刻をログに記録
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
echo "[$TIMESTAMP] 緊急停止処理開始" >> emergency_stop.log

# 1. 実行中のプロセスを強制終了
echo "1. アプリプロセスを強制終了中..."
PIDS=$(pgrep -f "battery.*controller")
if [ -n "$PIDS" ]; then
    echo "   見つかったプロセス: $PIDS"
    kill -TERM $PIDS
    sleep 2
    
    # まだ残っている場合は強制終了
    REMAINING_PIDS=$(pgrep -f "battery.*controller")
    if [ -n "$REMAINING_PIDS" ]; then
        echo "   強制終了: $REMAINING_PIDS"
        kill -KILL $REMAINING_PIDS
    fi
    echo "   ✅ プロセス停止完了"
else
    echo "   ℹ️  実行中のプロセスが見つかりませんでした"
fi

# 2. PIDファイルをクリーンアップ
echo "2. PIDファイルをクリーンアップ中..."
PID_FILES=(
    "battery_control.pid"
    "secure_battery_control.pid"
    "*.pid"
)

for pid_file in "${PID_FILES[@]}"; do
    if ls $pid_file 1> /dev/null 2>&1; then
        rm -f $pid_file
        echo "   削除: $pid_file"
    fi
done
echo "   ✅ PIDファイルクリーンアップ完了"

# 3. 一時ファイルをクリーンアップ
echo "3. 一時ファイルをクリーンアップ中..."
TEMP_FILES=(
    ".auth_cache.enc"
    "nohup.out"
    "*.tmp"
)

for temp_file in "${TEMP_FILES[@]}"; do
    if ls $temp_file 1> /dev/null 2>&1; then
        rm -f $temp_file
        echo "   削除: $temp_file"
    fi
done
echo "   ✅ 一時ファイルクリーンアップ完了"

# 4. セキュリティログに記録
echo "4. セキュリティログに記録中..."
if [ -f "security.log" ]; then
    echo "[$TIMESTAMP] EMERGENCY_STOP: 緊急停止処理実行" >> security.log
    echo "   ✅ セキュリティログ記録完了"
else
    echo "   ⚠️  セキュリティログファイルが見つかりません"
fi

# 5. Tapoデバイスの状態確認（可能であれば）
echo "5. Tapoデバイス状態確認..."
if command -v python3 >/dev/null 2>&1; then
    python3 -c "
try:
    from config import DEVICE_IP
    print(f'   デバイスIP: {DEVICE_IP}')
    print('   ⚠️  Tapoアプリで手動確認を推奨します')
except:
    print('   ℹ️  設定ファイルから情報を取得できませんでした')
" 2>/dev/null
else
    echo "   ℹ️  Python3が利用できません"
fi

# 6. 最終状態確認
echo "6. 最終状態確認..."
REMAINING_PROCESSES=$(pgrep -f "battery.*controller" | wc -l)
if [ "$REMAINING_PROCESSES" -eq 0 ]; then
    echo "   ✅ 全てのアプリプロセスが停止されました"
else
    echo "   ⚠️  まだ実行中のプロセスがあります: $REMAINING_PROCESSES 個"
    pgrep -f "battery.*controller"
fi

echo ""
echo "🚨 緊急停止処理完了"
echo "=================================="
echo "📋 次の手順:"
echo "1. Tapoアプリでデバイスの状態を確認"
echo "2. 充電器の物理的な状態を確認"
echo "3. バッテリーの状態を確認"
echo "4. 必要に応じて電源ケーブルを物理的に抜く"
echo ""
echo "📝 ログファイル:"
echo "   - emergency_stop.log (緊急停止ログ)"
echo "   - security.log (セキュリティログ)"
echo ""
echo "❓ 問題が解決しない場合:"
echo "   1. システムを再起動"
echo "   2. Tapoデバイスを再起動"
echo "   3. ネットワーク設定を確認"

# ログに完了を記録
echo "[$TIMESTAMP] 緊急停止処理完了" >> emergency_stop.log
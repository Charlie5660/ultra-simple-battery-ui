#!/bin/bash
# 日次チェックスクリプト
# 使用方法: ./daily_check.sh

echo "🔋 バッテリー充電制御アプリ - 日次チェック"
echo "========================================"
echo "📅 チェック実行日時: $(date)"
echo

# 1. プロセス状態確認
echo "🔍 1. プロセス状態確認"
echo "----------------------------------------"
if pgrep -f "battery" > /dev/null; then
    echo "✅ バッテリー制御プロセス: 実行中"
    ps aux | grep -v grep | grep battery
else
    echo "❌ バッテリー制御プロセス: 停止中"
fi
echo

# 2. バッテリー状態確認
echo "🔋 2. 現在のバッテリー状態"
echo "----------------------------------------"
pmset -g batt
echo

# 3. ログファイル確認
echo "📊 3. ログファイル確認"
echo "----------------------------------------"

if [ -f "security.log" ]; then
    echo "📄 セキュリティログ (最新5行):"
    tail -5 security.log
    echo
else
    echo "❌ security.log が見つかりません"
fi

if [ -f "secure_battery_control.log" ]; then
    echo "📄 アプリログ (最新5行):"
    tail -5 secure_battery_control.log
    echo
else
    echo "⚠️  secure_battery_control.log が見つかりません"
fi

# 4. ディスク使用量確認
echo "💾 4. ログファイルサイズ確認"
echo "----------------------------------------"
for log in security.log secure_battery_control.log emergency_stop.log; do
    if [ -f "$log" ]; then
        size=$(du -h "$log" | cut -f1)
        echo "📁 $log: $size"
    fi
done
echo

# 5. ネットワーク接続確認
echo "🌐 5. Tapoデバイス接続確認"
echo "----------------------------------------"
DEVICE_IP=$(python3 -c "
try:
    import config
    print(config.TAPO_SETTINGS['device_ip'])
except:
    print('設定取得エラー')
")

if [ "$DEVICE_IP" != "設定取得エラー" ] && [ "$DEVICE_IP" != "" ]; then
    echo "📡 Tapo P110M ($DEVICE_IP) への接続テスト:"
    if ping -c 3 "$DEVICE_IP" > /dev/null 2>&1; then
        echo "✅ 接続OK"
    else
        echo "❌ 接続NG - ネットワーク確認が必要"
    fi
else
    echo "⚠️  デバイスIP設定が見つかりません"
fi
echo

# 6. エラー件数確認
echo "⚠️  6. エラー件数確認 (過去24時間)"
echo "----------------------------------------"
if [ -f "security.log" ]; then
    today=$(date '+%Y-%m-%d')
    error_count=$(grep -c "ERROR" security.log | grep "$today" | wc -l || echo "0")
    echo "📈 本日のエラー件数: $error_count"
    
    if [ "$error_count" -gt 10 ]; then
        echo "🚨 警告: エラーが多発しています ($error_count件)"
    elif [ "$error_count" -gt 0 ]; then
        echo "⚠️  注意: エラーが発生しています ($error_count件)"
    else
        echo "✅ エラーなし"
    fi
else
    echo "⚠️  ログファイルが見つかりません"
fi
echo

# 7. 推奨アクション
echo "📝 7. 推奨アクション"
echo "----------------------------------------"
echo "💡 定期実行推奨:"
echo "   - 週次: ./weekly_check.sh"
echo "   - 月次: ./monthly_maintenance.sh" 
echo "   - 緊急時: ./emergency_stop.sh"
echo
echo "📚 詳細ログ確認:"
echo "   - tail -f security.log"
echo "   - tail -f secure_battery_control.log"
echo

echo "✅ 日次チェック完了"
echo "========================================"
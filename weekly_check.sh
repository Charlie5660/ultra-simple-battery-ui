#!/bin/bash
# 週次チェックスクリプト
# 使用方法: ./weekly_check.sh

echo "📊 バッテリー充電制御アプリ - 週次レポート"
echo "=========================================="
echo "📅 レポート実行日時: $(date)"
echo "📅 対象期間: 過去7日間"
echo

# 1. システム稼働時間統計
echo "⏱️  1. システム稼働時間統計"
echo "----------------------------------------"
echo "システム稼働時間: $(uptime)"
echo

# 2. バッテリー充放電統計
echo "🔋 2. バッテリー統計 (過去7日間)"
echo "----------------------------------------"
if [ -f "security.log" ]; then
    # 過去7日間のバッテリー記録を分析
    echo "📈 充電回数統計:"
    grep -c "STATUS.*充電中" security.log 2>/dev/null || echo "データなし"
    
    echo "📉 放電回数統計:"
    grep -c "STATUS.*放電中" security.log 2>/dev/null || echo "データなし"
else
    echo "⚠️  ログファイルが見つかりません"
fi
echo

# 3. エラー統計
echo "⚠️  3. エラー統計 (過去7日間)"
echo "----------------------------------------"
if [ -f "security.log" ]; then
    error_types=("ERROR" "WARN" "FAIL")
    total_errors=0
    
    for error_type in "${error_types[@]}"; do
        count=$(grep -c "$error_type" security.log 2>/dev/null || echo "0")
        echo "🚨 ${error_type}: ${count}件"
        total_errors=$((total_errors + count))
    done
    
    echo "📊 総エラー数: ${total_errors}件"
    
    if [ "$total_errors" -gt 50 ]; then
        echo "🔥 警告: エラーが多発しています - 詳細確認が必要"
    elif [ "$total_errors" -gt 10 ]; then
        echo "⚠️  注意: 定期メンテナンスを検討してください"
    else
        echo "✅ エラー数は正常範囲内です"
    fi
else
    echo "⚠️  ログファイルが見つかりません"
fi
echo

# 4. ログファイル管理
echo "📁 4. ログファイル管理"
echo "----------------------------------------"
log_files=("security.log" "secure_battery_control.log" "emergency_stop.log")

for log_file in "${log_files[@]}"; do
    if [ -f "$log_file" ]; then
        size=$(du -h "$log_file" | cut -f1)
        lines=$(wc -l < "$log_file")
        echo "📄 $log_file: $size ($lines 行)"
        
        # 10MB以上の場合は警告
        size_mb=$(du -m "$log_file" | cut -f1)
        if [ "$size_mb" -gt 10 ]; then
            echo "  ⚠️  警告: ファイルサイズが大きくなっています"
            echo "  💡 推奨: ログローテーションを検討してください"
        fi
    else
        echo "📄 $log_file: 見つかりません"
    fi
done
echo

# 5. Tapoデバイス接続統計
echo "📡 5. Tapoデバイス接続統計"
echo "----------------------------------------"
DEVICE_IP=$(python3 -c "
try:
    import config
    print(config.TAPO_SETTINGS['device_ip'])
except:
    print('設定取得エラー')
")

if [ "$DEVICE_IP" != "設定取得エラー" ] && [ "$DEVICE_IP" != "" ]; then
    echo "📍 対象デバイス: $DEVICE_IP"
    
    # 接続テスト
    if ping -c 5 "$DEVICE_IP" > /dev/null 2>&1; then
        echo "✅ 現在の接続状態: OK"
    else
        echo "❌ 現在の接続状態: NG"
        echo "🔧 推奨アクション: ネットワーク設定確認"
    fi
    
    # ログから接続エラー統計
    if [ -f "security.log" ]; then
        connection_errors=$(grep -c "接続.*エラー\|connection.*error" security.log 2>/dev/null || echo "0")
        echo "📊 週間接続エラー数: ${connection_errors}件"
    fi
else
    echo "⚠️  デバイス設定が見つかりません"
fi
echo

# 6. セキュリティチェック
echo "🔒 6. セキュリティチェック"
echo "----------------------------------------"
security_files=("secure_config.enc" ".salt" "security.py" "auth_security.py")

for file in "${security_files[@]}"; do
    if [ -f "$file" ]; then
        perms=$(stat -f %Mp%Lp "$file")
        echo "🛡️  $file: 権限 $perms"
        
        # 推奨権限チェック
        if [[ "$file" == *.enc ]] || [[ "$file" == .salt ]]; then
            if [ "$perms" != "600" ]; then
                echo "  ⚠️  警告: 推奨権限は600です"
            fi
        elif [[ "$file" == *.py ]]; then
            if [ "$perms" != "700" ] && [ "$perms" != "755" ]; then
                echo "  ⚠️  警告: 推奨権限は700または755です"
            fi
        fi
    else
        echo "🛡️  $file: 見つかりません"
    fi
done
echo

# 7. 推奨保守アクション
echo "🔧 7. 推奨保守アクション"
echo "----------------------------------------"
echo "📋 週次推奨作業:"
echo "   ✅ ログファイル確認 (完了)"
echo "   ⏳ バッテリー健康状態確認: pmset -g batt"
echo "   ⏳ Tapoアプリでのデバイス状態確認"
echo "   ⏳ Wi-Fi信号強度確認"
echo

echo "📅 次回実行推奨日: $(date -d '+7 days' '+%Y-%m-%d' 2>/dev/null || date -v+7d '+%Y-%m-%d')"
echo

echo "✅ 週次チェック完了"
echo "=========================================="
#!/bin/bash

# 本格運用モード起動スクリプト（通常版使用）

echo "🚀 バッテリー充電制御アプリ - 本格運用モード起動"
echo "=================================================="

# Pythonスクリプトのディレクトリに移動
cd "$(dirname "$0")"

# ログファイルの設定
LOG_FILE="production_battery_control.log"
PID_FILE="production_battery_control.pid"

# 既に実行中かチェック
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if ps -p $PID > /dev/null 2>&1; then
        echo "✅ バッテリー制御アプリは既に実行中です (PID: $PID)"
        echo "📊 現在の状態を確認するには: tail -f $LOG_FILE"
        exit 0
    else
        echo "🧹 古いPIDファイルを削除します"
        rm "$PID_FILE"
    fi
fi

# 設定確認
echo "⚙️  本格運用設定を確認中..."
python3 -c "
import config
print(f'📊 チェック間隔: {config.CHARGE_SETTINGS[\"check_interval\"]}秒')
print(f'🔋 充電制御: {config.CHARGE_SETTINGS[\"start_threshold\"]}% → {config.CHARGE_SETTINGS[\"stop_threshold\"]}%')
print(f'🐛 デバッグモード: {config.OTHER_SETTINGS[\"debug_mode\"]}')
print(f'🔧 シミュレーション: {config.OTHER_SETTINGS[\"simulation_mode\"]}')
print(f'📡 デバイスIP: {config.TAPO_SETTINGS[\"device_ip\"]}')
"

echo ""
echo "🔍 システム準備チェック..."

# バッテリー状態確認
echo "🔋 現在のバッテリー状態:"
pmset -g batt | head -2

# Tapoデバイス接続確認
DEVICE_IP=$(python3 -c "import config; print(config.TAPO_SETTINGS['device_ip'])")
echo ""
echo "📡 Tapoデバイス接続テスト ($DEVICE_IP):"
if ping -c 2 "$DEVICE_IP" > /dev/null 2>&1; then
    echo "✅ 接続OK"
else
    echo "❌ 接続NG - 確認してください"
    echo "⚠️  ネットワーク接続に問題がある可能性があります"
fi

echo ""
echo "🚀 バックグラウンドで本格運用を開始します..."

# ログファイル作成・権限設定
if [ ! -f "$LOG_FILE" ]; then
    touch "$LOG_FILE"
fi
chmod 644 "$LOG_FILE"

# バックグラウンドで実行
nohup python3 battery_charge_controller.py > "$LOG_FILE" 2>&1 &
PID=$!

# PIDを保存
echo $PID > "$PID_FILE"
chmod 644 "$PID_FILE"

echo "✅ 本格運用モード開始完了 (PID: $PID)"
echo "📄 ログファイル: $LOG_FILE"
echo "🛑 停止方法: ./stop_production_mode.sh"
echo ""
echo "📊 リアルタイム監視:"
echo "   tail -f $LOG_FILE"
echo ""
echo "📅 定期チェック:"
echo "   ./daily_check.sh    (日次)"
echo "   ./weekly_check.sh   (週次)"
echo ""

# 5秒間の初期ログを表示
echo "🔍 初期動作ログ (5秒間):"
echo "========================"
sleep 5
if [ -f "$LOG_FILE" ]; then
    tail -10 "$LOG_FILE"
else
    echo "ログファイルがまだ作成されていません"
fi

echo ""
echo "🎉 本格運用モード正常起動完了！"
echo "=================================================="
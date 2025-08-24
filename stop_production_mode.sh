#!/bin/bash

# 本格運用モード停止スクリプト

echo "🛑 バッテリー充電制御アプリ - 本格運用モード停止"
echo "=============================================="

cd "$(dirname "$0")"

PID_FILE="production_battery_control.pid"
LOG_FILE="production_battery_control.log"

if [ ! -f "$PID_FILE" ]; then
    echo "❌ PIDファイルが見つかりません"
    echo "💡 プロセスが実行されていない可能性があります"
    
    # 念のためプロセス確認
    if pgrep -f "battery_charge_controller.py" > /dev/null; then
        echo "🔍 関連プロセスが見つかりました："
        pgrep -f "battery_charge_controller.py" | while read pid; do
            echo "  PID: $pid"
            kill $pid 2>/dev/null
        done
        echo "✅ 関連プロセスを停止しました"
    fi
    exit 1
fi

PID=$(cat "$PID_FILE")

if ps -p $PID > /dev/null 2>&1; then
    echo "🛑 プロセス停止中... (PID: $PID)"
    kill $PID
    
    # 停止確認 (最大10秒待機)
    for i in {1..10}; do
        if ! ps -p $PID > /dev/null 2>&1; then
            echo "✅ プロセスが正常に停止しました"
            break
        fi
        echo "⏳ 停止待機中... ($i/10)"
        sleep 1
    done
    
    # まだ動作している場合は強制停止
    if ps -p $PID > /dev/null 2>&1; then
        echo "⚠️  強制停止を実行します"
        kill -9 $PID
        echo "💥 プロセスを強制停止しました"
    fi
else
    echo "⚠️  プロセスが既に停止しています (PID: $PID)"
fi

# PIDファイル削除
rm "$PID_FILE"
echo "🧹 PIDファイルを削除しました"

# 最終ログ表示
echo ""
echo "📄 最終ログ (最新10行):"
echo "========================"
if [ -f "$LOG_FILE" ]; then
    tail -10 "$LOG_FILE"
else
    echo "ログファイルが見つかりません"
fi

echo ""
echo "📊 停止時のシステム状態:"
echo "========================"
echo "🔋 バッテリー状態:"
pmset -g batt | head -2

echo ""
echo "✅ 本格運用モード停止完了"
echo "🔄 再開方法: ./start_production_mode.sh"
echo "=============================================="
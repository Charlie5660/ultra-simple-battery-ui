#!/bin/bash

# バッテリー充電制御アプリを起動するスクリプト

echo "バッテリー充電制御アプリを起動しています..."

# Pythonスクリプトのディレクトリに移動
cd "$(dirname "$0")"

# ログファイルの設定
LOG_FILE="battery_control.log"
PID_FILE="battery_control.pid"

# 既に実行中かチェック
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if ps -p $PID > /dev/null 2>&1; then
        echo "バッテリー制御アプリは既に実行中です (PID: $PID)"
        exit 1
    else
        echo "古いPIDファイルを削除します"
        rm "$PID_FILE"
    fi
fi

# バックグラウンドで実行
echo "バックグラウンドでアプリを起動中..."
nohup python3 battery_charge_controller.py > "$LOG_FILE" 2>&1 &
PID=$!

# PIDを保存
echo $PID > "$PID_FILE"

echo "バッテリー制御アプリが起動しました (PID: $PID)"
echo "ログファイル: $LOG_FILE"
echo "停止方法: ./stop_battery_control.sh"
echo ""
echo "最新のログを確認:"
tail -f "$LOG_FILE"
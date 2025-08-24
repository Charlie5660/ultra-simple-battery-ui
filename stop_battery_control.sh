#!/bin/bash

# バッテリー充電制御アプリを停止するスクリプト

echo "バッテリー充電制御アプリを停止しています..."

# Pythonスクリプトのディレクトリに移動
cd "$(dirname "$0")"

PID_FILE="battery_control.pid"

# PIDファイルが存在するかチェック
if [ ! -f "$PID_FILE" ]; then
    echo "PIDファイルが見つかりません。アプリは実行されていない可能性があります。"
    
    # プロセス名で検索して停止を試行
    echo "プロセス名でバッテリー制御アプリを検索中..."
    PIDS=$(pgrep -f "battery_charge_controller.py")
    
    if [ -n "$PIDS" ]; then
        echo "見つかったプロセス: $PIDS"
        echo "これらのプロセスを停止しますか? (y/N)"
        read -r response
        if [[ "$response" =~ ^[Yy]$ ]]; then
            kill $PIDS
            echo "プロセスを停止しました"
        fi
    else
        echo "実行中のバッテリー制御アプリが見つかりませんでした"
    fi
    exit 1
fi

# PIDファイルからPIDを読み取り
PID=$(cat "$PID_FILE")

# プロセスが実行中かチェック
if ps -p $PID > /dev/null 2>&1; then
    echo "プロセス $PID を停止中..."
    kill $PID
    
    # プロセスが停止するまで待機
    for i in {1..10}; do
        if ! ps -p $PID > /dev/null 2>&1; then
            echo "プロセスが正常に停止しました"
            break
        fi
        sleep 1
    done
    
    # 強制終了が必要かチェック
    if ps -p $PID > /dev/null 2>&1; then
        echo "プロセスを強制終了します..."
        kill -9 $PID
    fi
else
    echo "プロセス $PID は既に停止しています"
fi

# PIDファイルを削除
rm "$PID_FILE"
echo "バッテリー制御アプリを停止しました"
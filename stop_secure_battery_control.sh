#!/bin/bash

# セキュアバッテリー充電制御アプリを停止するスクリプト

echo "🔒 セキュアバッテリー充電制御アプリを停止しています..."

# Pythonスクリプトのディレクトリに移動
cd "$(dirname "$0")"

PID_FILE="secure_battery_control.pid"

# PIDファイルが存在するかチェック
if [ ! -f "$PID_FILE" ]; then
    echo "PIDファイルが見つかりません。アプリは実行されていない可能性があります。"
    
    # プロセス名で検索して停止を試行
    echo "プロセス名でセキュアバッテリー制御アプリを検索中..."
    PIDS=$(pgrep -f "secure_battery_controller.py")
    
    if [ -n "$PIDS" ]; then
        echo "見つかったプロセス: $PIDS"
        echo "これらのプロセスを停止しますか? (y/N)"
        read -r response
        if [[ "$response" =~ ^[Yy]$ ]]; then
            kill $PIDS
            echo "プロセスを停止しました"
            
            # セキュリティログ記録
            if [ -f "security.log" ]; then
                echo "[$(date '+%Y-%m-%d %H:%M:%S')] STOP: 手動プロセス停止" >> security.log
            fi
        fi
    else
        echo "実行中のセキュアバッテリー制御アプリが見つかりませんでした"
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
            echo "✅ プロセスが正常に停止しました"
            break
        fi
        sleep 1
    done
    
    # 強制終了が必要かチェック
    if ps -p $PID > /dev/null 2>&1; then
        echo "プロセスを強制終了します..."
        kill -9 $PID
        echo "⚠️  プロセスを強制終了しました"
    fi
    
    # セキュリティログ記録
    if [ -f "security.log" ]; then
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] STOP: 正常停止 (PID: $PID)" >> security.log
    fi
    
else
    echo "プロセス $PID は既に停止しています"
fi

# PIDファイルを削除
rm "$PID_FILE"

# 実行中のプロセスを念のため再チェック
REMAINING_PIDS=$(pgrep -f "secure_battery_controller.py")
if [ -n "$REMAINING_PIDS" ]; then
    echo "⚠️  まだ実行中のプロセスがあります: $REMAINING_PIDS"
    echo "手動で停止してください: kill $REMAINING_PIDS"
else
    echo "🔒 セキュアバッテリー制御アプリを完全に停止しました"
fi

# セキュリティファイルの状態確認
echo ""
echo "📋 セキュリティファイルの状態:"
if [ -f "secure_config.enc" ]; then
    echo "✅ 暗号化設定ファイル: 存在"
else
    echo "❌ 暗号化設定ファイル: 不在"
fi

if [ -f ".salt" ]; then
    echo "✅ ソルトファイル: 存在"
else
    echo "❌ ソルトファイル: 不在"
fi

if [ -f "security.log" ]; then
    LOG_SIZE=$(wc -l < security.log)
    echo "📝 セキュリティログ: $LOG_SIZE 行"
else
    echo "📝 セキュリティログ: なし"
fi
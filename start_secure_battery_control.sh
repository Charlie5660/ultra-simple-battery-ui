#!/bin/bash

# セキュアバッテリー充電制御アプリを起動するスクリプト

echo "🔒 セキュアバッテリー充電制御アプリを起動しています..."

# Pythonスクリプトのディレクトリに移動
cd "$(dirname "$0")"

# ログファイルの設定
LOG_FILE="secure_battery_control.log"
PID_FILE="secure_battery_control.pid"

# 既に実行中かチェック
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if ps -p $PID > /dev/null 2>&1; then
        echo "🔒 セキュアバッテリー制御アプリは既に実行中です (PID: $PID)"
        exit 1
    else
        echo "古いPIDファイルを削除します"
        rm "$PID_FILE"
    fi
fi

# セキュリティチェック
echo "セキュリティチェックを実行中..."

# 重要ファイルの権限チェック
if [ -f "security.py" ]; then
    SECURITY_PERM=$(stat -f "%Mp%Lp" security.py)
    if [ "$SECURITY_PERM" != "100600" ]; then
        echo "⚠️  security.pyの権限を修正中..."
        chmod 600 security.py
    fi
fi

if [ -f "secure_config.enc" ]; then
    CONFIG_PERM=$(stat -f "%Mp%Lp" secure_config.enc)
    if [ "$CONFIG_PERM" != "100600" ]; then
        echo "⚠️  設定ファイルの権限を修正中..."
        chmod 600 secure_config.enc
    fi
fi

if [ -f ".salt" ]; then
    SALT_PERM=$(stat -f "%Mp%Lp" .salt)
    if [ "$SALT_PERM" != "100600" ]; then
        echo "⚠️  ソルトファイルの権限を修正中..."
        chmod 600 .salt
    fi
fi

# ログファイルの権限設定
if [ ! -f "$LOG_FILE" ]; then
    touch "$LOG_FILE"
fi
chmod 600 "$LOG_FILE"

echo "✅ セキュリティチェック完了"

# バックグラウンドで実行
echo "バックグラウンドでアプリを起動中..."
nohup python3 secure_battery_controller.py > "$LOG_FILE" 2>&1 &
PID=$!

# PIDを保存
echo $PID > "$PID_FILE"
chmod 600 "$PID_FILE"

echo "✅ セキュアバッテリー制御アプリが起動しました (PID: $PID)"
echo "ログファイル: $LOG_FILE"
echo "停止方法: ./stop_secure_battery_control.sh"
echo ""
echo "最新のログを確認:"
echo "※ 設定復号化のパスワード入力が必要な場合があります"
sleep 2
tail -f "$LOG_FILE"
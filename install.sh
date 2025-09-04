#!/bin/bash
# Battery Manager - インストールスクリプト (商用版)

echo "🔋 Battery Manager - インストール開始"
echo "======================================"

# 前提条件チェック
echo "1. システム要件チェック..."

# macOS確認
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "❌ エラー: このアプリはmacOS専用です"
    exit 1
fi

# Python3確認
if ! command -v python3 &> /dev/null; then
    echo "❌ エラー: Python 3がインストールされていません"
    echo "Homebrewでインストール: brew install python"
    exit 1
fi

echo "✅ macOS / Python 3 確認完了"

# 2. 依存関係インストール
echo ""
echo "2. 依存ライブラリインストール..."
pip3 install tapo asyncio-mqtt

if [ $? -eq 0 ]; then
    echo "✅ ライブラリインストール完了"
else
    echo "❌ ライブラリインストールに失敗しました"
    exit 1
fi

# 3. アプリケーションディレクトリ作成
APP_DIR="$HOME/BatteryManager"
echo ""
echo "3. アプリケーションディレクトリ作成..."
echo "インストール先: $APP_DIR"

if [ ! -d "$APP_DIR" ]; then
    mkdir -p "$APP_DIR"
    echo "✅ ディレクトリ作成完了"
else
    echo "ℹ️ ディレクトリは既に存在します"
fi

# 4. ファイルコピー
echo ""
echo "4. アプリケーションファイルコピー..."

# 必要ファイルをコピー
cp battery_manager_app.py "$APP_DIR/"
cp battery_controller_core.py "$APP_DIR/"
cp app_config.py "$APP_DIR/"
cp setup_wizard.py "$APP_DIR/"

# 実行権限付与
chmod +x "$APP_DIR/battery_manager_app.py"
chmod +x "$APP_DIR/setup_wizard.py"

echo "✅ ファイルコピー完了"

# 5. 起動スクリプト作成
echo ""
echo "5. 起動スクリプト作成..."

cat > "$APP_DIR/start_battery_manager.sh" << 'EOF'
#!/bin/bash
# Battery Manager 起動スクリプト

cd "$(dirname "$0")"

# 初回起動チェック
if [ ! -f "app_config.py" ] || [ ! -s "app_config.py" ]; then
    echo "初回起動: セットアップウィザードを開始します..."
    python3 setup_wizard.py
    exit 0
fi

# 通常起動
echo "Battery Manager を起動しています..."
python3 battery_manager_app.py
EOF

chmod +x "$APP_DIR/start_battery_manager.sh"

# 6. デスクトップショートカット作成
echo ""
echo "6. デスクトップショートカット作成..."

cat > "$HOME/Desktop/Battery Manager.command" << EOF
#!/bin/bash
cd "$APP_DIR"
./start_battery_manager.sh
EOF

chmod +x "$HOME/Desktop/Battery Manager.command"

# 7. 完了メッセージ
echo ""
echo "🎉 インストール完了!"
echo "======================================"
echo "アプリケーション場所: $APP_DIR"
echo "デスクトップショートカット: Battery Manager.command"
echo ""
echo "使用方法:"
echo "1. デスクトップの「Battery Manager.command」をダブルクリック"
echo "2. 初回起動時はセットアップウィザードが開きます"
echo "3. Tapo P110Mの設定を入力してください"
echo ""
echo "サポート: GitHub リポジトリをご確認ください"
echo "⚠️ 注意: 充電器をTapo P110Mに接続してからご利用ください"
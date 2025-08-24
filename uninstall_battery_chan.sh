#!/bin/bash
echo "🔋⚡ Battery Chan アンインストール"
echo "================================"

read -p "本当にBattery Chanをアンインストールしますか？ (y/N): " confirm

if [[ $confirm == [yY] || $confirm == [yY][eE][sS] ]]; then
    echo "🗑️  アンインストール中..."
    
    # アプリケーションフォルダから削除
    if [ -d "/Applications/Battery Chan.app" ]; then
        rm -rf "/Applications/Battery Chan.app"
        echo "✅ アプリケーションを削除しました"
    fi
    
    # デスクトップエイリアス削除
    if [ -L "~/Desktop/Battery Chan.app" ]; then
        rm "~/Desktop/Battery Chan.app"
        echo "✅ デスクトップエイリアスを削除しました"
    fi
    
    # 設定ファイル削除確認
    read -p "設定ファイルも削除しますか？ (y/N): " delete_config
    
    if [[ $delete_config == [yY] || $delete_config == [yY][eE][sS] ]]; then
        cd "/Users/yamakawadaiki/battery_charge_app"
        rm -f secure_config.enc .salt *.log
        echo "✅ 設定ファイルを削除しました"
    fi
    
    echo ""
    echo "🎉 Battery Chanのアンインストールが完了しました"
    echo "👋 ご利用ありがとうございました！"
else
    echo "❌ アンインストールをキャンセルしました"
fi

read -p "Enterキーを押して終了..."

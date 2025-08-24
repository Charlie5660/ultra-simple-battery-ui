#!/usr/bin/env python3
"""
可愛いバッテリー充電制御アプリのアイコン作成スクリプト
"""

import os
from PIL import Image, ImageDraw, ImageFont
import subprocess

def create_cute_battery_icon():
    """可愛いバッテリーアイコンを作成"""
    
    # 1024x1024の高解像度でアイコンを作成
    size = 1024
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # 背景円（グラデーション風）
    center_x, center_y = size // 2, size // 2
    radius = size // 2 - 50
    
    # 背景の可愛いピンクグラデーション
    for i in range(radius, 0, -5):
        alpha = int(255 * (1 - (radius - i) / radius) * 0.8)
        color = (255, 182, 193, alpha)  # ライトピンク
        draw.ellipse([center_x - i, center_y - i, center_x + i, center_y + i], fill=color)
    
    # メインのバッテリー本体（可愛い角丸）
    battery_width = 300
    battery_height = 180
    battery_x = center_x - battery_width // 2
    battery_y = center_y - battery_height // 2 + 20
    
    # バッテリー外枠（白色）
    draw.rounded_rectangle(
        [battery_x, battery_y, battery_x + battery_width, battery_y + battery_height],
        radius=25, fill=(255, 255, 255, 255), outline=(100, 100, 100, 255), width=8
    )
    
    # バッテリープラス端子
    terminal_width = 30
    terminal_height = 60
    terminal_x = battery_x + battery_width
    terminal_y = center_y - terminal_height // 2 + 20
    draw.rounded_rectangle(
        [terminal_x, terminal_y, terminal_x + terminal_width, terminal_y + terminal_height],
        radius=10, fill=(200, 200, 200, 255)
    )
    
    # 充電レベル表示（緑色、75%程度）
    charge_margin = 20
    charge_width = battery_width - charge_margin * 2
    charge_height = battery_height - charge_margin * 2
    charge_level = 0.75  # 75%
    
    # 充電部分（グラデーション緑）
    filled_width = int(charge_width * charge_level)
    for i in range(0, filled_width, 5):
        alpha = 200 + int(55 * (i / filled_width))
        color = (50 + int(100 * (i / filled_width)), 255, 100, alpha)
        draw.rectangle([
            battery_x + charge_margin + i,
            battery_y + charge_margin,
            battery_x + charge_margin + min(i + 5, filled_width),
            battery_y + battery_height - charge_margin
        ], fill=color)
    
    # 可愛い目（アニメ風）
    eye_size = 40
    eye_y = battery_y - 80
    
    # 左目
    left_eye_x = center_x - 40
    draw.ellipse([left_eye_x - eye_size//2, eye_y - eye_size//2, 
                  left_eye_x + eye_size//2, eye_y + eye_size//2], 
                  fill=(0, 0, 0, 255))
    # 目のハイライト
    highlight_size = eye_size // 3
    draw.ellipse([left_eye_x - eye_size//4, eye_y - eye_size//4,
                  left_eye_x - eye_size//4 + highlight_size, eye_y - eye_size//4 + highlight_size],
                  fill=(255, 255, 255, 255))
    
    # 右目
    right_eye_x = center_x + 40
    draw.ellipse([right_eye_x - eye_size//2, eye_y - eye_size//2,
                  right_eye_x + eye_size//2, eye_y + eye_size//2],
                  fill=(0, 0, 0, 255))
    # 目のハイライト
    draw.ellipse([right_eye_x - eye_size//4, eye_y - eye_size//4,
                  right_eye_x - eye_size//4 + highlight_size, eye_y - eye_size//4 + highlight_size],
                  fill=(255, 255, 255, 255))
    
    # 可愛い口（笑顔）
    mouth_width = 80
    mouth_height = 40
    mouth_y = battery_y + battery_height + 40
    draw.arc([center_x - mouth_width//2, mouth_y - mouth_height//2,
              center_x + mouth_width//2, mouth_y + mouth_height//2],
              start=0, end=180, fill=(255, 100, 100, 255), width=12)
    
    # 電気のスパーク効果（キラキラ）
    sparkles = [
        (center_x - 150, center_y - 150, 15),
        (center_x + 150, center_y - 120, 12),
        (center_x - 120, center_y + 150, 10),
        (center_x + 130, center_y + 140, 14),
        (center_x - 200, center_y + 50, 8),
        (center_x + 180, center_y - 80, 11)
    ]
    
    for spark_x, spark_y, spark_size in sparkles:
        # 星型のキラキラ
        star_color = (255, 255, 100, 200)  # 黄色
        # 縦線
        draw.rectangle([spark_x - 2, spark_y - spark_size, 
                       spark_x + 2, spark_y + spark_size], fill=star_color)
        # 横線
        draw.rectangle([spark_x - spark_size, spark_y - 2,
                       spark_x + spark_size, spark_y + 2], fill=star_color)
        # 斜め線
        draw.rectangle([spark_x - spark_size//2, spark_y - spark_size//2,
                       spark_x + spark_size//2, spark_y + spark_size//2], fill=star_color)
    
    # 小さな稲妻マーク（充電中を表現）
    lightning_points = [
        (center_x + 20, battery_y + 30),
        (center_x + 50, battery_y + 30),
        (center_x + 30, battery_y + 60),
        (center_x + 60, battery_y + 60),
        (center_x + 35, battery_y + 90),
        (center_x + 10, battery_y + 70),
        (center_x + 25, battery_y + 50),
        (center_x, battery_y + 50)
    ]
    draw.polygon(lightning_points, fill=(255, 255, 0, 255), outline=(255, 200, 0, 255))
    
    return img

def create_icns_file():
    """macOS用の.icnsファイルを作成"""
    print("🎨 可愛いバッテリーアイコンを作成中...")
    
    # 高解像度アイコン作成
    icon = create_cute_battery_icon()
    
    # 必要なサイズでアイコンセットを作成
    icon_dir = "/Users/yamakawadaiki/battery_charge_app/BatteryChargeControl.iconset"
    
    # iconsetディレクトリ作成
    os.makedirs(icon_dir, exist_ok=True)
    
    # 様々なサイズのアイコンを生成
    sizes = [
        (16, "icon_16x16.png"),
        (32, "icon_16x16@2x.png"),
        (32, "icon_32x32.png"),
        (64, "icon_32x32@2x.png"),
        (128, "icon_128x128.png"),
        (256, "icon_128x128@2x.png"),
        (256, "icon_256x256.png"),
        (512, "icon_256x256@2x.png"),
        (512, "icon_512x512.png"),
        (1024, "icon_512x512@2x.png")
    ]
    
    for size, filename in sizes:
        resized_icon = icon.resize((size, size), Image.Resampling.LANCZOS)
        resized_icon.save(os.path.join(icon_dir, filename))
        print(f"  ✅ {filename} ({size}x{size}) 作成完了")
    
    # .icnsファイルを生成
    icns_path = "/Users/yamakawadaiki/battery_charge_app/BatteryChargeControl.icns"
    
    try:
        result = subprocess.run([
            "iconutil", "-c", "icns", 
            "-o", icns_path,
            icon_dir
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"🎉 .icnsファイル作成成功: {icns_path}")
            
            # iconsetディレクトリを削除
            import shutil
            shutil.rmtree(icon_dir)
            
            return icns_path
        else:
            print(f"❌ .icns作成エラー: {result.stderr}")
            return None
            
    except FileNotFoundError:
        print("❌ iconutilコマンドが見つかりません")
        # PNGアイコンとして保存
        png_path = "/Users/yamakawadaiki/battery_charge_app/BatteryChargeControl.png"
        icon.save(png_path)
        print(f"📄 代替でPNGアイコンを保存: {png_path}")
        return png_path

def create_app_bundle():
    """macOS用のアプリケーションバンドルを作成"""
    app_name = "BatteryChargeControl"
    app_path = f"/Users/yamakawadaiki/battery_charge_app/{app_name}.app"
    
    print(f"📦 {app_name}.appバンドルを作成中...")
    
    # アプリバンドル構造作成
    contents_dir = os.path.join(app_path, "Contents")
    macos_dir = os.path.join(contents_dir, "MacOS")
    resources_dir = os.path.join(contents_dir, "Resources")
    
    os.makedirs(macos_dir, exist_ok=True)
    os.makedirs(resources_dir, exist_ok=True)
    
    # Info.plistファイル作成
    info_plist = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleName</key>
    <string>Battery Charge Control</string>
    <key>CFBundleDisplayName</key>
    <string>🔋 Battery Charge Control</string>
    <key>CFBundleIdentifier</key>
    <string>com.yamakawadaiki.batterychargecontrol</string>
    <key>CFBundleVersion</key>
    <string>1.0</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0</string>
    <key>CFBundleExecutable</key>
    <string>BatteryChargeControl</string>
    <key>CFBundleIconFile</key>
    <string>BatteryChargeControl.icns</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleSignature</key>
    <string>BCCL</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.15</string>
    <key>NSHighResolutionCapable</key>
    <true/>
</dict>
</plist>"""
    
    with open(os.path.join(contents_dir, "Info.plist"), "w") as f:
        f.write(info_plist)
    
    # 実行スクリプト作成
    launcher_script = f"""#!/bin/bash
cd "{os.path.dirname(os.path.abspath(__file__))}/../../../"
exec ./start_production_mode.sh
"""
    
    launcher_path = os.path.join(macos_dir, app_name)
    with open(launcher_path, "w") as f:
        f.write(launcher_script)
    
    # 実行権限付与
    os.chmod(launcher_path, 0o755)
    
    # アイコンをリソースにコピー
    icon_path = create_icns_file()
    if icon_path and os.path.exists(icon_path):
        import shutil
        if icon_path.endswith('.icns'):
            shutil.copy2(icon_path, os.path.join(resources_dir, "BatteryChargeControl.icns"))
        else:
            # PNGファイルの場合、アイコンとして表示されるようにコピー
            shutil.copy2(icon_path, os.path.join(resources_dir, "BatteryChargeControl.png"))
    
    print(f"🎉 {app_name}.app 作成完了!")
    print(f"📍 場所: {app_path}")
    print("\n🚀 使用方法:")
    print(f"  1. Finderで {app_path} を開く")
    print("  2. アプリケーションフォルダにドラッグ&ドロップ")
    print("  3. Launchpadまたはアプリケーション一覧から起動")
    
    return app_path

def main():
    """メイン関数"""
    print("🔋⚡ 可愛いバッテリー充電制御アプリアイコン作成ツール")
    print("=" * 60)
    
    try:
        # Pillowライブラリの確認
        import PIL
        print("✅ Pillowライブラリ確認完了")
    except ImportError:
        print("❌ Pillowライブラリが必要です")
        print("インストール: pip3 install Pillow")
        return
    
    # macOSアプリケーションバンドル作成
    app_path = create_app_bundle()
    
    print("\n" + "=" * 60)
    print("🎨 アイコン作成完了!")
    print("🎉 可愛いバッテリーアイコンのアプリが完成しました!")
    print("=" * 60)

if __name__ == "__main__":
    main()
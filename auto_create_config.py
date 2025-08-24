#!/usr/bin/env python3
"""
自動セキュア設定作成スクリプト
対話入力なしでテスト用セキュア設定を作成
"""

import os
from security import SecureConfig, secure_file_permissions

def create_test_secure_config():
    """テスト用セキュア設定を自動作成"""
    print("🔒 テスト用セキュア設定を作成中...")
    
    # テスト用設定データ
    config_data = {
        'TAPO_USERNAME': 'test@example.com',
        'TAPO_PASSWORD': 'test_password_123',
        'DEVICE_IP': '192.168.1.100',
        'CHARGE_START_THRESHOLD': 30,
        'CHARGE_STOP_THRESHOLD': 78,
        'CHECK_INTERVAL': 60,
        'DEBUG_MODE': True,
        'SIMULATION_MODE': True
    }
    
    # 暗号化パスワード
    encryption_password = "battery_test_2025"
    
    print("📋 作成する設定:")
    print(f"  メールアドレス: {config_data['TAPO_USERNAME']}")
    print(f"  デバイスIP: {config_data['DEVICE_IP']}")
    print(f"  充電制御: {config_data['CHARGE_START_THRESHOLD']}% → {config_data['CHARGE_STOP_THRESHOLD']}%")
    print(f"  チェック間隔: {config_data['CHECK_INTERVAL']}秒")
    print(f"  シミュレーションモード: {config_data['SIMULATION_MODE']}")
    
    # セキュア設定を作成
    secure_config = SecureConfig()
    
    try:
        # 暗号化して保存
        if secure_config.encrypt_config(config_data, encryption_password):
            print("✅ セキュア設定ファイルが作成されました")
            
            # ファイル権限を設定
            if os.path.exists(secure_config.config_file):
                secure_file_permissions(secure_config.config_file)
                print(f"📁 {secure_config.config_file} の権限を設定")
            
            if os.path.exists(secure_config.salt_file):
                secure_file_permissions(secure_config.salt_file)
                print(f"📁 {secure_config.salt_file} の権限を設定")
            
            print("\n🔐 暗号化情報:")
            print(f"  暗号化パスワード: {encryption_password}")
            print("  ⚠️  実際の使用時は強力なパスワードに変更してください")
            
            print("\n📂 作成されたファイル:")
            print(f"  - {secure_config.config_file} (暗号化設定)")
            print(f"  - {secure_config.salt_file} (暗号化ソルト)")
            
            return True
        else:
            print("❌ セキュア設定ファイルの作成に失敗しました")
            return False
            
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        return False

def create_real_config_template():
    """実際の設定用テンプレートを作成"""
    template_content = '''# セキュア設定作成用テンプレート
# 以下の値を実際の情報に変更してから使用してください

TAPO_SETTINGS = {
    "username": "your_tapo_email@example.com",     # Tapoアカウントのメールアドレス
    "password": "your_tapo_password",              # Tapoアカウントのパスワード
    "device_ip": "192.168.1.100",                  # Tapo P110MのIPアドレス
}

CHARGE_SETTINGS = {
    "start_threshold": 30,     # 充電開始閾値 (%)
    "stop_threshold": 78,      # 充電停止閾値 (%)
    "check_interval": 60,      # チェック間隔 (秒)
}

OTHER_SETTINGS = {
    "debug_mode": True,        # デバッグモード
    "simulation_mode": False,  # 実機テスト時はFalseに変更
}

# 暗号化パスワード（8文字以上の強力なパスワードを設定）
ENCRYPTION_PASSWORD = "your_strong_password_here"
'''
    
    template_file = "config_template.py"
    with open(template_file, 'w', encoding='utf-8') as f:
        f.write(template_content)
    
    os.chmod(template_file, 0o600)
    print(f"📝 設定テンプレートを作成しました: {template_file}")
    print("   実際の情報に変更してから使用してください")

def verify_config():
    """作成されたセキュア設定を検証"""
    print("\n🔍 セキュア設定の検証中...")
    
    secure_config = SecureConfig()
    
    try:
        # テスト用パスワードで復号化テスト
        config_data = secure_config.decrypt_config("battery_test_2025")
        
        if config_data:
            print("✅ セキュア設定の復号化成功")
            print("📋 設定内容:")
            for key, value in config_data.items():
                if 'PASSWORD' in key:
                    print(f"  {key}: {'*' * len(str(value))}")
                else:
                    print(f"  {key}: {value}")
            return True
        else:
            print("❌ セキュア設定の復号化失敗")
            return False
            
    except Exception as e:
        print(f"❌ 検証エラー: {e}")
        return False

def main():
    """メイン関数"""
    print("🔒 自動セキュア設定作成ツール")
    print("=" * 40)
    
    # 既存ファイルの確認
    if os.path.exists("secure_config.enc"):
        print("⚠️  既存のセキュア設定ファイルが見つかりました")
        print("既存ファイルを削除して新しい設定を作成します...")
        os.remove("secure_config.enc")
        
    if os.path.exists(".salt"):
        os.remove(".salt")
    
    # テスト用セキュア設定を作成
    if create_test_secure_config():
        print("\n" + "="*40)
        
        # 設定を検証
        verify_config()
        
        # 実際の設定用テンプレートも作成
        print("\n" + "="*40)
        create_real_config_template()
        
        print("\n🎯 次のステップ:")
        print("1. テスト実行: python3 ultra_secure_battery_controller.py")
        print("2. 実際の設定: config_template.py を編集後、再作成")
        print("3. 事前チェック: python3 pre_test_check.py")
        
        return True
    else:
        print("❌ セキュア設定の作成に失敗しました")
        return False

if __name__ == "__main__":
    main()
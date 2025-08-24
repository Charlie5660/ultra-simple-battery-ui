#!/usr/bin/env python3
import os
import sys
from security import SecureConfig, validate_ip_address, validate_email, secure_file_permissions

def setup_secure_configuration():
    """セキュアな設定ファイルを初期セットアップ"""
    print("🔒 バッテリー充電制御アプリ - セキュア設定セットアップ")
    print("=" * 60)
    
    secure_config = SecureConfig()
    
    # 既存の暗号化設定ファイルがあるかチェック
    if os.path.exists(secure_config.config_file):
        print(f"既存の暗号化設定ファイルが見つかりました: {secure_config.config_file}")
        choice = input("上書きしますか？ (y/N): ").lower()
        if choice != 'y':
            print("セットアップを中止しました")
            return False
    
    print("\nTapo P110Mの設定情報を入力してください:")
    print("-" * 40)
    
    # ユーザー入力の収集と検証
    config_data = {}
    
    # Tapoユーザー名（メールアドレス）
    while True:
        username = input("Tapoアカウントのメールアドレス: ").strip()
        if not username:
            print("❌ メールアドレスを入力してください")
            continue
        if not validate_email(username):
            print("❌ 有効なメールアドレス形式ではありません")
            continue
        config_data['TAPO_USERNAME'] = username
        break
    
    # Tapoパスワード
    import getpass
    while True:
        password = getpass.getpass("Tapoアカウントのパスワード: ")
        if not password:
            print("❌ パスワードを入力してください")
            continue
        if len(password) < 6:
            print("❌ パスワードは6文字以上で入力してください")
            continue
        config_data['TAPO_PASSWORD'] = password
        break
    
    # デバイスIPアドレス
    while True:
        device_ip = input("Tapo P110MのIPアドレス (例: 192.168.1.100): ").strip()
        if not device_ip:
            print("❌ IPアドレスを入力してください")
            continue
        if not validate_ip_address(device_ip):
            print("❌ 有効なIPアドレス形式ではありません")
            continue
        config_data['DEVICE_IP'] = device_ip
        break
    
    print("\n充電制御設定:")
    print("-" * 20)
    
    # 充電開始閾値
    while True:
        try:
            start_threshold = input("充電開始閾値 (%) [デフォルト: 30]: ").strip()
            if not start_threshold:
                start_threshold = 30
            else:
                start_threshold = int(start_threshold)
            
            if start_threshold < 5 or start_threshold > 95:
                print("❌ 閾値は5-95%の範囲で入力してください")
                continue
            
            config_data['CHARGE_START_THRESHOLD'] = start_threshold
            break
        except ValueError:
            print("❌ 数値で入力してください")
    
    # 充電停止閾値
    while True:
        try:
            stop_threshold = input("充電停止閾値 (%) [デフォルト: 78]: ").strip()
            if not stop_threshold:
                stop_threshold = 78
            else:
                stop_threshold = int(stop_threshold)
            
            if stop_threshold < 10 or stop_threshold > 100:
                print("❌ 閾値は10-100%の範囲で入力してください")
                continue
            
            if stop_threshold <= start_threshold:
                print("❌ 停止閾値は開始閾値より大きい値を設定してください")
                continue
            
            config_data['CHARGE_STOP_THRESHOLD'] = stop_threshold
            break
        except ValueError:
            print("❌ 数値で入力してください")
    
    # 監視間隔
    while True:
        try:
            check_interval = input("バッテリーチェック間隔 (秒) [デフォルト: 60]: ").strip()
            if not check_interval:
                check_interval = 60
            else:
                check_interval = int(check_interval)
            
            if check_interval < 10 or check_interval > 3600:
                print("❌ 間隔は10-3600秒の範囲で入力してください")
                continue
            
            config_data['CHECK_INTERVAL'] = check_interval
            break
        except ValueError:
            print("❌ 数値で入力してください")
    
    # デバッグ・シミュレーション設定
    print("\nその他の設定:")
    print("-" * 15)
    
    debug_mode = input("デバッグモード (y/N): ").lower() == 'y'
    config_data['DEBUG_MODE'] = debug_mode
    
    simulation_mode = input("シミュレーションモード (Y/n): ").lower()
    config_data['SIMULATION_MODE'] = simulation_mode != 'n'
    
    print("\n設定内容の確認:")
    print("-" * 20)
    print(f"メールアドレス: {config_data['TAPO_USERNAME']}")
    print(f"デバイスIP: {config_data['DEVICE_IP']}")
    print(f"充電制御: {config_data['CHARGE_START_THRESHOLD']}% → {config_data['CHARGE_STOP_THRESHOLD']}%")
    print(f"チェック間隔: {config_data['CHECK_INTERVAL']}秒")
    print(f"デバッグモード: {config_data['DEBUG_MODE']}")
    print(f"シミュレーションモード: {config_data['SIMULATION_MODE']}")
    
    confirm = input("\nこの設定で保存しますか？ (Y/n): ").lower()
    if confirm == 'n':
        print("セットアップを中止しました")
        return False
    
    # 暗号化して保存
    print("\n設定を暗号化して保存中...")
    if secure_config.encrypt_config(config_data):
        print("✅ セキュアな設定ファイルが作成されました")
        
        # ファイル権限の設定
        secure_file_permissions(secure_config.config_file)
        if os.path.exists(secure_config.salt_file):
            secure_file_permissions(secure_config.salt_file)
        
        print("\n⚠️  重要な注意事項:")
        print("1. 設定ファイルの暗号化に使用したパスワードを忘れないでください")
        print("2. secure_config.enc と .salt ファイルを安全に保管してください")
        print("3. これらのファイルを削除すると設定が復元できなくなります")
        
        return True
    else:
        print("❌ 設定ファイルの作成に失敗しました")
        return False

def main():
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        # テスト用の設定データで暗号化テスト
        print("テスト用設定で暗号化テスト")
        test_config = {
            'TAPO_USERNAME': 'test@example.com',
            'TAPO_PASSWORD': 'test_password',
            'DEVICE_IP': '192.168.1.100',
            'CHARGE_START_THRESHOLD': 30,
            'CHARGE_STOP_THRESHOLD': 78,
            'CHECK_INTERVAL': 60,
            'DEBUG_MODE': True,
            'SIMULATION_MODE': True
        }
        
        secure_config = SecureConfig("test_config.enc")
        if secure_config.encrypt_config(test_config, "test123"):
            print("テスト暗号化成功")
            
            # 復号化テスト
            decrypted = secure_config.decrypt_config("test123")
            if decrypted == test_config:
                print("テスト復号化成功")
                os.remove("test_config.enc")
                if os.path.exists(".salt"):
                    os.remove(".salt")
            else:
                print("テスト復号化失敗")
        return
    
    # 通常のセットアップ
    setup_secure_configuration()

if __name__ == "__main__":
    main()
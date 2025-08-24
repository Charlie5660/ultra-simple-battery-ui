#!/usr/bin/env python3
"""
セキュア設定作成支援スクリプト
コマンドライン引数でセキュア設定を作成
"""

import sys
import getpass
from security import SecureConfig, validate_ip_address, validate_email, secure_file_permissions

def create_config_with_prompts():
    """プロンプトによる対話的設定作成"""
    print("🔒 セキュア設定を作成します")
    print("=" * 40)
    
    config_data = {}
    
    # Tapoアカウント情報
    print("\n📧 Tapoアカウント情報:")
    while True:
        username = input("メールアドレス: ").strip()
        if username and validate_email(username):
            config_data['TAPO_USERNAME'] = username
            break
        print("❌ 有効なメールアドレスを入力してください")
    
    while True:
        password = getpass.getpass("パスワード: ")
        if len(password) >= 6:
            config_data['TAPO_PASSWORD'] = password
            break
        print("❌ パスワードは6文字以上で入力してください")
    
    # デバイス情報
    print("\n🔌 Tapo P110M デバイス情報:")
    while True:
        device_ip = input("IPアドレス (例: 192.168.1.100): ").strip()
        if device_ip and validate_ip_address(device_ip):
            config_data['DEVICE_IP'] = device_ip
            break
        print("❌ 有効なIPアドレスを入力してください")
    
    # 充電制御設定
    print("\n⚡ 充電制御設定:")
    
    # 開始閾値
    while True:
        start_str = input("充電開始閾値 (%) [30]: ").strip()
        if not start_str:
            config_data['CHARGE_START_THRESHOLD'] = 30
            break
        try:
            start_threshold = int(start_str)
            if 5 <= start_threshold <= 95:
                config_data['CHARGE_START_THRESHOLD'] = start_threshold
                break
            print("❌ 5-95の範囲で入力してください")
        except ValueError:
            print("❌ 数値で入力してください")
    
    # 停止閾値  
    while True:
        stop_str = input("充電停止閾値 (%) [78]: ").strip()
        if not stop_str:
            config_data['CHARGE_STOP_THRESHOLD'] = 78
            break
        try:
            stop_threshold = int(stop_str)
            if stop_threshold > config_data['CHARGE_START_THRESHOLD'] and stop_threshold <= 100:
                config_data['CHARGE_STOP_THRESHOLD'] = stop_threshold
                break
            print(f"❌ {config_data['CHARGE_START_THRESHOLD']}より大きく100以下で入力してください")
        except ValueError:
            print("❌ 数値で入力してください")
    
    # 監視間隔
    while True:
        interval_str = input("チェック間隔 (秒) [60]: ").strip()
        if not interval_str:
            config_data['CHECK_INTERVAL'] = 60
            break
        try:
            interval = int(interval_str)
            if 10 <= interval <= 3600:
                config_data['CHECK_INTERVAL'] = interval
                break
            print("❌ 10-3600秒の範囲で入力してください")
        except ValueError:
            print("❌ 数値で入力してください")
    
    # その他設定
    print("\n🔧 その他の設定:")
    debug_mode = input("デバッグモード (y/N): ").lower() == 'y'
    config_data['DEBUG_MODE'] = debug_mode
    
    simulation_mode = input("シミュレーションモード (Y/n): ").lower() != 'n'
    config_data['SIMULATION_MODE'] = simulation_mode
    
    return config_data

def create_test_config():
    """テスト用設定を作成"""
    return {
        'TAPO_USERNAME': 'test@example.com',
        'TAPO_PASSWORD': 'test_password_123',
        'DEVICE_IP': '192.168.1.100',
        'CHARGE_START_THRESHOLD': 30,
        'CHARGE_STOP_THRESHOLD': 78,
        'CHECK_INTERVAL': 60,
        'DEBUG_MODE': True,
        'SIMULATION_MODE': True
    }

def save_secure_config(config_data, password=None):
    """セキュア設定を保存"""
    secure_config = SecureConfig()
    
    print("\n🔐 設定を暗号化中...")
    if password is None:
        while True:
            password = getpass.getpass("暗号化用パスワードを設定してください: ")
            confirm = getpass.getpass("パスワードを再入力してください: ")
            
            if password == confirm:
                if len(password) >= 8:
                    break
                else:
                    print("❌ パスワードは8文字以上で設定してください")
            else:
                print("❌ パスワードが一致しません")
    
    # 設定確認
    print("\n📋 設定内容の確認:")
    print(f"メールアドレス: {config_data['TAPO_USERNAME']}")
    print(f"デバイスIP: {config_data['DEVICE_IP']}")
    print(f"充電制御: {config_data['CHARGE_START_THRESHOLD']}% → {config_data['CHARGE_STOP_THRESHOLD']}%")
    print(f"チェック間隔: {config_data['CHECK_INTERVAL']}秒")
    print(f"デバッグモード: {config_data['DEBUG_MODE']}")
    print(f"シミュレーションモード: {config_data['SIMULATION_MODE']}")
    
    confirm = input("\nこの設定で保存しますか？ (Y/n): ").lower()
    if confirm == 'n':
        print("❌ 設定作成を中止しました")
        return False
    
    # 暗号化保存
    if secure_config.encrypt_config(config_data, password):
        print("✅ セキュア設定ファイルが作成されました")
        
        # ファイル権限設定
        secure_file_permissions(secure_config.config_file)
        if hasattr(secure_config, 'salt_file'):
            secure_file_permissions(secure_config.salt_file)
        
        print("\n🔒 セキュリティ情報:")
        print("- 設定ファイル: secure_config.enc")
        print("- ソルトファイル: .salt")
        print("- 両ファイルとも重要です（削除しないでください）")
        print("- 暗号化パスワードを安全に保管してください")
        
        return True
    else:
        print("❌ セキュア設定ファイルの作成に失敗しました")
        return False

def main():
    """メイン関数"""
    print("🔒 セキュア設定作成ツール")
    print("=" * 30)
    
    if len(sys.argv) > 1:
        if sys.argv[1] == '--test':
            print("🧪 テスト用設定を作成します")
            config_data = create_test_config()
            return save_secure_config(config_data, "test123")
        elif sys.argv[1] == '--help':
            print("使用方法:")
            print("  python3 create_secure_config.py           # 対話モード")
            print("  python3 create_secure_config.py --test    # テスト設定")
            print("  python3 create_secure_config.py --help    # ヘルプ")
            return
    
    # 既存設定ファイルの確認
    secure_config = SecureConfig()
    if secure_config.config_file and hasattr(secure_config, 'config_file'):
        import os
        if os.path.exists(secure_config.config_file):
            print("⚠️  既存のセキュア設定ファイルが見つかりました")
            choice = input("上書きしますか？ (y/N): ").lower()
            if choice != 'y':
                print("設定作成を中止しました")
                return
    
    # 対話的設定作成
    try:
        config_data = create_config_with_prompts()
        save_secure_config(config_data)
    except KeyboardInterrupt:
        print("\n\n❌ 設定作成が中断されました")
    except Exception as e:
        print(f"\n❌ エラーが発生しました: {e}")

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
非インタラクティブセキュア設定作成スクリプト
config.pyの設定を使用してセキュア設定を作成
"""

import sys
import os
from security import SecureConfig

def create_secure_from_config():
    """config.pyからセキュア設定を作成"""
    try:
        # config.pyを読み込み
        import config
        
        # 設定データ準備
        config_data = {
            'TAPO_USERNAME': config.TAPO_SETTINGS['username'],
            'TAPO_PASSWORD': config.TAPO_SETTINGS['password'], 
            'DEVICE_IP': config.TAPO_SETTINGS['device_ip'],
            'CHARGE_START_THRESHOLD': config.CHARGE_SETTINGS['start_threshold'],
            'CHARGE_STOP_THRESHOLD': config.CHARGE_SETTINGS['stop_threshold'],
            'CHECK_INTERVAL': config.CHARGE_SETTINGS['check_interval'],
            'DEBUG_MODE': config.OTHER_SETTINGS['debug_mode'],
            'SIMULATION_MODE': config.OTHER_SETTINGS['simulation_mode']
        }
        
        encryption_password = config.ENCRYPTION_PASSWORD
        
        if not encryption_password:
            print("❌ config.pyでENCRYPTION_PASSWORDが設定されていません")
            return False
            
        # セキュア設定作成
        secure_config = SecureConfig()
        success = secure_config.encrypt_config(config_data, encryption_password)
        
        if success:
            print("✅ セキュア設定ファイル (secure_config.enc) を作成しました")
            print("\n📋 設定内容:")
            print(f"  メールアドレス: {config_data['TAPO_USERNAME']}")
            print(f"  デバイスIP: {config_data['DEVICE_IP']}")
            print(f"  充電制御: {config_data['CHARGE_START_THRESHOLD']}% → {config_data['CHARGE_STOP_THRESHOLD']}%")
            print(f"  チェック間隔: {config_data['CHECK_INTERVAL']}秒")
            print(f"  シミュレーションモード: {config_data['SIMULATION_MODE']}")
            return True
        else:
            print("❌ セキュア設定の保存に失敗しました")
            return False
            
    except ImportError:
        print("❌ config.pyが見つかりません")
        return False
    except KeyError as e:
        print(f"❌ config.pyに必要な設定項目がありません: {e}")
        return False
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        return False

def main():
    print("🔒 非インタラクティブセキュア設定作成")
    print("=" * 50)
    
    # 既存ファイル確認
    if os.path.exists('secure_config.enc'):
        print("⚠️  既存のセキュア設定ファイルが見つかりました")
        print("💡 自動的に上書きします...")
        
    success = create_secure_from_config()
    
    if success:
        print("\n🎉 セキュア設定作成完了！")
        print("📚 次のステップ:")
        print("  python3 ultra_secure_battery_controller.py")
        return 0
    else:
        print("\n❌ セキュア設定作成に失敗しました")
        return 1

if __name__ == "__main__":
    sys.exit(main())
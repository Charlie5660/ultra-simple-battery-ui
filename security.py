#!/usr/bin/env python3
import os
import json
import getpass
import hashlib
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

class SecureConfig:
    """設定ファイルの暗号化・復号化を行うクラス"""
    
    def __init__(self, config_file="secure_config.enc"):
        self.config_file = config_file
        self.salt_file = ".salt"
        
    def _derive_key(self, password: str, salt: bytes) -> bytes:
        """パスワードから暗号化キーを生成"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key
    
    def _get_or_create_salt(self) -> bytes:
        """ソルトを取得または生成"""
        if os.path.exists(self.salt_file):
            with open(self.salt_file, 'rb') as f:
                return f.read()
        else:
            salt = os.urandom(16)
            with open(self.salt_file, 'wb') as f:
                f.write(salt)
            # ソルトファイルの権限を制限
            os.chmod(self.salt_file, 0o600)
            return salt
    
    def encrypt_config(self, config_data: dict, password: str = None) -> bool:
        """設定データを暗号化して保存"""
        try:
            if password is None:
                password = getpass.getpass("設定暗号化用のパスワードを入力してください: ")
            
            # ソルトを取得
            salt = self._get_or_create_salt()
            
            # キーを生成
            key = self._derive_key(password, salt)
            fernet = Fernet(key)
            
            # データをJSON化して暗号化
            json_data = json.dumps(config_data, ensure_ascii=False, indent=2)
            encrypted_data = fernet.encrypt(json_data.encode())
            
            # 暗号化ファイルに保存
            with open(self.config_file, 'wb') as f:
                f.write(encrypted_data)
            
            # ファイル権限を制限（所有者のみ読み書き可能）
            os.chmod(self.config_file, 0o600)
            
            print(f"設定ファイルが暗号化されました: {self.config_file}")
            return True
            
        except Exception as e:
            print(f"設定暗号化エラー: {e}")
            return False
    
    def decrypt_config(self, password: str = None) -> dict:
        """暗号化された設定ファイルを復号化"""
        try:
            if not os.path.exists(self.config_file):
                raise FileNotFoundError(f"設定ファイルが見つかりません: {self.config_file}")
            
            if not os.path.exists(self.salt_file):
                raise FileNotFoundError(f"ソルトファイルが見つかりません: {self.salt_file}")
            
            if password is None:
                password = getpass.getpass("設定復号化用のパスワードを入力してください: ")
            
            # ソルトを読み込み
            with open(self.salt_file, 'rb') as f:
                salt = f.read()
            
            # キーを生成
            key = self._derive_key(password, salt)
            fernet = Fernet(key)
            
            # 暗号化ファイルを読み込み
            with open(self.config_file, 'rb') as f:
                encrypted_data = f.read()
            
            # 復号化
            decrypted_data = fernet.decrypt(encrypted_data)
            config_data = json.loads(decrypted_data.decode())
            
            return config_data
            
        except Exception as e:
            print(f"設定復号化エラー: {e}")
            return {}

class SecurityLogger:
    """セキュアなログ管理クラス"""
    
    def __init__(self, log_file="security.log"):
        self.log_file = log_file
        self._setup_log_file()
    
    def _setup_log_file(self):
        """ログファイルの権限を設定"""
        if not os.path.exists(self.log_file):
            with open(self.log_file, 'w') as f:
                f.write("")
        
        # ログファイルの権限を制限
        os.chmod(self.log_file, 0o600)
    
    def log_event(self, event_type: str, message: str, sensitive_data=False):
        """セキュリティイベントをログ記録"""
        from datetime import datetime
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 機密データの場合はハッシュ化
        if sensitive_data and isinstance(message, str):
            message_hash = hashlib.sha256(message.encode()).hexdigest()[:16]
            log_message = f"[{timestamp}] {event_type}: データハッシュ={message_hash}"
        else:
            log_message = f"[{timestamp}] {event_type}: {message}"
        
        try:
            with open(self.log_file, 'a') as f:
                f.write(log_message + "\n")
        except Exception as e:
            print(f"ログ記録エラー: {e}")

def validate_ip_address(ip: str) -> bool:
    """IPアドレスの妥当性をチェック"""
    import ipaddress
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False

def validate_email(email: str) -> bool:
    """メールアドレスの妥当性をチェック"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def secure_file_permissions(file_path: str):
    """ファイルの権限を安全に設定"""
    try:
        # 所有者のみ読み書き可能に設定
        os.chmod(file_path, 0o600)
        print(f"ファイル権限を設定しました: {file_path} (600)")
    except Exception as e:
        print(f"権限設定エラー: {e}")

def cleanup_sensitive_data():
    """メモリ上の機密データをクリア（Python GCに依存）"""
    import gc
    gc.collect()

if __name__ == "__main__":
    # セキュリティモジュールのテスト
    print("セキュリティモジュールのテスト")
    print("=" * 40)
    
    # IP検証テスト
    test_ips = ["192.168.1.100", "256.256.256.256", "localhost"]
    for ip in test_ips:
        result = validate_ip_address(ip)
        print(f"IP検証 {ip}: {'✅' if result else '❌'}")
    
    # メール検証テスト
    test_emails = ["test@example.com", "invalid-email", "user@domain.org"]
    for email in test_emails:
        result = validate_email(email)
        print(f"メール検証 {email}: {'✅' if result else '❌'}")
    
    print("\nセキュリティモジュール準備完了")
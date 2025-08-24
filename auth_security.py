#!/usr/bin/env python3
import os
import json
import time
import hashlib
import secrets
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
import base64

class SecureAuthManager:
    """Tapo認証のセキュリティ管理クラス"""
    
    def __init__(self, token_cache_file=".auth_cache.enc"):
        self.token_cache_file = token_cache_file
        self.max_retry_attempts = 3
        self.retry_delay = 5  # 秒
        self.token_expiry_hours = 2  # トークンの有効期限
        self.failed_attempts = {}  # IP別の失敗回数
        self.lockout_duration = 300  # 5分間のロックアウト
        
    def _generate_session_key(self) -> bytes:
        """セッション専用の暗号化キーを生成"""
        return Fernet.generate_key()
    
    def _encrypt_token_data(self, data: dict, key: bytes) -> bytes:
        """トークンデータを暗号化"""
        fernet = Fernet(key)
        json_data = json.dumps(data, ensure_ascii=False)
        return fernet.encrypt(json_data.encode())
    
    def _decrypt_token_data(self, encrypted_data: bytes, key: bytes) -> dict:
        """トークンデータを復号化"""
        try:
            fernet = Fernet(key)
            decrypted_data = fernet.decrypt(encrypted_data)
            return json.loads(decrypted_data.decode())
        except Exception:
            return {}
    
    def cache_auth_token(self, username: str, device_ip: str, token_data: dict):
        """認証トークンを一時キャッシュ（セキュア）"""
        try:
            # セッションキーを生成
            session_key = self._generate_session_key()
            
            # キャッシュデータを準備
            cache_data = {
                'username_hash': hashlib.sha256(username.encode()).hexdigest(),
                'device_ip_hash': hashlib.sha256(device_ip.encode()).hexdigest(),
                'token_data': token_data,
                'created_at': datetime.now().isoformat(),
                'expires_at': (datetime.now() + timedelta(hours=self.token_expiry_hours)).isoformat(),
                'session_id': secrets.token_hex(16)
            }
            
            # 暗号化して保存
            encrypted_data = self._encrypt_token_data(cache_data, session_key)
            
            with open(self.token_cache_file, 'wb') as f:
                # セッションキーと暗号化データを結合
                f.write(len(session_key).to_bytes(4, 'big'))
                f.write(session_key)
                f.write(encrypted_data)
            
            # ファイル権限を制限
            os.chmod(self.token_cache_file, 0o600)
            
            return True
            
        except Exception as e:
            print(f"トークンキャッシュエラー: {e}")
            return False
    
    def get_cached_auth_token(self, username: str, device_ip: str) -> dict:
        """キャッシュされた認証トークンを取得"""
        try:
            if not os.path.exists(self.token_cache_file):
                return {}
            
            with open(self.token_cache_file, 'rb') as f:
                # セッションキーを読み取り
                key_length = int.from_bytes(f.read(4), 'big')
                session_key = f.read(key_length)
                encrypted_data = f.read()
            
            # 復号化
            cache_data = self._decrypt_token_data(encrypted_data, session_key)
            
            if not cache_data:
                return {}
            
            # 有効期限チェック
            expires_at = datetime.fromisoformat(cache_data['expires_at'])
            if datetime.now() > expires_at:
                self.clear_auth_cache()
                return {}
            
            # ユーザー・デバイス照合
            username_hash = hashlib.sha256(username.encode()).hexdigest()
            device_ip_hash = hashlib.sha256(device_ip.encode()).hexdigest()
            
            if (cache_data.get('username_hash') == username_hash and 
                cache_data.get('device_ip_hash') == device_ip_hash):
                return cache_data.get('token_data', {})
            
            return {}
            
        except Exception as e:
            print(f"トークンキャッシュ読み取りエラー: {e}")
            return {}
    
    def clear_auth_cache(self):
        """認証キャッシュをクリア"""
        try:
            if os.path.exists(self.token_cache_file):
                os.remove(self.token_cache_file)
        except Exception as e:
            print(f"キャッシュクリアエラー: {e}")
    
    def record_auth_failure(self, device_ip: str):
        """認証失敗を記録（ブルートフォース対策）"""
        current_time = time.time()
        
        if device_ip not in self.failed_attempts:
            self.failed_attempts[device_ip] = {
                'count': 0,
                'last_attempt': current_time,
                'locked_until': 0
            }
        
        attempt_data = self.failed_attempts[device_ip]
        
        # 前回の失敗から時間が経過している場合はリセット
        if current_time - attempt_data['last_attempt'] > self.lockout_duration:
            attempt_data['count'] = 0
        
        attempt_data['count'] += 1
        attempt_data['last_attempt'] = current_time
        
        # 最大試行回数を超えた場合はロックアウト
        if attempt_data['count'] >= self.max_retry_attempts:
            attempt_data['locked_until'] = current_time + self.lockout_duration
            print(f"⚠️  IP {device_ip} を{self.lockout_duration}秒間ロックアウトしました")
    
    def is_ip_locked(self, device_ip: str) -> bool:
        """IPがロックアウト中かチェック"""
        if device_ip not in self.failed_attempts:
            return False
        
        attempt_data = self.failed_attempts[device_ip]
        current_time = time.time()
        
        if current_time < attempt_data.get('locked_until', 0):
            remaining = int(attempt_data['locked_until'] - current_time)
            print(f"⚠️  IP {device_ip} はロックアウト中です（残り{remaining}秒）")
            return True
        
        return False
    
    def record_auth_success(self, device_ip: str):
        """認証成功時に失敗記録をクリア"""
        if device_ip in self.failed_attempts:
            del self.failed_attempts[device_ip]
    
    def validate_network_security(self, device_ip: str) -> bool:
        """ネットワークセキュリティの検証"""
        import ipaddress
        
        try:
            ip = ipaddress.ip_address(device_ip)
            
            # プライベートIPアドレスのみ許可
            if not ip.is_private:
                print(f"⚠️  パブリックIP {device_ip} への接続は推奨されません")
                return False
            
            # ローカルループバックは除外
            if ip.is_loopback:
                print(f"⚠️  ループバックIP {device_ip} は無効です")
                return False
            
            return True
            
        except Exception as e:
            print(f"IP検証エラー: {e}")
            return False
    
    def secure_connection_params(self) -> dict:
        """セキュアな接続パラメータを返す"""
        return {
            'timeout': 10,  # 接続タイムアウト
            'verify_ssl': True,  # SSL証明書検証
            'max_retries': 1,  # 最大リトライ回数
        }
    
    def sanitize_auth_logs(self, log_message: str) -> str:
        """ログメッセージから機密情報を除去"""
        import re
        
        # パスワードパターンを検出して隠す
        patterns = [
            (r'password["\s]*[:=]["\s]*([^"\\s,}]+)', r'password: [REDACTED]'),
            (r'token["\s]*[:=]["\s]*([^"\\s,}]+)', r'token: [REDACTED]'),
            (r'auth["\s]*[:=]["\s]*([^"\\s,}]+)', r'auth: [REDACTED]'),
        ]
        
        sanitized = log_message
        for pattern, replacement in patterns:
            sanitized = re.sub(pattern, replacement, sanitized, flags=re.IGNORECASE)
        
        return sanitized

class SecureNetworkMonitor:
    """ネットワーク通信のセキュリティ監視"""
    
    def __init__(self):
        self.connection_history = []
        self.suspicious_patterns = []
    
    def log_connection_attempt(self, device_ip: str, success: bool, response_time: float):
        """接続試行をログ記録"""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'device_ip': device_ip,
            'success': success,
            'response_time': response_time
        }
        
        self.connection_history.append(entry)
        
        # 履歴を最新100件に制限
        if len(self.connection_history) > 100:
            self.connection_history = self.connection_history[-100:]
        
        # 疑わしいパターンの検出
        self._detect_suspicious_activity(device_ip, success, response_time)
    
    def _detect_suspicious_activity(self, device_ip: str, success: bool, response_time: float):
        """疑わしい活動の検出"""
        # 異常に遅い応答時間
        if response_time > 30:
            self.suspicious_patterns.append({
                'type': 'SLOW_RESPONSE',
                'device_ip': device_ip,
                'response_time': response_time,
                'timestamp': datetime.now().isoformat()
            })
        
        # 連続する失敗
        recent_failures = [
            entry for entry in self.connection_history[-10:]
            if entry['device_ip'] == device_ip and not entry['success']
        ]
        
        if len(recent_failures) >= 3:
            self.suspicious_patterns.append({
                'type': 'MULTIPLE_FAILURES',
                'device_ip': device_ip,
                'failure_count': len(recent_failures),
                'timestamp': datetime.now().isoformat()
            })
    
    def get_security_report(self) -> dict:
        """セキュリティレポートを生成"""
        total_connections = len(self.connection_history)
        successful_connections = sum(1 for entry in self.connection_history if entry['success'])
        
        return {
            'total_connections': total_connections,
            'successful_connections': successful_connections,
            'success_rate': successful_connections / total_connections if total_connections > 0 else 0,
            'suspicious_patterns': len(self.suspicious_patterns),
            'latest_suspicious': self.suspicious_patterns[-5:] if self.suspicious_patterns else []
        }

if __name__ == "__main__":
    # セキュリティモジュールのテスト
    print("認証セキュリティモジュールのテスト")
    print("=" * 40)
    
    auth_manager = SecureAuthManager()
    
    # トークンキャッシュテスト
    test_token = {'access_token': 'test_token_123', 'expires_in': 3600}
    if auth_manager.cache_auth_token('test@example.com', '192.168.1.100', test_token):
        print("✅ トークンキャッシュ成功")
        
        cached_token = auth_manager.get_cached_auth_token('test@example.com', '192.168.1.100')
        if cached_token == test_token:
            print("✅ トークン取得成功")
        else:
            print("❌ トークン取得失敗")
    
    # IPバリデーションテスト
    test_ips = ['192.168.1.100', '8.8.8.8', '127.0.0.1']
    for ip in test_ips:
        result = auth_manager.validate_network_security(ip)
        print(f"IP検証 {ip}: {'✅' if result else '❌'}")
    
    # クリーンアップ
    auth_manager.clear_auth_cache()
    print("\n認証セキュリティモジュール準備完了")
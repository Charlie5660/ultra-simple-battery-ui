# バッテリー充電制御アプリの設定ファイル
# 以下の値を実際の情報に変更してから使用してください

TAPO_SETTINGS = {
    "username": "",                    # Tapoアカウントのメールアドレス
    "password": "",                    # Tapoアカウントのパスワード  
    "device_ip": "",                   # Tapo P110MのIPアドレス (例: "192.168.0.220")
}

CHARGE_SETTINGS = {
    "start_threshold": 30,     # 充電開始閾値 (%)
    "stop_threshold": 78,      # 充電停止閾値 (%)
    "check_interval": 300,     # チェック間隔 (秒) - 本格運用用5分間隔
}

OTHER_SETTINGS = {
    "debug_mode": False,       # デバッグモード - 本格運用ではOFF
    "simulation_mode": False,  # 実機テスト時はFalseに変更
}

# 暗号化パスワード（8文字以上の強力なパスワードを設定）
ENCRYPTION_PASSWORD = ""

# 使用方法:
# 1. TAPO_SETTINGSの値を実際のTapo認証情報に変更
# 2. simulation_modeをFalseに変更（実機テスト時）
# 3. ENCRYPTION_PASSWORDを設定（セキュア版使用時）
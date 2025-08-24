# セキュア設定作成用テンプレート
# 以下の値を実際の情報に変更してから使用してください

TAPO_SETTINGS = {
    "username": "your_tapo_email@example.com",     # ferrari.2020.ty@gmail.com
    "password": "your_tapo_password",              # ty5622Tp
    "device_ip": "192.168.0.220",                  # 192.168.0.220
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
ENCRYPTION_PASSWORD = "your_strong_password_here" # ty5622Mj@24

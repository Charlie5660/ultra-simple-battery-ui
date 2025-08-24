# バッテリー充電制御アプリ

Tapo P110Mを使ってMacBookのバッテリー充電を自動制御するPythonアプリです。

## 機能

- バッテリー残量が30%以下になったら充電開始
- バッテリー残量が78%以上になったら充電停止
- バックグラウンドで常時監視
- Tapo P110Mスマートプラグによる充電器制御

## 必要な環境

- macOS
- Python 3.7以上
- Tapo P110Mスマートプラグ
- MacBookの充電器

## セットアップ手順

### 1. Pythonライブラリのインストール

```bash
pip install tapo
```

### 2. Tapo P110Mの設定

1. Tapoアプリでデバイスをセットアップ
2. デバイスのIPアドレスを確認
3. `config.py`ファイルを編集

### 3. 設定ファイルの編集

`config.py`を開いて以下の情報を入力：

```python
TAPO_USERNAME = "your_email@example.com"  # Tapoアカウントのメールアドレス
TAPO_PASSWORD = "your_password"           # Tapoアカウントのパスワード
DEVICE_IP = "192.168.1.100"              # Tapo P110MのIPアドレス

# 必要に応じて閾値も変更可能
CHARGE_START_THRESHOLD = 30  # 充電開始の閾値（%）
CHARGE_STOP_THRESHOLD = 78   # 充電停止の閾値（%）
```

### 4. ハードウェア接続

1. MacBookの充電器をTapo P110Mに接続
2. Tapo P110Mをコンセントに接続
3. MacBookにUSB-Cケーブルを接続

## 使用方法

### テスト実行

```bash
python3 battery_charge_controller.py
```

### バックグラウンド実行

```bash
./start_battery_control.sh
```

### 停止

```bash
./stop_battery_control.sh
```

### ログ確認

```bash
tail -f battery_control.log
```

## ファイル構成

- `battery_charge_controller.py` - メインアプリケーション
- `config.py` - 設定ファイル
- `battery_monitor.py` - 基本的なバッテリー監視機能
- `start_battery_control.sh` - バックグラウンド起動スクリプト
- `stop_battery_control.sh` - 停止スクリプト
- `battery_control.log` - ログファイル（実行時に生成）
- `battery_control.pid` - プロセスIDファイル（実行時に生成）

## トラブルシューティング

### Tapoライブラリのエラー

```bash
pip install --upgrade tapo
```

### デバイス接続エラー

- Tapo P110MのIPアドレスを確認
- Wi-Fi接続を確認
- Tapoアプリでデバイスが正常に動作することを確認

### バッテリー情報取得エラー

- macOSの電源管理設定を確認
- ターミナルで `pmset -g batt` が動作することを確認

## 安全に関する注意

- 初回は必ずテスト実行で動作を確認してください
- バッテリーの健康状態を定期的に確認してください
- 異常を感じた場合は即座に使用を停止してください

## カスタマイズ

`config.py`で以下の設定を変更できます：

- `CHARGE_START_THRESHOLD`: 充電開始の閾値
- `CHARGE_STOP_THRESHOLD`: 充電停止の閾値
- `CHECK_INTERVAL`: バッテリーチェックの間隔（秒）
- `SIMULATION_MODE`: シミュレーションモード（True/False）

## ライセンス

このソフトウェアは教育・個人使用目的で提供されています。使用は自己責任でお願いします。
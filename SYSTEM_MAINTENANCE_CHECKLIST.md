# ✅ System Maintenance Checklist - 安定動作維持のためのチェック項目

> **作成日**: 2025年8月24日  
> **実行頻度**: 毎週推奨  
> **目的**: Ultra Simple UIの安定動作維持・問題早期発見

---

## 📋 週次ヘルスチェック項目

### **🔍 1. システムリソース監視**

#### **CPU使用率チェック**
```bash
ps aux | sort -nr -k 3 | head -10
```
**正常基準**: 
- ✅ Ultra Simple UI: 0.0-0.1% CPU
- ⚠️ 80%超過プロセスがある場合は要調査

#### **メモリ使用量チェック** 
```bash
ps aux | sort -nr -k 4 | head -10
```
**正常基準**:
- ✅ Ultra Simple UI: 100-150MB
- ⚠️ 5GB超過プロセスがある場合は要調査

### **🔋 2. Ultra Simple UI動作確認**

#### **プロセス生存確認**
```bash
ps aux | grep ultra_simple_ui | grep -v grep
```
**期待結果**: PID表示、CPU 0.0%, 継続稼働時間

#### **設定値確認**
```bash
grep -n "120000\|auto_mode = True" ultra_simple_ui.py
```
**期待結果**: 
- 120秒間隔設定
- 自動制御デフォルトON

### **🔋 3. バッテリー・充電確認**

#### **バッテリー状況**
```bash
pmset -g batt
```
**正常パターン**:
- ✅ 30%以下: 充電中
- ✅ 78%以上: 放電中
- ✅ 30-78%: どちらでも正常

#### **Tapo接続確認**
```bash
ping -c 2 192.168.0.220
```
**期待結果**: 2パケット受信、応答時間30ms以下

---

## 🚨 異常検知・対応手順

### **異常CPU使用プロセス発見時**

#### **対応手順**:
1. **プロセス特定**: `ps aux | awk '$3 > 80.0 {print $2, $11, $3"%"}'`
2. **プロセス詳細確認**: `ps -p [PID] -o pid,etime,pcpu,pmem,comm`
3. **安全停止**: `kill -TERM [PID]`
4. **強制停止（必要時）**: `kill -KILL [PID]`
5. **原因調査**: ログ確認・再発防止策検討

### **Ultra Simple UI停止発見時**

#### **対応手順**:
1. **再起動**: `python3 ultra_simple_ui.py &`
2. **設定確認**: config.py、Tapo接続確認
3. **ログ確認**: エラーメッセージの確認
4. **必要時**: Git履歴からの復旧 `git checkout [commit-hash] ultra_simple_ui.py`

### **バッテリー制御異常時**

#### **対応手順**:
1. **手動制御テスト**: UIボタンでの充電開始/停止確認
2. **Tapo接続確認**: ping、デバイス電源状態確認
3. **設定リセット**: config.pyの再確認
4. **緊急時**: ACアダプター直接接続

---

## 🛠️ 定期メンテナンス作業

### **毎週実施**

#### **1. システムクリーンアップ**
```bash
# 一時ファイル削除
find /var/folders -name "*python*" -mtime +7 -exec rm -rf {} \; 2>/dev/null

# ログローテーション
if [ -f ~/battery_monitor.log ] && [ $(wc -l < ~/battery_monitor.log) -gt 1000 ]; then
    tail -500 ~/battery_monitor.log > ~/battery_monitor.log.tmp
    mv ~/battery_monitor.log.tmp ~/battery_monitor.log
fi
```

#### **2. 設定バックアップ**
```bash
cp config.py config.py.backup.$(date +%Y%m%d)
cp -r BatteryChargeControl.app BatteryChargeControl.app.backup.$(date +%Y%m%d)
```

### **毎月実施**

#### **3. バッテリー健康度チェック**
```bash
# バッテリー詳細情報
system_profiler SPPowerDataType | grep -E "(Cycle Count|Condition)"

# 容量確認
ioreg -l | grep -E "(MaxCapacity|CurrentCapacity)"
```

#### **4. 長期間動作プロセス確認**
```bash
ps -eo pid,etime,comm | sort -k2 -r | head -20
```

---

## 📊 正常動作の基準値

### **Ultra Simple UI**
- **CPU使用率**: 0.0-0.1%
- **メモリ使用量**: 100-150MB  
- **稼働時間**: 連続動作可能
- **監視間隔**: 120秒

### **システム全体**
- **CPU使用率**: 50%以下（通常時）
- **メモリ使用**: 80%以下
- **ディスク使用**: 90%以下
- **バッテリー範囲**: 30-78%で適切制御

### **ネットワーク**
- **Tapo応答**: 30ms以下
- **パケット損失**: 0%
- **接続安定性**: 継続接続可能

---

## 🔄 自動監視スクリプト（オプション）

### **battery_health_check.sh**
```bash
#!/bin/bash
# 自動ヘルスチェックスクリプト

LOG_FILE="$HOME/battery_monitor.log"
DATE=$(date '+%Y-%m-%d %H:%M:%S')

echo "[$DATE] Battery Health Check Start" >> $LOG_FILE

# Ultra Simple UI生存確認
if pgrep -f ultra_simple_ui.py > /dev/null; then
    CPU=$(ps aux | grep ultra_simple_ui | grep -v grep | awk '{print $3}')
    echo "[$DATE] Ultra Simple UI: Running (CPU: ${CPU}%)" >> $LOG_FILE
else
    echo "[$DATE] WARNING: Ultra Simple UI not running" >> $LOG_FILE
fi

# 異常CPU使用確認
HIGH_CPU=$(ps aux | awk '$3 > 80.0 && $11 !~ /WindowServer/ {print $2, $11, $3"%"}')
if [ ! -z "$HIGH_CPU" ]; then
    echo "[$DATE] WARNING: High CPU usage: $HIGH_CPU" >> $LOG_FILE
fi

# バッテリー状況
BATTERY=$(pmset -g batt | grep -o '[0-9]*%' | head -1)
echo "[$DATE] Battery Level: $BATTERY" >> $LOG_FILE

echo "[$DATE] Battery Health Check Complete" >> $LOG_FILE
```

### **cron設定（オプション）**
```bash
# 毎時間実行
0 * * * * ~/battery_health_check.sh

# 毎日午前9時に詳細チェック
0 9 * * * ~/detailed_health_check.sh
```

---

## ✅ 今回の確認結果（2025年8月24日 14:17）

### **✅ システム状況**
- **Ultra Simple UI**: 正常動作中（33分30秒稼働）
- **CPU使用率**: 0.0%（効率的）
- **メモリ使用**: 109MB（適正）
- **バッテリー**: 19%充電中（正常制御）

### **✅ 設定状況**  
- **監視間隔**: 120秒（最適化済み）
- **自動制御**: デフォルトON（バグ修正済み）
- **Tapo接続**: 正常（14.3ms平均応答）

### **✅ システム健全性**
- **異常CPU使用**: なし
- **異常メモリ使用**: なし  
- **ディスク使用**: 4%（健全）
- **ネットワーク**: 安定

---

## 🎯 維持すべき重要ポイント

### **1. 現在の設定を変更しない**
- ✅ 120秒監視間隔
- ✅ auto_mode = True
- ✅ 30%/78%閾値

### **2. 定期的な確認を怠らない**
- 📅 週1回のヘルスチェック
- 🔍 異常プロセスの早期発見
- 💾 設定ファイルのバックアップ

### **3. 問題発生時の迅速対応**
- 🚨 異常CPU使用の即座停止
- 🔄 Ultra Simple UI再起動手順
- ⚡ 緊急時のACアダプター直接接続

---

**🔋⚡ System Maintenance - Stable Operation Guaranteed ⚡🔋**

*現在完璧動作中 → 定期確認で継続安定 → 長期間安心使用*

**Status**: 🎊 **PERFECTLY STABLE & MAINTAINED** 🎊
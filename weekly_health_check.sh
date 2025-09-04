#!/bin/bash
# 週1回の包括的システムヘルスチェック

LOG_FILE="$HOME/weekly_battery_check.log"
DATE=$(date '+%Y-%m-%d %H:%M:%S')

echo "========================================" >> $LOG_FILE
echo "[$DATE] Weekly Battery System Health Check" >> $LOG_FILE
echo "========================================" >> $LOG_FILE

# 1. システム稼働時間
UPTIME=$(uptime | awk '{print $3,$4}' | sed 's/,//')
echo "System Uptime: $UPTIME" >> $LOG_FILE

# 2. Ultra Simple UI稼働状況
UI_PID=$(pgrep -f ultra_simple_ui.py)
if [ ! -z "$UI_PID" ]; then
    ELAPSED=$(ps -p $UI_PID -o etime= | tr -d ' ')
    CPU=$(ps -p $UI_PID -o %cpu= | tr -d ' ')
    MEM=$(ps -p $UI_PID -o %mem= | tr -d ' ')
    echo "Ultra Simple UI: Running (PID: $UI_PID, Elapsed: $ELAPSED, CPU: $CPU%, MEM: $MEM%)" >> $LOG_FILE
else
    echo "Ultra Simple UI: NOT RUNNING - RESTARTING..." >> $LOG_FILE
    cd /Users/$(whoami)/battery_charge_app
    python3 ultra_simple_ui.py &
    echo "Ultra Simple UI: Restarted" >> $LOG_FILE
fi

# 3. バッテリー詳細情報
echo "--- Battery Information ---" >> $LOG_FILE
pmset -g batt >> $LOG_FILE

# 4. バッテリー健康度
echo "--- Battery Health ---" >> $LOG_FILE
system_profiler SPPowerDataType | grep -E "(Cycle Count|Condition|Full Charge Capacity)" >> $LOG_FILE

# 5. 長時間動作プロセス（24時間以上）
echo "--- Long Running Processes (24h+) ---" >> $LOG_FILE
ps -eo pid,etime,comm | awk '$2 ~ /-/ || ($2 ~ /:/ && $2 !~ /^[0-9][0-9]?:/)' | head -10 >> $LOG_FILE

# 6. ディスク使用量
echo "--- Disk Usage ---" >> $LOG_FILE
df -h / >> $LOG_FILE

# 7. メモリ使用量
echo "--- Memory Usage ---" >> $LOG_FILE
vm_stat | grep -E "(Pages free|Pages active|Pages inactive)" >> $LOG_FILE

# 8. Tapo接続テスト
echo "--- Tapo P110M Connection ---" >> $LOG_FILE
if ping -c 3 192.168.0.220 >/dev/null 2>&1; then
    echo "Tapo P110M: Connection OK" >> $LOG_FILE
    # 接続時間測定
    PING_TIME=$(ping -c 1 192.168.0.220 | grep "time=" | awk -F'time=' '{print $2}' | awk '{print $1}')
    echo "Response time: ${PING_TIME}" >> $LOG_FILE
else
    echo "Tapo P110M: Connection FAILED" >> $LOG_FILE
fi

# 9. 設定ファイルバックアップ
echo "--- Configuration Backup ---" >> $LOG_FILE
if [ -f /Users/$(whoami)/battery_charge_app/config.py ]; then
    BACKUP_FILE="/Users/$(whoami)/battery_charge_app/config.py.backup.$(date +%Y%m%d)"
    cp /Users/$(whoami)/battery_charge_app/config.py "$BACKUP_FILE"
    echo "Config backup created: $BACKUP_FILE" >> $LOG_FILE
fi

# 10. ログファイルローテーション
LOG_SIZE=$(wc -l < "$LOG_FILE")
if [ "$LOG_SIZE" -gt 1000 ]; then
    tail -500 "$LOG_FILE" > "$LOG_FILE.tmp"
    mv "$LOG_FILE.tmp" "$LOG_FILE"
    echo "Log rotated (kept last 500 lines)" >> $LOG_FILE
fi

echo "[$DATE] Weekly Health Check Completed" >> $LOG_FILE
echo "" >> $LOG_FILE
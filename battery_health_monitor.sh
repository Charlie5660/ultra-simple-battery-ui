#!/bin/bash
# バッテリー健全性監視スクリプト
# 自動実行・問題検知・復旧機能

LOG_FILE="$HOME/battery_monitor.log"
PID_FILE="$HOME/.battery_ui.pid"
DATE=$(date '+%Y-%m-%d %H:%M:%S')

echo "[$DATE] Battery Health Monitor - Start Check" >> $LOG_FILE

# 1. Ultra Simple UI プロセス確認
UI_PID=$(pgrep -f ultra_simple_ui.py)
if [ ! -z "$UI_PID" ]; then
    # プロセス生存確認
    ELAPSED=$(ps -p $UI_PID -o etime= | tr -d ' ')
    CPU=$(ps -p $UI_PID -o %cpu= | tr -d ' ')
    echo "[$DATE] Ultra Simple UI: Running (PID: $UI_PID, Elapsed: $ELAPSED, CPU: $CPU%)" >> $LOG_FILE
    
    # 異常な長時間動作検知（12時間以上）
    # macOSでは etimes の代わりに etime を解析
    if echo "$ELAPSED" | grep -q "-"; then
        # 日単位の場合（例: "1-02:30:45"）
        DAYS=$(echo "$ELAPSED" | cut -d- -f1)
        if [ "$DAYS" -ge 1 ]; then
            echo "[$DATE] WARNING: Ultra Simple UI running too long ($ELAPSED)" >> $LOG_FILE
            echo "[$DATE] ACTION: Restarting Ultra Simple UI" >> $LOG_FILE
            
            # 古いプロセス停止
            kill $UI_PID
            sleep 3
            
            # 新しいプロセス開始
            cd /Users/yamakawadaiki/battery_charge_app
            python3 ultra_simple_ui.py &
            NEW_PID=$!
            echo $NEW_PID > $PID_FILE
            echo "[$DATE] Ultra Simple UI restarted (New PID: $NEW_PID)" >> $LOG_FILE
        fi
    elif echo "$ELAPSED" | grep -E "^[0-9]{2}:" >/dev/null; then
        # 時間単位の場合（例: "15:30:45"）- 12時間以上の場合
        HOURS=$(echo "$ELAPSED" | cut -d: -f1)
        if [ "$HOURS" -ge 12 ]; then
            echo "[$DATE] WARNING: Ultra Simple UI running too long ($ELAPSED)" >> $LOG_FILE
            echo "[$DATE] ACTION: Restarting Ultra Simple UI" >> $LOG_FILE
            
            # 古いプロセス停止
            kill $UI_PID
            sleep 3
            
            # 新しいプロセス開始
            cd /Users/yamakawadaiki/battery_charge_app
            python3 ultra_simple_ui.py &
            NEW_PID=$!
            echo $NEW_PID > $PID_FILE
            echo "[$DATE] Ultra Simple UI restarted (New PID: $NEW_PID)" >> $LOG_FILE
        fi
    fi
else
    echo "[$DATE] ERROR: Ultra Simple UI not running" >> $LOG_FILE
    echo "[$DATE] ACTION: Starting Ultra Simple UI" >> $LOG_FILE
    
    # Ultra Simple UI 開始
    cd /Users/yamakawadaiki/battery_charge_app
    python3 ultra_simple_ui.py &
    NEW_PID=$!
    echo $NEW_PID > $PID_FILE
    echo "[$DATE] Ultra Simple UI started (PID: $NEW_PID)" >> $LOG_FILE
fi

# 2. バッテリー状況確認
BATTERY_INFO=$(pmset -g batt)
BATTERY_PERCENT=$(echo "$BATTERY_INFO" | grep -o '[0-9]*%' | head -1 | tr -d '%')
IS_CHARGING=$(echo "$BATTERY_INFO" | grep -q "charging" && echo "yes" || echo "no")

echo "[$DATE] Battery: $BATTERY_PERCENT%, Charging: $IS_CHARGING" >> $LOG_FILE

# 3. 緊急バッテリー警告（5%以下）
if [ "$BATTERY_PERCENT" -le 5 ] && [ "$IS_CHARGING" = "no" ]; then
    echo "[$DATE] CRITICAL: Battery at $BATTERY_PERCENT% and not charging!" >> $LOG_FILE
    # システム通知
    osascript -e "display notification \"バッテリー危険レベル: $BATTERY_PERCENT%\" with title \"緊急警告\""
fi

# 4. 異常CPU使用確認
HIGH_CPU_PROCESSES=$(ps aux | awk '$3 > 80.0 && $11 !~ /WindowServer|kernel_task/ {print $2, $11, $3"%"}')
if [ ! -z "$HIGH_CPU_PROCESSES" ]; then
    echo "[$DATE] WARNING: High CPU usage detected:" >> $LOG_FILE
    echo "$HIGH_CPU_PROCESSES" >> $LOG_FILE
fi

# 5. Tapo接続確認
if ping -c 1 192.168.0.220 >/dev/null 2>&1; then
    echo "[$DATE] Tapo P110M: Connection OK" >> $LOG_FILE
else
    echo "[$DATE] WARNING: Tapo P110M connection failed" >> $LOG_FILE
fi

echo "[$DATE] Battery Health Monitor - Check Complete" >> $LOG_FILE
echo "" >> $LOG_FILE
#!/bin/bash
# Cron監視システム設定スクリプト

echo "🛡️ バッテリー監視システム - Cron設定"

# 現在のcronジョブ確認
echo "現在のcronジョブ："
crontab -l 2>/dev/null || echo "cronジョブは設定されていません"

# 新しいcronジョブ設定
echo ""
echo "推奨するcronジョブ設定："
echo "# バッテリーヘルスチェック（30分毎）"
echo "*/30 * * * * /Users/yamakawadaiki/battery_charge_app/battery_health_monitor.sh"
echo ""
echo "# 週1回の完全システムヘルスチェック（日曜日 午前9時）"
echo "0 9 * * 0 /Users/yamakawadaiki/battery_charge_app/weekly_health_check.sh"

# cron設定ファイル作成
CRON_FILE="/tmp/battery_cron"
cat > $CRON_FILE << 'EOF'
# Battery Management System - Automated Monitoring
# 30分毎のヘルスチェック
*/30 * * * * /Users/yamakawadaiki/battery_charge_app/battery_health_monitor.sh

# 週1回の完全チェック
0 9 * * 0 /Users/yamakawadaiki/battery_charge_app/weekly_health_check.sh
EOF

echo ""
echo "設定ファイルが作成されました: $CRON_FILE"
echo ""
echo "実行する場合："
echo "  crontab $CRON_FILE"
echo ""
echo "設定確認："
echo "  crontab -l"
echo ""
echo "無効化する場合："
echo "  crontab -r"
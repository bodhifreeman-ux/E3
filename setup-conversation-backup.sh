#!/bin/bash

# Setup Automated Claude Conversation Backups
# Configures daily backups via cron

set -e

SCRIPT_DIR="/home/bodhifreeman/E3/E3"
BACKUP_SCRIPT="$SCRIPT_DIR/backup-claude-conversations.sh"

echo "=== Claude Conversation Backup Setup ==="
echo ""

# Check if backup script exists
if [ ! -f "$BACKUP_SCRIPT" ]; then
    echo "❌ Error: Backup script not found at $BACKUP_SCRIPT"
    exit 1
fi

# Make sure script is executable
chmod +x "$BACKUP_SCRIPT"
echo "✓ Backup script is executable"

# Test run the backup
echo ""
echo "🧪 Testing backup script..."
"$BACKUP_SCRIPT"

# Setup cron job
echo ""
echo "⏰ Setting up automated daily backups..."

# Cron job: Run daily at 2 AM
CRON_JOB="0 2 * * * $BACKUP_SCRIPT >> /var/log/claude-backup.log 2>&1"

# Check if cron job already exists
if crontab -l 2>/dev/null | grep -q "$BACKUP_SCRIPT"; then
    echo "⚠ Cron job already exists, skipping..."
else
    # Add cron job
    (crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -
    echo "✓ Cron job added: Daily backup at 2:00 AM"
fi

echo ""
echo "=== Setup Complete ==="
echo ""
echo "📅 Automated backup schedule: Daily at 2:00 AM"
echo "📂 Backup location: /home/bodhifreeman/E3/E3/conversation-history/"
echo "📜 Log file: /var/log/claude-backup.log"
echo ""
echo "To run backup manually:"
echo "  $BACKUP_SCRIPT"
echo ""
echo "To view cron schedule:"
echo "  crontab -l"
echo ""
echo "To view backup logs:"
echo "  tail -f /var/log/claude-backup.log"

# Claude Code Conversation History System

A comprehensive backup system for preserving all Claude Code conversations.

## Overview

This system automatically backs up all Claude Code conversation histories, ensuring you never lose valuable discussions, code examples, or decisions made during development sessions.

## Features

- ✅ **Automated Daily Backups** - Runs at 2 AM every day
- ✅ **Auto-Generated Summaries** - Automatically creates summaries when conversations are compacted
- ✅ **Manual Summary Creation** - Save important conversation summaries with your notes
- ✅ **Timestamped Archives** - Each backup is dated for easy reference
- ✅ **Smart Cleanup** - Automatically removes backups older than 30 days
- ✅ **Manual Backup Support** - Run backups anytime
- ✅ **Session Extraction** - Latest sessions copied to readable format
- ✅ **Compression** - Efficient tar.gz compression
- ✅ **Searchable Index** - All summaries indexed for easy browsing

## Quick Start

### Initial Setup

```bash
# Run the setup script (one-time)
./setup-conversation-backup.sh
```

This will:
1. Test the backup system
2. Create the backup directory structure
3. Set up daily automated backups via cron

### Manual Backup

```bash
# Run a backup anytime
./backup-claude-conversations.sh
```

## Directory Structure

```
conversation-history/
├── backups/                        # Compressed backup archives
│   ├── claude-cache_20260105_140530.tar.gz
│   └── claude-cache_20260104_020000.tar.gz
├── sessions/                       # Latest session data (readable)
│   └── [current session files]
├── summaries/                      # Conversation summaries
│   ├── INDEX.md                    # Searchable index of all summaries
│   ├── auto-generated/             # Auto-created snapshots
│   │   └── auto_summary_*.md
│   └── [manual summaries].md       # Your detailed summaries
└── MANIFEST.txt                    # Backup inventory
```

## Backup Locations

The script searches for and backs up Claude data from:

- `~/.claude/` - Main Claude cache directory
- `~/.config/claude/` - Configuration files
- `~/.local/share/claude/` - Application data
- `~/.cache/claude/` - Cache data
- `/tmp/claude-*` - Temporary session data

## Creating Conversation Summaries

### Manual Summary (Recommended for Important Conversations)

When you reach a good stopping point or before compacting a long conversation:

```bash
./save-conversation-summary.sh
```

This will:
1. Prompt you for a title
2. Open an editor with a summary template
3. Save your notes about key topics, decisions, and action items
4. Add the summary to the searchable index

### Auto-Generated Summaries

Summaries are automatically created:
- During each backup (daily at 2 AM)
- When you manually run `./backup-claude-conversations.sh`

Auto-summaries include:
- Timestamp and session info
- Recent commands executed
- Recently modified files
- Git status and recent commits
- Context snapshot for quick reference

### View All Summaries

```bash
# View the index
cat conversation-history/summaries/INDEX.md

# List all summaries
ls -lt conversation-history/summaries/

# Search summaries
grep -r "topic" conversation-history/summaries/
```

## Viewing Conversation History

### Option 1: Browse Session Files

```bash
cd /home/bodhifreeman/E3/E3/conversation-history/sessions/
ls -la
# Open and read individual session files
```

### Option 2: Extract Specific Backup

```bash
cd /home/bodhifreeman/E3/E3/conversation-history/backups/

# List available backups
ls -lh

# Extract a specific backup
tar -xzf claude-cache_20260105_140530.tar.gz

# View contents
cd .claude/
ls -la
```

### Option 3: Search All Conversations

```bash
# Search all backups for a specific term
cd /home/bodhifreeman/E3/E3/conversation-history/backups/
for backup in *.tar.gz; do
    echo "Searching $backup..."
    tar -xzf "$backup" -O 2>/dev/null | grep -i "your search term" && echo "Found in: $backup"
done
```

## Restoring Conversations

### Restore Latest Backup

```bash
cd /home/bodhifreeman/E3/E3/conversation-history/backups/

# Find latest backup
LATEST=$(ls -t *.tar.gz | head -1)

# Extract to Claude directory
tar -xzf "$LATEST" -C ~/
```

### Restore Specific Date

```bash
# Extract backup from specific date
tar -xzf claude-cache_20260105_140530.tar.gz -C ~/
```

## Automation Details

### Cron Schedule

```bash
# View current cron jobs
crontab -l

# Expected output:
0 2 * * * /home/bodhifreeman/E3/E3/backup-claude-conversations.sh >> /var/log/claude-backup.log 2>&1
```

### Log Monitoring

```bash
# View backup logs
tail -f /var/log/claude-backup.log

# View recent backups
tail -100 /var/log/claude-backup.log
```

## Advanced Usage

### Export Conversations to Text

```bash
# Create a simple script to export all conversations
#!/bin/bash
EXPORT_DIR="claude-conversations-export-$(date +%Y%m%d)"
mkdir -p "$EXPORT_DIR"

cd /home/bodhifreeman/E3/E3/conversation-history/sessions/
for file in *; do
    if [ -f "$file" ]; then
        cat "$file" > "$EXPORT_DIR/$file.txt"
    fi
done

echo "Exported to: $EXPORT_DIR"
```

### Sync to Remote Backup

```bash
# Add to cron for remote backup (e.g., to another server)
rsync -avz /home/bodhifreeman/E3/E3/conversation-history/ \
    user@backup-server:/backups/claude-conversations/
```

### Search Across All History

```bash
# Create a search utility
#!/bin/bash
SEARCH_TERM="$1"

if [ -z "$SEARCH_TERM" ]; then
    echo "Usage: $0 <search-term>"
    exit 1
fi

echo "Searching all Claude conversations for: $SEARCH_TERM"
echo "========================================"

cd /home/bodhifreeman/E3/E3/conversation-history/backups/
for backup in *.tar.gz; do
    if tar -xzf "$backup" -O 2>/dev/null | grep -qi "$SEARCH_TERM"; then
        echo "✓ Found in: $backup"
        echo "  Date: $(echo $backup | grep -oP '\d{8}_\d{6}')"
    fi
done
```

## Maintenance

### Manual Cleanup

```bash
# Remove backups older than 30 days
find /home/bodhifreeman/E3/E3/conversation-history/backups/ \
    -name "*.tar.gz" -mtime +30 -delete

# Remove backups older than 7 days (more aggressive)
find /home/bodhifreeman/E3/E3/conversation-history/backups/ \
    -name "*.tar.gz" -mtime +7 -delete
```

### Disable Automated Backups

```bash
# Remove cron job
crontab -l | grep -v "backup-claude-conversations.sh" | crontab -
```

### Re-enable Automated Backups

```bash
# Run setup script again
./setup-conversation-backup.sh
```

## Troubleshooting

### No Backups Created

```bash
# Check if Claude cache exists
ls -la ~/.claude/

# Run backup script with verbose output
bash -x ./backup-claude-conversations.sh
```

### Cron Job Not Running

```bash
# Check cron service status
systemctl status cron

# Verify cron job exists
crontab -l | grep claude

# Check system logs
grep -i cron /var/log/syslog
```

### Backup Size Too Large

```bash
# Check backup sizes
du -sh /home/bodhifreeman/E3/E3/conversation-history/backups/*

# Manually cleanup large/old backups
cd /home/bodhifreeman/E3/E3/conversation-history/backups/
ls -lhS  # Sort by size
rm <large-backup-file>.tar.gz
```

## Best Practices

1. **Regular Verification** - Periodically verify backups are working:
   ```bash
   ./backup-claude-conversations.sh
   ```

2. **Off-site Backup** - Consider syncing to cloud storage or remote server

3. **Version Control** - Keep important conversations in git repositories

4. **Documentation** - Document important decisions from conversations in project docs

5. **Security** - Conversation history may contain sensitive data:
   ```bash
   # Encrypt backups
   tar -czf - conversation-history/ | gpg -c > conversations-encrypted.tar.gz.gpg
   ```

## Integration with E3

This conversation backup system is integrated into the E3 project:

```
E3/
├── backup-claude-conversations.sh    # Main backup script
├── setup-conversation-backup.sh      # Setup automation
├── CONVERSATION-HISTORY.md           # This documentation
└── conversation-history/             # Backup storage
    ├── backups/                      # Compressed archives
    ├── sessions/                     # Latest sessions
    └── MANIFEST.txt                  # Inventory
```

## Support

For issues or questions:
- Check logs: `tail -f /var/log/claude-backup.log`
- Verify cron: `crontab -l`
- Manual run: `./backup-claude-conversations.sh`

---

**Never lose a valuable conversation again!**

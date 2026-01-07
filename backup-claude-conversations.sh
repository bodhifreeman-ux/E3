#!/bin/bash

# Backup Claude Code Conversation History
# This script backs up all Claude Code conversation histories to a centralized location

set -e

# Configuration
BACKUP_DIR="/home/bodhifreeman/E3/conversation-history"
CLAUDE_CACHE_DIR="/home/bodhifreeman/.claude"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

# Create backup directory structure
mkdir -p "$BACKUP_DIR/backups"
mkdir -p "$BACKUP_DIR/sessions"

echo "=== Claude Code Conversation History Backup ==="
echo "Timestamp: $(date)"
echo "Backup Directory: $BACKUP_DIR"
echo ""

# Function to backup conversation data
backup_conversations() {
    local source_dir="$1"
    local backup_name="$2"

    if [ -d "$source_dir" ]; then
        echo "📦 Backing up: $backup_name"

        # Create timestamped backup
        local backup_file="$BACKUP_DIR/backups/${backup_name}_${TIMESTAMP}.tar.gz"
        tar -czf "$backup_file" -C "$(dirname "$source_dir")" "$(basename "$source_dir")" 2>/dev/null || true

        if [ -f "$backup_file" ]; then
            local size=$(du -h "$backup_file" | cut -f1)
            echo "   ✓ Backed up: $size - $backup_file"
            return 0
        else
            echo "   ⚠ No data found in $source_dir"
            return 1
        fi
    else
        echo "   ⚠ Directory not found: $source_dir"
        return 1
    fi
}

# Backup main Claude cache directory
if [ -d "$CLAUDE_CACHE_DIR" ]; then
    echo "🔍 Found Claude cache directory: $CLAUDE_CACHE_DIR"
    backup_conversations "$CLAUDE_CACHE_DIR" "claude-cache"

    # Copy latest session data to readable format
    if [ -d "$CLAUDE_CACHE_DIR" ]; then
        cp -r "$CLAUDE_CACHE_DIR"/* "$BACKUP_DIR/sessions/" 2>/dev/null || true
        echo "   ✓ Copied latest sessions to: $BACKUP_DIR/sessions/"
    fi
else
    echo "⚠ Claude cache directory not found: $CLAUDE_CACHE_DIR"
    echo "   Searching for alternative locations..."
fi

# Search for other possible Claude data locations
SEARCH_PATHS=(
    "$HOME/.config/claude"
    "$HOME/.local/share/claude"
    "$HOME/.cache/claude"
    "/tmp/claude-*"
)

for path in "${SEARCH_PATHS[@]}"; do
    if [ -d "$path" ] || ls $path 1> /dev/null 2>&1; then
        echo "🔍 Found additional Claude data: $path"
        backup_name=$(basename "$path" | tr '/' '_')
        backup_conversations "$path" "$backup_name"
    fi
done

# Create a manifest file
MANIFEST="$BACKUP_DIR/MANIFEST.txt"
cat > "$MANIFEST" << EOF
Claude Code Conversation History Backup
========================================
Backup Date: $(date)
Backup Location: $BACKUP_DIR

Contents:
---------
EOF

ls -lh "$BACKUP_DIR/backups/" >> "$MANIFEST" 2>/dev/null || echo "No backups created" >> "$MANIFEST"

echo ""
echo "=== Backup Complete ==="
echo "📄 Manifest: $MANIFEST"
echo "📁 Backups: $BACKUP_DIR/backups/"
echo "📂 Sessions: $BACKUP_DIR/sessions/"
echo ""

# Show backup summary
if [ -d "$BACKUP_DIR/backups" ]; then
    BACKUP_COUNT=$(ls -1 "$BACKUP_DIR/backups" 2>/dev/null | wc -l)
    TOTAL_SIZE=$(du -sh "$BACKUP_DIR/backups" 2>/dev/null | cut -f1)
    echo "📊 Summary:"
    echo "   Total backups: $BACKUP_COUNT"
    echo "   Total size: $TOTAL_SIZE"
fi

# Cleanup old backups (keep last 30 days)
echo ""
echo "🧹 Cleaning up old backups (keeping last 30 days)..."
find "$BACKUP_DIR/backups" -name "*.tar.gz" -mtime +30 -delete 2>/dev/null || true
echo "   ✓ Cleanup complete"

echo ""
echo "📝 Creating automatic conversation summary..."
AUTO_SUMMARY_SCRIPT="$(dirname "$0")/auto-save-summary.sh"
if [ -f "$AUTO_SUMMARY_SCRIPT" ]; then
    "$AUTO_SUMMARY_SCRIPT"
    echo "   ✓ Summary created"
else
    echo "   ⚠ Auto-summary script not found, skipping"
fi

echo ""
echo "✅ All conversation history has been backed up!"
echo ""
echo "To restore conversations, extract the desired backup:"
echo "   tar -xzf $BACKUP_DIR/backups/<backup-file>.tar.gz -C ~/.claude"
echo ""
echo "To view conversation summaries:"
echo "   cat $BACKUP_DIR/summaries/INDEX.md"

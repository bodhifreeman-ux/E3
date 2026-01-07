#!/bin/bash

# Auto-Save Conversation Summary
# Automatically creates a summary when conversation context is compacted
# This script can be called automatically or manually

set -e

SUMMARY_DIR="/home/bodhifreeman/E3/conversation-history/summaries"
AUTO_SUMMARY_DIR="$SUMMARY_DIR/auto-generated"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
DATE_READABLE=$(date +"%Y-%m-%d %H:%M:%S")

# Create directories
mkdir -p "$AUTO_SUMMARY_DIR"

# Generate filename
SUMMARY_FILE="$AUTO_SUMMARY_DIR/auto_summary_${TIMESTAMP}.md"

# Get conversation context from Claude cache if available
CLAUDE_CACHE="$HOME/.claude"
LATEST_SESSION=""

if [ -d "$CLAUDE_CACHE" ]; then
    # Find most recent session file
    LATEST_SESSION=$(find "$CLAUDE_CACHE" -type f -printf '%T@ %p\n' 2>/dev/null | sort -rn | head -1 | cut -d' ' -f2-)
fi

# Create auto-generated summary
cat > "$SUMMARY_FILE" << EOF
# Auto-Generated Conversation Summary

**Generated:** $DATE_READABLE
**Type:** Automatic (Conversation Compaction)

## Session Information

- **Timestamp:** $TIMESTAMP
- **Working Directory:** $(pwd)
- **User:** $USER
- **Hostname:** $(hostname)

## Context Snapshot

This summary was automatically generated when the conversation was compacted.
The full conversation history is preserved in the backup archives.

## Recent Activity

EOF

# Try to extract some context from recent commands/files
echo "### Recent Commands" >> "$SUMMARY_FILE"
echo '```bash' >> "$SUMMARY_FILE"
if [ -f "$HOME/.bash_history" ]; then
    tail -20 "$HOME/.bash_history" >> "$SUMMARY_FILE" 2>/dev/null || echo "# History not available" >> "$SUMMARY_FILE"
else
    echo "# History not available" >> "$SUMMARY_FILE"
fi
echo '```' >> "$SUMMARY_FILE"
echo "" >> "$SUMMARY_FILE"

# List recently modified files in current project
echo "### Recently Modified Files (Last Hour)" >> "$SUMMARY_FILE"
echo '```' >> "$SUMMARY_FILE"
find /home/bodhifreeman/E3 -type f -mmin -60 -not -path '*/\.*' -not -path '*/llama.cpp/*' 2>/dev/null | head -20 >> "$SUMMARY_FILE" || echo "None" >> "$SUMMARY_FILE"
echo '```' >> "$SUMMARY_FILE"
echo "" >> "$SUMMARY_FILE"

# Git status if in a repo
if git -C /home/bodhifreeman/E3 rev-parse --git-dir > /dev/null 2>&1; then
    echo "### Git Status" >> "$SUMMARY_FILE"
    echo '```' >> "$SUMMARY_FILE"
    git -C /home/bodhifreeman/E3 status --short >> "$SUMMARY_FILE" 2>/dev/null || echo "No changes" >> "$SUMMARY_FILE"
    echo '```' >> "$SUMMARY_FILE"
    echo "" >> "$SUMMARY_FILE"

    echo "### Recent Commits" >> "$SUMMARY_FILE"
    echo '```' >> "$SUMMARY_FILE"
    git -C /home/bodhifreeman/E3 log --oneline -5 >> "$SUMMARY_FILE" 2>/dev/null || echo "No commits" >> "$SUMMARY_FILE"
    echo '```' >> "$SUMMARY_FILE"
    echo "" >> "$SUMMARY_FILE"
fi

# Session file info
if [ -n "$LATEST_SESSION" ] && [ -f "$LATEST_SESSION" ]; then
    echo "### Claude Session Data" >> "$SUMMARY_FILE"
    echo "- Latest session file: \`$(basename "$LATEST_SESSION")\`" >> "$SUMMARY_FILE"
    echo "- Size: $(du -h "$LATEST_SESSION" | cut -f1)" >> "$SUMMARY_FILE"
    echo "- Modified: $(stat -c %y "$LATEST_SESSION")" >> "$SUMMARY_FILE"
fi

echo "" >> "$SUMMARY_FILE"
echo "---" >> "$SUMMARY_FILE"
echo "" >> "$SUMMARY_FILE"
echo "**Note:** This is an automatic snapshot. For detailed summaries, use \`./save-conversation-summary.sh\`" >> "$SUMMARY_FILE"

# Also create a quick index entry
INDEX_FILE="$SUMMARY_DIR/INDEX.md"
if [ ! -f "$INDEX_FILE" ]; then
    cat > "$INDEX_FILE" << 'EOFINDEX'
# Conversation Summaries Index

This file indexes all conversation summaries for quick reference.

## Manual Summaries

[Summaries you create manually with descriptions]

## Auto-Generated Summaries

EOFINDEX
fi

# Add entry to index
echo "- [$DATE_READABLE](auto-generated/auto_summary_${TIMESTAMP}.md) - Auto-generated snapshot" >> "$INDEX_FILE"

echo "✅ Auto-summary saved: $SUMMARY_FILE"
echo "📋 Index updated: $INDEX_FILE"

# Return the filename for potential piping
echo "$SUMMARY_FILE"

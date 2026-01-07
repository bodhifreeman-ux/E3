#!/bin/bash

# Save Claude Code Conversation Summary
# Call this script to manually save the current conversation summary

set -e

SUMMARY_DIR="/home/bodhifreeman/E3/conversation-history/summaries"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
DATE_READABLE=$(date +"%Y-%m-%d %H:%M:%S")

# Create summaries directory
mkdir -p "$SUMMARY_DIR"

echo "=== Save Conversation Summary ==="
echo "Timestamp: $DATE_READABLE"
echo ""

# Prompt for summary title
read -p "Enter a title for this conversation (or press Enter to auto-generate): " TITLE

if [ -z "$TITLE" ]; then
    TITLE="Conversation_${TIMESTAMP}"
else
    # Sanitize title for filename
    TITLE=$(echo "$TITLE" | tr ' ' '_' | tr -cd '[:alnum:]_-')
fi

SUMMARY_FILE="$SUMMARY_DIR/${TIMESTAMP}_${TITLE}.md"

# Create summary template
cat > "$SUMMARY_FILE" << 'EOF'
# Conversation Summary

**Date:** DATE_PLACEHOLDER
**Title:** TITLE_PLACEHOLDER

## Overview

[Briefly describe what this conversation was about]

## Key Topics Discussed

1.
2.
3.

## Important Decisions Made

-
-
-

## Code/Commands Generated

```bash
# List key commands or code snippets here
```

## Files Modified

-
-
-

## Action Items / Follow-ups

- [ ]
- [ ]
- [ ]

## Notes

[Any additional notes, context, or references]

---

**Context Preserved:** This summary was created when the conversation was compacted.
All detailed history is preserved in the backup archives.
EOF

# Replace placeholders
sed -i "s/DATE_PLACEHOLDER/$DATE_READABLE/g" "$SUMMARY_FILE"
sed -i "s/TITLE_PLACEHOLDER/$TITLE/g" "$SUMMARY_FILE"

echo "✓ Created summary template: $SUMMARY_FILE"
echo ""
echo "📝 Opening editor to fill in summary..."
echo "   (Save and close the editor when done)"
echo ""

# Open in editor (tries $EDITOR, then nano, then vi)
if [ -n "$EDITOR" ]; then
    $EDITOR "$SUMMARY_FILE"
elif command -v nano &> /dev/null; then
    nano "$SUMMARY_FILE"
elif command -v vi &> /dev/null; then
    vi "$SUMMARY_FILE"
else
    echo "⚠ No editor found. Please edit manually: $SUMMARY_FILE"
fi

echo ""
echo "✅ Conversation summary saved!"
echo "📄 File: $SUMMARY_FILE"
echo ""
echo "To view all summaries:"
echo "  ls -lt $SUMMARY_DIR/"
echo ""
echo "To search summaries:"
echo "  grep -r 'search term' $SUMMARY_DIR/"

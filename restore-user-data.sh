#!/bin/bash
set -o errexit  # Exit on error

if [ $# -eq 0 ]; then
    echo "❌ Usage: $0 <backup_directory>"
    echo "💡 Example: $0 backend/backups/20231225_143022"
    exit 1
fi

BACKUP_DIR="$1"

if [ ! -d "$BACKUP_DIR" ]; then
    echo "❌ Backup directory not found: $BACKUP_DIR"
    exit 1
fi

echo "📋 Restoring user data from: $BACKUP_DIR"

cd backend

# Restore poems.json
if [ -f "$BACKUP_DIR/poems.json" ]; then
    echo "📋 Restoring poems.json..."
    cp "$BACKUP_DIR/poems.json" poems.json
else
    echo "⚠️  No poems.json found in backup"
fi

# Restore images
if [ -d "$BACKUP_DIR/images" ]; then
    echo "🖼️  Restoring images..."
    mkdir -p static/images
    cp "$BACKUP_DIR/images"/* static/images/ 2>/dev/null || true
    echo "  Restored $(ls "$BACKUP_DIR/images" | wc -l) images"
else
    echo "⚠️  No images directory found in backup"
fi

echo "✅ User data restored successfully!"
#!/bin/bash
set -o errexit  # Exit on error

echo "💾 Backing up user-generated poems and images..."

cd backend

# Create backup directory with timestamp
BACKUP_DIR="backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

# Check if poems.json exists
if [ -f "poems.json" ]; then
    echo "📋 Backing up poems.json..."
    cp poems.json "$BACKUP_DIR/poems.json"
    
    # Extract modern poems and their images
    echo "🖼️  Backing up modern poem images..."
    if [ -d "static/images" ]; then
        mkdir -p "$BACKUP_DIR/images"
        
        # Get list of modern poem image filenames
        modern_images=$(./venv/bin/python -c "
import json
try:
    with open('poems.json', 'r') as f:
        poems = json.load(f)
    modern_poems = [p for p in poems if p.get('type') == 'modern']
    for poem in modern_poems:
        if 'image_filename' in poem:
            print(poem['image_filename'])
        else:
            print(f'{poem[\"id\"]}.png')
except:
    pass
        ")
        
        # Copy modern poem images
        for image in $modern_images; do
            if [ -f "static/images/$image" ]; then
                echo "  Copying $image"
                cp "static/images/$image" "$BACKUP_DIR/images/"
            fi
        done
    fi
    
    # Count modern poems
    modern_count=$(./venv/bin/python -c "
import json
try:
    with open('poems.json', 'r') as f:
        poems = json.load(f)
    modern_poems = [p for p in poems if p.get('type') == 'modern']
    print(len(modern_poems))
except:
    print(0)
    ")
    
    echo "✅ Backup complete!"
    echo "📊 Backed up $modern_count modern poems to: $BACKUP_DIR"
    echo "💡 To restore: ./restore-user-data.sh $BACKUP_DIR"
else
    echo "⚠️  No poems.json found - nothing to backup"
fi
#!/bin/bash
set -o errexit  # Exit on error

echo "🔄 Resetting poems to original state..."

cd backend

# Check if ORIGINAL_poems.json exists
if [ ! -f "ORIGINAL_poems.json" ]; then
    echo "❌ Error: ORIGINAL_poems.json not found!"
    exit 1
fi

# Remove existing poems.json if it exists
if [ -f "poems.json" ]; then
    echo "🗑️  Removing existing poems.json..."
    rm poems.json
fi

# Copy ORIGINAL_poems.json to poems.json
echo "📋 Copying ORIGINAL_poems.json to poems.json..."
cp ORIGINAL_poems.json poems.json

# Remove images for modern poems (check poems.json for type)
echo "🖼️  Removing images for modern poems..."
if [ -d "static/images" ]; then
    # Use Python to get list of modern poem IDs
    modern_ids=$(python3 -c "
import json
try:
    with open('poems.json', 'r') as f:
        poems = json.load(f)
    modern_ids = [str(p['id']) for p in poems if p.get('type') == 'modern']
    print(' '.join(modern_ids))
except:
    print('')  # If error, print nothing
")
    
    for file in static/images/*.png; do
        if [ -f "$file" ]; then
            filename=$(basename "$file")
            number=$(echo "$filename" | sed 's/\.png$//')
            
            # Check if this number is in the modern_ids list
            if echo "$modern_ids" | grep -w "$number" > /dev/null; then
                echo "🗑️  Removing modern poem image: $filename"
                rm "$file"
            fi
        fi
    done
else
    echo "⚠️  static/images directory not found, skipping image cleanup"
fi

echo "✅ Poems reset complete!"
echo "📊 Original poems restored: $(wc -l < poems.json) lines"

# Clear the illustration cache for local development
echo "🧹 Clearing illustration cache..."
if curl -s "http://localhost:8000/clear-cache" > /dev/null 2>&1; then
    echo "✅ Illustration cache cleared successfully"
else
    echo "⚠️  Could not clear cache (server may not be running)"
fi 
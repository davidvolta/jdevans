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

# Remove images with IDs 253 or greater
echo "🖼️  Removing images with IDs 253 or greater..."
if [ -d "static/images" ]; then
    for file in static/images/*.png; do
        if [ -f "$file" ]; then
            # Extract the number from filename (e.g., "253.png" -> "253")
            filename=$(basename "$file")
            number=$(echo "$filename" | sed 's/\.png$//')
            
            # Check if it's a number and >= 253
            if [[ "$number" =~ ^[0-9]+$ ]] && [ "$number" -ge 253 ]; then
                echo "🗑️  Removing image: $filename"
                rm "$file"
            fi
        fi
    done
else
    echo "⚠️  static/images directory not found, skipping image cleanup"
fi

echo "✅ Poems reset complete!"
echo "📊 Original poems restored: $(wc -l < poems.json) lines" 
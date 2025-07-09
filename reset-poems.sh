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

echo "✅ Poems reset complete!"
echo "📊 Original poems restored: $(wc -l < poems.json) lines" 
#!/bin/bash

# Quick git push script with commit message
# Usage: ./push.sh "Your commit message"

set -e  # Exit on any error

# Check if commit message provided
if [ -z "$1" ]; then
    echo "❌ Please provide a commit message"
    echo "Usage: ./push.sh \"Your commit message\""
    exit 1
fi

COMMIT_MESSAGE="$1"

echo "🔄 Git push routine starting..."

# Check git status
echo "📋 Current status:"
git status --short

# Add all changes
echo "➕ Adding all changes..."
git add .

# Check if there are changes to commit
if git diff --staged --quiet; then
    echo "✅ No changes to commit"
    exit 0
fi

# Show what will be committed
echo "📦 Changes to be committed:"
git diff --staged --name-only

# Commit with provided message
echo "💾 Committing changes..."
git commit -m "$COMMIT_MESSAGE"

# Push to origin
echo "🚀 Pushing to origin..."
git push

echo "✅ Push complete!"
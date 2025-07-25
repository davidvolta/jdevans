#!/bin/bash
set -o errexit  # Exit on error

echo "🚀 Building for PRODUCTION (preserving user poems)..."

# Check if we're in a CI/CD environment (skip interactive prompt)
if [ -n "$CI" ] || [ -n "$RENDER" ] || [ -n "$GITHUB_ACTIONS" ] || [ -n "$VERCEL" ] || [ "$ENV" = "production" ]; then
    echo "✅ Detected CI/CD environment - proceeding with production build"
elif [ "$ENV" != "production" ]; then
    echo "⚠️  Warning: This script is intended for production deployment."
    echo "⚠️  It will NOT reset poems.json and will preserve user-generated content."
    echo "⚠️  For local development, use ./local-build.sh instead."
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ Build cancelled."
        exit 1
    fi
fi

echo "🔧 Installing frontend dependencies..."
cd frontend
npm install

echo "🚀 Building React app..."
npm run build

echo "🧼 Cleaning old frontend files (but preserving images and poems)..."
find ../backend/static -type f ! -path "../backend/static/images/*" -delete
find ../backend/static -type d -empty -delete

echo "📦 Copying React build to backend/static..."
cp -r dist/* ../backend/static/

echo "✅ PRODUCTION build complete - user poems preserved!"
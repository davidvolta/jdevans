#!/usr/bin/env bash

set -o errexit  # Exit on error

echo "🔧 Installing frontend dependencies..."
cd frontend
npm install

echo "🚀 Building React app..."
npm run build

echo "📦 Copying build files to backend/static..."
rm -rf ../backend/static/*
cp -r dist/* ../backend/static/

echo "✅ Frontend build complete."

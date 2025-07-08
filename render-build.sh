set -o errexit  # Exit on error

echo "🔧 Installing frontend dependencies..."
cd frontend
npm install

echo "🚀 Building React app..."
npm run build

echo "🧼 Cleaning old frontend files (but preserving images)..."
find ../backend/static -type f ! -path "../backend/static/images/*" -delete
find ../backend/static -type d -empty -delete

echo "📦 Copying React build to backend/static..."
cp -r dist/* ../backend/static/

echo "✅ Frontend build complete."
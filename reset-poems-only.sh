#!/bin/bash
set -o errexit  # Exit on error

echo "🔄 RESET POEMS - Manual Reset"
echo "This will restore poems.json to the original state."
echo ""

read -p "Are you sure you want to reset poems? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Reset cancelled."
    exit 1
fi

echo "🔄 Resetting poems to original state..."
./reset-poems.sh

echo ""
echo "✅ Poems reset complete!"
echo "📊 You can now restart your server to see the changes." 
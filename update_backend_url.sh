#!/bin/bash
# Script to update Google Cloud Run URL in the frontend

if [ -z "$1" ]; then
    echo "Usage: ./update_backend_url.sh https://your-cloud-run-url.com"
    echo "Example: ./update_backend_url.sh https://vibeai-backend-abc123-uc.a.run.app"
    exit 1
fi

BACKEND_URL="$1"

echo "Updating backend URL to: $BACKEND_URL"

# Update all API calls in the JavaScript file
sed -i.bak "s|https://vibeai-backend-xxxxx-uc.a.run.app|$BACKEND_URL|g" static/js/script.js

echo "✅ Updated API URLs in static/js/script.js"
echo "✅ Backup created as static/js/script.js.bak"

echo ""
echo "🚀 Ready to deploy to Netlify!"
echo "1. Commit these changes: git add . && git commit -m 'Deploy V2 frontend'"
echo "2. Push to GitHub: git push origin main"
echo "3. Update Netlify build settings:"
echo "   - Build command: echo 'V2 static files ready'"
echo "   - Publish directory: ."
echo "   - Or use the netlify.toml file"

#!/bin/bash

# Script to restructure repository for Vercel deployment
# Run this from the root directory of your project

echo "🚀 Restructuring repository for Vercel deployment..."

# Copy SvelteKit files to root
echo "📁 Copying SvelteKit files to root..."
cp -r vro-daptar-svelte/* ./
cp vro-daptar-svelte/.* ./ 2>/dev/null || true

# Move credentials
echo "🔑 Moving credentials.json..."
mv vro-daptar-svelte/credentials.json ./ 2>/dev/null || echo "credentials.json not found in subdirectory"

# Install dependencies
echo "📦 Installing dependencies..."
npm install

# Remove old files (optional - uncomment if desired)
# echo "🗑️  Removing old Flask files..."
# rm -rf templates/ *.py requirements.txt Procfile

echo "✅ Restructuring complete!"
echo ""
echo "📋 Next steps:"
echo "1. Set environment variables in Vercel dashboard"
echo "2. Deploy to Vercel"
echo "3. Test the application"
echo ""
echo "🔗 Check DEPLOYMENT_GUIDE.md for detailed instructions"
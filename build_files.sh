#!/bin/bash

# Exit immediately if any command exits with a non-zero status
set -e

echo "=== Vercel Custom Django + Tailwind CSS Build ==="

echo "Installing Python dependencies from requirements.txt..."
python3 -m pip install -r requirements.txt

echo "Installing Node.js dependencies..."
npm install

echo "Compiling Tailwind CSS..."
npm run build

echo "Collecting Django static files..."
python3 manage.py collectstatic --noinput --clear

echo "Re-organizing static files for Vercel CDN..."
# Ensure destination folder exists
mkdir -p static_output/static
# Copy collected static files into static_output/static
cp -r staticfiles/* static_output/static/

echo "=== Build Complete ==="

#!/bin/bash

# Exit immediately if any command exits with a non-zero status
set -e

echo "=== Vercel Custom Django + Tailwind CSS Build ==="

echo "Installing Python dependencies from requirements.txt..."
if python3 -m pip install --user -r requirements.txt; then
    echo "Python dependencies installed successfully using --user."
elif python3 -m pip install -r requirements.txt --break-system-packages; then
    echo "Python dependencies installed successfully using --break-system-packages."
else
    echo "ERROR: Failed to install Python dependencies!"
    exit 1
fi

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

#!/bin/bash
# Build script for backend executable
# Packages FastAPI backend with PyInstaller

echo "=== AutoSniper Backend Build ==="
echo ""

# Check if PyInstaller is installed
if ! command -v pyinstaller &> /dev/null; then
    echo "PyInstaller not found. Installing..."
    pip install pyinstaller
fi

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf build dist

# Build backend
echo "Building backend executable..."
pyinstaller backend.spec

# Check if build succeeded
if [ -d "dist/autosniper-backend" ]; then
    echo ""
    echo "✅ Build successful!"
    echo "Output: dist/autosniper-backend/"
    echo ""
    echo "Files:"
    ls -lh dist/autosniper-backend/
else
    echo ""
    echo "❌ Build failed!"
    exit 1
fi

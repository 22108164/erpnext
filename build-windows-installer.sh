#!/bin/bash
# NxLIMS Windows Installer Build Script
# Builds electron app and creates NSIS installer for Windows

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$SCRIPT_DIR/.."
DESKTOP_APP="$PROJECT_ROOT/desktop/nxlims-desktop"
VERSION="1.0.0"
BUILD_OUTPUT="$DESKTOP_APP/dist"

echo "=================================="
echo "NxLIMS Windows Installer Builder"
echo "=================================="
echo ""

# Check prerequisites
echo "[1] Checking prerequisites..."
if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found. Please install Node.js 16+"
    exit 1
fi

if ! command -v npm &> /dev/null; then
    echo "❌ npm not found. Please install npm"
    exit 1
fi

if ! command -v git &> /dev/null; then
    echo "❌ git not found. Please install git"
    exit 1
fi

echo "✓ Node.js version: $(node --version)"
echo "✓ npm version: $(npm --version)"
echo ""

# Navigate to desktop app directory
cd "$DESKTOP_APP"

# Clean previous builds
echo "[2] Cleaning previous builds..."
rm -rf node_modules dist out
echo "✓ Cleaned"
echo ""

# Install dependencies
echo "[3] Installing npm dependencies..."
npm install --production
echo "✓ Dependencies installed"
echo ""

# Build Windows installer
echo "[4] Building Windows installer..."
echo "   Target: NSIS Installer (.exe)"
echo "   Architecture: x64"
echo "   Output: $BUILD_OUTPUT"
echo ""

npm run dist:win

# Check if build was successful
if [ -f "$BUILD_OUTPUT/NxLIMS Setup 1.0.0.exe" ]; then
    echo ""
    echo "=================================="
    echo "✓ BUILD SUCCESSFUL"
    echo "=================================="
    echo ""
    echo "Installer location:"
    echo "  $BUILD_OUTPUT/NxLIMS Setup 1.0.0.exe"
    echo ""
    echo "File size:"
    ls -lh "$BUILD_OUTPUT"/*.exe | awk '{print "  " $5 " (" $9 ")"}'
    echo ""
    echo "Next steps:"
    echo "  1. Transfer the .exe file to Windows machine"
    echo "  2. Run as Administrator"
    echo "  3. Follow the installation wizard"
    echo ""
else
    echo ""
    echo "❌ BUILD FAILED"
    echo ""
    echo "Check the output above for errors"
    exit 1
fi

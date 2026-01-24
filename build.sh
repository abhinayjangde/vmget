#!/bin/bash

# Build script for vmget executable

set -e

echo "Building vmget executable..."

# Build with PyInstaller
uv run pyinstaller --onefile --name vmget src/vmget/__main__.py

# Clean up build artifacts
rm -rf build vmget.spec

echo "Build complete! Executable is in dist/vmget"

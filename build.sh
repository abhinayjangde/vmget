#!/bin/bash

uv run pyinstaller --onefile .\app\vmget.py

# Clean up the build files
rm -rf build vmget.spec

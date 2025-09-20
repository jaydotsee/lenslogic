#!/bin/bash
#
# Secure build script for LensLogic executable
# Creates a single-file executable respecting .gitignore exclusions
#

set -e  # Exit on any error

echo "Building LensLogic executable (GITIGNORE-AWARE)..."
echo "=================================================="

# Function to parse .gitignore and create find exclusions
parse_gitignore() {
    if [ ! -f ".gitignore" ]; then
        echo "❌ .gitignore file not found!" >&2
        exit 1
    fi

    # Create temporary file for find exclusions
    local temp_file
    temp_file=$(mktemp)

    # Parse .gitignore line by line
    while IFS= read -r line; do
        # Skip empty lines and comments
        if [[ -z "$line" || "$line" =~ ^[[:space:]]*# ]]; then
            continue
        fi

        # Remove leading/trailing whitespace
        pattern=$(echo "$line" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')

        # Skip empty patterns after cleaning
        if [[ -z "$pattern" ]]; then
            continue
        fi

        # Handle different gitignore pattern types
        if [[ "$pattern" == "/"* ]]; then
            # Pattern starts with / - root relative
            pattern_clean=${pattern#/}
            echo "! -path \"./$pattern_clean\" ! -path \"./$pattern_clean/*\"" >> "$temp_file"
        elif [[ "$pattern" == *"/" ]]; then
            # Pattern ends with / - directory only
            pattern_clean=${pattern%/}
            echo "! -path \"*/$pattern_clean\" ! -path \"*/$pattern_clean/*\" ! -name \"$pattern_clean\"" >> "$temp_file"
        elif [[ "$pattern" == *"*"* ]]; then
            # Pattern contains wildcards
            echo "! -name \"$pattern\" ! -path \"*/$pattern\" ! -path \"*/$pattern/*\"" >> "$temp_file"
        else
            # Simple filename or directory pattern
            echo "! -name \"$pattern\" ! -path \"*/$pattern\" ! -path \"*/$pattern/*\"" >> "$temp_file"
        fi

    done < .gitignore

    echo "$temp_file"
}

# Security check function using gitignore-based exclusions
check_security_with_gitignore() {
    echo "🔍 Performing .gitignore-based security scan..."
    echo "📄 Reading .gitignore patterns..."

    # Count patterns being read
    local pattern_count=0
    while IFS= read -r line; do
        # Skip empty lines and comments
        if [[ -z "$line" || "$line" =~ ^[[:space:]]*# ]]; then
            continue
        fi

        # Remove leading/trailing whitespace
        pattern=$(echo "$line" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')

        # Skip empty patterns after cleaning
        if [[ -z "$pattern" ]]; then
            continue
        fi

        echo "  📝 $pattern"
        ((pattern_count++))
    done < .gitignore

    echo "✅ Loaded $pattern_count exclusion patterns from .gitignore"

    # Get gitignore exclusions
    local exclusions_file
    exclusions_file=$(parse_gitignore)

    # Build find command to check for files that would be included
    local find_cmd="find . -type f"

    # Add gitignore exclusions
    while read -r exclusion; do
        find_cmd="$find_cmd $exclusion"
    done < "$exclusions_file"

    # Look for potentially sensitive files that aren't excluded by gitignore
    local sensitive_files
    sensitive_files=$(eval "$find_cmd" 2>/dev/null | grep -E '\.(key|secret|private|credential)$|\.env\.|config.*\.(yaml|yml|json)$|api.*key|token.*\.|password.*\.' | grep -v '__pycache__' | head -10)

    # Clean up temp file
    rm -f "$exclusions_file"

    if [[ -n "$sensitive_files" ]]; then
        echo "⚠️  WARNING: Found potentially sensitive files not excluded by .gitignore:"
        echo "$sensitive_files"
        echo ""
        echo "These files would be included in the build. Consider adding them to .gitignore."
        echo ""
        echo "Continue anyway? (type 'yes' to proceed, anything else to abort)"
        read -r response
        if [ "$response" != "yes" ]; then
            echo "Build aborted for security."
            exit 1
        fi
        echo "⚠️  User chose to proceed despite security warnings!"
    else
        echo "🔒 Security scan passed - no sensitive files detected outside .gitignore exclusions"
    fi
}

# Clean any previous builds
echo "🧹 Cleaning previous builds..."
rm -rf build/ dist/ *.spec

# Security scan using gitignore patterns
check_security_with_gitignore

# Check for required dependencies
echo "🔍 Checking dependencies..."
MISSING_DEPS=""

if ! python -c "import PyInstaller" &> /dev/null; then
    MISSING_DEPS="$MISSING_DEPS pyinstaller"
fi

if ! python -c "import rich" &> /dev/null; then
    MISSING_DEPS="$MISSING_DEPS rich"
fi

if ! python -c "import questionary" &> /dev/null; then
    MISSING_DEPS="$MISSING_DEPS questionary"
fi

if ! python -c "import exiftool" &> /dev/null; then
    MISSING_DEPS="$MISSING_DEPS pyexiftool"
fi

if [[ -n "$MISSING_DEPS" ]]; then
    echo "Missing dependencies:$MISSING_DEPS"
    echo "Installing missing dependencies..."
    pip install $MISSING_DEPS
fi

# Create temporary directory for safe file collection
echo "Creating secure build environment..."
TEMP_BUILD_DIR=$(mktemp -d)
echo "Temporary build directory: $TEMP_BUILD_DIR"

# Function to copy files respecting .gitignore exclusions
copy_with_gitignore_exclusions() {
    local src_pattern="$1"
    local dest_base="$2"
    local description="$3"

    echo "📂 $description"

    # Get gitignore exclusions
    local exclusions_file
    exclusions_file=$(parse_gitignore)

    # Build find command with gitignore exclusions
    local find_cmd="find . -type f -path \"$src_pattern\""

    # Add gitignore exclusions
    while read -r exclusion; do
        find_cmd="$find_cmd $exclusion"
    done < "$exclusions_file"

    # Execute find and copy matching files
    local copied_count=0
    local files_found
    files_found=$(eval "$find_cmd" 2>/dev/null)

    if [[ -z "$files_found" ]]; then
        echo "  ⚠️  No files found matching pattern: $src_pattern"
    else
        while IFS= read -r file; do
            # Skip the current file if it starts with ./
            file_clean=${file#./}

            # Create directory structure in destination
            dest_dir="$dest_base/$(dirname "$file_clean")"
            mkdir -p "$dest_dir"
            cp "$file" "$dest_dir/"
            echo "  ✅ $file_clean"
            ((copied_count++))
        done <<< "$files_found"
    fi

    # Clean up temp file
    rm -f "$exclusions_file"

    echo "  📊 Copied $copied_count files"
}

# Copy files using .gitignore exclusions
echo "📦 Collecting files (respecting .gitignore exclusions)..."

# Copy main entry point
if [ -f "src/main.py" ]; then
    mkdir -p "$TEMP_BUILD_DIR/src"
    cp src/main.py "$TEMP_BUILD_DIR/src/"
    echo "  ✅ src/main.py"
else
    echo "❌ ERROR: src/main.py not found!"
    exit 1
fi

# Copy all source files from src/ directory
copy_with_gitignore_exclusions "./src/*.py" "$TEMP_BUILD_DIR" "Copying main source files..."
copy_with_gitignore_exclusions "./src/*/*.py" "$TEMP_BUILD_DIR" "Copying module files..."
copy_with_gitignore_exclusions "./src/*/*/*.py" "$TEMP_BUILD_DIR" "Copying nested module files..."

# Copy configuration files
copy_with_gitignore_exclusions "./config/*.yaml" "$TEMP_BUILD_DIR" "Copying configuration files..."
copy_with_gitignore_exclusions "./config/*.yml" "$TEMP_BUILD_DIR" "Copying YAML configuration files..."

# Copy requirements.txt if it exists
if [ -f "requirements.txt" ]; then
    cp requirements.txt "$TEMP_BUILD_DIR/"
    echo "  ✅ requirements.txt"
fi

# Verify essential files exist
echo "🔍 Verifying essential files..."
if [ ! -f "$TEMP_BUILD_DIR/src/main.py" ]; then
    echo "❌ ERROR: src/main.py not found in build!"
    rm -rf "$TEMP_BUILD_DIR"
    exit 1
fi

if [ ! -f "$TEMP_BUILD_DIR/config/default_config.yaml" ]; then
    echo "❌ ERROR: config/default_config.yaml not found in build!"
    rm -rf "$TEMP_BUILD_DIR"
    exit 1
fi

echo "✅ All essential files verified"

# Create __init__.py files for proper Python module structure
find "$TEMP_BUILD_DIR/src" -type d -exec touch {}/__init__.py \;

# Show what's being included
echo ""
echo "Files to be included in executable:"
echo "===================================="
find "$TEMP_BUILD_DIR" -type f | sort

echo ""
echo "Building executable with PyInstaller..."

# Save current directory and Python path
ORIGINAL_DIR=$(pwd)
PYTHON_PATH=$(python -c "import sys; print(sys.executable)")
cd "$TEMP_BUILD_DIR"

# Create a launch script in the temp directory
cat > lenslogic_launcher.py << 'EOF'
#!/usr/bin/env python3
"""
LensLogic launcher script for PyInstaller
"""

import sys
import os
from pathlib import Path

# Add src directory to Python path
src_dir = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_dir))

# Import and run main
from main import main

if __name__ == "__main__":
    main()
EOF

# Run PyInstaller with comprehensive options
"$PYTHON_PATH" -m PyInstaller --clean --onefile \
  --add-data "config:config" \
  --add-data "src:src" \
  --console \
  --name "LensLogic" \
  --distpath "$ORIGINAL_DIR/dist" \
  --hidden-import="exiftool" \
  --hidden-import="pymediainfo" \
  --hidden-import="rich" \
  --hidden-import="questionary" \
  --hidden-import="pathlib" \
  --hidden-import="yaml" \
  --icon="$ORIGINAL_DIR/icon.ico" \
  lenslogic_launcher.py 2>/dev/null || \
"$PYTHON_PATH" -m PyInstaller --clean --onefile \
  --add-data "config:config" \
  --add-data "src:src" \
  --console \
  --name "LensLogic" \
  --distpath "$ORIGINAL_DIR/dist" \
  --hidden-import="exiftool" \
  --hidden-import="pymediainfo" \
  --hidden-import="rich" \
  --hidden-import="questionary" \
  --hidden-import="pathlib" \
  --hidden-import="yaml" \
  lenslogic_launcher.py

# Return to original directory
cd "$ORIGINAL_DIR"

# Clean up temporary directory
echo "Cleaning up temporary files..."
rm -rf "$TEMP_BUILD_DIR"

echo ""
if [ -f "./dist/LensLogic" ]; then
    echo "✅ Build completed successfully!"
    echo "=================================="
    echo "Executable location: ./dist/LensLogic"
    echo "File size: $(du -h ./dist/LensLogic | cut -f1)"
    echo ""
    echo "Test with: ./dist/LensLogic --help"
    echo "Run with:  ./dist/LensLogic --interactive"
    echo ""
    echo "🎯 LensLogic Features Available:"
    echo "   • Smart photo & video organization"
    echo "   • Professional XMP sidecar generation"
    echo "   • Camera slug naming (iPhone, DSLR, etc.)"
    echo "   • Comprehensive metadata extraction"
    echo "   • XMP library analysis and reporting"
    echo "   • Geolocation and GPS support"
    echo "   • Interactive mode with Rich console"
    echo ""
    echo "📸🎬 Ready for professional photo & video workflows!"
else
    echo "❌ Build failed - executable not found"
    exit 1
fi
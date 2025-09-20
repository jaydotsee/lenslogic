#!/usr/bin/env python3
"""
LensLogic Demo - Shows functionality without requiring full dependencies
"""

def show_ascii_logo():
    print("""
 ██▓    ▓█████  ███▄    █   ██████  ██▓     ▒█████    ▄████  ██▓ ▄████▄
▓██▒    ▓█   ▀  ██ ▀█   █ ▒██    ▒ ▓██▒    ▒██▒  ██▒ ██▒ ▀█▒▓██▒▒██▀ ▀█
▒██░    ▒███   ▓██  ▀█ ██▒░ ▓██▄   ▒██░    ▒██░  ██▒▒██░▄▄▄░▒██▒▒▓█    ▄
▒██░    ▒▓█  ▄ ▓██▒  ▐▌██▒  ▒   ██▒▒██░    ▒██   ██░░▓█  ██▓░██░▒▓▓▄ ▄██▒
░██████▒░▒████▒▒██░   ▓██░▒██████▒▒░██████▒░ ████▓▒░░▒▓███▀▒░██░▒ ▓███▀ ░
░ ▒░▓  ░░░ ▒░ ░░ ▒░   ▒ ▒ ▒ ▒▓▒ ▒ ░░ ▒░▓  ░░ ▒░▒░▒░  ░▒   ▒ ░▓  ░ ░▒ ▒  ░
░ ░ ▒  ░ ░ ░  ░░ ░░   ░ ▒░░ ░▒  ░ ░░ ░ ▒  ░  ░ ▒ ▒░   ░   ░  ▒ ░  ░  ▒
  ░ ░      ░      ░   ░ ░ ░  ░  ░    ░ ░   ░ ░ ░ ▒  ░ ░   ░  ▒ ░░
    ░  ░   ░  ░         ░       ░      ░  ░    ░ ░        ░  ░  ░ ░
                                                              ░

    Smart photo organization powered by metadata
    """)

def show_features():
    print("""
🎯 LensLogic Features:

📁 CORE ORGANIZATION:
   • Smart file organization based on EXIF metadata
   • Customizable naming patterns with metadata variables
   • Flexible folder structures (2025/09/19/ format and more)
   • RAW/JPEG separation with configurable folder names
   • Dry run mode to preview changes before applying

🚀 QUICK WINS (New Features):
   ✅ Auto-rotate images based on EXIF orientation
   ✅ Shooting session detection (time-based grouping)
   ✅ Basic statistics dashboard (camera/lens usage)
   ✅ Backup verification (checksum validation)

📊 ADVANCED FEATURES:
   • Geolocation: GPS extraction, reverse geocoding, KML export
   • Duplicate detection: Hash/pixel/histogram comparison methods
   • Interactive menu system with Rich UI
   • Comprehensive statistics with charts
   • Social media optimization (Instagram, Facebook, Twitter)
   • Incremental backup sync with verification

⚙️ CONFIGURATION:
   • YAML-based configuration system
   • Interactive configuration wizard (--config-wizard)
   • Quick setup option (--quick-setup)
   • Hierarchical config (defaults → user → custom → CLI)

🛠️ USAGE EXAMPLES:

   # Show this demo
   python demo.py

   # Install dependencies first
   pip install -r requirements.txt

   # Display logo
   python src/main.py --logo

   # Run configuration wizard
   python src/main.py --config-wizard

   # Quick setup
   python src/main.py --quick-setup

   # Basic organization
   python src/main.py -s ~/Pictures/Unsorted -d ~/Pictures/Organized

   # Dry run to preview
   python src/main.py --dry-run

   # Advanced statistics with charts
   python src/main.py --advanced-stats

   # Detect shooting sessions
   python src/main.py --detect-sessions

   # Optimize for Instagram
   python src/main.py --social-media instagram

   # Backup photos
   python src/main.py --backup

   # Interactive mode
   python src/main.py --interactive

📦 BUILD EXECUTABLE:
   # Install PyInstaller
   pip install pyinstaller

   # Build standalone executable
   pyinstaller lenslogic.spec

   # Run executable
   ./dist/lenslogic --help

🎨 ASCII LOGOS:
   The tool includes beautiful ASCII art logos in multiple styles:
   • Full logo (shown above)
   • Compact logo
   • Simple logo
   • Camera-themed logo

💡 PHOTOGRAPHER-FRIENDLY:
   • Supports all major RAW formats
   • Preserves EXIF metadata
   • Creates XMP sidecar files
   • GPS track integration
   • Equipment usage tracking
   • Session-based organization
   • Quality assessment tools
    """)

def main():
    print("=" * 70)
    show_ascii_logo()
    print("=" * 70)
    show_features()
    print("=" * 70)

    print("""
🚀 Ready to get started?

1. Install dependencies: pip install -r requirements.txt
2. Run setup wizard: python src/main.py --config-wizard
3. Start organizing: python src/main.py

For help: python src/main.py --help
    """)

if __name__ == "__main__":
    main()
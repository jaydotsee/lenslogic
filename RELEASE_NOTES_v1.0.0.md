# LensLogic v1.0.0 Release Notes

## 🎉 Initial Public Release

LensLogic is a smart photo and video organization tool powered by metadata, designed for photographers, videographers, and content creators who need professional-grade file management capabilities.

## ✨ Key Features

### Core Organization
- **Smart File Organization**: Automatically organize photos and videos based on EXIF/metadata
- **Customizable Naming Patterns**: Flexible file naming using template variables
- **Folder Structure Templates**: Create custom folder hierarchies based on date, camera, location
- **RAW/JPEG Separation**: Automatically separate RAW files from processed images
- **Custom Destination Override**: Organize to client-specific folders without changing configuration

### Advanced Features
- **Interactive Menu System**: User-friendly CLI interface with Rich formatting
- **Configuration Wizard**: Step-by-step setup for beginners
- **Backup & Restore**: Full backup/restore functionality with multiple destinations
- **Session Detection**: Automatic grouping of photos by shooting sessions
- **Statistics & Analytics**: Comprehensive library analysis with visual charts
- **Social Media Export**: Optimize images for Instagram, Facebook, Twitter
- **Geolocation Support**: GPS extraction, reverse geocoding, and location-based organization
- **XMP Sidecar Files**: Generate metadata sidecar files for RAW processors
- **Duplicate Detection**: Hash, pixel, and histogram-based duplicate detection

### Professional Support
- **Video Formats**: MP4, MOV, AVI, MKV, ProRes, MXF, R3D, BRAW
- **RAW Formats**: CR2, CR3, NEF, ARW, ORF, DNG, RAF, RW2, PEF, SRW
- **Image Formats**: JPEG, PNG, TIFF, HEIC, HEIF, WebP, BMP, GIF

## 📦 Installation

### macOS (Apple Silicon)
```bash
# Download the release
tar -xzf lenslogic-v1.0.0-macos-arm64.tar.gz
# Make executable (if needed)
chmod +x lenslogic
# Move to PATH (optional)
sudo mv lenslogic /usr/local/bin/
```

### From Source
```bash
git clone https://github.com/YOUR_USERNAME/lenslogic.git
cd lenslogic
pip install -r requirements.txt
python src/main.py --help
```

## 🚀 Quick Start

```bash
# Interactive mode (recommended for first-time users)
lenslogic --interactive

# Configuration wizard
lenslogic --config-wizard

# Basic organization
lenslogic --source /path/to/photos --destination /path/to/organized

# Client-specific organization
lenslogic --custom-destination /Projects/ClientName --source /imports

# Dry run preview
lenslogic --dry-run
```

## 🆕 What's New

### Custom Destination Override
- New `--custom-destination` CLI flag for one-time destination override
- Interactive menu option "🎯 Organize with Custom Destination"
- Perfect for wedding photographers and client-specific projects

### Enhanced Features
- Comprehensive backup and restore functionality
- Session detection for automatic photo grouping
- Advanced statistics with visual charts
- Social media optimization for multiple platforms
- Professional video format support

## 📋 System Requirements

- **Operating System**: macOS, Windows, Linux
- **Python**: 3.8+ (if running from source)
- **External Tools** (optional):
  - ExifTool for enhanced metadata extraction
  - MediaInfo for video metadata

## 📚 Documentation

- [README](README.md) - Overview and basic usage
- [User Guide](USER_GUIDE.md) - Comprehensive usage guide
- [Developer Guide](DEVELOPER_GUIDE.md) - For contributors
- [API Reference](API_REFERENCE.md) - Module documentation

## 🐛 Known Issues

- Video files may show "unknown" camera name in some cases
- Test suite is minimal (manual testing via dry-run mode recommended)

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📄 License

MIT License - See [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

Special thanks to all early testers and contributors who helped shape LensLogic into a professional photo organization tool.

---

**Download**: [lenslogic-v1.0.0-macos-arm64.tar.gz](#)

**SHA256**: `f87ec9b90239027d9bf68dcf04dc0003d277df620a4b948bc5925037522937c7`

**Platform**: macOS (Apple Silicon)
**File Size**: 49MB (compressed)
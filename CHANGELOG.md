# Changelog

All notable changes to LensLogic will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial public release of LensLogic
- Smart photo and video organization using EXIF/metadata
- Interactive menu system with Rich UI
- Configuration wizard for easy setup
- Comprehensive backup and restore functionality
- Advanced statistics and analytics with charts
- Session detection for grouping photos by shooting sessions
- Social media optimization (Instagram, Facebook, Twitter)
- Geolocation support with reverse geocoding
- XMP sidecar file generation
- Duplicate detection using multiple algorithms
- Incremental backup with integrity verification
- Professional video format support (ProRes, MXF, R3D, BRAW)
- Camera name normalization and slugging
- Extensive test suite with unit and integration tests

### Features

#### Core Organization
- Automatic file organization based on EXIF metadata
- Customizable naming patterns with template variables
- Folder structure templates for flexible organization
- RAW/JPEG separation with dedicated folders
- Support for 50+ file formats including professional video formats

#### Advanced Features
- **Interactive Menu**: User-friendly CLI interface with Rich formatting
- **Configuration Wizard**: Step-by-step setup for beginners
- **Backup & Restore**: Full backup/restore functionality with multiple destinations
- **Session Detection**: Automatic grouping of photos by shooting sessions
- **Statistics & Analytics**: Comprehensive library analysis with visual charts
- **Social Media Export**: Optimize images for different platforms and formats
- **Geolocation**: GPS extraction, reverse geocoding, and location-based organization
- **XMP Sidecars**: Generate metadata sidecar files for RAW processors

#### Technical Features
- **Dry Run Mode**: Preview changes before applying
- **Duplicate Detection**: Hash, pixel, and histogram-based duplicate detection
- **Progress Tracking**: Real-time progress bars and detailed statistics
- **Error Handling**: Comprehensive error reporting and recovery
- **Cross-platform**: Support for Windows, macOS, and Linux
- **Performance**: Optimized for large photo libraries

#### Supported Formats
- **Images**: JPEG, PNG, TIFF, HEIC, HEIF, WebP, BMP, GIF
- **RAW**: CR2, CR3, NEF, ARW, ORF, DNG, RAF, RW2, PEF, SRW, X3F
- **Videos**: MP4, MOV, AVI, MKV, WebM, FLV, WMV, M4V, MPG, MPEG
- **Professional**: ProRes, MXF, R3D, BRAW, DNxHD

### Installation Options
- Source installation with pip requirements
- Standalone executable via PyInstaller
- Cross-platform compatibility

### Documentation
- Comprehensive README with examples
- API Reference documentation
- Developer Guide for contributors
- User Guide with detailed workflows
- Architecture documentation

---

## Release Notes

This is the initial public release of LensLogic, a comprehensive photo and video organization tool built for photographers, videographers, and content creators who need professional-grade file management capabilities.

### Key Highlights

🚀 **Professional Features**: Support for professional video formats, XMP sidecars, and advanced metadata extraction

📊 **Analytics**: Comprehensive library statistics with visual charts and reports

🔄 **Backup & Restore**: Full backup solution with incremental sync and integrity verification

🎯 **Session Detection**: Automatically group photos by shooting sessions

📱 **Social Media Ready**: Optimize images for Instagram, Facebook, Twitter with proper sizing

🌍 **Geolocation**: GPS extraction and reverse geocoding for location-based organization

⚙️ **User-Friendly**: Interactive menu system and configuration wizard for easy setup

🧪 **Well-Tested**: Comprehensive test suite with 200+ tests covering all major functionality

### Perfect For

- **Professional Photographers**: RAW workflow support, XMP sidecars, advanced organization
- **Content Creators**: Social media optimization, batch processing, session detection
- **Photo Enthusiasts**: Easy organization, duplicate detection, backup solutions
- **Video Professionals**: Support for ProRes, MXF, R3D, BRAW and other professional formats

### Getting Started

```bash
# Quick start
git clone <repository-url>
cd lenslogic
pip install -r requirements.txt
python src/main.py --config-wizard
```

For detailed installation and usage instructions, see the [README.md](README.md) and [USER_GUIDE.md](USER_GUIDE.md).
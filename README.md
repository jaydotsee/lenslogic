# LensLogic

Smart photo organization powered by metadata. A comprehensive Python CLI tool for organizing photo and video libraries with advanced features including EXIF data extraction, geolocation, duplicate detection, and customizable organization patterns.

## Features

### Core Functionality
- **Smart File Organization**: Automatically organize photos and videos based on EXIF metadata
- **Customizable Naming Patterns**: Flexible file naming using metadata variables
- **Folder Structure Templates**: Create custom folder hierarchies based on date, camera, location
- **RAW/JPEG Separation**: Automatically separate RAW files from processed images
- **Duplicate Detection**: Find and handle duplicate files using hash, pixel, or histogram comparison

### Quick Wins (New!)
- **Auto-Rotate Images**: Automatically correct image orientation based on EXIF data
- **Session Detection**: Group photos by shooting sessions (time-based)
- **Advanced Statistics**: Comprehensive analytics with charts (camera usage, shooting patterns)
- **Backup Verification**: Checksum validation of backup integrity
- **Social Media Export**: Optimize images for Instagram, Facebook, Twitter with proper sizing
- **Incremental Sync**: Smart backup that only syncs changed files

### Advanced Features
- **Geolocation Support**:
  - Extract GPS coordinates from photos
  - Reverse geocoding to get location names
  - Organize by location (country/city)
  - Export GPS data to KML files for mapping
- **Interactive Menu System**: User-friendly menu-driven interface with Rich UI
- **Configuration Wizard**: Step-by-step setup with `--config-wizard`
- **Dry Run Mode**: Preview changes before applying them
- **Progress Tracking**: Real-time progress bars and detailed statistics
- **Sidecar XMP Files**: Generate metadata sidecar files for RAW processors

## Installation

### From Source

```bash
# Clone the repository
git clone https://github.com/your-username/lenslogic.git
cd lenslogic

# Install dependencies
pip install -r requirements.txt

# Run from source
python src/main.py --help
```

### Build Standalone Executable

```bash
# Build executable using PyInstaller
pyinstaller lenslogic.spec

# The executable will be in the dist/ directory
./dist/lenslogic --help
```

## Usage

### Command Line Interface

```bash
# Basic usage - organize photos from current directory
lenslogic

# Specify source and destination
lenslogic -s /path/to/photos -d /path/to/organized

# Dry run to preview changes
lenslogic --dry-run

# Interactive mode
lenslogic --interactive

# Analyze library statistics
lenslogic --analyze

# Export GPS locations to KML
lenslogic --export-gps locations.kml
```

### Command Line Options

#### Basic Options
```
-s, --source          Source directory containing photos
-d, --destination     Destination directory for organized photos
-c, --config         Path to custom configuration file
--dry-run            Preview changes without modifying files
-p, --pattern        File naming pattern
-f, --folder-structure  Folder organization structure
--no-preserve        Move files instead of copying
-v, --verbose        Enable verbose output
--quiet              Suppress output except errors
```

#### Analysis & Statistics
```
--analyze            Basic library statistics
--advanced-stats     Comprehensive statistics with charts
--chart-dir DIR      Directory for generated charts
--detect-sessions    Detect shooting sessions
--organize-sessions  Organize photos by sessions
```

#### Social Media & Export
```
--social-media PLATFORM    Optimize for platform (instagram/facebook/twitter)
--social-format FORMAT     Format type (post/story/cover)
--social-output DIR        Output directory for social media files
--export-gps FILE          Export GPS locations to KML file
```

#### Backup & Sync
```
--backup             Backup to configured destinations
--backup-to DEST     Backup to specific destinations
--verify-backup      Verify backup integrity
```

#### Configuration
```
--config-wizard      Run interactive configuration wizard
--quick-setup        Quick configuration setup
--reset-config       Reset configuration to defaults
--save-config        Save current configuration
```

#### Other
```
-i, --interactive    Launch interactive menu
--logo              Display LensLogic logo
```

### Interactive Mode

Launch the interactive menu with:

```bash
lenslogic --interactive
```

The menu provides options for:
- Quick organize with current settings
- Configure all settings interactively
- Select directories
- Preview changes (dry run)
- Analyze library statistics
- Export GPS locations
- Advanced options (cache management, config import/export)

## Configuration

The tool uses a hierarchical configuration system:

1. **Default Configuration**: Built-in defaults
2. **User Configuration**: `~/.lenslogic/config.yaml`
3. **Custom Configuration**: Specified with `-c` flag
4. **Command Line Arguments**: Override any setting

### Configuration Structure

```yaml
general:
  source_directory: "."
  destination_directory: "./organized"
  dry_run: false
  verbose: true
  preserve_originals: true
  skip_duplicates: true

file_types:
  images: [jpg, jpeg, png, heic, heif]
  raw: [raw, cr2, cr3, nef, arw, dng]
  videos: [mp4, avi, mov, mkv]

organization:
  folder_structure: "{year}/{month:02d}/{day:02d}"
  separate_raw: true
  raw_folder: "RAW"
  jpg_folder: "JPG"

naming:
  pattern: "{year}{month:02d}{day:02d}_{hour:02d}{minute:02d}{second:02d}_{camera}_{original_name}"
  include_sequence: true
  camera_names:
    "Canon EOS R5": "R5"
    "NIKON D850": "D850"

geolocation:
  enabled: true
  reverse_geocode: true
  add_location_to_folder: false

duplicate_detection:
  method: "hash"  # hash, pixel, histogram
  threshold: 0.95
  action: "skip"  # skip, rename, move
```

### Pattern Variables

Available variables for naming patterns and folder structures:

**Date/Time Variables:**
- `{year}`, `{month}`, `{day}` - Date components
- `{hour}`, `{minute}`, `{second}` - Time components
- `{date}` - YYYYMMDD format
- `{time}` - HHMMSS format
- `{month_name}`, `{month_short}` - Month names
- `{weekday}` - Day of week

**Camera Variables:**
- `{camera}` - Simplified camera name
- `{camera_make}`, `{camera_model}` - Full camera info
- `{lens}` - Lens model

**Technical Variables:**
- `{iso}`, `{f_number}`, `{focal_length}` - Camera settings
- `{width}`, `{height}` - Image dimensions

**Location Variables (when geolocation enabled):**
- `{country}`, `{city}`, `{state}` - Location components

**Other:**
- `{original_name}` - Original filename without extension

## Examples

### Example 1: Basic Organization

```bash
lenslogic -s ~/Pictures/Unsorted -d ~/Pictures/Organized
```

Organizes photos from Unsorted folder into Organized folder using default settings.

### Example 2: Custom Pattern with Dry Run

```bash
lenslogic --dry-run -p "{camera}_{date}_{time}_{original_name}" -f "{year}/{camera}/{month_name}"
```

Preview organization with custom naming and folder patterns.

### Example 3: RAW Workflow

```bash
lenslogic -s /media/card -d ~/Photos --no-preserve
```

Move (not copy) files from memory card, automatically separating RAW and JPEG files.

### Example 4: Location-Based Organization

Edit config to enable location folders:
```yaml
geolocation:
  add_location_to_folder: true
  location_folder_pattern: "{country}/{city}"
```

Then run:
```bash
lenslogic -s ~/Travel/Photos -d ~/Travel/Organized
```

### Example 5: Configuration Wizard (New!)

```bash
# Full interactive wizard
lenslogic --config-wizard

# Quick setup for beginners
lenslogic --quick-setup
```

Set up LensLogic with guided configuration.

### Example 6: Advanced Statistics (New!)

```bash
# Generate comprehensive statistics with charts
lenslogic --advanced-stats

# Save charts to specific directory
lenslogic --advanced-stats --chart-dir ~/Photos/Analytics
```

Analyze your photo library with detailed statistics and visual charts.

### Example 7: Session Detection (New!)

```bash
# Detect shooting sessions
lenslogic --detect-sessions

# Detect and organize by sessions
lenslogic --detect-sessions --organize-sessions
```

Group photos by shooting sessions based on time and location.

### Example 8: Social Media Optimization (New!)

```bash
# Optimize for Instagram posts
lenslogic --social-media instagram

# Optimize for Instagram stories
lenslogic --social-media instagram --social-format story

# Optimize for Facebook with custom output
lenslogic --social-media facebook --social-output ~/Social/Facebook
```

Automatically resize and optimize images for social media platforms.

### Example 9: Backup and Sync (New!)

```bash
# Backup to configured destinations
lenslogic --backup

# Backup to specific locations
lenslogic --backup-to /media/backup1 /media/backup2

# Verify backup integrity
lenslogic --verify-backup
```

Incremental backup with integrity verification.

## Building for Distribution

To create a standalone executable:

```bash
# Install PyInstaller
pip install pyinstaller

# Build using spec file
pyinstaller lenslogic.spec

# Or build with custom options
pyinstaller --onefile --name lenslogic \
  --add-data "config/default_config.yaml:config" \
  src/main.py
```

## Troubleshooting

### Common Issues

1. **"No EXIF data found"**: Some image formats may not contain EXIF data. The tool will use file modification date as fallback.

2. **Geolocation not working**: Ensure you have internet connection for reverse geocoding. The tool caches lookups to minimize API calls.

3. **Duplicate detection slow**: For large libraries, use "hash" method instead of "pixel" or "histogram" for faster processing.

4. **Permission errors**: Ensure you have read/write permissions for source and destination directories.

## Performance Tips

- Use `--dry-run` first to preview changes
- Enable caching for geolocation lookups
- For large libraries (>10,000 files), consider processing in batches
- Use hash-based duplicate detection for speed
- Disable verbose output for faster processing

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.
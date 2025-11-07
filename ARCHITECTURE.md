# LensLogic Architecture Documentation

## Table of Contents
1. [Overview](#overview)
2. ### [System Architecture](#system-architecture)
3. [Core Modules](#core-modules)
4. [Process Flows](#process-flows)
5. [Data Flow Diagrams](#data-flow-diagrams)
6. [Configuration System](#configuration-system)
7. [Module Interactions](#module-interactions)
8. [Advanced Features](#advanced-features)

## Overview

LensLogic is a sophisticated photo and video organization tool that leverages metadata extraction to intelligently organize media files. The system follows a modular architecture with clear separation of concerns, comprehensive configuration options, and professional-grade features suitable for both casual users and photography professionals.

### Key Capabilities
- **Intelligent Organization**: Date, location, and camera-based folder structures
- **Metadata Extraction**: Comprehensive EXIF, XMP, and video metadata processing
- **Geolocation Services**: GPS extraction and reverse geocoding
- **Professional Workflows**: Adobe Lightroom/Camera Raw integration
- **Backup & Verification**: Incremental sync with integrity checking
- **Advanced Analytics**: Usage statistics and shooting pattern analysis

## System Architecture

### High-Level Architecture

```mermaid
graph TB
    subgraph "User Interface Layer"
        CLI[Command Line Interface]
        IM[Interactive Menu]
        CW[Configuration Wizard]
    end

    subgraph "Core Orchestration"
        LL[LensLogic Main Class]
        CM[Configuration Manager]
        PT[Progress Tracker]
    end

    subgraph "Processing Modules"
        EE[Enhanced EXIF Extractor]
        VE[Video Extractor]
        FR[File Renamer]
        FO[Folder Organizer]
        DD[Duplicate Detector]
        SD[Session Detector]
    end

    subgraph "Services"
        GS[Geolocation Service]
        BM[Backup Manager]
        SG[Statistics Generator]
        XA[XMP Analyzer]
        IP[Image Processor]
    end

    subgraph "Utilities"
        CS[Camera Slugger]
        SP[Sidecar Processor]
    end

    subgraph "External Dependencies"
        ET[ExifTool]
        MI[MediaInfo]
        NOM[Nominatim API]
        PIL[Pillow/PIL]
    end

    CLI --> LL
    IM --> LL
    CW --> CM

    LL --> CM
    LL --> PT
    LL --> EE
    LL --> VE
    LL --> FR
    LL --> FO
    LL --> DD
    LL --> SD
    LL --> GS
    LL --> BM
    LL --> SG
    LL --> XA
    LL --> IP

    EE --> ET
    EE --> PIL
    VE --> MI
    GS --> NOM
    FR --> CS
    FO --> CS
    IP --> PIL
```

### Component Layers

1. **User Interface Layer**: CLI, Interactive Menu, Configuration Wizard
2. **Core Orchestration**: Main application logic and configuration management
3. **Processing Modules**: Core file processing and organization logic
4. **Services**: Advanced features and analytics
5. **Utilities**: Helper functions and specialized processors
6. **External Dependencies**: Third-party libraries and APIs

## Core Modules

### 1. Enhanced EXIF Extractor (`enhanced_exif_extractor.py`)

**Purpose**: Comprehensive metadata extraction from photos and videos using multiple engines.

**Key Features**:
- Multi-engine support (PyExifTool, PIL, exif library)
- Video metadata integration via MediaInfo
- Metadata caching for performance
- Comprehensive field extraction (camera, GPS, technical settings)

**Key Methods**:
- `extract_metadata(file_path)`: Main extraction method
- `_extract_with_exiftool()`: Professional-grade extraction
- `_extract_gps_with_exiftool()`: GPS data extraction
- `_extract_professional_metadata()`: Advanced camera settings

### 2. Video Extractor (`enhanced_video_extractor.py`)

**Purpose**: Specialized video metadata extraction using MediaInfo.

**Key Features**:
- Support for 20+ video formats
- Technical metadata (codec, bitrate, resolution, duration)
- Audio track information
- Professional video format support

**Key Methods**:
- `extract_metadata(file_path)`: Main video extraction
- `_extract_with_mediainfo()`: MediaInfo integration
- `_process_video_track()`: Video stream analysis
- `_process_audio_track()`: Audio stream analysis

### 3. File Renamer (`file_renamer.py`)

**Purpose**: Intelligent file renaming using metadata-driven templates.

**Key Features**:
- Flexible naming patterns with metadata variables
- Camera name simplification via slugging
- Automatic sequence numbering for duplicates
- Cross-platform filename sanitization

**Template Variables**:
- Date/time: `{year}`, `{month}`, `{day}`, `{time}`
- Camera: `{camera}`, `{camera_make}`, `{camera_model}`
- Technical: `{iso}`, `{f_number}`, `{exposure}`, `{focal_length}`
- Location: `{has_gps}`, `{latitude}`, `{longitude}`

### 4. Folder Organizer (`folder_organizer.py`)

**Purpose**: Dynamic folder structure creation based on metadata.

**Key Features**:
- Date-based hierarchical organization
- Location-aware folder structures
- File type separation (RAW/JPEG/Video)
- Customizable folder templates

**Folder Structure Templates**:
- Basic: `{year}/{month:02d}/{day:02d}`
- With location: `{year}/{month:02d}/{day:02d}/{city}`
- Camera-based: `{year}/{camera}/{month:02d}`

### 5. Geolocation Service (`geolocation.py`)

**Purpose**: GPS coordinate extraction and reverse geocoding.

**Key Features**:
- EXIF GPS data extraction
- Reverse geocoding via Nominatim API
- Location caching to minimize API calls
- KML export for geographic visualization

**Key Methods**:
- `extract_gps_from_metadata()`: GPS coordinate extraction
- `get_location_info()`: Reverse geocoding
- `export_locations_to_kml()`: Geographic data export

### 6. Duplicate Detector (`duplicate_detector.py`)

**Purpose**: Intelligent duplicate file detection and handling.

**Key Features**:
- Multiple detection algorithms (hash, pixel comparison, histogram)
- Configurable actions (skip, rename, move)
- Performance optimization with caching
- Similarity threshold configuration

**Detection Methods**:
- File hash comparison (fastest)
- Pixel-by-pixel comparison (most accurate)
- Histogram analysis (perceptual similarity)

### 7. Session Detector (`session_detector.py`)

**Purpose**: Automatic detection and grouping of photo shooting sessions.

**Key Features**:
- Time-based session detection
- Geographic proximity grouping
- Configurable time and distance thresholds
- Session naming and organization

### 8. Backup Manager (`backup_manager.py`)

**Purpose**: Incremental backup with integrity verification.

**Key Features**:
- Incremental sync (only changed files)
- SHA256 checksum verification
- Multiple destination support
- Progress tracking and statistics

**Key Methods**:
- `incremental_sync()`: Smart backup process
- `verify_backup()`: Integrity checking
- `calculate_file_checksum()`: File integrity validation

### 9. Statistics Generator (`statistics_generator.py`)

**Purpose**: Comprehensive analytics and reporting.

**Key Features**:
- Camera and lens usage statistics
- Shooting pattern analysis
- Matplotlib-based visualization
- Detailed reporting capabilities

**Analytics Provided**:
- Camera brand and model distribution
- Lens usage patterns
- ISO, aperture, and shutter speed trends
- Shooting time patterns
- Location-based statistics

### 10. XMP Analyzer (`xmp_analyzer.py`)

**Purpose**: Professional workflow integration with Adobe products.

**Key Features**:
- XMP sidecar file analysis
- Adobe Lightroom library integration
- Comprehensive metadata reporting
- Professional workflow statistics

## Process Flows

### Main Photo Organization Workflow

```mermaid
flowchart TD
    A[Start: User Initiates Organization] --> B[Load Configuration]
    B --> C[Scan Source Directory]
    C --> D[Filter Supported File Types]
    D --> E[Process Each File]

    E --> F[Extract Metadata]
    F --> G{Metadata Extracted?}
    G -->|Yes| H[Enhance with GPS Data]
    G -->|No| I[Use File Properties]

    H --> J[Determine Destination Path]
    I --> J

    J --> K[Generate New Filename]
    K --> L{Check for Duplicates}
    L -->|Found| M[Apply Duplicate Strategy]
    L -->|None| N[Create Destination Directory]
    M --> N

    N --> O[Copy/Move File]
    O --> P{Generate Sidecar?}
    P -->|Yes| Q[Create XMP Sidecar]
    P -->|No| R[Update Progress]
    Q --> R

    R --> S{More Files?}
    S -->|Yes| E
    S -->|No| T[Generate Statistics]
    T --> U[Display Summary]
    U --> V[End]
```

### Metadata Extraction Process

```mermaid
flowchart TD
    A[File Input] --> B{File Type?}
    B -->|Image| C[Enhanced EXIF Extractor]
    B -->|Video| D[Video Extractor]

    C --> E{ExifTool Available?}
    E -->|Yes| F[Extract with ExifTool]
    E -->|No| G[Fallback to PIL/exif]

    F --> H[Professional Metadata]
    G --> I[Basic Metadata]

    D --> J{MediaInfo Available?}
    J -->|Yes| K[Extract with MediaInfo]
    J -->|No| L[Basic File Properties]

    K --> M[Comprehensive Video Data]
    L --> N[Limited Video Data]

    H --> O[Merge with File Properties]
    I --> O
    M --> O
    N --> O

    O --> P[Cache Metadata]
    P --> Q[Return Metadata Dict]
```

### Configuration Loading Process

```mermaid
flowchart TD
    A[Application Start] --> B[Load Default Config]
    B --> C[Check User Config Directory]
    C --> D{User Config Exists?}
    D -->|Yes| E[Load User Config]
    D -->|No| F[Create Default User Config]

    E --> G[Merge Configurations]
    F --> G

    G --> H[Parse CLI Arguments]
    H --> I[Apply CLI Overrides]
    I --> J[Validate Configuration]
    J --> K{Valid?}
    K -->|Yes| L[Configuration Ready]
    K -->|No| M[Show Configuration Errors]
    M --> N[Exit or Fix Config]

    L --> O[Initialize Modules]
```

### Geolocation Enhancement Process

```mermaid
flowchart TD
    A[Metadata with GPS Coordinates] --> B{GPS Data Present?}
    B -->|No| C[Skip Geolocation]
    B -->|Yes| D[Check Location Cache]

    D --> E{Cache Hit?}
    E -->|Yes| F[Return Cached Location]
    E -->|No| G[Call Nominatim API]

    G --> H{API Success?}
    H -->|Yes| I[Parse Location Data]
    H -->|No| J[Log Error & Continue]

    I --> K[Cache Location Data]
    K --> L[Add to Metadata]
    F --> L
    J --> M[Return Original Metadata]
    L --> N[Enhanced Metadata]

    C --> M
    M --> O[Continue Processing]
    N --> O
```

## Data Flow Diagrams

### Overall Data Flow

```mermaid
flowchart LR
    subgraph "Input Sources"
        SF[Source Files]
        UC[User Config]
        CC[CLI Commands]
    end

    subgraph "Processing Pipeline"
        ME[Metadata Extraction]
        FP[File Processing]
        OR[Organization Rules]
        QA[Quality Assurance]
    end

    subgraph "Output Destinations"
        OF[Organized Files]
        SF_OUT[Sidecar Files]
        RP[Reports]
        ST[Statistics]
        BK[Backups]
    end

    subgraph "External Services"
        GPS[GPS/Geolocation]
        API[External APIs]
    end

    SF --> ME
    UC --> OR
    CC --> OR

    ME --> FP
    OR --> FP
    GPS --> ME
    API --> ME

    FP --> QA
    QA --> OF
    QA --> SF_OUT
    QA --> RP
    QA --> ST
    QA --> BK
```

### Module Interaction Flow

```mermaid
flowchart TD
    subgraph "Core Layer"
        LL[LensLogic Main]
        CM[Config Manager]
    end

    subgraph "Processing Layer"
        EE[EXIF Extractor]
        VE[Video Extractor]
        FR[File Renamer]
        FO[Folder Organizer]
    end

    subgraph "Enhancement Layer"
        GS[Geolocation Service]
        DD[Duplicate Detector]
        SD[Session Detector]
    end

    subgraph "Output Layer"
        BM[Backup Manager]
        SG[Statistics Generator]
        SP[Sidecar Processor]
    end

    LL --> CM
    LL --> EE
    LL --> VE
    EE --> GS
    VE --> GS
    EE --> FR
    VE --> FR
    FR --> FO
    FO --> DD
    DD --> SD
    SD --> BM
    BM --> SG
    SG --> SP

    CM -.-> EE
    CM -.-> VE
    CM -.-> FR
    CM -.-> FO
    CM -.-> GS
    CM -.-> DD
    CM -.-> SD
    CM -.-> BM
    CM -.-> SG
    CM -.-> SP
```

## Configuration System

### Configuration Hierarchy

```mermaid
flowchart TD
    A[Default Config YAML] --> B[User Config Directory]
    B --> C[Custom Config File]
    C --> D[Environment Variables]
    D --> E[CLI Arguments]
    E --> F[Runtime Overrides]

    F --> G[Final Configuration]

    subgraph "Configuration Sections"
        H[General Settings]
        I[File Type Definitions]
        J[Organization Rules]
        K[Naming Patterns]
        L[Feature Toggles]
        M[Service Settings]
    end

    G --> H
    G --> I
    G --> J
    G --> K
    G --> L
    G --> M
```

### Configuration Flow

The configuration system follows a hierarchical approach where each level can override the previous:

1. **Default Configuration** (`config/default_config.yaml`): Base settings
2. **User Configuration** (`~/.lenslogic/config.yaml`): User preferences
3. **Custom Configuration**: Specified via `--config` parameter
4. **CLI Arguments**: Command-line overrides
5. **Runtime Updates**: Interactive menu modifications

## Module Interactions

### Metadata Processing Chain

```mermaid
sequenceDiagram
    participant U as User
    participant LL as LensLogic
    participant EE as EXIF Extractor
    participant VE as Video Extractor
    participant GS as Geolocation Service
    participant FR as File Renamer
    participant FO as Folder Organizer

    U->>LL: Start Organization
    LL->>EE: Extract Photo Metadata
    EE-->>LL: Photo Metadata
    LL->>VE: Extract Video Metadata
    VE-->>LL: Video Metadata
    LL->>GS: Enhance with GPS
    GS-->>LL: Location Data
    LL->>FR: Generate New Name
    FR-->>LL: New Filename
    LL->>FO: Determine Destination
    FO-->>LL: Destination Path
    LL-->>U: File Organized
```

### Backup and Verification Flow

```mermaid
sequenceDiagram
    participant U as User
    participant LL as LensLogic
    participant BM as Backup Manager
    participant FS as File System

    U->>LL: Request Backup
    LL->>BM: Initialize Backup
    BM->>FS: Scan Source Directory
    FS-->>BM: File List
    BM->>BM: Calculate Checksums
    BM->>FS: Copy Changed Files
    FS-->>BM: Copy Status
    BM->>BM: Verify Integrity
    BM-->>LL: Backup Complete
    LL-->>U: Backup Summary
```

## Advanced Features

### Session Detection Algorithm

```mermaid
flowchart TD
    A[Photo Collection] --> B[Sort by Timestamp]
    B --> C[Initialize First Session]
    C --> D[Process Next Photo]
    D --> E{Time Gap > Threshold?}
    E -->|No| F{Location Change > Threshold?}
    E -->|Yes| G[Start New Session]
    F -->|No| H[Add to Current Session]
    F -->|Yes| G
    G --> I[Name Session]
    H --> J{More Photos?}
    I --> J
    J -->|Yes| D
    J -->|No| K[Finalize Sessions]
```

### Duplicate Detection Strategy

```mermaid
flowchart TD
    A[File Comparison Request] --> B{Quick Hash Match?}
    B -->|Yes| C[Mark as Duplicate]
    B -->|No| D{Enable Deep Analysis?}
    D -->|No| E[Mark as Unique]
    D -->|Yes| F[Pixel Comparison]
    F --> G{Similarity > Threshold?}
    G -->|Yes| H[Perceptual Duplicate]
    G -->|No| I[Histogram Analysis]
    I --> J{Histogram Match?}
    J -->|Yes| K[Similar Content]
    J -->|No| E

    C --> L[Apply Duplicate Action]
    H --> L
    K --> L
    E --> M[Continue Processing]
    L --> M
```

### Performance Optimization

The system implements several performance optimizations:

1. **Metadata Caching**: Avoids re-extracting metadata for unchanged files
2. **Incremental Processing**: Only processes new or modified files
3. **Parallel Processing**: Multi-threaded file processing where appropriate
4. **Memory Management**: Efficient handling of large image files
5. **API Rate Limiting**: Respectful usage of external geolocation services

### Error Handling Strategy

```mermaid
flowchart TD
    A[Operation Start] --> B[Try Primary Method]
    B --> C{Success?}
    C -->|Yes| D[Continue Processing]
    C -->|No| E[Log Error Details]
    E --> F{Fallback Available?}
    F -->|Yes| G[Try Fallback Method]
    F -->|No| H[Graceful Degradation]
    G --> I{Fallback Success?}
    I -->|Yes| J[Continue with Limitations]
    I -->|No| H
    H --> K[Log Warning & Continue]
    D --> L[Operation Complete]
    J --> L
    K --> L
```

This comprehensive architecture provides a robust, scalable foundation for photo organization with clear separation of concerns, extensive configuration options, and professional-grade features suitable for both casual users and photography professionals.

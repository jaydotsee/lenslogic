# -*- mode: python ; coding: utf-8 -*-

import sys
from pathlib import Path

# Get the path to the project root
project_root = Path.cwd()
src_path = project_root / "src"

# Add src to Python path
sys.path.insert(0, str(src_path))

a = Analysis(
    ['src/main.py'],
    pathex=[str(src_path)],
    binaries=[],
    datas=[
        ('config/default_config.yaml', 'config'),
    ],
    hiddenimports=[
        # Rich modules - include all rich submodules
        'rich',
        'rich.console',
        'rich.panel',
        'rich.table',
        'rich.columns',
        'rich.layout',
        'rich.text',
        'rich.align',
        'rich.progress',
        'rich.progress.Progress',
        'rich.progress.SpinnerColumn',
        'rich.progress.TextColumn',
        'rich.progress.BarColumn',
        'rich.progress.TaskProgressColumn',
        'rich.progress.TimeRemainingColumn',
        'rich.status',
        'rich.markdown',
        'rich.syntax',
        'rich.traceback',
        'rich.pretty',
        'rich.prompt',
        'rich.tree',
        'rich.spinner',
        'rich.bar',

        # Questionary
        'questionary',
        'questionary.prompts',
        'questionary.prompts.text',
        'questionary.prompts.confirm',
        'questionary.prompts.select',
        'questionary.prompts.checkbox',
        'questionary.prompts.rawselect',
        'questionary.prompts.expand',
        'questionary.prompts.path',
        'questionary.prompts.press_any_key_to_continue',
        'questionary.prompts.autocomplete',

        # Other dependencies
        'yaml',
        'PIL',
        'PIL.Image',
        'PIL.ImageOps',
        'PIL.ExifTags',
        'exifread',
        'geopy',
        'geopy.geocoders',
        'geopy.geocoders.nominatim',
        'dateutil',
        'dateutil.parser',
        'pathvalidate',
        'colorama',
        'click',
        'numpy',
        'imagehash',
        'send2trash',

        # Standard library modules that sometimes need explicit inclusion
        'sqlite3',
        'json',
        'csv',
        'logging',
        'logging.handlers',
        'hashlib',
        'shutil',
        'tempfile',
        'pathlib',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Exclude unnecessary modules to reduce size
        'tkinter',
        'pandas',
        'scipy',
        'jupyter',
        'notebook',
        'IPython',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='lenslogic',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)

# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for STT Keyboard

This file configures how PyInstaller bundles the application into an executable.
"""

import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# Collect all data files
datas = [
    ('src/stt_keyboard/config/default_config.yaml', 'stt_keyboard/config'),
]

# Optional: Include a default model (uncomment and adjust path)
# WARNING: This will significantly increase executable size
# datas += [
#     ('models/vosk-model-small-en-us-0.15', 'models/vosk-model-small-en-us-0.15'),
# ]

# Collect Vosk data files
datas += collect_data_files('vosk')

# Hidden imports that PyInstaller might miss
hiddenimports = [
    'vosk',
    'sounddevice',
    'numpy',
    'keyboard',
    'pyyaml',
    'pydantic',
    'PyQt6.QtCore',
    'PyQt6.QtGui',
    'PyQt6.QtWidgets',
]

# Additional hidden imports for plugins
hiddenimports += collect_submodules('stt_keyboard.plugins')

# Binaries (if any platform-specific libraries needed)
binaries = []

# Analysis
a = Analysis(
    ['launcher.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'scipy',
        'pandas',
        'PIL',
        'tkinter',
        'test',
        'unittest',
        'pytest',
    ],
    noarchive=False,
)

# Remove duplicate or unnecessary files
pyz = PYZ(a.pure)

# Executable configuration
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='STTKeyboard',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,  # Compress with UPX if available
    console=False,  # Set to True for debugging
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Set to 'resources/icon.ico' if you have an icon file
)

# Collect files for distribution
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='STTKeyboard',
)

# macOS .app bundle
if sys.platform == 'darwin':
    app = BUNDLE(
        coll,
        name='STTKeyboard.app',
        icon='resources/icon.icns',  # Add icon if available
        bundle_identifier='com.stt-keyboard.app',
        info_plist={
            'NSPrincipalClass': 'NSApplication',
            'NSHighResolutionCapable': 'True',
            'NSMicrophoneUsageDescription': 'STT Keyboard needs access to your microphone for speech recognition.',
            'NSAppleEventsUsageDescription': 'STT Keyboard needs to control keyboard input.',
        },
    )

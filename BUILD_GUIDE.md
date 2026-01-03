# Building Standalone Executables

This guide explains how to build standalone executables for Windows, macOS, and Linux so users can run the application without installing Python.

## Prerequisites

Install PyInstaller:
```bash
pip install pyinstaller
```

## Platform-Specific Builds

### Windows (.exe)

**On a Windows machine:**

```bash
# 1. Install dependencies
pip install -r requirements.txt
pip install pyinstaller

# 2. Build the executable
python scripts/build_exe.py --platform windows

# Output: dist/STTKeyboard.exe
```

**Notes for Windows:**
- The EXE will be in `dist/STTKeyboard/`
- Include the entire folder when distributing (contains DLLs)
- For a single-file EXE, use the `--onefile` option
- May need to run as administrator for hotkey support

### macOS (.app)

**On a macOS machine:**

```bash
# 1. Install dependencies
pip install -r requirements.txt
pip install pyinstaller

# 2. Build the application
python scripts/build_exe.py --platform macos

# Output: dist/STTKeyboard.app
```

**Creating a DMG installer:**
```bash
# Install create-dmg
brew install create-dmg

# Create DMG
python scripts/build_exe.py --platform macos --create-dmg

# Output: dist/STTKeyboard.dmg
```

**Notes for macOS:**
- Requires Accessibility and Microphone permissions
- May need to sign the app for distribution
- Users need to right-click > Open first time (if not signed)

### Linux (AppImage)

**On a Linux machine:**

```bash
# 1. Install dependencies
pip install -r requirements.txt
pip install pyinstaller

# 2. Build the executable
python scripts/build_exe.py --platform linux

# Output: dist/STTKeyboard
```

**Creating an AppImage:**
```bash
# Download AppImage tools
wget https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage
chmod +x appimagetool-x86_64.AppImage

# Build AppImage
python scripts/build_exe.py --platform linux --create-appimage

# Output: dist/STTKeyboard.AppImage
```

## PyInstaller Spec File

The build process uses `stt-keyboard.spec` which you can customize:

```bash
# Generate a spec file (if you want to customize)
pyi-makespec --windowed --onedir src/stt_keyboard/__main__.py --name STTKeyboard

# Build using the spec file
pyinstaller stt-keyboard.spec
```

## Including Speech Models

**Option 1: Separate Download (Recommended)**
- Keep the executable small
- Users download models after installation
- Include the `download_model.py` script in the distribution

**Option 2: Bundle Model**
- Include a default model in the executable
- Much larger file size (40MB-1.8GB)
- Edit `stt-keyboard.spec` to include model files:

```python
datas=[
    ('models/vosk-model-small-en-us-0.15', 'models/vosk-model-small-en-us-0.15'),
],
```

## Reducing Executable Size

1. **Use UPX compression:**
```bash
# Install UPX
# Windows: https://github.com/upx/upx/releases
# macOS: brew install upx
# Linux: sudo apt install upx

# Build with compression
pyinstaller --upx-dir=/path/to/upx stt-keyboard.spec
```

2. **Exclude unnecessary packages:**
Edit `stt-keyboard.spec` to exclude unused modules:
```python
excludes=[
    'matplotlib',
    'scipy',
    'pandas',
    'PIL',
]
```

3. **Use --onefile for single executable:**
```bash
pyinstaller --onefile stt-keyboard.spec
```
**Trade-off:** Slower startup, but easier distribution

## Distribution Checklist

- [ ] Build executable for target platform
- [ ] Test on clean system (without Python installed)
- [ ] Include README with usage instructions
- [ ] Include download_model.py script (or bundle a model)
- [ ] Include LICENSE file
- [ ] Create installer (optional but recommended)

## Creating Installers

### Windows Installer (Inno Setup)

1. Download and install [Inno Setup](https://jrsoftware.org/isinfo.php)
2. Use the included `installer.iss` script
3. Build the installer

### macOS DMG

```bash
create-dmg \
  --volname "STT Keyboard" \
  --window-pos 200 120 \
  --window-size 600 300 \
  --icon-size 100 \
  --app-drop-link 425 120 \
  "STTKeyboard.dmg" \
  "dist/STTKeyboard.app"
```

### Linux Package

**Debian/Ubuntu (.deb):**
```bash
# Use the provided debian/ directory
dpkg-buildpackage -us -uc
```

## Troubleshooting

### Missing DLLs on Windows
- Install Visual C++ Redistributable
- Include in installer or document requirement

### "App is damaged" on macOS
- Code sign the application
- Or tell users to: `xattr -cr STTKeyboard.app`

### Permission errors on Linux
- Make AppImage executable: `chmod +x STTKeyboard.AppImage`
- Document need for input permissions

### Large executable size
- Use `--exclude-module` for unused packages
- Don't bundle speech models
- Use UPX compression

## Automated Build Script

Use the provided build script for easy cross-platform builds:

```bash
# Build for current platform
python scripts/build_exe.py

# Build with specific options
python scripts/build_exe.py --platform windows --onefile --compress

# Build and create installer
python scripts/build_exe.py --platform windows --installer
```

## CI/CD Builds

For automated builds on GitHub Actions, see `.github/workflows/build.yml`

This will automatically build executables for all platforms when you create a release.

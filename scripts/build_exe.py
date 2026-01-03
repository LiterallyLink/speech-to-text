#!/usr/bin/env python3
"""
Build script for creating standalone executables

This script automates the process of building executables for different platforms
using PyInstaller.
"""

import argparse
import platform
import subprocess
import sys
import shutil
from pathlib import Path


def get_current_platform():
    """Detect current platform"""
    system = platform.system()
    if system == "Windows":
        return "windows"
    elif system == "Darwin":
        return "macos"
    elif system == "Linux":
        return "linux"
    else:
        return "unknown"


def check_pyinstaller():
    """Check if PyInstaller is installed"""
    try:
        import PyInstaller
        return True
    except ImportError:
        return False


def clean_build_dirs():
    """Clean previous build artifacts"""
    print("Cleaning previous builds...")

    dirs_to_clean = ['build', 'dist']
    for dir_name in dirs_to_clean:
        dir_path = Path(dir_name)
        if dir_path.exists():
            shutil.rmtree(dir_path)
            print(f"  Removed {dir_name}/")

    # Remove spec files if auto-generated
    for spec_file in Path('.').glob('*.spec'):
        if spec_file.name != 'stt-keyboard.spec':
            spec_file.unlink()
            print(f"  Removed {spec_file}")


def build_executable(platform_name, onefile=False, compress=True):
    """
    Build executable using PyInstaller

    Args:
        platform_name: Target platform (windows, macos, linux)
        onefile: Create single-file executable
        compress: Use UPX compression
    """
    print(f"\nBuilding executable for {platform_name}...")

    # Check if spec file exists
    spec_file = Path('stt-keyboard.spec')
    if not spec_file.exists():
        print("Error: stt-keyboard.spec not found!")
        return False

    # Build PyInstaller command
    cmd = ['pyinstaller']

    if onefile:
        cmd.append('--onefile')

    if not compress:
        cmd.append('--noupx')

    # Add spec file
    cmd.append(str(spec_file))

    # Run PyInstaller
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=False)

    if result.returncode == 0:
        print("\n✓ Build successful!")

        # Show output location
        dist_dir = Path('dist')
        if platform_name == 'macos':
            output = dist_dir / 'STTKeyboard.app'
        elif onefile:
            exe_name = 'STTKeyboard.exe' if platform_name == 'windows' else 'STTKeyboard'
            output = dist_dir / exe_name
        else:
            output = dist_dir / 'STTKeyboard'

        print(f"\nExecutable location: {output}")

        # Include helper script in dist
        copy_helper_files(dist_dir, platform_name)

        return True
    else:
        print("\n✗ Build failed!")
        return False


def copy_helper_files(dist_dir, platform_name):
    """Copy necessary helper files to distribution directory"""
    print("\nCopying helper files...")

    files_to_copy = [
        ('README.md', 'README.md'),
        ('QUICKSTART.md', 'QUICKSTART.md'),
        ('scripts/download_model.py', 'download_model.py'),
        ('requirements.txt', 'requirements.txt'),
    ]

    for src, dst in files_to_copy:
        src_path = Path(src)
        if src_path.exists():
            dst_path = dist_dir / dst
            shutil.copy2(src_path, dst_path)
            print(f"  Copied {src} -> {dst_path}")


def create_windows_installer(dist_dir):
    """Create Windows installer using Inno Setup"""
    print("\nCreating Windows installer...")

    iss_file = Path('installer.iss')
    if not iss_file.exists():
        print("Warning: installer.iss not found. Skipping installer creation.")
        return False

    # Check if Inno Setup is installed
    iscc_paths = [
        r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
        r"C:\Program Files\Inno Setup 6\ISCC.exe",
    ]

    iscc = None
    for path in iscc_paths:
        if Path(path).exists():
            iscc = path
            break

    if not iscc:
        print("Error: Inno Setup not found. Please install from https://jrsoftware.org/isinfo.php")
        return False

    # Run Inno Setup
    cmd = [iscc, str(iss_file)]
    result = subprocess.run(cmd)

    return result.returncode == 0


def create_macos_dmg(dist_dir):
    """Create macOS DMG installer"""
    print("\nCreating macOS DMG...")

    # Check if create-dmg is available
    result = subprocess.run(['which', 'create-dmg'], capture_output=True)
    if result.returncode != 0:
        print("Error: create-dmg not found. Install with: brew install create-dmg")
        return False

    app_path = dist_dir / 'STTKeyboard.app'
    dmg_path = dist_dir / 'STTKeyboard.dmg'

    if not app_path.exists():
        print(f"Error: {app_path} not found!")
        return False

    # Remove old DMG if exists
    if dmg_path.exists():
        dmg_path.unlink()

    cmd = [
        'create-dmg',
        '--volname', 'STT Keyboard',
        '--window-pos', '200', '120',
        '--window-size', '600', '300',
        '--icon-size', '100',
        '--app-drop-link', '425', '120',
        str(dmg_path),
        str(app_path),
    ]

    result = subprocess.run(cmd)
    return result.returncode == 0


def create_linux_appimage(dist_dir):
    """Create Linux AppImage"""
    print("\nCreating Linux AppImage...")
    print("Note: AppImage creation requires manual setup.")
    print("See: https://appimage.org/")

    # This is a placeholder - full AppImage creation is complex
    print("\nTo create an AppImage:")
    print("1. Create AppDir structure")
    print("2. Copy files to AppDir")
    print("3. Use appimagetool to create AppImage")

    return False


def main():
    parser = argparse.ArgumentParser(description='Build STT Keyboard executables')

    parser.add_argument(
        '--platform',
        choices=['windows', 'macos', 'linux', 'auto'],
        default='auto',
        help='Target platform (default: auto-detect)'
    )

    parser.add_argument(
        '--onefile',
        action='store_true',
        help='Create single-file executable (slower startup)'
    )

    parser.add_argument(
        '--no-compress',
        action='store_true',
        help='Disable UPX compression'
    )

    parser.add_argument(
        '--clean',
        action='store_true',
        help='Clean build directories before building'
    )

    parser.add_argument(
        '--installer',
        action='store_true',
        help='Create installer (Windows: .exe, macOS: .dmg, Linux: .AppImage)'
    )

    parser.add_argument(
        '--no-build',
        action='store_true',
        help='Skip building, only create installer from existing dist/'
    )

    args = parser.parse_args()

    # Check PyInstaller
    if not check_pyinstaller():
        print("Error: PyInstaller is not installed!")
        print("Install it with: pip install pyinstaller")
        sys.exit(1)

    # Determine platform
    if args.platform == 'auto':
        target_platform = get_current_platform()
        if target_platform == 'unknown':
            print("Error: Could not detect platform!")
            sys.exit(1)
        print(f"Auto-detected platform: {target_platform}")
    else:
        target_platform = args.platform

    # Warn about cross-compilation
    current_platform = get_current_platform()
    if target_platform != current_platform:
        print(f"Warning: Building for {target_platform} on {current_platform}")
        print("Cross-compilation may not work correctly!")
        response = input("Continue? (y/N): ")
        if response.lower() != 'y':
            sys.exit(0)

    # Clean if requested
    if args.clean:
        clean_build_dirs()

    # Build executable
    if not args.no_build:
        success = build_executable(
            target_platform,
            onefile=args.onefile,
            compress=not args.no_compress
        )

        if not success:
            sys.exit(1)

    # Create installer if requested
    if args.installer:
        dist_dir = Path('dist')

        if target_platform == 'windows':
            create_windows_installer(dist_dir)
        elif target_platform == 'macos':
            create_macos_dmg(dist_dir)
        elif target_platform == 'linux':
            create_linux_appimage(dist_dir)

    print("\n✓ Build complete!")
    print(f"\nDistribution files are in: dist/")

    # Show next steps
    print("\nNext steps:")
    print("1. Test the executable on a clean system (without Python)")
    print("2. Run: dist/STTKeyboard/STTKeyboard (or STTKeyboard.exe on Windows)")
    print("3. Download a speech model: python download_model.py --language en-us --size small")
    print("4. Distribute the dist/STTKeyboard/ folder (or create an installer)")


if __name__ == '__main__':
    main()

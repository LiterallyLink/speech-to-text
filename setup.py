"""Setup script for STT Keyboard"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text() if readme_file.exists() else ""

setup(
    name="stt-keyboard",
    version="1.0.0",
    author="STT Keyboard Team",
    description="System-wide offline speech-to-text keyboard input",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/stt-keyboard",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.10",
    install_requires=[
        "PyQt6>=6.6.0",
        "vosk>=0.3.45",
        "sounddevice>=0.4.6",
        "keyboard>=0.13.5",
        "pyyaml>=6.0",
        "pydantic>=2.5.0",
        "numpy>=1.24.0,<2.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "stt-keyboard=stt_keyboard.app:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Multimedia :: Sound/Audio :: Speech",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    keywords="speech-to-text voice-recognition keyboard dictation offline",
)

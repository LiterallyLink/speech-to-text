#!/usr/bin/env python3
"""
Vosk Model Download Utility

Downloads and manages Vosk speech recognition models for different languages.
"""

import argparse
import json
import sys
import urllib.request
import zipfile
from pathlib import Path
from typing import Dict, List


# Available Vosk models
# [Inference] Model URLs and sizes based on Vosk API documentation
MODELS = {
    "en-us": {
        "small": {
            "url": "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip",
            "size": "40MB",
            "name": "vosk-model-small-en-us-0.15"
        },
        "large": {
            "url": "https://alphacephei.com/vosk/models/vosk-model-en-us-0.22.zip",
            "size": "1.8GB",
            "name": "vosk-model-en-us-0.22"
        }
    },
    "en-gb": {
        "small": {
            "url": "https://alphacephei.com/vosk/models/vosk-model-small-en-gb-0.15.zip",
            "size": "40MB",
            "name": "vosk-model-small-en-gb-0.15"
        }
    },
    "en-in": {
        "small": {
            "url": "https://alphacephei.com/vosk/models/vosk-model-small-en-in-0.4.zip",
            "size": "40MB",
            "name": "vosk-model-small-en-in-0.4"
        }
    },
    "es": {
        "small": {
            "url": "https://alphacephei.com/vosk/models/vosk-model-small-es-0.42.zip",
            "size": "39MB",
            "name": "vosk-model-small-es-0.42"
        },
        "large": {
            "url": "https://alphacephei.com/vosk/models/vosk-model-es-0.42.zip",
            "size": "1.4GB",
            "name": "vosk-model-es-0.42"
        }
    },
    "fr": {
        "small": {
            "url": "https://alphacephei.com/vosk/models/vosk-model-small-fr-0.22.zip",
            "size": "41MB",
            "name": "vosk-model-small-fr-0.22"
        },
        "large": {
            "url": "https://alphacephei.com/vosk/models/vosk-model-fr-0.22.zip",
            "size": "1.4GB",
            "name": "vosk-model-fr-0.22"
        }
    },
    "de": {
        "small": {
            "url": "https://alphacephei.com/vosk/models/vosk-model-small-de-0.15.zip",
            "size": "45MB",
            "name": "vosk-model-small-de-0.15"
        },
        "large": {
            "url": "https://alphacephei.com/vosk/models/vosk-model-de-0.21.zip",
            "size": "1.9GB",
            "name": "vosk-model-de-0.21"
        }
    },
    "ru": {
        "small": {
            "url": "https://alphacephei.com/vosk/models/vosk-model-small-ru-0.22.zip",
            "size": "45MB",
            "name": "vosk-model-small-ru-0.22"
        },
        "large": {
            "url": "https://alphacephei.com/vosk/models/vosk-model-ru-0.22.zip",
            "size": "2.5GB",
            "name": "vosk-model-ru-0.22"
        }
    },
    "pt": {
        "small": {
            "url": "https://alphacephei.com/vosk/models/vosk-model-small-pt-0.3.zip",
            "size": "31MB",
            "name": "vosk-model-small-pt-0.3"
        }
    },
    "zh": {
        "small": {
            "url": "https://alphacephei.com/vosk/models/vosk-model-small-cn-0.22.zip",
            "size": "42MB",
            "name": "vosk-model-small-cn-0.22"
        },
        "large": {
            "url": "https://alphacephei.com/vosk/models/vosk-model-cn-0.22.zip",
            "size": "1.3GB",
            "name": "vosk-model-cn-0.22"
        }
    },
    "ja": {
        "small": {
            "url": "https://alphacephei.com/vosk/models/vosk-model-small-ja-0.22.zip",
            "size": "48MB",
            "name": "vosk-model-small-ja-0.22"
        }
    },
    "it": {
        "small": {
            "url": "https://alphacephei.com/vosk/models/vosk-model-small-it-0.22.zip",
            "size": "48MB",
            "name": "vosk-model-small-it-0.22"
        }
    },
    "nl": {
        "small": {
            "url": "https://alphacephei.com/vosk/models/vosk-model-small-nl-0.22.zip",
            "size": "39MB",
            "name": "vosk-model-small-nl-0.22"
        }
    },
    "uk": {
        "small": {
            "url": "https://alphacephei.com/vosk/models/vosk-model-small-uk-v3-small.zip",
            "size": "87MB",
            "name": "vosk-model-small-uk-v3-small"
        }
    }
}


def download_with_progress(url: str, dest_path: Path):
    """Download file with progress bar"""
    
    def report_progress(block_num, block_size, total_size):
        downloaded = block_num * block_size
        percent = min(100, (downloaded * 100) // total_size)
        mb_downloaded = downloaded / (1024 * 1024)
        mb_total = total_size / (1024 * 1024)
        
        bar_length = 50
        filled = int(bar_length * percent / 100)
        bar = '=' * filled + '-' * (bar_length - filled)
        
        print(f'\r[{bar}] {percent}% ({mb_downloaded:.1f}/{mb_total:.1f} MB)', end='')
        sys.stdout.flush()
    
    print(f"Downloading from {url}")
    urllib.request.urlretrieve(url, dest_path, reporthook=report_progress)
    print()  # New line after progress bar


def extract_zip(zip_path: Path, extract_to: Path):
    """Extract zip file"""
    print(f"Extracting to {extract_to}")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
    print("Extraction complete")


def list_models():
    """List all available models"""
    print("\nAvailable Vosk Models:")
    print("=" * 60)
    
    for lang, sizes in sorted(MODELS.items()):
        lang_name = {
            "en-us": "English (US)",
            "en-gb": "English (UK)",
            "en-in": "English (India)",
            "es": "Spanish",
            "fr": "French",
            "de": "German",
            "ru": "Russian",
            "pt": "Portuguese",
            "zh": "Chinese",
            "ja": "Japanese",
            "it": "Italian",
            "nl": "Dutch",
            "uk": "Ukrainian"
        }.get(lang, lang.upper())
        
        print(f"\n{lang_name} ({lang}):")
        for size, info in sizes.items():
            print(f"  {size:8} - {info['size']:>7} - {info['name']}")
    
    print("\nUsage: python download_model.py --language LANG --size SIZE")
    print("Example: python download_model.py --language en-us --size small")


def download_model(language: str, size: str, models_dir: Path):
    """Download and extract a model"""
    
    # Validate language and size
    if language not in MODELS:
        print(f"Error: Language '{language}' not found")
        print("Run with --list to see available languages")
        return False
    
    if size not in MODELS[language]:
        print(f"Error: Size '{size}' not available for language '{language}'")
        print(f"Available sizes: {', '.join(MODELS[language].keys())}")
        return False
    
    model_info = MODELS[language][size]
    model_name = model_info['name']
    model_url = model_info['url']
    
    # Create models directory
    models_dir.mkdir(parents=True, exist_ok=True)
    
    # Check if model already exists
    model_path = models_dir / model_name
    if model_path.exists():
        response = input(f"Model {model_name} already exists. Re-download? (y/n): ")
        if response.lower() != 'y':
            print("Download cancelled")
            return True
    
    # Download
    zip_path = models_dir / f"{model_name}.zip"
    try:
        download_with_progress(model_url, zip_path)
    except Exception as e:
        print(f"\nError downloading model: {e}")
        if zip_path.exists():
            zip_path.unlink()
        return False
    
    # Extract
    try:
        extract_zip(zip_path, models_dir)
    except Exception as e:
        print(f"Error extracting model: {e}")
        return False
    finally:
        # Clean up zip file
        if zip_path.exists():
            zip_path.unlink()
    
    print(f"\nModel successfully installed to: {model_path}")
    print(f"\nTo use this model, update your config.yaml:")
    print(f"  speech:")
    print(f"    model_path: \"models/{model_name}\"")
    print(f"    language: \"{language}\"")
    
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Download Vosk speech recognition models"
    )
    parser.add_argument(
        '--list', 
        action='store_true',
        help='List all available models'
    )
    parser.add_argument(
        '--language', '-l',
        type=str,
        help='Language code (e.g., en-us, es, fr)'
    )
    parser.add_argument(
        '--size', '-s',
        type=str,
        choices=['small', 'large'],
        help='Model size (small or large)'
    )
    parser.add_argument(
        '--models-dir',
        type=Path,
        default=Path('models'),
        help='Directory to save models (default: ./models)'
    )
    
    args = parser.parse_args()
    
    if args.list:
        list_models()
        return
    
    if not args.language or not args.size:
        parser.print_help()
        print("\nRun with --list to see available models")
        return
    
    success = download_model(args.language, args.size, args.models_dir)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

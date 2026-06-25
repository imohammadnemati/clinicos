#!/usr/bin/env python3
"""
Download Vosk models automatically.
Run this script during build to download all required models.
Models are downloaded from alphacephei.com and extracted to models/vosk/.
"""

import os
import sys
import requests
import zipfile
import shutil
from tqdm import tqdm

# List of models to download (name, URL)
MODELS = [
    ("vosk-model-small-en-us-0.15", "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip"),
    ("vosk-model-en-us-0.22-lgraph", "https://alphacephei.com/vosk/models/vosk-model-en-us-0.22-lgraph.zip"),
    ("vosk-model-small-tr-0.3", "https://alphacephei.com/vosk/models/vosk-model-small-tr-0.3.zip"),
    ("vosk-model-ar-mgb2-0.4", "https://alphacephei.com/vosk/models/vosk-model-ar-mgb2-0.4.zip"),
    ("vosk-model-small-fa-0.42", "https://alphacephei.com/vosk/models/vosk-model-small-fa-0.42.zip"),
    ("vosk-model-small-fa-0.5", "https://alphacephei.com/vosk/models/vosk-model-small-fa-0.5.zip"),
]

BASE_DIR = "models/vosk"
os.makedirs(BASE_DIR, exist_ok=True)


def download_file(url, dest_path):
    """Download a file with progress bar."""
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    block_size = 1024  # 1 Kibibyte
    with open(dest_path, 'wb') as f:
        for data in tqdm(
            response.iter_content(block_size),
            total=total_size // block_size,
            unit='KiB',
            unit_scale=True,
            desc=os.path.basename(dest_path)
        ):
            f.write(data)


def extract_zip(zip_path, extract_to):
    """Extract zip file and remove archive."""
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
    os.remove(zip_path)


def main():
    print("=" * 60)
    print("=== Downloading Vosk models ===")
    print("=" * 60)

    for name, url in MODELS:
        dest_dir = os.path.join(BASE_DIR, name)
        # Check if model already exists
        if os.path.exists(dest_dir) and os.path.isdir(dest_dir):
            # Check if directory is not empty
            if os.listdir(dest_dir):
                print(f"✅ Model {name} already exists, skipping.")
                continue
            else:
                # Empty directory, remove it
                os.rmdir(dest_dir)

        print(f"⬇️  Downloading {name} from {url} ...")
        zip_path = os.path.join(BASE_DIR, f"{name}.zip")
        try:
            download_file(url, zip_path)
            print(f"📦 Extracting {name} ...")
            extract_zip(zip_path, BASE_DIR)
            # The zip extracts to a folder with the same name (usually)
            # but sometimes the extracted folder name differs.
            # We'll rename it to the expected name if necessary.
            extracted_items = os.listdir(BASE_DIR)
            # Find the extracted folder (should be a directory)
            extracted_folders = [item for item in extracted_items if os.path.isdir(os.path.join(BASE_DIR, item))]
            if extracted_folders:
                extracted_folder = extracted_folders[0]
                if extracted_folder != name:
                    # Rename to the expected name
                    shutil.move(os.path.join(BASE_DIR, extracted_folder), dest_dir)
                    print(f"✅ Renamed extracted folder to {name}")
                else:
                    # It's already correct
                    print(f"✅ Model {name} installed.")
            else:
                # If no folder, maybe the zip extracted files directly? Shouldn't happen for Vosk.
                print(f"⚠️  No folder found for {name}, but zip extraction completed.")
        except Exception as e:
            print(f"❌ Failed to download/extract {name}: {e}", file=sys.stderr)
            # Clean up partial zip if exists
            if os.path.exists(zip_path):
                os.remove(zip_path)
            sys.exit(1)

    print("=" * 60)
    print("✅ All models downloaded successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()

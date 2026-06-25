#!/usr/bin/env python3
"""
Download Vosk models at runtime (lazy loading) or during build.
Models are downloaded only when needed, reducing build time and preventing timeout.
"""

import os
import sys
import requests
import zipfile
import shutil
import logging
from tqdm import tqdm

logger = logging.getLogger(__name__)

# ============================================================
# Model Configuration
# ============================================================
MODELS = {
    "vosk-model-small-fa-0.5": "https://alphacephei.com/vosk/models/vosk-model-small-fa-0.5.zip",
    "vosk-model-small-en-us-0.15": "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip",
    "vosk-model-ar-mgb2-0.4": "https://alphacephei.com/vosk/models/vosk-model-ar-mgb2-0.4.zip",
    "vosk-model-small-tr-0.3": "https://alphacephei.com/vosk/models/vosk-model-small-tr-0.3.zip",
    # Optional large models (download only if needed)
    "vosk-model-en-us-0.22-lgraph": "https://alphacephei.com/vosk/models/vosk-model-en-us-0.22-lgraph.zip",
    "vosk-model-small-fa-0.42": "https://alphacephei.com/vosk/models/vosk-model-small-fa-0.42.zip",
}

BASE_DIR = "models/vosk"
os.makedirs(BASE_DIR, exist_ok=True)


# ============================================================
# Helper Functions
# ============================================================
def download_file(url, dest_path):
    """Download a file with progress bar."""
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    block_size = 1024
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


def download_model(model_name, url):
    """Download a single model."""
    dest_dir = os.path.join(BASE_DIR, model_name)
    if os.path.exists(dest_dir) and os.listdir(dest_dir):
        logger.info(f"Model {model_name} already exists, skipping.")
        return True

    logger.info(f"Downloading {model_name} ...")
    zip_path = os.path.join(BASE_DIR, f"{model_name}.zip")
    try:
        download_file(url, zip_path)
        logger.info(f"Extracting {model_name} ...")
        extract_zip(zip_path, BASE_DIR)

        # Find extracted folder (zip might extract to a different name)
        extracted_items = os.listdir(BASE_DIR)
        extracted_folders = [
            item for item in extracted_items
            if os.path.isdir(os.path.join(BASE_DIR, item)) and item != model_name
        ]
        if extracted_folders:
            extracted_folder = extracted_folders[0]
            # Move and rename to expected name
            shutil.move(os.path.join(BASE_DIR, extracted_folder), dest_dir)
            logger.info(f"Renamed extracted folder to {model_name}")

        logger.info(f"Model {model_name} installed successfully.")
        return True
    except Exception as e:
        logger.error(f"Failed to download {model_name}: {e}")
        if os.path.exists(zip_path):
            os.remove(zip_path)
        return False


def ensure_model(model_name):
    """Ensure a specific model is downloaded. Called at runtime."""
    url = MODELS.get(model_name)
    if not url:
        logger.error(f"Unknown model: {model_name}")
        return False
    return download_model(model_name, url)


def download_all_models():
    """Download all models (called during build if needed)."""
    logger.info("=" * 60)
    logger.info("=== Downloading all Vosk models ===")
    logger.info("=" * 60)
    for name, url in MODELS.items():
        download_model(name, url)
    logger.info("=" * 60)
    logger.info("✅ All models downloaded successfully!")
    logger.info("=" * 60)


def list_available_models():
    """List installed models."""
    logger.info("Installed Vosk models:")
    for name in MODELS.keys():
        path = os.path.join(BASE_DIR, name)
        if os.path.exists(path) and os.listdir(path):
            size_mb = sum(
                os.path.getsize(os.path.join(root, f))
                for root, _, files in os.walk(path)
                for f in files
            ) / (1024 * 1024)
            logger.info(f"  ✅ {name} ({size_mb:.1f} MB)")
        else:
            logger.info(f"  ❌ {name} (not installed)")


# ============================================================
# Main Entry Point
# ============================================================
if __name__ == "__main__":
    # Configure logging for CLI
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )

    if len(sys.argv) > 1 and sys.argv[1] == "--list":
        list_available_models()
    else:
        download_all_models()

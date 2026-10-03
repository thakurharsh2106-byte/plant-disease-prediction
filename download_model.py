#!/usr/bin/env python3
"""
PlantGuard AI - Automated Model Weights Downloader
Downloads the pre-trained PyTorch model weights (201 MB) if not already present.
"""
import os
import sys

def download_weights():
    target_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Flask Deployed App')
    target_path = os.path.join(target_dir, 'plant_disease_model_1_latest.pt')

    if os.path.exists(target_path):
        print(f"✅ Model weights already exist at: {target_path}")
        return

    print("📥 Downloading pre-trained model weights (201 MB) from Google Drive...")
    try:
        import gdown
    except ImportError:
        print("Installing gdown...")
        import subprocess
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'gdown'])
        import gdown

    folder_url = "https://drive.google.com/drive/folders/1ewJWAiduGuld_9oGSrTuLumg9y62qS6A?usp=share_link"
    gdown.download_folder(folder_url, output=target_dir, quiet=False, use_cookies=False)
    print("✅ Model download complete.")

if __name__ == '__main__':
    download_weights()

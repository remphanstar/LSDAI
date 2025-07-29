#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced Downloading Integration - Fixed URL Processing
LSDAI v2.0 Enhancement Suite - Download Management Script

This script handles the complete download process for WebUI setup including:
- Virtual environment setup with custom requirements
- WebUI installation and updates  
- Extension installation from URLs
- Model and asset downloads with proper URL handling

FIXED: Corrected URL processing to handle individual downloads instead of 
concatenating multiple URLs into a single string.
FIXED: Implemented a more robust venv creation method for Colab.
"""

import os
import sys
import subprocess
import time
from pathlib import Path
import json

# --- ADDED PLATFORM CHECK AND VENV DEPENDENCY INSTALL ---
IS_DEBIAN = os.path.exists('/etc/debian_version')
# --- END ADDITION ---

# Setup environment paths
HOME = Path(os.environ.get('home_path', '/content'))
SCR_PATH = Path(os.environ.get('scr_path', HOME / 'LSDAI'))
VENV_PATH = Path(os.environ.get('venv_path', HOME / 'venv'))
SETTINGS_PATH = Path(os.environ.get('settings_path', SCR_PATH / 'settings.json'))
SCRIPTS_PATH = SCR_PATH / 'scripts'

# Add modules to Python path for imports
if str(SCR_PATH / 'modules') not in sys.path:
    sys.path.insert(0, str(SCR_PATH / 'modules'))

# Import required modules
try:
    import json_utils as js
    from webui_utils import get_current_webui, get_webui_config, get_extensions_directory
    print("✅ Core modules imported successfully.")
except ImportError as e:
    print(f"❌ Failed to import core modules: {e}")
    print("   Make sure the LSDAI project structure is properly set up.")
    sys.exit(1)

# Enhanced downloader header
print("--- LSDAI ENHANCED DOWNLOADER ---")
print(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
print("===================================")

# 1. VIRTUAL ENVIRONMENT SETUP (ROBUST VERSION)
# ---------------------------------------------
print("\n🐍 1. Setting up Virtual Environment...")
print(f"   - Target Venv Path: {VENV_PATH}")

try:
    if IS_DEBIAN and not VENV_PATH.exists():
        print("   - Debian-based system detected. Ensuring python3-venv is installed.")
        try:
            subprocess.run(['apt-get', 'update', '-qq'], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
            subprocess.run(['apt-get', 'install', '-y', '-qq', 'python3-venv'], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
            print("     ✅ python3-venv installed or already present.")
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            print(f"   - ⚠️  Could not install python3-venv. This may cause issues. Error: {e.stderr.decode() if hasattr(e, 'stderr') and e.stderr else e}")

    if not VENV_PATH.exists():
        print("   - Creating venv directory...")
        VENV_PATH.mkdir(parents=True, exist_ok=True)
        
        # Create virtual environment WITHOUT pip to avoid ensurepip issues
        print("   - Creating virtual environment core...")
        subprocess.run([sys.executable, '-m', 'venv', str(VENV_PATH), '--without-pip'], 
                       check=True, capture_output=True, text=True)
        
        # Manually install pip using get-pip.py
        print("   - Downloading get-pip.py...")
        get_pip_path = SCR_PATH / "get-pip.py"
        subprocess.run(['curl', '-sLo', str(get_pip_path), "https://bootstrap.pypa.io/get-pip.py"], check=True)
        
        print("   - Installing pip into the virtual environment...")
        python_path = VENV_PATH / 'bin' / 'python'
        subprocess.run([str(python_path), str(get_pip_path)], check=True, capture_output=True, text=True)
        
        # Install requirements
        pip_path = VENV_PATH / 'bin' / 'pip'
        requirements_file = SCRIPTS_PATH / 'requirements.txt'
        if requirements_file.exists():
            print(f"   - Installing dependencies from {requirements_file}...")
            subprocess.run([str(pip_path), 'install', '-r', str(requirements_file)], 
                           check=True, capture_output=False)
        else:
            print("   - ⚠️ requirements.txt not found. Skipping dependency installation.")
    else:
        print("   - ✅ Venv already exists. Skipping creation.")
except Exception as e:
    print(f"   - ❌ ERROR during Venv setup: {e}")
    print("      Please check the error messages above. The notebook may not have permission to create directories or run commands.")

print("   - Venv setup complete.")


# 2. WEBUI INSTALLATION
# ---------------------
print("\n🚀 2. Installing WebUI...")
try:
    WEBUI_TYPE = get_current_webui()
    WEBUI_CONFIG = get_webui_config(WEBUI_TYPE)
    WEBUI_PATH = WEBUI_CONFIG['install_path']
    WEBUI_REPO_URL = WEBUI_CONFIG['repo_url']
    
    print(f"   - Selected WebUI: {WEBUI_TYPE}")
    print(f"   - Target Path: {WEBUI_PATH}")

    if not WEBUI_PATH.exists():
        print(f"   - Cloning from {WEBUI_REPO_URL}...")
        get_ipython().system(f'git clone --depth 1 {WEBUI_REPO_URL} "{WEBUI_PATH}"')
    else:
        print("   - ✅ WebUI directory already exists. Skipping clone.")
        print("   - Attempting to pull latest changes...")
        os.chdir(WEBUI_PATH)
        get_ipython().system('git pull')
        os.chdir(str(HOME))

except Exception as e:
    print(f"   - ❌ ERROR during WebUI installation: {e}")

print("   - WebUI installation step complete.")

# 3. EXTENSION INSTALLATION
# -------------------------
print("\n🔧 3. Installing Extensions...")
try:
    WIDGETS_DATA = js.read(SETTINGS_PATH, 'WIDGETS', {})
    EXTENSIONS_URLS_STR = WIDGETS_DATA.get('Extensions_url', '')
    EXTENSIONS_PATH = get_extensions_directory(WEBUI_TYPE)
    
    print(f"   - Target Extensions Directory: {EXTENSIONS_PATH}")
    EXTENSIONS_PATH.mkdir(parents=True, exist_ok=True)

    if not EXTENSIONS_URLS_STR or not EXTENSIONS_URLS_STR.strip():
        print("   - No extension URLs provided. Skipping.")
    else:
        urls = [url.strip() for url in EXTENSIONS_URLS_STR.split(',') if url.strip()]
        print(f"   - Found {len(urls)} extension(s) to install.")
        
        for url in urls:
            try:
                repo_name = url.split('/')[-1].replace('.git', '')
                target_path = EXTENSIONS_PATH / repo_name
                print(f"\n   - Processing: {repo_name}")
                if not target_path.exists():
                    get_ipython().system(f'git clone "{url}" "{target_path}"')
                else:
                    print(f"     - ✅ Already exists. Skipping clone.")
            except Exception as e:
                print(f"     - ❌ ERROR cloning {url}: {e}")

except Exception as e:
    print(f"   - ❌ ERROR during extension installation: {e}")

print("   - Extension installation step complete.")


# 4. MODEL & ASSET DOWNLOAD - FIXED URL PROCESSING
# ------------------------------------------------
print("\n🎨 4. Downloading Models and Assets...")
print("   - Reading from settings.json to download selected assets.")

try:
    from modules.Manager import m_download
    
    WIDGETS_DATA = js.read(SETTINGS_PATH, 'WIDGETS', {})
    model_files = '_xl_models_data.py' if WIDGETS_DATA.get('XL_models') else '_models_data.py'
    models_data_path = SCRIPTS_PATH / model_files
    
    local_vars = {}
    if models_data_path.exists():
        with open(models_data_path) as f:
            exec(f.read(), {}, local_vars)
    
    model_list = local_vars.get('model_list', {})
    vae_list = local_vars.get('vae_list', {})
    lora_list = local_vars.get('lora_list', {})
    controlnet_list = local_vars.get('controlnet_list', {})

    download_queue = []

    def add_to_queue(selection, data_dict):
        if not selection or selection == ['none']: 
            return
        
        items = selection if isinstance(selection, list) else [selection]
        for item_name in items:
            if item_name in data_dict:
                data = data_dict[item_name]
                if isinstance(data, dict):
                    if data.get('url'): 
                        download_queue.append(data['url'])
                elif isinstance(data, list):
                    for sub_item in data:
                        if isinstance(sub_item, dict) and sub_item.get('url'): 
                            download_queue.append(sub_item['url'])
    
    add_to_queue(WIDGETS_DATA.get('model'), model_list)
    add_to_queue(WIDGETS_DATA.get('vae'), vae_list)
    add_to_queue(WIDGETS_DATA.get('lora'), lora_list)
    add_to_queue(WIDGETS_DATA.get('controlnet'), controlnet_list)
    
    for url_key in ['Model_url', 'Vae_url', 'LoRA_url', 'Embedding_url']:
        urls_string = WIDGETS_DATA.get(url_key, '')
        if urls_string and urls_string.strip():
            custom_urls = [url.strip() for url in urls_string.split(',') if url.strip()]
            download_queue.extend(custom_urls)

    if not download_queue:
        print("   - No models selected for download.")
    else:
        print(f"   - Starting download of {len(download_queue)} item(s)...")
        
        successful_downloads = 0
        failed_downloads = 0
        
        for i, url in enumerate(download_queue, 1):
            try:
                print(f"\n   - [{i}/{len(download_queue)}] Processing: {url}")
                success = m_download(url, log=True, unzip=True)
                
                if success:
                    successful_downloads += 1
                    print(f"     ✅ Download successful")
                else:
                    failed_downloads += 1
                    print(f"     ❌ Download failed")
                    
            except Exception as e:
                failed_downloads += 1
                print(f"     ❌ Download error: {e}")
        
        print(f"\n   📊 Download Summary:")
        print(f"      - Total items: {len(download_queue)}")
        print(f"      - Successful: {successful_downloads}")
        print(f"      - Failed: {failed_downloads}")
        
        if failed_downloads > 0:
            print(f"      ⚠️ {failed_downloads} downloads failed. Check the URLs and try again.")
    
except Exception as e:
    print(f"   - ❌ ERROR during model download phase: {e}")
    import traceback
    print(f"   - Full error details: {traceback.format_exc()}")

print("   - Model download step complete.")

print("\n" + "="*35)
print("🎉 LSDAI Enhanced Download Complete!")
print("   Please review the output above for any errors.")
print("="*35)

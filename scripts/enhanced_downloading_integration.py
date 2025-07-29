# ~ enhanced_downloading_integration.py | RAW DEBUG & VERBOSE OUTPUT VERSION ~

import os
import sys
import json
from pathlib import Path
import time

# --- Setup Paths and Modules ---
# This initial setup is critical and assumes Cell 1 ran correctly.
try:
    # Add the modules directory to the Python path
    SCR_PATH = Path(os.environ.get('scr_path', '/content/LSDAI'))
    sys.path.insert(0, str(SCR_PATH / 'modules'))
    
    import json_utils as js
    from webui_utils import get_webui_config, get_current_webui, get_extensions_directory
    print("✅ Core modules imported successfully.")
except ImportError as e:
    print(f"❌ FATAL: Could not import a required module: {e}")
    print("   Please re-run Cell 1 (Setup) to ensure all paths are correctly configured.")
    sys.exit(1)

# --- Constants and Settings ---
SETTINGS_PATH = Path(os.environ.get('settings_path'))
HOME = Path(os.environ.get('home_path'))
VENV_PATH = Path(os.environ.get('venv_path'))
SCRIPTS_PATH = SCR_PATH / 'scripts'
REQUIREMENTS_PATH = SCRIPTS_PATH / 'requirements.txt'

# --- Main Execution Block ---
print("--- LSDAI RAW DEBUG DOWNLOADER ---")
print(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
print("="*35)

# 1. VIRTUAL ENVIRONMENT SETUP
# ----------------------------
print("\n🐍 1. Setting up Virtual Environment...")
print(f"   - Target Venv Path: {VENV_PATH}")

if (VENV_PATH / 'bin' / 'pip').exists():
    print("   - ✅ Venv with pip already exists. Skipping creation.")
else:
    if VENV_PATH.exists():
        print(f"   - ⚠️ Found an incomplete venv. Removing it now.")
        get_ipython().system(f'rm -rf "{VENV_PATH}"')
    
    print("   - Creating venv directory...")
    get_ipython().system(f'python -m venv "{VENV_PATH}"')
    
    print("\n   - Installing/Updating pip, setuptools, and wheel...")
    get_ipython().system(f'"{VENV_PATH}/bin/python" -m pip install --upgrade pip setuptools wheel')
    
    if REQUIREMENTS_PATH.exists():
        print(f"\n   - Installing dependencies from {REQUIREMENTS_PATH}...")
        get_ipython().system(f'"{VENV_PATH}/bin/pip" install -r "{REQUIREMENTS_PATH}"')
    else:
        print(f"   - ⚠️ WARNING: requirements.txt not found at {REQUIREMENTS_PATH}. Skipping dependency installation.")

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
        os.chdir(HOME)

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


# 4. MODEL & ASSET DOWNLOAD
# -------------------------
print("\n🎨 4. Downloading Models and Assets...")
print("   - NOTE: This version uses the original `downloading_en.py` for model downloads.")
print("   - Running the script now with raw output...")

try:
    # Ensure we are in the correct directory for the script to run
    os.chdir(SCR_PATH)
    # Use '%run' to execute the original download script in the current kernel context
    # This will inherit the environment and print output directly.
    get_ipython().run_line_magic('run', '-i scripts/downloading_en.py')
    os.chdir(HOME)
except Exception as e:
    print(f"   - ❌ ERROR running downloading_en.py: {e}")
    os.chdir(HOME)

print("   - Model download step complete.")

print("\n" + "="*35)
print("🎉 LSDAI Raw Debug Download Complete!")
print("   Please review the output above for any errors.")
print("="*35)

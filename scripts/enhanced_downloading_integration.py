# ~ enhanced_downloading_integration.py | RAW DEBUG & VERBOSE OUTPUT VERSION ~

import os
import sys
import json
from pathlib import Path
import time
import subprocess

# --- Setup Paths and Modules ---
try:
    SCR_PATH = Path(os.environ.get('scr_path', '/content/LSDAI'))
    sys.path.insert(0, str(SCR_PATH / 'modules'))
    
    import json_utils as js
    from webui_utils import get_webui_config, get_current_webui, get_extensions_directory
    print("✅ Core modules imported successfully.")
except ImportError as e:
    print(f"❌ FATAL: Could not import a required module: {e}")
    sys.exit(1)

# --- Constants and Settings ---
SETTINGS_PATH = Path(os.environ.get('settings_path'))
HOME = Path(os.environ.get('home_path'))
VENV_PATH = Path(os.environ.get('venv_path'))
SCRIPTS_PATH = SCR_PATH / 'scripts'
REQUIREMENTS_PATH = SCRIPTS_PATH / 'requirements.txt'

# --- Main Execution Block ---
print("--- LSDAI ENHANCED DOWNLOADER ---")
print(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
print("="*35)

# 1. ROBUST VIRTUAL ENVIRONMENT SETUP
# ------------------------------------
print("\n🐍 1. Setting up Virtual Environment...")
print(f"   - Target Venv Path: {VENV_PATH}")

try:
    if not (VENV_PATH / 'bin' / 'pip').exists():
        if VENV_PATH.exists():
            print(f"   - ⚠️ Found an incomplete venv. Removing it now.")
            get_ipython().system(f'rm -rf "{VENV_PATH}"')
        
        # 1. Create venv without pip/ensurepip to avoid common errors
        print("   - Creating venv directory...")
        subprocess.run([sys.executable, '-m', 'venv', str(VENV_PATH), '--without-pip'], check=True)
        
        # 2. Download get-pip.py for a reliable pip installation
        print("   - Downloading get-pip.py...")
        get_pip_path = SCR_PATH / "get-pip.py"
        subprocess.run(['curl', '-sLo', str(get_pip_path), "https://bootstrap.pypa.io/get-pip.py"], check=True)
        
        # 3. Install pip using the venv's python interpreter
        venv_python = VENV_PATH / 'bin' / 'python'
        print(f"   - Installing pip into the virtual environment...")
        subprocess.run([str(venv_python), str(get_pip_path)], check=True, capture_output=True, text=True)
        
        # 4. Install dependencies from requirements.txt
        if REQUIREMENTS_PATH.exists():
            print(f"   - Installing dependencies from {REQUIREMENTS_PATH}...")
            pip_executable = VENV_PATH / 'bin' / 'pip'
            get_ipython().system(f'"{pip_executable}" install -r "{REQUIREMENTS_PATH}"')
        else:
            print(f"   - ⚠️ WARNING: requirements.txt not found at {REQUIREMENTS_PATH}. Skipping.")
    else:
        print("   - ✅ Venv with pip already exists. Skipping creation.")
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


# 4. MODEL & ASSET DOWNLOAD
# -------------------------
print("\n🎨 4. Downloading Models and Assets...")
print("   - Reading from settings.json to download selected assets.")

try:
    from modules.Manager import m_download
    
    WIDGETS_DATA = js.read(SETTINGS_PATH, 'WIDGETS', {})
    model_files = '_xl_models_data.py' if WIDGETS_DATA.get('XL_models') else '_models_data.py'
    models_data_path = SCRIPTS_PATH / model_files
    
    local_vars = {}
    with open(models_data_path) as f:
        exec(f.read(), {}, local_vars)
    
    model_list = local_vars.get('model_list', {})
    vae_list = local_vars.get('vae_list', {})
    lora_list = local_vars.get('lora_list', {})
    controlnet_list = local_vars.get('controlnet_list', {})

    download_queue = []

    def add_to_queue(selection, data_dict):
        if not selection or selection == ['none']: return
        
        items = selection if isinstance(selection, list) else [selection]
        for item_name in items:
            if item_name in data_dict:
                data = data_dict[item_name]
                if isinstance(data, dict):
                    if data.get('url'): download_queue.append(data['url'])
                elif isinstance(data, list):
                    for sub_item in data:
                        if sub_item.get('url'): download_queue.append(sub_item['url'])
    
    add_to_queue(WIDGETS_DATA.get('model'), model_list)
    add_to_queue(WIDGETS_DATA.get('vae'), vae_list)
    add_to_queue(WIDGETS_DATA.get('lora'), lora_list)
    add_to_queue(WIDGETS_DATA.get('controlnet'), controlnet_list)
    
    for url_key in ['Model_url', 'Vae_url', 'LoRA_url', 'Embedding_url']:
        urls = WIDGETS_DATA.get(url_key, '')
        if urls:
            download_queue.extend([url.strip() for url in urls.split(',') if url.strip()])

    if not download_queue:
        print("   - No models selected for download.")
    else:
        print(f"   - Starting download of {len(download_queue)} item(s)...")
        download_command = " ".join([f'"{url}"' for url in download_queue])
        m_download(download_command, log=True, unzip=True)
    
except Exception as e:
    print(f"   - ❌ ERROR during model download phase: {e}")

print("   - Model download step complete.")

print("\n" + "="*35)
print("🎉 LSDAI Enhanced Download Complete!")
print("   Please review the output above for any errors.")
print("="*35)

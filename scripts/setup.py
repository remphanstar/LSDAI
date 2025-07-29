# ~ setup.py | by ANXETY - FINAL CORRECTED & COMPLETE VERSION ~

from IPython.display import display, HTML, clear_output
from typing import Dict, List, Tuple, Optional, Union
from pathlib import Path
from tqdm import tqdm
import nest_asyncio
import importlib
import argparse
import aiohttp
import asyncio
import time
import json
import sys
import os

# --- Civitai API Token ---
CIVITAI_API_TOKEN = "9d333451a6148a1682349e326967efc2"

nest_asyncio.apply()  # Async support for Jupyter


# ======================== CONSTANTS =======================

def detect_platform_home():
    """Detect the appropriate home directory based on platform."""
    if 'COLAB_GPU' in os.environ or '/content' in os.getcwd():
        return Path('/content')
    elif 'KAGGLE_URL_BASE' in os.environ or '/kaggle' in os.getcwd():
        return Path('/kaggle/working')
    elif '/teamspace/' in os.getcwd() or any('LIGHTNING'in k for k in os.environ):
        return Path('/teamspace/studios/this_studio')
    elif '/workspace/' in os.getcwd():
        return Path('/workspace')
    else:
        cwd = Path.cwd()
        return cwd.parent if cwd.name == 'LSDAI' else cwd

HOME = detect_platform_home()
SCR_PATH = HOME / 'LSDAI'
SETTINGS_PATH = SCR_PATH / 'settings.json'
VENV_PATH = HOME / 'venv'
MODULES_FOLDER = SCR_PATH / "modules"

os.environ.update({
    'home_path': str(HOME),
    'scr_path': str(SCR_PATH),
    'venv_path': str(VENV_PATH),
    'settings_path': str(SETTINGS_PATH)
})

# GitHub configuration
DEFAULT_USER = 'remphanstar'
DEFAULT_REPO = 'LSDAI'
DEFAULT_BRANCH = 'main'
DEFAULT_LANG = 'en'
BASE_GITHUB_URL = "https://raw.githubusercontent.com"

# --- COMPLETE FILE MANIFEST ---
# This dictionary now contains every single file from the repository.
FILE_STRUCTURE = {
    '': [
        'LICENSE',
        'setup_enhancements.py',
        'test_integration.py'
    ],
    'CSS': [
        'auto-cleaner.css',
        'download-result.css',
        'enhanced-widgets.css',
        'main-widgets.css'
    ],
    'JS': [
        'enhanced-widgets.js',
        'main-widgets.js'
    ],
    'modules': [
        '_season.py',
        'AdvancedLogging.py',
        'CivitaiAPI.py',
        'CloudSync.py',
        'enhanced_model_selector.py',
        'EnhancedModelManager.py',
        'ExtensionManager.py',
        'json_utils.py',
        'Manager.py',
        'ModelBenchmarking.py',
        'NotificationSystem.py',
        'TunnelHub.py',
        'webui_utils.py',
        'widget_factory.py'
    ],
    'scripts': [
        '_models-data.py',
        '_xl-models-data.py',
        'auto-cleaner.py',
        'download-result.py',
        'downloading-en.py',
        'enhanced-downloading-integration.py',
        'enhanced-launch-integration.py',
        'enhanced-launch.py',
        'enhanced-setup.py',
        'enhanced-widgets-en.py',
        'enhanced-widgets-integration.py',
        'enhanced_model_selector.py',
        'launch.py',
        'master-integration.py',
        'migrate-settings.py',
        'requirements.txt',
        'requirementsbackup.txt',
        'setup.py',
        'webui-installer.py',
        'widgets-en.py'
    ],
    '__configs__': {
        '': [
            'card-no-preview.png',
            'gradio-tunneling.py',
            'notification.mp3',
            'styles.csv',
            'tagcomplete-tags-parser.py',
            'user.css'
        ],
        'A1111': ['_extensions.txt', 'config.json', 'ui-config.json'],
        'Classic': ['_extensions.txt', 'config.json', 'ui-config.json'],
        'ComfyUI': {
            '': ['_extensions.txt', 'comfy.settings.json', 'install-deps.py'],
            'Comfy-Manager': ['config.ini'],
            'workflows': ['anxety-workflow.json']
        },
        'Forge': ['_extensions.txt', 'config.json', 'ui-config.json'],
        'ReForge': ['_extensions.txt', 'config.json', 'ui-config.json'],
        'SD-UX': ['_extensions.txt', 'config.json', 'ui-config.json']
    }
}


# =================== UTILITY FUNCTIONS ====================
def reinitialize_paths(base_path):
    global HOME, SCR_PATH, SETTINGS_PATH, VENV_PATH, MODULES_FOLDER
    HOME = base_path
    SCR_PATH = HOME / 'LSDAI'
    SETTINGS_PATH = SCR_PATH / 'settings.json'
    VENV_PATH = HOME / 'venv'
    MODULES_FOLDER = SCR_PATH / "modules"
    os.environ.update({
        'home_path': str(HOME), 'scr_path': str(SCR_PATH),
        'venv_path': str(VENV_PATH), 'settings_path': str(SETTINGS_PATH)
    })

def _get_start_timer() -> int:
    try:
        if SETTINGS_PATH.exists():
            return json.loads(SETTINGS_PATH.read_text()).get("ENVIRONMENT", {}).get("start_timer", int(time.time() - 5))
    except (json.JSONDecodeError, OSError): pass
    return int(time.time() - 5)

def save_env_to_json(data: dict, filepath: Path) -> None:
    filepath.parent.mkdir(parents=True, exist_ok=True)
    existing_data = {}
    if filepath.exists():
        try: existing_data = json.loads(filepath.read_text())
        except (json.JSONDecodeError, OSError): pass
    merged_data = {**existing_data, **data}
    filepath.write_text(json.dumps(merged_data, indent=4))

# =================== MODULE MANAGEMENT ====================
def _clear_module_cache(modules_folder=None):
    target_folder = Path(modules_folder if modules_folder else MODULES_FOLDER).resolve()
    modules_to_remove = []
    for name, module in sys.modules.items():
        if hasattr(module, "__file__") and module.__file__:
            try:
                if target_folder in Path(module.__file__).resolve().parents:
                    modules_to_remove.append(name)
            except (ValueError, RuntimeError, OSError): continue
    for name in modules_to_remove:
        try: del sys.modules[name]
        except KeyError: pass
    importlib.invalidate_caches()

def setup_module_folder(modules_folder=None):
    target_folder = Path(modules_folder if modules_folder else MODULES_FOLDER)
    target_folder.mkdir(parents=True, exist_ok=True)
    _clear_module_cache(target_folder)
    if str(target_folder) not in sys.path:
        sys.path.insert(0, str(target_folder))

# =================== ENVIRONMENT SETUP ====================
def detect_environment():
    if 'COLAB_GPU' in os.environ or '/content' in os.getcwd(): return 'Google Colab'
    if 'KAGGLE_URL_BASE' in os.environ or '/kaggle' in os.getcwd(): return 'Kaggle'
    if '/teamspace/' in os.getcwd() or any('LIGHTNING' in k for k in os.environ): return 'Lightning.ai'
    if '/workspace/' in os.getcwd(): return 'Vast.ai'
    print("Warning: Unknown environment, assuming Colab compatibility")
    return 'Google Colab'

def parse_fork_arg(fork_arg):
    if not fork_arg: return DEFAULT_USER, DEFAULT_REPO
    parts = fork_arg.split("/", 1)
    return parts[0], (parts[1] if len(parts) > 1 else DEFAULT_REPO)

def create_environment_data(env, lang, user, repo, branch):
    return {"ENVIRONMENT": {
        "env_name": env, "install_deps": ('aria2c' in os.popen('command -v aria2c').read()),
        "fork": f"{user}/{repo}", "branch": branch, "lang": lang,
        "home_path": os.environ['home_path'], "scr_path": os.environ['scr_path'],
        "venv_path": os.environ['venv_path'], "settings_path": os.environ['settings_path'],
        "start_timer": _get_start_timer(), "public_ip": "", "civitai_api_token": CIVITAI_API_TOKEN
    }}

# ===================== DOWNLOAD LOGIC =====================
def generate_file_list(structure: Dict, base_url: str) -> List[Tuple[str, Path]]:
    items = []
    def walk(struct: Dict, path_parts: List[str]):
        for key, value in struct.items():
            current_path = [*path_parts, key] if key else path_parts
            if isinstance(value, dict):
                walk(value, current_path)
            else:
                url_path = "/".join(current_path)
                for file in value:
                    url = f"{base_url}/{url_path}/{file}" if url_path else f"{base_url}/{file}"
                    file_path = SCR_PATH / Path(*current_path) / file
                    items.append((url, file_path))
    walk(structure, [])
    return items

async def download_file(session: aiohttp.ClientSession, url: str, path: Path, retries: int = 3) -> Tuple[bool, str, Path, Optional[str]]:
    for attempt in range(retries):
        try:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as resp:
                if resp.status == 404:
                    return (False, url, path, f"HTTP error 404: Not Found")
                resp.raise_for_status()
                path.parent.mkdir(parents=True, exist_ok=True)
                temp_path = path.with_suffix(path.suffix + '.tmp')
                temp_path.write_bytes(await resp.read())
                temp_path.rename(path)
                return (True, url, path, None)
        except (asyncio.TimeoutError, aiohttp.ClientError) as e:
            if attempt == retries - 1: return (False, url, path, str(e))
            await asyncio.sleep(2 ** attempt)
    return (False, url, path, "Max retries exceeded")

async def download_files_async(user, repo, branch, log_errors):
    base_url = f"{BASE_GITHUB_URL}/{user}/{repo}/{branch}"
    file_list = generate_file_list(FILE_STRUCTURE, base_url)
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=10)) as session:
        tasks = [download_file(session, url, path) for url, path in file_list]
        errors, successful = [], 0
        for future in tqdm(asyncio.as_completed(tasks), total=len(tasks), desc="Downloading files", unit="file"):
            success, url, path, error = await future
            if success: successful += 1
            else: errors.append((url, path, error))
        clear_output()
        print(f"Downloaded {successful}/{len(file_list)} files successfully")
        if errors:
            print(f"\\n{len(errors)} files failed to download.")
            if log_errors:
                print("\\nErrors occurred:")
                for url, path, error in errors[:15]: print(f"URL: {url}\\n  Error: {error}\\n")
            critical_files = ['json_utils.py', '_season.py']
            if any(cf in str(e[1]) for e in errors for cf in critical_files):
                raise RuntimeError(f"Critical files failed to download.")

# ===================== MAIN EXECUTION =====================
async def main_async(args=None):
    parser = argparse.ArgumentParser(description='LSDAI Download Manager')
    parser.add_argument('--lang', default=DEFAULT_LANG)
    parser.add_argument('--branch', default=DEFAULT_BRANCH)
    parser.add_argument('--fork', default=None)
    parser.add_argument('-s', '--skip-download', action="store_true")
    parser.add_argument('-l', "--log", action="store_true")
    args, _ = parser.parse_known_args(args)
    try:
        env = detect_environment()
        print(f"🌍 Detected environment: {env}")
        print(f"📁 Using home directory: {HOME}")
        user, repo = parse_fork_arg(args.fork)
        if not args.skip_download:
            await download_files_async(user, repo, args.branch, args.log)
        setup_module_folder()
        save_env_to_json(create_environment_data(env, args.lang, user, repo, args.branch), SETTINGS_PATH)
        if CIVITAI_API_TOKEN:
            os.environ['CIVITAI_API_TOKEN'] = CIVITAI_API_TOKEN
        try:
            from _season import display_info
            display_info(env, os.environ['scr_path'], args.branch, args.lang, f"{user}/{repo}")
        except ImportError as e:
            print(f"Warning: Could not load season display: {e}")
            print("Setup completed successfully!")
    except Exception as e:
        print(f"Setup failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main_async())

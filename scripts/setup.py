# LSDAI Setup Script - Enhanced for Cross-Platform Compatibility
# Handles environment detection, file downloads, and Python path setup
# FIXED: Better error handling and environment detection

import asyncio
import aiohttp
import argparse
import importlib
import json
import os
import sys
import time
from pathlib import Path
from typing import Dict, List, Tuple

# =================== CONSTANTS ===================
DEFAULT_USER = "remphanstar"
DEFAULT_REPO = "LSDAI"
DEFAULT_BRANCH = "main"
DEFAULT_LANG = "en"

# Determine base paths based on environment
if 'COLAB_GPU' in os.environ or '/content' in os.getcwd():
    BASE_PATH = Path('/content')
    ENV_TYPE = 'colab'
elif 'KAGGLE_URL_BASE' in os.environ or '/kaggle' in os.getcwd():
    BASE_PATH = Path('/kaggle/working')
    ENV_TYPE = 'kaggle'
elif any('LIGHTNING' in k for k in os.environ) or '/teamspace/' in os.getcwd():
    BASE_PATH = Path('/teamspace/studios/this_studio')
    ENV_TYPE = 'lightning'
else:
    BASE_PATH = Path.cwd()
    ENV_TYPE = 'local'

# Global paths
HOME = BASE_PATH
SCR_PATH = HOME / 'LSDAI'
SETTINGS_PATH = SCR_PATH / 'settings.json'
VENV_PATH = HOME / 'venv'
MODULES_FOLDER = SCR_PATH / "modules"

# Update environment variables immediately
os.environ.update({
    'home_path': str(HOME),
    'scr_path': str(SCR_PATH),
    'venv_path': str(VENV_PATH),
    'settings_path': str(SETTINGS_PATH)
})

print(f"🔧 LSDAI Setup v2.1 | Environment: {ENV_TYPE} | Base: {BASE_PATH}")

# GitHub file structure for download
GITHUB_FILE_STRUCTURE = {
    "": [  # Root files
        "LICENSE", "README.md", ".gitignore"
    ],
    "scripts": [
        "setup.py", "widgets_en.py", "downloading_en.py", "launch.py",
        "enhanced_widgets_integration.py", "enhanced_downloading_integration.py", 
        "enhanced_launch_integration.py", "download_result.py", "_models_data.py"
    ],
    "modules": [
        "__init__.py", "json_utils.py", "widget_factory.py", "webui_utils.py",
        "Manager.py", "CivitaiAPI.py", "EnhancedManager.py", "ExtensionManager.py",
        "CloudSync.py", "NotificationSystem.py", "AdvancedLogging.py", "ModelBenchmarking.py"
    ],
    "__configs__": {
        "ComfyUI": ["_extensions.txt"],
        "A1111": ["_extensions.txt"]
    },
    "CSS": [
        "main-widgets.css", "download-result.css"
    ],
    "JS": [
        "main-widgets.js"
    ]
}

# =================== UTILITY FUNCTIONS ====================
def reinitialize_paths(base_path):
    """Reinitialize all paths if needed"""
    global HOME, SCR_PATH, SETTINGS_PATH, VENV_PATH, MODULES_FOLDER
    HOME = Path(base_path)
    SCR_PATH = HOME / 'LSDAI'
    SETTINGS_PATH = SCR_PATH / 'settings.json'
    VENV_PATH = HOME / 'venv'
    MODULES_FOLDER = SCR_PATH / "modules"
    
    os.environ.update({
        'home_path': str(HOME), 'scr_path': str(SCR_PATH),
        'venv_path': str(VENV_PATH), 'settings_path': str(SETTINGS_PATH)
    })

def _get_start_timer() -> int:
    """Get start timer from existing settings or create new one"""
    try:
        if SETTINGS_PATH.exists():
            with open(SETTINGS_PATH, 'r') as f:
                data = json.load(f)
                return data.get("ENVIRONMENT", {}).get("start_timer", int(time.time() - 5))
    except (json.JSONDecodeError, OSError):
        pass
    return int(time.time() - 5)

def save_env_to_json(data: dict, filepath: Path) -> None:
    """Save environment data to JSON file with proper error handling"""
    try:
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        # Load existing data if file exists
        existing_data = {}
        if filepath.exists():
            try:
                with open(filepath, 'r') as f:
                    existing_data = json.load(f)
            except (json.JSONDecodeError, OSError):
                existing_data = {}
        
        # Merge data
        merged_data = {**existing_data, **data}
        
        # Write back to file
        with open(filepath, 'w') as f:
            json.dump(merged_data, f, indent=4)
            
        print(f"✅ Settings saved to {filepath}")
        
    except Exception as e:
        print(f"⚠️ Warning: Could not save settings: {e}")

# =================== MODULE MANAGEMENT ====================
def _clear_module_cache(modules_folder=None):
    """Clear Python module cache for the modules folder"""
    target_folder = Path(modules_folder if modules_folder else MODULES_FOLDER).resolve()
    modules_to_remove = []
    
    for name, module in sys.modules.items():
        if hasattr(module, "__file__") and module.__file__:
            try:
                if target_folder in Path(module.__file__).resolve().parents:
                    modules_to_remove.append(name)
            except (ValueError, RuntimeError, OSError):
                continue
    
    for name in modules_to_remove:
        try:
            del sys.modules[name]
        except KeyError:
            pass
    
    importlib.invalidate_caches()

def setup_module_folder(modules_folder=None):
    """Setup modules folder and add to Python path"""
    target_folder = Path(modules_folder if modules_folder else MODULES_FOLDER)
    target_folder.mkdir(parents=True, exist_ok=True)
    
    _clear_module_cache(target_folder)
    
    if str(target_folder) not in sys.path:
        sys.path.insert(0, str(target_folder))
        print(f"✅ Added {target_folder} to Python path")

# =================== ENVIRONMENT SETUP ====================
def detect_environment():
    """Detect the current environment with improved accuracy"""
    
    # Google Colab detection
    if 'COLAB_GPU' in os.environ or '/content' in os.getcwd():
        return 'Google Colab'
    
    # Kaggle detection
    if 'KAGGLE_URL_BASE' in os.environ or '/kaggle' in os.getcwd():
        return 'Kaggle'
    
    # Lightning.ai detection
    if '/teamspace/' in os.getcwd() or any('LIGHTNING' in k for k in os.environ):
        return 'Lightning.ai'
    
    # Vast.ai detection
    if '/workspace/' in os.getcwd():
        return 'Vast.ai'
    
    # Paperspace detection
    if '/notebooks/' in os.getcwd() or 'PAPERSPACE' in os.environ:
        return 'Paperspace'
    
    # Local/other environments
    print("⚠️ Unknown environment detected, assuming Colab compatibility")
    return 'Google Colab'

def parse_fork_arg(fork_arg):
    """Parse fork argument into user and repo"""
    if not fork_arg:
        return DEFAULT_USER, DEFAULT_REPO
    
    parts = fork_arg.split("/", 1)
    return parts[0], (parts[1] if len(parts) > 1 else DEFAULT_REPO)

def create_environment_data(env, lang, user, repo, branch):
    """Create environment data dictionary"""
    
    # Detect if dependencies are available
    install_deps = False
    try:
        import subprocess
        result = subprocess.run(['which', 'aria2c'], capture_output=True, text=True)
        install_deps = result.returncode == 0
    except:
        pass
    
    return {
        "ENVIRONMENT": {
            "env_name": env,
            "install_deps": install_deps,
            "fork": f"{user}/{repo}",
            "branch": branch,
            "lang": lang,
            "home_path": str(HOME),
            "scr_path": str(SCR_PATH),
            "venv_path": str(VENV_PATH),
            "settings_path": str(SETTINGS_PATH),
            "start_timer": _get_start_timer(),
            "public_ip": "",
            "civitai_api_token": ""
        }
    }

# ===================== DOWNLOAD LOGIC =====================
def generate_file_list(structure: Dict, base_url: str) -> List[Tuple[str, Path]]:
    """Generate list of files to download from GitHub structure"""
    items = []
    
    def walk(struct: Dict, path_parts: List[str]):
        for key, value in struct.items():
            current_path = [*path_parts, key] if key else path_parts
            
            if isinstance(value, dict):
                walk(value, current_path)
            else:
                url_path = "/".join(current_path)
                for file in value:
                    url = f"{base_url}/{url_path}/{file}".replace("//", "/")
                    local_path = SCR_PATH / Path(*current_path) / file
                    items.append((url, local_path))
    
    walk(structure, [])
    return items

async def download_file(session: aiohttp.ClientSession, url: str, filepath: Path, semaphore: asyncio.Semaphore) -> bool:
    """Download a single file with error handling"""
    
    async with semaphore:
        try:
            filepath.parent.mkdir(parents=True, exist_ok=True)
            
            async with session.get(url) as response:
                if response.status == 200:
                    content = await response.read()
                    filepath.write_bytes(content)
                    return True
                else:
                    print(f"⚠️ Failed to download {url}: HTTP {response.status}")
                    return False
                    
        except Exception as e:
            print(f"⚠️ Error downloading {filepath.name}: {e}")
            return False

async def download_files_async(user: str, repo: str, branch: str, log_errors: bool = False) -> None:
    """Download all files asynchronously"""
    
    base_url = f"https://raw.githubusercontent.com/{user}/{repo}/{branch}"
    file_list = generate_file_list(GITHUB_FILE_STRUCTURE, base_url)
    
    print(f"📥 Downloading {len(file_list)} files from {user}/{repo}@{branch}...")
    
    # Limit concurrent downloads to avoid overwhelming the server
    semaphore = asyncio.Semaphore(10)
    
    connector = aiohttp.TCPConnector(limit=50, limit_per_host=10)
    timeout = aiohttp.ClientTimeout(total=30)
    
    async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
        tasks = [download_file(session, url, filepath, semaphore) for url, filepath in file_list]
        results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Count successful downloads
    successful = sum(1 for result in results if result is True)
    failed = len(file_list) - successful
    
    print(f"📊 Download Results: {successful} successful, {failed} failed")
    
    if failed > 0 and log_errors:
        print("⚠️ Some files failed to download. This is usually not critical.")
    
    # Verify critical files
    critical_files = [
        SCR_PATH / "scripts" / "widgets_en.py",
        SCR_PATH / "scripts" / "downloading_en.py",
        SCR_PATH / "scripts" / "launch.py",
        SCR_PATH / "modules" / "json_utils.py"
    ]
    
    missing_critical = [f for f in critical_files if not f.exists()]
    
    if missing_critical:
        print("❌ Critical files missing:")
        for file in missing_critical:
            print(f"   - {file}")
        raise Exception("Critical files are missing. Setup cannot continue.")
    else:
        print("✅ All critical files downloaded successfully")

# =================== ENHANCEMENT SUPPORT ===================
def check_enhancement_dependencies():
    """Check if enhancement dependencies can be loaded"""
    
    print("🔍 Checking enhancement dependencies...")
    
    try:
        # Try to import key enhancement modules
        test_imports = [
            ("ipywidgets", "Enhanced UI widgets"),
            ("aiohttp", "Async HTTP client"),
            ("requests", "HTTP requests"),
            ("pathlib", "Path handling")
        ]
        
        available_modules = []
        for module_name, description in test_imports:
            try:
                __import__(module_name)
                available_modules.append((module_name, description))
            except ImportError:
                print(f"⚠️ {module_name} not available - {description} will be limited")
        
        if len(available_modules) >= len(test_imports) * 0.75:
            print("✅ Enhancement dependencies mostly available")
            return True
        else:
            print("⚠️ Some enhancement features may be limited")
            return False
            
    except Exception as e:
        print(f"⚠️ Enhancement dependency check failed: {e}")
        return False

# ================= MAIN SETUP FUNCTION ===================
def run_original_setup(branch="main", fork_arg="", lang=DEFAULT_LANG, ignore_deps=False, log_errors=False):
    """Main setup function - runs the original LSDAI setup process"""
    
    print(f"🚀 LSDAI Setup Starting | Branch: {branch}")
    print("=" * 50)
    
    try:
        # Setup module folder first
        setup_module_folder()
        
        # Detect environment
        env = detect_environment()
        print(f"🌍 Environment detected: {env}")
        
        # Parse fork argument
        user, repo = parse_fork_arg(fork_arg)
        print(f"📂 Repository: {user}/{repo}")
        
        # Create and save environment data
        env_data = create_environment_data(env, lang, user, repo, branch)
        save_env_to_json(env_data, SETTINGS_PATH)
        
        # Check enhancement dependencies unless ignored
        if not ignore_deps:
            check_enhancement_dependencies()
        
        # Download all project files
        print("📥 Starting file downloads...")
        asyncio.run(download_files_async(user, repo, branch, log_errors))
        
        # Final verification
        print("🔍 Performing final verification...")
        
        if not SCR_PATH.exists():
            raise Exception(f"LSDAI directory not created: {SCR_PATH}")
        
        if not SETTINGS_PATH.exists():
            raise Exception(f"Settings file not created: {SETTINGS_PATH}")
        
        print("✅ LSDAI setup completed successfully!")
        print(f"📁 Project location: {SCR_PATH}")
        print(f"⚙️ Settings file: {SETTINGS_PATH}")
        print("🚀 Ready to run widgets and downloading scripts!")
        
        return True
        
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        print("🔧 Try running the setup again or check your internet connection")
        return False

def setup_basic_environment():
    """Setup basic environment without full download (for emergency use)"""
    
    print("🆘 Setting up basic environment...")
    
    try:
        # Create basic directory structure
        SCR_PATH.mkdir(parents=True, exist_ok=True)
        (SCR_PATH / "scripts").mkdir(exist_ok=True)
        (SCR_PATH / "modules").mkdir(exist_ok=True)
        
        # Setup module path
        setup_module_folder()
        
        # Create minimal settings
        basic_env = create_environment_data(detect_environment(), DEFAULT_LANG, DEFAULT_USER, DEFAULT_REPO, DEFAULT_BRANCH)
        save_env_to_json(basic_env, SETTINGS_PATH)
        
        print("✅ Basic environment setup complete")
        print("⚠️ You'll need to run full setup later for complete functionality")
        
        return True
        
    except Exception as e:
        print(f"❌ Basic environment setup failed: {e}")
        return False

# ================ CLI INTERFACE =================
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="LSDAI Setup Script v2.1")
    parser.add_argument("--branch", default=DEFAULT_BRANCH, help="Git branch to use")
    parser.add_argument("--fork", default="", help="GitHub fork in format: user/repo")
    parser.add_argument("--lang", default=DEFAULT_LANG, help="Language code")
    parser.add_argument("--ignore-deps", action="store_true", help="Skip dependency checks")
    parser.add_argument("--log-errors", action="store_true", help="Show detailed error logs")
    parser.add_argument("--basic-only", action="store_true", help="Setup basic environment only")
    
    args = parser.parse_args()
    
    try:
        if args.basic_only:
            success = setup_basic_environment()
        else:
            success = run_original_setup(
                branch=args.branch,
                fork_arg=args.fork,
                lang=args.lang,
                ignore_deps=args.ignore_deps,
                log_errors=args.log_errors
            )
        
        if success:
            print("\n🎉 Setup completed successfully!")
            if not args.basic_only:
                print("📋 Next steps:")
                print("   1. Run Cell 2 (Widgets) to configure your setup")
                print("   2. Run Cell 3 (Downloading) to install WebUI and models")
                print("   3. Run Cell 4 (Launch) to start the WebUI")
        else:
            print("\n💥 Setup failed. Check the error messages above.")
            print("🔧 You can try running with --basic-only for minimal setup")
            
    except KeyboardInterrupt:
        print("\n⏹️ Setup cancelled by user")
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        print("🔧 Try running with --basic-only for minimal setup")

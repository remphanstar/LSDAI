# ~ downloading-en.py | by ANXETY - COMPLETE FIXED VERSION ~

import json_utils as js
from pathlib import Path
import subprocess
import requests
import shutil
import shlex
import time
import json
import sys
import re
import os

# FIXED: Better dependency verification
def verify_dependencies():
    """Verify and install required tools safely."""
    print("🔧 Checking system dependencies...")
    
    required_tools = {
        'git': 'git',
        'curl': 'curl', 
        'wget': 'wget',
        'aria2c': 'aria2',
        'unzip': 'unzip'
    }

    missing = []
    for tool, package in required_tools.items():
        if not shutil.which(tool):
            missing.append(package)

    if missing:
        print(f"📦 Installing missing tools: {', '.join(missing)}")
        try:
            # Update package list first
            subprocess.run(['apt-get', 'update', '-qq'], 
                         check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            # Install missing packages
            subprocess.run(['apt-get', 'install', '-y', '-qq'] + missing, 
                         check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print("✅ System dependencies installed")
            
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            print(f"⚠️  Warning: Could not install some dependencies: {e}")
            print("Continuing with available tools...")

# Verify dependencies first
verify_dependencies()

# Import order - after dependency verification
from IPython.display import clear_output
from IPython.utils import capture
from urllib.parse import urlparse
from IPython import get_ipython
from datetime import timedelta

# Basic setup
osENV = os.environ
CD = os.chdir
ipySys = get_ipython().system
ipyRun = get_ipython().run_line_magic

# Constants and Paths
PATHS = {k: Path(v) for k, v in osENV.items() if k.endswith('_path')}
HOME, VENV, SCR_PATH = PATHS['home_path'], PATHS['venv_path'], PATHS['scr_path']
SETTINGS_PATH = PATHS['settings_path']
SCRIPTS = SCR_PATH / 'scripts'

# Load settings
settings = js.read(SETTINGS_PATH)
UI = settings.get('WEBUI', {}).get('current', 'A1111')
WEBUI = settings.get('WEBUI', {}).get('webui_path', str(HOME / UI))
FORK_REPO = js.read(SETTINGS_PATH, 'ENVIRONMENT.fork')
BRANCH = js.read(SETTINGS_PATH, 'ENVIRONMENT.branch')

widget_settings = settings.get('WIDGETS', {})
webui_settings = settings.get('WEBUI', {})

# Apply widget settings to local scope for backward compatibility
locals().update(widget_settings)

# Safe import of custom modules with fallback
try:
    from webui_utils import handle_setup_timer
    from Manager import m_download, m_clone
    from CivitaiAPI import CivitAiAPI
except ImportError as e:
    print(f"❌ Fatal Error: Could not import custom modules: {e}")
    print("The setup in Cell 1 may have failed. Please restart the runtime and try again.")
    sys.exit(1)

class COLORS:
    R, G, Y, B, X = "\033[31m", "\033[32m", "\033[33m", "\033[34m", "\033[0m"
COL = COLORS

# --- FIXED VENV SETUP ---
def setup_venv():
    """Create and setup virtual environment with proper error handling."""
    CD(HOME)
    
    print(f"🐍 Setting up Python virtual environment...")
    
    # Check if venv exists and is functional
    pip_executable = VENV / 'bin' / 'pip'
    python_executable = VENV / 'bin' / 'python'
    
    venv_is_broken = False
    if VENV.exists():
        if not pip_executable.exists() or not python_executable.exists():
            print(f"⚠️  Virtual environment exists but is incomplete")
            venv_is_broken = True
        else:
            # Test if venv is functional
            try:
                result = subprocess.run([str(pip_executable), '--version'], 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode != 0:
                    venv_is_broken = True
            except Exception:
                venv_is_broken = True
    
    # Create or recreate venv if needed
    if not VENV.exists() or venv_is_broken:
        print(f"🌱 Creating new virtual environment at {VENV}...")
        
        # Remove broken venv
        if VENV.exists():
            try:
                shutil.rmtree(VENV)
                print("🗑️  Removed broken virtual environment")
            except Exception as e:
                print(f"⚠️  Warning: Could not remove old venv: {e}")
        
        try:
            # Create venv with system site packages for Colab compatibility
            create_cmd = [sys.executable, '-m', 'venv', str(VENV), '--system-site-packages']
            result = subprocess.run(create_cmd, check=True, capture_output=True, text=True)
            
            # Verify creation
            if not pip_executable.exists():
                raise RuntimeError("Virtual environment creation failed - pip not found after creation")
            
            print("✅ Virtual environment created successfully")
                
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to create virtual environment:")
            print(f"Command: {' '.join(create_cmd)}")
            print(f"Error: {e.stderr}")
            print("📦 Falling back to system pip...")
            pip_executable = 'pip'
        except Exception as e:
            print(f"❌ Unexpected error creating venv: {e}")
            print("📦 Falling back to system pip...")
            pip_executable = 'pip'
    
    # Install or update dependencies
    requirements_path = SCRIPTS / "requirements.txt"
    
    if not requirements_path.exists():
        print(f"⚠️  requirements.txt not found at {requirements_path}")
        print("📦 Installing essential dependencies...")
        
        # Essential packages for SD WebUI
        essential_packages = [
            "torch==2.1.2+cu121",
            "torchvision==0.16.2+cu121", 
            "xformers==0.0.23.post1",
            "transformers==4.36.2",
            "diffusers==0.25.0",
            "gradio==4.7.1",
            "fastapi==0.105.0",
            "accelerate==0.25.0",
            "safetensors==0.4.1"
        ]
        
        try:
            install_cmd = [
                str(pip_executable), "install", "--quiet",
                "--extra-index-url", "https://download.pytorch.org/whl/cu121"
            ] + essential_packages
            
            subprocess.run(install_cmd, check=True, capture_output=True, text=True, timeout=900)
            print("✅ Essential dependencies installed")
            
        except subprocess.TimeoutExpired:
            print("⚠️  Installation timed out, continuing...")
        except Exception as e:
            print(f"⚠️  Some essential packages failed to install: {e}")
            print("Continuing anyway...")
        
        return

    print(f"📦 Installing dependencies from {requirements_path}...")
    
    try:
        install_cmd = [str(pip_executable), "install", "-r", str(requirements_path), "--quiet"]
        
        result = subprocess.run(
            install_cmd,
            check=True,
            capture_output=True,
            text=True,
            timeout=1800  # 30 minute timeout
        )
        
        if widget_settings.get('detailed_download') == 'on':
            print("📋 Installation output:")
            print(result.stdout)
            
        print("✅ Virtual environment dependencies installed successfully")
        
    except subprocess.TimeoutExpired:
        print("⏱️  Dependency installation timed out after 30 minutes")
        print("📦 Continuing with existing packages...")
        
    except subprocess.CalledProcessError as e:
        print(f"⚠️  Some dependencies failed to install:")
        if widget_settings.get('detailed_download') == 'on':
            print(f"Error output: {e.stderr}")
        print("📦 Continuing with available packages...")
        
    except Exception as e:
        print(f"❌ Unexpected error during installation: {e}")
        print("📦 Continuing anyway...")

# Execute Venv Setup
setup_venv()

# WEBUI and EXTENSION INSTALLATION
if not Path(WEBUI).exists():
    print(f"⌚ Unpacking Stable Diffusion {UI}...")
    ipyRun('run', f"{SCRIPTS}/webui-installer.py")
else:
    print(f"🔧 WebUI {UI} already exists at {WEBUI}")

# DOWNLOAD LOGIC
print('📦 Downloading models and other assets...')

def handle_errors(func):
    """Decorator to catch and log exceptions."""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(f">> An error occurred in {func.__name__}: {str(e)}")
            return None
    return wrapper

# Load model data safely
model_files = '_xl-models-data.py' if widget_settings.get('XL_models', False) else '_models-data.py'
model_data_path = SCRIPTS / model_files

try:
    print(f"📖 Loading model data from {model_data_path}")
    with open(model_data_path) as f:
        exec(f.read())
    print(f"✅ Model data loaded: {len(locals().get('model_list', {}))} models, {len(locals().get('vae_list', {}))} VAEs, {len(locals().get('lora_list', {}))} LoRAs")
except Exception as e:
    print(f"⚠️  Warning: Could not load model data: {e}")
    model_list, vae_list, controlnet_list, lora_list = {}, {}, {}, {}

extension_repo = []

# Directory mapping for prefixes
PREFIX_MAP = {
    'model': (webui_settings.get('model_dir', ''), '$ckpt'),
    'vae': (webui_settings.get('vae_dir', ''), '$vae'),
    'lora': (webui_settings.get('lora_dir', ''), '$lora'),
    'embed': (webui_settings.get('embed_dir', ''), '$emb'),
    'extension': (webui_settings.get('extension_dir', ''), '$ext'),
    'adetailer': (webui_settings.get('adetailer_dir', ''), '$ad'),
    'control': (webui_settings.get('control_dir', ''), '$cnet'),
    'upscale': (webui_settings.get('upscale_dir', ''), '$ups'),
    'clip': (webui_settings.get('clip_dir', ''), '$clip'),
    'unet': (webui_settings.get('unet_dir', ''), '$unet'),
    'vision': (webui_settings.get('vision_dir', ''), '$vis'),
    'encoder': (webui_settings.get('encoder_dir', ''), '$enc'),
    'diffusion': (webui_settings.get('diffusion_dir', ''), '$diff'),
    'config': (webui_settings.get('config_dir', ''), '$cfg')
}

# Create directories
for dir_path, _ in PREFIX_MAP.values():
    if dir_path:
        os.makedirs(dir_path, exist_ok=True)

def _clean_url(url):
    """Clean and normalize URLs."""
    url = url.replace('/blob/', '/resolve/') if 'huggingface.co' in url else url
    url = url.replace('/blob/', '/raw/') if 'github.com' in url else url
    return url

def _extract_filename(url):
    """Extract filename from URL with bracket notation support."""
    if match := re.search(r'\[(.*?)\]', url):
        return match.group(1)
    if any(d in urlparse(url).netloc for d in ["civitai.com", "drive.google.com"]):
        return None
    return Path(urlparse(url).path).name

@handle_errors
def _process_download_link(link):
    """Process a download link and extract prefix, URL, and filename."""
    link = _clean_url(link)
    if ':' in link:
        prefix, path = link.split(':', 1)
        if prefix in PREFIX_MAP:
            return prefix, re.sub(r'\[.*?\]', '', path), _extract_filename(path)
    return None, link, None

@handle_errors
def manual_download(url, dst_dir, file_name=None, prefix=None):
    """Handle manual download with CivitAI API integration."""
    if 'civitai' in url:
        token = widget_settings.get('civitai_token', '') or os.getenv('CIVITAI_API_TOKEN', '')
        if not token or token == "Set in setup.py":
            print(f"⚠️  Warning: CivitAI token required for {url}")
            print("Please set your CivitAI token in the widgets or setup.py")
            return
            
        print(f"🎨 Processing CivitAI URL: {url}")
        api = CivitAiAPI(token, log=widget_settings.get('detailed_download') == 'on')
        data = api.validate_download(url, file_name)
        if not data:
            print(f"❌ Failed to get CivitAI download data for {url}")
            return
        url = data.download_url
        file_name = data.model_name
        print(f"✅ CivitAI download prepared: {file_name}")
    
    download_cmd = f'"{url}" "{dst_dir}" "{file_name or ""}"'
    print(f"⬇️  Downloading to {dst_dir}")
    m_download(download_cmd, log=widget_settings.get('detailed_download') == 'on', unzip=True)

def _parse_selection_numbers(num_str, max_num):
    """Parse number selections from string."""
    if not num_str: 
        return []
    
    num_str = num_str.replace(',', ' ').strip()
    unique_numbers = set()
    max_length = len(str(max_num))
    
    for part in num_str.split():
        if not part.isdigit(): 
            continue
            
        part_int = int(part)
        if part_int <= max_num:
            unique_numbers.add(part_int)
            continue
            
        # Handle concatenated numbers
        current_position = 0
        part_len = len(part)
        while current_position < part_len:
            found = False
            for length in range(min(max_length, part_len - current_position), 0, -1):
                substring = part[current_position:current_position + length]
                if substring.isdigit():
                    num = int(substring)
                    if 1 <= num <= max_num:
                        unique_numbers.add(num)
                        current_position += length
                        found = True
                        break
            if not found: 
                current_position += 1
                
    return sorted(unique_numbers)

def handle_submodels(selection, num_selection, model_dict, dst_dir, base_url):
    """Handle model selection and number parsing."""
    selected = []
    selections = selection if isinstance(selection, (list, tuple)) else [selection]

    # Handle dropdown/checkbox selections
    for sel in selections:
        if sel and sel.lower() != 'none':
            if sel == 'ALL':
                selected.extend(model_dict.values())
            elif sel in model_dict:
                item = model_dict[sel]
                selected.extend(item if isinstance(item, list) else [item])

    # Handle number selections
    if num_selection:
        max_num = len(model_dict)
        numbers = _parse_selection_numbers(num_selection, max_num)
        print(f"📊 Selected model numbers: {numbers}")
        for num in numbers:
            if 1 <= num <= max_num:
                name = list(model_dict.keys())[num - 1]
                item = model_dict[name]
                selected.extend(item if isinstance(item, list) else [item])

    # Remove duplicates while preserving order
    unique_models = {
        (model.get('name') or os.path.basename(model['url'])): model 
        for model in selected
    }.values()

    download_entries = [
        f'"{model["url"]}" "{dst_dir}" "{model.get("name", "")}"' 
        for model in unique_models
    ]
    
    result = (base_url + ", " if base_url else "") + ", ".join(download_entries)
    return result

# Process downloads
print("🔄 Processing selected models and assets...")

line = ""

# Models
if widget_settings.get('model') or widget_settings.get('model_num'):
    print("🎨 Processing model selections...")
    line = handle_submodels(
        widget_settings.get('model', []), 
        widget_settings.get('model_num', ''), 
        model_list, 
        webui_settings.get('model_dir', ''), 
        line
    )

# VAEs  
if widget_settings.get('vae', 'none') != 'none' or widget_settings.get('vae_num'):
    print("🎭 Processing VAE selections...")
    line = handle_submodels(
        widget_settings.get('vae', ''), 
        widget_settings.get('vae_num', ''), 
        vae_list, 
        webui_settings.get('vae_dir', ''), 
        line
    )

# LoRAs
if widget_settings.get('lora') and widget_settings.get('lora') != ('none',):
    print("✨ Processing LoRA selections...")
    line = handle_submodels(
        widget_settings.get('lora', []), 
        '', 
        lora_list, 
        webui_settings.get('lora_dir', ''), 
        line
    )

# ControlNets
if widget_settings.get('controlnet') and widget_settings.get('controlnet') != ('none',):
    print("🎮 Processing ControlNet selections...")
    line = handle_submodels(
        widget_settings.get('controlnet', []), 
        widget_settings.get('controlnet_num', ''), 
        controlnet_list, 
        webui_settings.get('control_dir', ''), 
        line
    )

# Execute downloads if we have selections
if line.strip():
    print(f"⬇️  Starting downloads...")
    if widget_settings.get('detailed_download') == 'on':
        print(f"Download command: {line[:200]}...")
    m_download(line, log=widget_settings.get('detailed_download') == 'on', unzip=True)
    print("✅ Model downloads completed")
else:
    print("⚠️  No models selected for download")

# Handle custom URLs
print("🌐 Processing custom download URLs...")

custom_downloads = []

if widget_settings.get('empowerment', False):
    # Empowerment mode - parse text area
    empowerment_text = widget_settings.get('empowerment_output', '')
    if empowerment_text:
        print("⚡ Processing empowerment mode URLs...")
        lines = empowerment_text.strip().split('\n')
        current_prefix = None
        
        for line_text in lines:
            line_text = line_text.strip()
            if not line_text or line_text.startswith('#'): 
                continue
            
            # Check for prefix tags
            tag_found = False
            for prefix, (_, short_tag) in PREFIX_MAP.items():
                if line_text.startswith(short_tag) or line_text.lower() == prefix:
                    current_prefix = prefix
                    tag_found = True
                    print(f"🏷️  Set prefix to: {prefix}")
                    break
            if tag_found: 
                continue
            
            # Process URLs
            if line_text.startswith('http') and current_prefix:
                custom_downloads.append(f"{current_prefix}:{line_text}")
            elif line_text.startswith('http'):
                custom_downloads.append(line_text)
else:
    # Individual URL fields
    url_fields = [
        ('Model_url', 'model'),
        ('Vae_url', 'vae'), 
        ('LoRA_url', 'lora'),
        ('Embedding_url', 'embed'),
        ('Extensions_url', 'extension'),
        ('ADetailer_url', 'adetailer'),
        ('custom_file_urls', None)
    ]
    
    for field_name, prefix in url_fields:
        url = widget_settings.get(field_name, '').strip()
        if url:
            if prefix:
                custom_downloads.append(f"{prefix}:{url}")
            else:
                custom_downloads.append(url)

# Process custom downloads
if custom_downloads:
    print(f"🌍 Processing {len(custom_downloads)} custom URLs...")
    
    for i, link in enumerate(custom_downloads, 1):
        if not link.strip():
            continue
            
        print(f"📥 [{i}/{len(custom_downloads)}] Processing: {link[:80]}...")
        
        prefix, url, filename = _process_download_link(link.strip())
        
        if prefix and prefix in PREFIX_MAP:
            dir_path, _ = PREFIX_MAP[prefix]
            if prefix == 'extension':
                extension_repo.append((url, filename))
                print(f"📝 Queued extension: {filename or 'Unknown'}")
            else:
                manual_download(url, dir_path, filename, prefix)
        else:
            # Download to general downloads folder
            downloads_dir = SCR_PATH / "Downloads"
            downloads_dir.mkdir(exist_ok=True)
            manual_download(link.strip(), downloads_dir, prefix="misc")

# Install custom extensions
if extension_repo:
    print(f"🔌 Installing {len(extension_repo)} custom extensions...")
    extension_dir = webui_settings.get('extension_dir', '')
    
    for repo_url, repo_name in extension_repo:
        print(f"📦 Installing: {repo_name or 'Extension'}")
        clone_cmd = f'"{repo_url}" "{extension_dir}" "{repo_name or ""}"'
        m_clone(clone_cmd, log=widget_settings.get('detailed_download') == 'on')
    
    print(f"✅ Installed {len(extension_repo)} custom extensions!")

print('🏁 All downloads completed successfully!')

# Display summary
total_selections = len([x for x in [
    widget_settings.get('model'),
    widget_settings.get('vae') if widget_settings.get('vae', 'none') != 'none' else None,
    widget_settings.get('lora') if widget_settings.get('lora') != ('none',) else None,
    widget_settings.get('controlnet') if widget_settings.get('controlnet') != ('none',) else None
] if x])

print(f"\n📊 Download Summary:")
print(f"   • Selected {total_selections} model/asset categories")
print(f"   • Processed {len(custom_downloads)} custom URLs") 
print(f"   • Installed {len(extension_repo)} extensions")
print(f"   • WebUI: {UI} at {WEBUI}")
print(f"✨ Ready to launch WebUI in the next cell!")

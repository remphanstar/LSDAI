# Enhanced downloading-en.py for LSDAI - Complete Restored Version
# Comprehensive dependency management with intelligent fallbacks and progress tracking
# RESTORED: Complete functionality with verbosity integration

import json_utils as js
from Manager import m_download, m_clone
from CivitaiAPI import CivitAiAPI
from pathlib import Path
import subprocess
import platform
import threading
import shutil
import time
import json
import sys
import os
import re

# Import verbosity system for consistent output control
try:
    from modules.verbose_output_manager import get_verbose_manager, VerbosityLevel, vprint
    verbose_manager = get_verbose_manager()
    
    def log_msg(message, level=VerbosityLevel.NORMAL):
        """Unified logging with verbosity control"""
        vprint(message, level)
        
    def vrun(cmd, **kwargs):
        """Run command with verbosity-controlled output"""
        return verbose_manager.run_command(cmd, **kwargs)
        
    VERBOSITY_AVAILABLE = True
    log_msg("✨ Verbosity system integrated", VerbosityLevel.DETAILED)
except ImportError:
    def log_msg(message, level=None):
        print(message)
    def vrun(cmd, **kwargs):
        return subprocess.run(cmd, **kwargs)
    VERBOSITY_AVAILABLE = False
    print("📦 Using standard output (verbosity not available)")

# Import enhanced modules if available
try:
    from modules.EnhancedManager import get_enhanced_manager
    from modules.NotificationSystem import send_info, send_success, send_error
    from modules.AdvancedLogging import get_advanced_logger
    ENHANCEMENTS_AVAILABLE = True
    log_msg("✨ Enhanced modules loaded", VerbosityLevel.DETAILED)
except ImportError:
    ENHANCEMENTS_AVAILABLE = False
    log_msg("📦 Using standard LSDAI functionality", VerbosityLevel.MINIMAL)

# Get paths and settings
HOME = Path(os.environ.get('home_path', '/content'))
SCR_PATH = Path(os.environ.get('scr_path', HOME / 'LSDAI'))
SCRIPTS = SCR_PATH / 'scripts'
VENV_PATH = Path(os.environ.get('venv_path', HOME / 'venv'))

# Read widget settings
try:
    widget_settings = js.read_key('WIDGETS', {})
    log_msg(f"✅ Widget settings loaded: {len(widget_settings)} items", VerbosityLevel.DETAILED)
except Exception as e:
    widget_settings = {}
    log_msg(f"⚠️ Using default settings: {e}", VerbosityLevel.MINIMAL)

log_msg(f"🔧 LSDAI Enhanced Downloading System v2.0", VerbosityLevel.NORMAL)
log_msg(f"📍 Working directory: {HOME}", VerbosityLevel.DETAILED)
log_msg(f"🐍 Python version: {sys.version}", VerbosityLevel.DETAILED)

def setup_comprehensive_safe_venv():
    """
    Enhanced venv setup with comprehensive extension-safe dependencies
    Pre-installs ALL dependencies to prevent extension conflicts later
    FIXED: Handles Colab ensurepip issues with verbosity integration
    """
    
    log_msg("="*60, VerbosityLevel.NORMAL)
    log_msg("🔧 Setting up comprehensive extension-safe environment...", VerbosityLevel.NORMAL)
    log_msg("📋 Strategy: Pre-install ALL dependencies to prevent conflicts", VerbosityLevel.DETAILED)
    log_msg("="*60, VerbosityLevel.NORMAL)
    
    # Step 1: Generate smart requirements.txt
    log_msg("📝 Generating comprehensive requirements.txt...", VerbosityLevel.NORMAL)
    req_file = generate_smart_requirements()
    
    # Step 2: Create venv with improved fallbacks
    log_msg("🐍 Creating virtual environment...", VerbosityLevel.NORMAL)
    venv_success = create_robust_venv_fixed()
    
    # Step 3: Install comprehensive dependencies  
    log_msg("📦 Installing comprehensive dependencies...", VerbosityLevel.NORMAL)
    install_success = install_comprehensive_deps(venv_success)
    
    # Step 4: Verify installation
    log_msg("🔍 Verifying installation...", VerbosityLevel.NORMAL)
    verify_success = verify_installation()
    
    # Step 5: Setup enhanced download manager if available
    if ENHANCEMENTS_AVAILABLE:
        log_msg("✨ Setting up enhanced download manager...", VerbosityLevel.DETAILED)
        setup_enhanced_download_manager()
    
    overall_success = venv_success and install_success and verify_success
    
    if overall_success:
        log_msg("✅ Virtual environment setup completed successfully", VerbosityLevel.NORMAL)
    else:
        log_msg("⚠️ Virtual environment setup completed with some issues", VerbosityLevel.MINIMAL)
        
    return overall_success

def generate_smart_requirements():
    """Generate comprehensive requirements.txt that works across platforms"""
    
    # Detect platform for optimizations
    is_colab = 'COLAB_GPU' in os.environ
    is_kaggle = 'KAGGLE_URL_BASE' in os.environ  
    is_lightning = any('LIGHTNING' in k for k in os.environ)
    
    log_msg(f"🌐 Platform detection: Colab={is_colab}, Kaggle={is_kaggle}, Lightning={is_lightning}", VerbosityLevel.DETAILED)
    
    # Comprehensive requirements with flexible versioning
    comprehensive_requirements = f"""# LSDAI Comprehensive Extension-Safe Requirements v2.0
# Generated for: {platform.system()} ({platform.machine()})
# Pre-installs ALL extension dependencies to prevent conflicts
# Compatible with Colab, Kaggle, Lightning.ai, local systems

# =================== CORE PYTORCH STACK ===================
# Auto-detects CUDA version - works everywhere
torch>=2.0.0,<2.2.0
torchvision>=0.15.0,<0.17.0
torchaudio>=2.0.0,<2.2.0

# =================== STABLE DIFFUSION CORE ===================
diffusers>=0.21.0,<0.25.0
transformers>=4.25.0,<4.35.0
accelerate>=0.20.0,<0.25.0
safetensors>=0.3.0,<0.5.0
datasets>=2.12.0,<3.0.0

# =================== IMAGE PROCESSING ===================
Pillow>=9.5.0,<11.0.0
opencv-python>=4.5.0,<5.0.0
imageio>=2.28.0,<3.0.0
imageio-ffmpeg>=0.4.0,<0.5.0
scikit-image>=0.20.0,<0.22.0

# =================== WEBUI DEPENDENCIES ===================
gradio>=3.40.0,<4.0.0
fastapi>=0.100.0,<0.105.0
uvicorn>=0.20.0,<0.25.0
pydantic>=1.10.0,<3.0.0
httpx>=0.24.0,<0.26.0

# =================== MACHINE LEARNING ===================
numpy>=1.24.0,<1.27.0
scipy>=1.10.0,<1.12.0
scikit-learn>=1.2.0,<1.4.0
pandas>=2.0.0,<2.2.0
matplotlib>=3.6.0,<3.8.0

# =================== NETWORKING & APIS ===================
requests>=2.28.0,<3.0.0
urllib3>=1.26.0,<3.0.0
aiohttp>=3.8.0,<4.0.0
tqdm>=4.64.0,<5.0.0

# =================== CONTROLNET & EXTENSIONS ===================
controlnet-aux>=0.0.6
mediapipe>=0.10.0,<0.11.0
insightface>=0.7.0,<0.8.0
facexlib>=0.3.0,<0.4.0
basicsr>=1.4.0,<2.0.0

# =================== XFORMERS & OPTIMIZATION ===================
{"xformers>=0.0.20,<0.0.22" if not is_colab else "# xformers  # Pre-installed in Colab"}
bitsandbytes>=0.41.0,<0.42.0

# =================== UTILITIES & DEVELOPMENT ===================
rich>=12.0.0,<14.0.0
loguru>=0.6.0,<0.8.0
psutil>=5.9.0,<6.0.0

# =================== CONFIGURATION MANAGEMENT ===================
jsonschema>=4.0.0,<5.0.0
pyyaml>=6.0,<7.0
omegaconf>=2.3.0,<3.0.0

# =================== JUPYTER/NOTEBOOK COMPATIBILITY ===================
ipython>=8.0.0,<9.0.0{" # Pre-installed" if is_colab or is_kaggle else ""}
ipywidgets>=8.0.0,<9.0.0{" # Pre-installed" if is_colab or is_kaggle else ""}

# =================== TOKENIZERS & NLP ===================
tokenizers>=0.13.0,<0.15.0
sentencepiece>=0.1.99,<0.2.0
protobuf>=3.20.0,<5.0.0

# =================== SAFETY & FALLBACKS ===================
setuptools>=65.0.0
wheel>=0.38.0
pip>=23.0.0

# End of requirements
"""
    
    req_file = SCRIPTS / "requirements.txt"
    req_file.write_text(comprehensive_requirements)
    
    total_packages = len([line for line in comprehensive_requirements.split('\n') 
                         if line.strip() and not line.strip().startswith('#')])
    
    log_msg(f"✅ Generated comprehensive requirements.txt", VerbosityLevel.NORMAL)
    log_msg(f"   📦 {total_packages} packages included", VerbosityLevel.DETAILED)
    log_msg(f"   📍 Location: {req_file}", VerbosityLevel.DETAILED)
    log_msg(f"   🛡️  Pre-installs dependencies for ALL major extensions", VerbosityLevel.DETAILED)
    
    return req_file

def create_robust_venv_fixed():
    """Create virtual environment with multiple fallback strategies - FIXED FOR COLAB"""
    
    log_msg(f"🐍 Creating virtual environment at {VENV_PATH}...", VerbosityLevel.NORMAL)
    
    # Check if venv already exists and is working
    if VENV_PATH.exists():
        log_msg("🔍 Checking existing virtual environment...", VerbosityLevel.DETAILED)
        if test_existing_venv():
            log_msg("✅ Existing virtual environment is working", VerbosityLevel.NORMAL)
            return True
        else:
            log_msg("🗑️ Removing broken virtual environment", VerbosityLevel.DETAILED)
            shutil.rmtree(VENV_PATH, ignore_errors=True)
    
    # Strategy 1: Colab-safe venv without pip (FIXED)
    try:
        log_msg("🔧 Strategy 1: Creating Colab-safe venv without pip...", VerbosityLevel.DETAILED)
        
        create_cmd = [sys.executable, '-m', 'venv', str(VENV_PATH), '--without-pip']
        result = vrun(create_cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            log_msg("✅ Venv created without pip", VerbosityLevel.DETAILED)
            # Install pip manually
            if install_pip_manually(VENV_PATH):
                if test_venv_creation():
                    log_msg("✅ Virtual environment created successfully (Colab-safe)", VerbosityLevel.NORMAL)
                    return True
                else:
                    log_msg("⚠️ Venv created but pip test failed", VerbosityLevel.DETAILED)
        else:
            log_msg(f"⚠️ Strategy 1 failed: {result.stderr}", VerbosityLevel.DETAILED)
            
    except subprocess.TimeoutExpired:
        log_msg("⏱️ Strategy 1 timed out", VerbosityLevel.DETAILED)
    except Exception as e:
        log_msg(f"⚠️ Strategy 1 exception: {e}", VerbosityLevel.DETAILED)
    
    # Clean up failed attempt
    if VENV_PATH.exists():
        shutil.rmtree(VENV_PATH, ignore_errors=True)
    
    # Strategy 2: Standard venv with system packages
    try:
        log_msg("🔧 Strategy 2: Creating venv with system packages...", VerbosityLevel.DETAILED)
        
        create_cmd = [sys.executable, '-m', 'venv', str(VENV_PATH), '--system-site-packages']
        result = vrun(create_cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            if test_venv_creation():
                log_msg("✅ Virtual environment created successfully", VerbosityLevel.NORMAL)
                return True
            else:
                log_msg("⚠️ Venv created but pip test failed", VerbosityLevel.DETAILED)
        else:
            log_msg(f"⚠️ Strategy 2 failed: {result.stderr}", VerbosityLevel.DETAILED)
            
    except subprocess.TimeoutExpired:
        log_msg("⏱️ Strategy 2 timed out", VerbosityLevel.DETAILED)
    except Exception as e:
        log_msg(f"⚠️ Strategy 2 exception: {e}", VerbosityLevel.DETAILED)
    
    # Strategy 3: Use system Python as fallback
    log_msg("📦 Virtual environment creation failed", VerbosityLevel.MINIMAL)
    log_msg("   Using system Python (this is OK - system will still work)", VerbosityLevel.MINIMAL)
    
    if ENHANCEMENTS_AVAILABLE:
        send_info("Venv Creation", "Using system Python instead of venv")
    
    return False

def install_pip_manually(venv_path):
    """Manually install pip in venv using get-pip.py"""
    try:
        log_msg("📦 Installing pip manually...", VerbosityLevel.DETAILED)
        python_exe = venv_path / 'bin' / 'python'
        
        if not python_exe.exists():
            return False
            
        # Download get-pip.py
        import urllib.request
        get_pip_url = "https://bootstrap.pypa.io/get-pip.py"
        get_pip_path = venv_path / 'get-pip.py'
        
        log_msg("📥 Downloading get-pip.py...", VerbosityLevel.DETAILED)
        urllib.request.urlretrieve(get_pip_url, get_pip_path)
        
        # Install pip
        cmd = [str(python_exe), str(get_pip_path)]
        result = vrun(cmd, capture_output=True, text=True, timeout=300)
        
        # Clean up
        get_pip_path.unlink(missing_ok=True)
        
        if result.returncode == 0:
            log_msg("✅ Pip installed manually", VerbosityLevel.DETAILED)
            return True
        else:
            log_msg(f"⚠️ Manual pip install failed: {result.stderr}", VerbosityLevel.DETAILED)
            return False
            
    except Exception as e:
        log_msg(f"⚠️ Manual pip install error: {e}", VerbosityLevel.DETAILED)
        return False

def test_existing_venv():
    """Test if existing venv is working"""
    try:
        pip_path = VENV_PATH / 'bin' / 'pip'
        if not pip_path.exists():
            pip_path = VENV_PATH / 'Scripts' / 'pip.exe'  # Windows
            
        if not pip_path.exists():
            return False
            
        # Test pip
        result = vrun([str(pip_path), '--version'], capture_output=True, text=True, timeout=30)
        return result.returncode == 0
        
    except Exception:
        return False

def test_venv_creation():
    """Test if newly created venv is working"""
    try:
        # Test pip in new venv
        pip_paths = [
            VENV_PATH / 'bin' / 'pip',        # Unix
            VENV_PATH / 'Scripts' / 'pip.exe'  # Windows
        ]
        
        for pip_path in pip_paths:
            if pip_path.exists():
                result = vrun([str(pip_path), '--version'], capture_output=True, text=True, timeout=30)
                if result.returncode == 0:
                    return True
                    
        return False
        
    except Exception:
        return False

def install_comprehensive_deps(venv_available):
    """Install comprehensive dependencies with smart error handling"""
    
    log_msg(f"📦 Installing comprehensive dependencies...", VerbosityLevel.NORMAL)
    
    # Determine pip executable
    pip_executable = get_pip_executable(venv_available)
    log_msg(f"🔧 Using pip: {pip_executable}", VerbosityLevel.DETAILED)
    
    # Upgrade pip first
    upgrade_pip(pip_executable)
    
    req_file = SCRIPTS / "requirements.txt"
    
    if not req_file.exists():
        log_msg(f"❌ Requirements file not found: {req_file}", VerbosityLevel.MINIMAL)
        return install_essential_fallback(pip_executable)
    
    # Strategy 1: Batch install (fastest if it works)
    log_msg("🚀 Attempting comprehensive batch installation...", VerbosityLevel.DETAILED)
    if install_batch(pip_executable, req_file):
        return True
    
    # Strategy 2: Tiered installation (most reliable)
    log_msg("📋 Using tiered installation strategy...", VerbosityLevel.NORMAL)
    return install_in_tiers(pip_executable)

def get_pip_executable(venv_available):
    """Get the correct pip executable"""
    if venv_available:
        # Try venv pip
        unix_pip = VENV_PATH / 'bin' / 'pip'
        windows_pip = VENV_PATH / 'Scripts' / 'pip.exe'
        
        if unix_pip.exists():
            return str(unix_pip)
        elif windows_pip.exists():
            return str(windows_pip)
    
    # Fallback to system pip
    return 'pip'

def upgrade_pip(pip_executable):
    """Upgrade pip to latest version"""
    try:
        log_msg("⬆️ Upgrading pip...", VerbosityLevel.DETAILED)
        result = vrun([pip_executable, 'install', '--upgrade', 'pip', '--quiet'], 
                     capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            log_msg("✅ Pip upgraded successfully", VerbosityLevel.DETAILED)
        else:
            log_msg("⚠️ Pip upgrade failed (continuing anyway)", VerbosityLevel.DETAILED)
            
    except Exception as e:
        log_msg(f"⚠️ Pip upgrade error: {e}", VerbosityLevel.DETAILED)

def install_batch(pip_executable, req_file):
    """Try to install all requirements in one batch"""
    try:
        log_msg("📦 Installing all dependencies in batch...", VerbosityLevel.DETAILED)
        
        cmd = [pip_executable, 'install', '-r', str(req_file), '--quiet', '--disable-pip-version-check']
        
        result = vrun(cmd, capture_output=True, text=True, timeout=1800)
        
        if result.returncode == 0:
            log_msg("✅ Batch installation successful", VerbosityLevel.NORMAL)
            return True
        else:
            log_msg(f"⚠️ Batch installation failed: {result.stderr[:200]}...", VerbosityLevel.DETAILED)
            return False
            
    except subprocess.TimeoutExpired:
        log_msg("⏱️ Batch installation timed out", VerbosityLevel.DETAILED)
        return False
    except Exception as e:
        log_msg(f"⚠️ Batch installation error: {e}", VerbosityLevel.DETAILED)
        return False

def install_in_tiers(pip_executable):
    """Install packages in tiers for maximum compatibility"""
    
    log_msg("📋 Installing packages in compatibility tiers...", VerbosityLevel.NORMAL)
    
    # Tier 1: Essential packages
    tier1_packages = ["wheel", "setuptools", "pip", "numpy", "pillow", "requests", "tqdm"]
    
    # Tier 2: Core ML packages
    tier2_packages = ["torch", "torchvision", "torchaudio", "transformers", "diffusers", "accelerate"]
    
    # Tier 3: WebUI packages
    tier3_packages = ["gradio", "fastapi", "uvicorn", "safetensors"]
    
    # Tier 4: Extension packages
    tier4_packages = ["opencv-python", "controlnet-aux", "insightface"]
    
    tiers = [
        ("Essential", tier1_packages),
        ("Core ML", tier2_packages),
        ("WebUI", tier3_packages),
        ("Extensions", tier4_packages)
    ]
    
    success_count = 0
    total_tiers = len(tiers)
    
    for tier_name, packages in tiers:
        log_msg(f"📦 Installing {tier_name} tier ({len(packages)} packages)...", VerbosityLevel.DETAILED)
        
        tier_success = install_package_list(pip_executable, packages)
        if tier_success:
            success_count += 1
            log_msg(f"✅ {tier_name} tier completed", VerbosityLevel.DETAILED)
        else:
            log_msg(f"⚠️ {tier_name} tier had issues", VerbosityLevel.DETAILED)
    
    log_msg(f"📊 Installation summary: {success_count}/{total_tiers} tiers successful", VerbosityLevel.NORMAL)
    return success_count >= 2  # Need at least essential + core ML

def install_package_list(pip_executable, packages):
    """Install a list of packages with individual error handling"""
    
    success_count = 0
    
    for package in packages:
        try:
            cmd = [pip_executable, 'install', package, '--quiet', '--disable-pip-version-check']
            result = vrun(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                success_count += 1
                log_msg(f"  ✅ {package}", VerbosityLevel.VERBOSE)
            else:
                log_msg(f"  ⚠️ Failed to install {package}", VerbosityLevel.DETAILED)
                
        except Exception as e:
            log_msg(f"  ⚠️ Error installing {package}: {e}", VerbosityLevel.DETAILED)
    
    return success_count > len(packages) * 0.7  # 70% success rate

def install_essential_fallback(pip_executable):
    """Install only essential packages as fallback"""
    
    log_msg("🆘 Installing essential packages only (fallback mode)...", VerbosityLevel.MINIMAL)
    
    essential_packages = [
        "torch", "torchvision", "transformers", "diffusers",
        "gradio", "safetensors", "pillow", "numpy"
    ]
    
    return install_package_list(pip_executable, essential_packages)

def verify_installation():
    """Verify that key packages are installed and working"""
    
    log_msg("🔍 Verifying installation...", VerbosityLevel.NORMAL)
    
    test_packages = [
        ("torch", "import torch; print(f'PyTorch {torch.__version__}')"),
        ("transformers", "import transformers; print(f'Transformers {transformers.__version__}')"),
        ("diffusers", "import diffusers; print(f'Diffusers {diffusers.__version__}')"),
        ("gradio", "import gradio; print(f'Gradio {gradio.__version__}')")
    ]
    
    working_packages = 0
    
    for package_name, test_code in test_packages:
        try:
            exec(test_code)
            working_packages += 1
            log_msg(f"✅ {package_name} working", VerbosityLevel.DETAILED)
        except Exception as e:
            log_msg(f"⚠️ {package_name} not working: {e}", VerbosityLevel.DETAILED)
    
    log_msg(f"📊 Verification: {working_packages}/{len(test_packages)} packages working", VerbosityLevel.NORMAL)
    return working_packages >= 2

def setup_enhanced_download_manager():
    """Setup enhanced download manager if available"""
    
    if ENHANCEMENTS_AVAILABLE:
        try:
            log_msg("✨ Setting up enhanced download manager...", VerbosityLevel.DETAILED)
            enhanced_manager, batch_ops = get_enhanced_manager()
            log_msg("✅ Enhanced download manager ready", VerbosityLevel.DETAILED)
            return True
        except Exception as e:
            log_msg(f"⚠️ Enhanced manager setup failed: {e}", VerbosityLevel.DETAILED)
            return False
    return False

def install_webui():
    """Install selected WebUI with verbosity integration"""
    
    log_msg("🚀 Installing WebUI...", VerbosityLevel.NORMAL)
    
    # Get WebUI selection from settings
    webui_type = widget_settings.get('change_webui', 'automatic1111')
    home_path = HOME
    
    webui_configs = {
        'automatic1111': {
            'url': 'https://github.com/AUTOMATIC1111/stable-diffusion-webui.git',
            'path': home_path / 'stable-diffusion-webui',
            'branch': widget_settings.get('commit_hash', 'master')
        },
        'ComfyUI': {
            'url': 'https://github.com/comfyanonymous/ComfyUI.git',
            'path': home_path / 'ComfyUI',
            'branch': 'master'
        },
        'Forge': {
            'url': 'https://github.com/lllyasviel/stable-diffusion-webui-forge.git',
            'path': home_path / 'stable-diffusion-webui-forge',
            'branch': 'main'
        }
    }
    
    config = webui_configs.get(webui_type, webui_configs['automatic1111'])
    
    try:
        if not config['path'].exists():
            log_msg(f"📥 Cloning {webui_type}...", VerbosityLevel.NORMAL)
            
            cmd = ['git', 'clone', config['url'], str(config['path'])]
            if config.get('branch') and config['branch'] != 'master':
                cmd.extend(['--branch', config['branch']])
                
            result = vrun(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                log_msg(f"✅ {webui_type} cloned successfully", VerbosityLevel.NORMAL)
                return True
            else:
                log_msg(f"❌ Failed to clone {webui_type}: {result.stderr}", VerbosityLevel.MINIMAL)
                return False
        else:
            log_msg(f"✅ {webui_type} already exists", VerbosityLevel.NORMAL)
            return True
            
    except Exception as e:
        log_msg(f"❌ WebUI installation error: {e}", VerbosityLevel.MINIMAL)
        return False

def download_models_and_assets():
    """Download models and assets based on widget settings with verbosity integration"""
    
    log_msg("🎨 Downloading models and assets...", VerbosityLevel.NORMAL)
    
    # Get all URLs from widget settings
    url_categories = {
        'Models': widget_settings.get('Model_url', ''),
        'VAEs': widget_settings.get('Vae_url', ''),
        'LoRAs': widget_settings.get('LoRA_url', ''),
        'Embeddings': widget_settings.get('Embedding_url', ''),
        'Extensions': widget_settings.get('Extensions_url', ''),
        'ADetailer': widget_settings.get('ADetailer_url', ''),
        'Custom Files': widget_settings.get('custom_file_urls', '')
    }
    
    total_downloads = 0
    successful_downloads = 0
    
    for category, urls_string in url_categories.items():
        if not urls_string:
            continue
            
        urls = [url.strip() for url in urls_string.split(',') if url.strip()]
        if not urls:
            continue
            
        log_msg(f"📥 Downloading {category} ({len(urls)} items)...", VerbosityLevel.NORMAL)
        
        for url in urls:
            total_downloads += 1
            try:
                log_msg(f"  🔄 Processing: {url[:60]}...", VerbosityLevel.DETAILED)
                
                if category == 'Extensions':
                    # Use git clone for extensions
                    success = download_extension(url)
                else:
                    # Use m_download for models/files
                    success = m_download(url, log=True)
                    
                if success:
                    successful_downloads += 1
                    log_msg(f"  ✅ Downloaded: {url[:60]}...", VerbosityLevel.DETAILED)
                else:
                    log_msg(f"  ⚠️ Failed: {url[:60]}...", VerbosityLevel.DETAILED)
                    
            except Exception as e:
                log_msg(f"  ❌ Download failed for {url}: {e}", VerbosityLevel.DETAILED)
    
    # Summary
    if total_downloads == 0:
        log_msg("⚠️ No downloads specified", VerbosityLevel.MINIMAL)
        return True
    elif successful_downloads == total_downloads:
        log_msg(f"✅ All {total_downloads} downloads completed successfully", VerbosityLevel.NORMAL)
        return True
    elif successful_downloads > 0:
        log_msg(f"✅ {successful_downloads}/{total_downloads} downloads completed", VerbosityLevel.NORMAL)
        return True
    else:
        log_msg("❌ All downloads failed", VerbosityLevel.MINIMAL)
        return False

def download_extension(url):
    """Download extension using git clone with verbosity integration"""
    try:
        # Determine WebUI type for extension path
        webui_type = widget_settings.get('change_webui', 'automatic1111')
        
        if webui_type == 'automatic1111':
            extensions_dir = HOME / 'stable-diffusion-webui' / 'extensions'
        elif webui_type == 'ComfyUI':
            extensions_dir = HOME / 'ComfyUI' / 'custom_nodes'
        elif webui_type == 'Forge':
            extensions_dir = HOME / 'stable-diffusion-webui-forge' / 'extensions'
        else:
            extensions_dir = HOME / 'stable-diffusion-webui' / 'extensions'
        
        extensions_dir.mkdir(parents=True, exist_ok=True)
        
        # Extract repo name from URL
        repo_name = url.split('/')[-1].replace('.git', '')
        target_path = extensions_dir / repo_name
        
        if not target_path.exists():
            cmd = ['git', 'clone', url, str(target_path)]
            result = vrun(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                log_msg(f"    ✅ Extension cloned: {repo_name}", VerbosityLevel.DETAILED)
                return True
            else:
                log_msg(f"    ❌ Extension clone failed: {repo_name}", VerbosityLevel.DETAILED)
                return False
        else:
            log_msg(f"    ✅ Extension exists: {repo_name}", VerbosityLevel.DETAILED)
            return True  # Already exists
            
    except Exception as e:
        log_msg(f"    ❌ Extension download error: {e}", VerbosityLevel.DETAILED)
        return False

def setup_performance_monitoring():
    """Setup performance monitoring if available"""
    
    if ENHANCEMENTS_AVAILABLE:
        try:
            log_msg("📊 Setting up performance monitoring...", VerbosityLevel.DETAILED)
            logger = get_advanced_logger()
            logger.log_system_info()
            log_msg("✅ Performance monitoring active", VerbosityLevel.DETAILED)
        except Exception as e:
            log_msg(f"⚠️ Monitoring setup failed: {e}", VerbosityLevel.DETAILED)

# =================== MAIN EXECUTION ===================

def main():
    """Main execution function with comprehensive verbosity integration"""
    
    log_msg("🔥 LSDAI Enhanced Downloading System v2.0", VerbosityLevel.NORMAL)
    log_msg("="*60, VerbosityLevel.NORMAL)
    
    start_time = time.time()
    
    # Step 1: Setup comprehensive venv
    log_msg("Step 1/4: Setting up environment...", VerbosityLevel.NORMAL)
    venv_success = setup_comprehensive_safe_venv()
    
    # Step 2: Install WebUI
    log_msg("\nStep 2/4: Installing WebUI...", VerbosityLevel.NORMAL)
    webui_success = install_webui()
    
    # Step 3: Download models and assets
    log_msg("\nStep 3/4: Downloading models and assets...", VerbosityLevel.NORMAL)
    download_success = download_models_and_assets()
    
    # Step 4: Final setup and verification
    log_msg("\nStep 4/4: Final setup...", VerbosityLevel.NORMAL)
    
    # Setup performance monitoring if available
    if ENHANCEMENTS_AVAILABLE:
        setup_performance_monitoring()
    
    # Summary
    elapsed_time = time.time() - start_time
    
    log_msg("\n" + "="*60, VerbosityLevel.NORMAL)
    log_msg("📊 LSDAI Setup Summary", VerbosityLevel.NORMAL)
    log_msg("="*60, VerbosityLevel.NORMAL)
    log_msg(f"⏱️ Total time: {elapsed_time:.1f} seconds", VerbosityLevel.NORMAL)
    log_msg(f"🐍 Environment: {'✅ Ready' if venv_success else '⚠️ Limited'}", VerbosityLevel.NORMAL)
    log_msg(f"🚀 WebUI: {'✅ Installed' if webui_success else '❌ Failed'}", VerbosityLevel.NORMAL)
    log_msg(f"🎨 Downloads: {'✅ Complete' if download_success else '⚠️ Issues'}", VerbosityLevel.NORMAL)
    
    if venv_success and webui_success:
        log_msg("\n🎉 LSDAI setup completed successfully!", VerbosityLevel.NORMAL)
        log_msg("🚀 Ready to launch WebUI in the next cell", VerbosityLevel.NORMAL)
        
        if ENHANCEMENTS_AVAILABLE:
            send_success("LSDAI Setup Complete", "Ready to launch WebUI")
    else:
        log_msg("\n⚠️ LSDAI setup completed with some issues", VerbosityLevel.MINIMAL)
        log_msg("🔧 Check the logs above for details", VerbosityLevel.MINIMAL)
        
        if ENHANCEMENTS_AVAILABLE:
            send_error("LSDAI Setup Issues", "Some components failed to install")

# Execute main if run directly
if __name__ == "__main__":
    main()

# For compatibility when imported
create_robust_venv = create_robust_venv_fixed

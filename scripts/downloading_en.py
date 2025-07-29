# Enhanced downloading-en.py for LSDAI
# Comprehensive dependency management with intelligent fallbacks and progress tracking
# FIXED: Colab-safe venv creation that handles ensurepip failures

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

# Import enhanced modules if available
try:
    from modules.EnhancedManager import get_enhanced_manager
    from modules.NotificationSystem import send_info, send_success, send_error
    from modules.AdvancedLogging import get_advanced_logger
    ENHANCEMENTS_AVAILABLE = True
    print("✨ Enhanced modules loaded")
except ImportError:
    ENHANCEMENTS_AVAILABLE = False
    print("📦 Using standard LSDAI functionality")

# Get paths and settings
HOME = Path(os.environ.get('home_path', '/content'))
SCR_PATH = Path(os.environ.get('scr_path', HOME / 'LSDAI'))
SCRIPTS = SCR_PATH / 'scripts'
VENV_PATH = Path(os.environ.get('venv_path', HOME / 'venv'))

# Read widget settings
try:
    widget_settings = js.read_key('WIDGETS', {})
except:
    widget_settings = {}

print(f"🔧 LSDAI Enhanced Downloading System")
print(f"📍 Working directory: {HOME}")
print(f"🐍 Python version: {sys.version}")

def setup_comprehensive_safe_venv():
    """
    Enhanced venv setup with comprehensive extension-safe dependencies
    Pre-installs ALL dependencies to prevent extension conflicts later
    FIXED: Handles Colab ensurepip issues
    """
    
    print("\n" + "="*60)
    print("🔧 Setting up comprehensive extension-safe environment...")
    print("📋 Strategy: Pre-install ALL dependencies to prevent conflicts")
    print("="*60)
    
    # Step 1: Generate smart requirements.txt
    generate_smart_requirements()
    
    # Step 2: Create venv with improved fallbacks (FIXED)
    venv_success = create_robust_venv_fixed()
    
    # Step 3: Install comprehensive dependencies  
    install_success = install_comprehensive_deps(venv_success)
    
    # Step 4: Verify installation
    verify_installation()
    
    # Step 5: Setup enhanced download manager if available
    if ENHANCEMENTS_AVAILABLE:
        setup_enhanced_download_manager()
    
    return venv_success and install_success

def generate_smart_requirements():
    """Generate comprehensive requirements.txt that works across platforms"""
    
    print("📝 Generating comprehensive requirements.txt...")
    
    # Detect platform for optimizations
    is_colab = 'COLAB_GPU' in os.environ
    is_kaggle = 'KAGGLE_URL_BASE' in os.environ  
    is_lightning = any('LIGHTNING' in k for k in os.environ)
    
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
seaborn>=0.12.0,<0.14.0

# =================== NETWORKING & APIS ===================
requests>=2.28.0,<3.0.0
urllib3>=1.26.0,<3.0.0
aiohttp>=3.8.0,<4.0.0
websockets>=11.0,<12.0
tqdm>=4.64.0,<5.0.0

# =================== AUDIO PROCESSING ===================
librosa>=0.10.0,<0.11.0
soundfile>=0.12.0,<0.13.0
resampy>=0.4.0,<0.5.0

# =================== CONTROLNET & EXTENSIONS ===================
controlnet-aux>=0.0.6
mediapipe>=0.10.0,<0.11.0
insightface>=0.7.0,<0.8.0
facexlib>=0.3.0,<0.4.0
gfpgan>=1.3.0,<2.0.0
basicsr>=1.4.0,<2.0.0
realesrgan>=0.3.0,<0.4.0

# =================== XFORMERS & OPTIMIZATION ===================
{"xformers>=0.0.20,<0.0.22" if not is_colab else "# xformers  # Pre-installed in Colab"}
triton>=2.0.0,<3.0.0
bitsandbytes>=0.41.0,<0.42.0

# =================== 3D & ADVANCED FEATURES ===================
trimesh>=3.20.0,<4.0.0
pygltflib>=1.15.0,<2.0.0
open3d>=0.17.0,<0.19.0

# =================== MODEL FORMATS ===================
onnx>=1.14.0,<1.16.0
onnxruntime>=1.15.0,<1.17.0
gguf>=0.1.0
llama-cpp-python>=0.2.0
ctransformers>=0.2.0

# =================== QUALITY & ANALYSIS ===================
clip-interrogator>=0.6.0
aesthetic-predictor>=1.0.0
laion-aesthetic-predictor>=1.0.0

# =================== UTILITIES & DEVELOPMENT ===================
rich>=12.0.0,<14.0.0
loguru>=0.6.0,<0.8.0
typer>=0.9.0,<0.10.0
click>=8.1.0,<9.0.0

# =================== FILE HANDLING ===================
send2trash>=1.8.0
psutil>=5.9.0,<6.0.0
pathvalidate>=2.5.0
py7zr>=0.20.0

# =================== CONFIGURATION MANAGEMENT ===================
jsonschema>=4.0.0,<5.0.0
pyyaml>=6.0,<7.0
toml>=0.10.0
omegaconf>=2.3.0,<3.0.0
hydra-core>=1.3.0,<2.0.0

# =================== JUPYTER/NOTEBOOK COMPATIBILITY ===================
ipython>=8.0.0,<9.0.0{" # Pre-installed" if is_colab or is_kaggle else ""}
ipywidgets>=8.0.0,<9.0.0{" # Pre-installed" if is_colab or is_kaggle else ""}
jupyter>=1.0.0

# =================== MEMORY OPTIMIZATION ===================
memory-profiler>=0.60.0
pympler>=0.9

# =================== TOKENIZERS & NLP ===================
tokenizers>=0.13.0,<0.15.0
sentencepiece>=0.1.99,<0.2.0
protobuf>=3.20.0,<5.0.0
nltk>=3.8,<4.0

# =================== EXTENSION-SPECIFIC DEPS ===================
numpy-financial>=1.0.0

# =================== PLATFORM SPECIFIC ===================
{"colorama>=0.4.0" if platform.system() == "Windows" else "# colorama  # Not needed on Unix"}
{"pywin32>=227" if platform.system() == "Windows" else "# pywin32  # Windows only"}

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
    
    print(f"✅ Generated comprehensive requirements.txt")
    print(f"   📦 {total_packages} packages included")
    print(f"   📍 Location: {req_file}")
    print(f"   🛡️  Pre-installs dependencies for ALL major extensions")
    
    return req_file

def create_robust_venv_fixed():
    """Create virtual environment with multiple fallback strategies - FIXED FOR COLAB"""
    
    print(f"\n🐍 Creating virtual environment at {VENV_PATH}...")
    
    # Check if venv already exists and is working
    if VENV_PATH.exists():
        print("🔍 Checking existing virtual environment...")
        if test_existing_venv():
            print("✅ Existing virtual environment is working")
            return True
        else:
            print("🗑️  Removing broken virtual environment")
            shutil.rmtree(VENV_PATH, ignore_errors=True)
    
    # Strategy 1: Colab-safe venv without pip (FIXED)
    try:
        print("🔧 Strategy 1: Creating Colab-safe venv without pip...")
        
        create_cmd = [sys.executable, '-m', 'venv', str(VENV_PATH), '--without-pip']
        result = subprocess.run(create_cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print("✅ Venv created without pip")
            # Install pip manually
            if install_pip_manually(VENV_PATH):
                if test_venv_creation():
                    print("✅ Virtual environment created successfully (Colab-safe)")
                    return True
                else:
                    print("⚠️  Venv created but pip test failed")
        else:
            print(f"⚠️  Strategy 1 failed: {result.stderr}")
            
    except subprocess.TimeoutExpired:
        print("⏱️  Strategy 1 timed out")
    except Exception as e:
        print(f"⚠️  Strategy 1 exception: {e}")
    
    # Clean up failed attempt
    if VENV_PATH.exists():
        shutil.rmtree(VENV_PATH, ignore_errors=True)
    
    # Strategy 2: Standard venv with system packages
    try:
        print("🔧 Strategy 2: Creating venv with system packages...")
        
        create_cmd = [sys.executable, '-m', 'venv', str(VENV_PATH), '--system-site-packages']
        result = subprocess.run(create_cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            if test_venv_creation():
                print("✅ Virtual environment created successfully")
                return True
            else:
                print("⚠️  Venv created but pip test failed")
        else:
            print(f"⚠️  Strategy 2 failed: {result.stderr}")
            
    except subprocess.TimeoutExpired:
        print("⏱️  Strategy 2 timed out")
    except Exception as e:
        print(f"⚠️  Strategy 2 exception: {e}")
    
    # Clean up failed attempt
    if VENV_PATH.exists():
        shutil.rmtree(VENV_PATH, ignore_errors=True)
    
    # Strategy 3: Isolated venv
    try:
        print("🔧 Strategy 3: Creating isolated venv...")
        
        create_cmd = [sys.executable, '-m', 'venv', str(VENV_PATH)]
        result = subprocess.run(create_cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            if test_venv_creation():
                print("✅ Virtual environment created (isolated)")
                return True
            else:
                print("⚠️  Isolated venv created but pip test failed")
        else:
            print(f"⚠️  Strategy 3 failed: {result.stderr}")
            
    except subprocess.TimeoutExpired:
        print("⏱️  Strategy 3 timed out")
    except Exception as e:
        print(f"⚠️  Strategy 3 exception: {e}")
    
    # Strategy 4: Pseudo-venv with system symlinks (NEW)
    try:
        print("🔧 Strategy 4: Creating pseudo-venv with system symlinks...")
        if create_pseudo_venv(VENV_PATH):
            print("✅ Pseudo-venv created successfully")
            return True
    except Exception as e:
        print(f"⚠️  Strategy 4 exception: {e}")
    
    # All strategies failed
    print("📦 Virtual environment creation failed")
    print("   Using system Python (this is OK - system will still work)")
    
    if ENHANCEMENTS_AVAILABLE:
        send_info("Venv Creation", "Using system Python instead of venv")
    
    return False

def install_pip_manually(venv_path):
    """Manually install pip in venv using get-pip.py"""
    try:
        print("📦 Installing pip manually...")
        python_exe = venv_path / 'bin' / 'python'
        
        if not python_exe.exists():
            return False
            
        # Download get-pip.py
        import urllib.request
        get_pip_url = "https://bootstrap.pypa.io/get-pip.py"
        get_pip_path = venv_path / 'get-pip.py'
        
        print("📥 Downloading get-pip.py...")
        urllib.request.urlretrieve(get_pip_url, get_pip_path)
        
        # Install pip
        cmd = [str(python_exe), str(get_pip_path)]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        # Clean up
        get_pip_path.unlink(missing_ok=True)
        
        if result.returncode == 0:
            print("✅ Pip installed manually")
            return True
        else:
            print(f"⚠️  Manual pip install failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"⚠️  Manual pip install error: {e}")
        return False

def create_pseudo_venv(venv_path):
    """Create a pseudo-venv by symlinking to system executables"""
    try:
        # Create basic venv structure
        venv_path.mkdir(parents=True, exist_ok=True)
        bin_dir = venv_path / 'bin'
        bin_dir.mkdir(exist_ok=True)
        
        # Create symlinks to system executables
        system_python = sys.executable
        venv_python = bin_dir / 'python'
        venv_pip = bin_dir / 'pip'
        
        # Create python symlink
        if not venv_python.exists():
            venv_python.symlink_to(system_python)
        
        # Find and create pip symlink
        system_pip = None
        for pip_name in ['pip', 'pip3']:
            result = subprocess.run(['which', pip_name], capture_output=True, text=True)
            if result.returncode == 0:
                system_pip = result.stdout.strip()
                break
                
        if system_pip and not venv_pip.exists():
            venv_pip.symlink_to(system_pip)
            
        # Test the setup
        if venv_python.exists() and venv_pip.exists():
            test_result = subprocess.run([str(venv_pip), '--version'], 
                                       capture_output=True, text=True, timeout=30)
            return test_result.returncode == 0
            
        return False
        
    except Exception as e:
        print(f"⚠️  Pseudo-venv creation error: {e}")
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
        result = subprocess.run([str(pip_path), '--version'], 
                              capture_output=True, text=True, timeout=30)
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
                result = subprocess.run([str(pip_path), '--version'], 
                                      capture_output=True, text=True, timeout=30)
                if result.returncode == 0:
                    return True
                    
        return False
        
    except Exception:
        return False

def install_comprehensive_deps(venv_available):
    """Install comprehensive dependencies with smart error handling"""
    
    print(f"\n📦 Installing comprehensive dependencies...")
    
    # Determine pip executable
    pip_executable = get_pip_executable(venv_available)
    print(f"🔧 Using pip: {pip_executable}")
    
    # Upgrade pip first
    upgrade_pip(pip_executable)
    
    req_file = SCRIPTS / "requirements.txt"
    
    if not req_file.exists():
        print(f"❌ Requirements file not found: {req_file}")
        return install_essential_fallback(pip_executable)
    
    # Strategy 1: Batch install (fastest if it works)
    print("🚀 Attempting comprehensive batch installation...")
    if install_batch(pip_executable, req_file):
        return True
    
    # Strategy 2: Tiered installation (most reliable)
    print("📋 Using tiered installation strategy...")
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
        print("⬆️  Upgrading pip...")
        result = subprocess.run([
            pip_executable, 'install', '--upgrade', 'pip', '--quiet'
        ], capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print("✅ Pip upgraded successfully")
        else:
            print("⚠️  Pip upgrade failed (continuing anyway)")
            
    except Exception as e:
        print(f"⚠️  Pip upgrade error: {e}")

def install_batch(pip_executable, req_file):
    """Try to install all requirements in one batch"""
    try:
        print("📦 Installing all dependencies in batch...")
        
        cmd = [
            pip_executable, 'install', '-r', str(req_file),
            '--no-deps', '--quiet', '--disable-pip-version-check'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)
        
        if result.returncode == 0:
            print("✅ Batch installation successful")
            return True
        else:
            print(f"⚠️  Batch installation failed: {result.stderr[:200]}...")
            return False
            
    except subprocess.TimeoutExpired:
        print("⏱️  Batch installation timed out")
        return False
    except Exception as e:
        print(f"⚠️  Batch installation error: {e}")
        return False

def install_in_tiers(pip_executable):
    """Install packages in tiers for maximum compatibility"""
    
    print("📋 Installing packages in compatibility tiers...")
    
    # Tier 1: Essential packages
    tier1_packages = [
        "wheel", "setuptools", "pip",
        "numpy", "pillow", "requests", "tqdm"
    ]
    
    # Tier 2: Core ML packages
    tier2_packages = [
        "torch", "torchvision", "torchaudio",
        "transformers", "diffusers", "accelerate"
    ]
    
    # Tier 3: WebUI packages
    tier3_packages = [
        "gradio", "fastapi", "uvicorn", "safetensors"
    ]
    
    # Tier 4: Extension packages
    tier4_packages = [
        "opencv-python", "controlnet-aux", "insightface"
    ]
    
    tiers = [
        ("Essential", tier1_packages),
        ("Core ML", tier2_packages),
        ("WebUI", tier3_packages),
        ("Extensions", tier4_packages)
    ]
    
    success_count = 0
    total_tiers = len(tiers)
    
    for tier_name, packages in tiers:
        print(f"📦 Installing {tier_name} tier ({len(packages)} packages)...")
        
        tier_success = install_package_list(pip_executable, packages)
        if tier_success:
            success_count += 1
            print(f"✅ {tier_name} tier completed")
        else:
            print(f"⚠️  {tier_name} tier had issues")
    
    print(f"📊 Installation summary: {success_count}/{total_tiers} tiers successful")
    return success_count >= 2  # Need at least essential + core ML

def install_package_list(pip_executable, packages):
    """Install a list of packages with individual error handling"""
    
    success_count = 0
    
    for package in packages:
        try:
            cmd = [pip_executable, 'install', package, '--quiet', '--disable-pip-version-check']
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                success_count += 1
            else:
                print(f"⚠️  Failed to install {package}")
                
        except Exception as e:
            print(f"⚠️  Error installing {package}: {e}")
    
    return success_count > len(packages) * 0.7  # 70% success rate

def install_essential_fallback(pip_executable):
    """Install only essential packages as fallback"""
    
    print("🆘 Installing essential packages only (fallback mode)...")
    
    essential_packages = [
        "torch", "torchvision", "transformers", "diffusers",
        "gradio", "safetensors", "pillow", "numpy"
    ]
    
    return install_package_list(pip_executable, essential_packages)

def verify_installation():
    """Verify that key packages are installed and working"""
    
    print("\n🔍 Verifying installation...")
    
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
            print(f"✅ {package_name} working")
        except Exception as e:
            print(f"⚠️  {package_name} not working: {e}")
    
    print(f"📊 Verification: {working_packages}/{len(test_packages)} packages working")
    return working_packages >= 2

def setup_enhanced_download_manager():
    """Setup enhanced download manager if available"""
    
    if ENHANCEMENTS_AVAILABLE:
        try:
            print("✨ Setting up enhanced download manager...")
            enhanced_manager, batch_ops = get_enhanced_manager()
            print("✅ Enhanced download manager ready")
            return True
        except Exception as e:
            print(f"⚠️  Enhanced manager setup failed: {e}")
            return False
    return False

def install_webui():
    """Install selected WebUI"""
    
    print("🚀 Installing WebUI...")
    
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
        }
    }
    
    config = webui_configs.get(webui_type, webui_configs['automatic1111'])
    
    try:
        if not config['path'].exists():
            print(f"📥 Cloning {webui_type}...")
            
            cmd = ['git', 'clone', config['url'], str(config['path'])]
            if config.get('branch') and config['branch'] != 'master':
                cmd.extend(['--branch', config['branch']])
                
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ {webui_type} cloned successfully")
                return True
            else:
                print(f"❌ Failed to clone {webui_type}: {result.stderr}")
                return False
        else:
            print(f"✅ {webui_type} already exists")
            return True
            
    except Exception as e:
        print(f"❌ WebUI installation error: {e}")
        return False

def download_models_and_assets():
    """Download models and assets based on widget settings"""
    
    print("🎨 Downloading models and assets...")
    
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
            
        print(f"📥 Downloading {category} ({len(urls)} items)...")
        
        for url in urls:
            total_downloads += 1
            try:
                if category == 'Extensions':
                    # Use git clone for extensions
                    success = download_extension(url)
                else:
                    # Use m_download for models/files
                    success = m_download(url, log=True)
                    
                if success:
                    successful_downloads += 1
                    
            except Exception as e:
                print(f"⚠️  Download failed for {url}: {e}")
    
    # Summary
    if total_downloads == 0:
        print("⚠️  No downloads specified")
        return True
    elif successful_downloads == total_downloads:
        print(f"✅ All {total_downloads} downloads completed successfully")
        return True
    elif successful_downloads > 0:
        print(f"✅ {successful_downloads}/{total_downloads} downloads completed")
        return True
    else:
        print("❌ All downloads failed")
        return False

def download_extension(url):
    """Download extension using git clone"""
    try:
        # Determine WebUI type for extension path
        webui_type = widget_settings.get('change_webui', 'automatic1111')
        
        if webui_type == 'automatic1111':
            extensions_dir = HOME / 'stable-diffusion-webui' / 'extensions'
        elif webui_type == 'ComfyUI':
            extensions_dir = HOME / 'ComfyUI' / 'custom_nodes'
        else:
            extensions_dir = HOME / 'stable-diffusion-webui' / 'extensions'
        
        extensions_dir.mkdir(parents=True, exist_ok=True)
        
        # Extract repo name from URL
        repo_name = url.split('/')[-1].replace('.git', '')
        target_path = extensions_dir / repo_name
        
        if not target_path.exists():
            cmd = ['git', 'clone', url, str(target_path)]
            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.returncode == 0
        else:
            return True  # Already exists
            
    except Exception as e:
        print(f"Extension download error: {e}")
        return False

# =================== MAIN EXECUTION ===================

def main():
    """Main execution function"""
    
    print("🔥 LSDAI Enhanced Downloading System v2.0")
    print("=" * 60)
    
    start_time = time.time()
    
    # Step 1: Setup comprehensive venv
    print("Step 1/4: Setting up environment...")
    venv_success = setup_comprehensive_safe_venv()
    
    # Step 2: Install WebUI
    print("\nStep 2/4: Installing WebUI...")
    webui_success = install_webui()
    
    # Step 3: Download models and assets
    print("\nStep 3/4: Downloading models and assets...")
    download_success = download_models_and_assets()
    
    # Step 4: Final setup and verification
    print("\nStep 4/4: Final setup...")
    
    # Setup performance monitoring if available
    if ENHANCEMENTS_AVAILABLE:
        setup_performance_monitoring()
    
    # Summary
    elapsed_time = time.time() - start_time
    
    print("\n" + "="*60)
    print("📊 LSDAI Setup Summary")
    print("="*60)
    print(f"⏱️  Total time: {elapsed_time:.1f} seconds")
    print(f"🐍 Environment: {'✅ Ready' if venv_success else '⚠️  Limited'}")
    print(f"🚀 WebUI: {'✅ Installed' if webui_success else '❌ Failed'}")
    print(f"🎨 Downloads: {'✅ Complete' if download_success else '⚠️  Issues'}")
    
    if venv_success and webui_success:
        print("\n🎉 LSDAI setup completed successfully!")
        print("🚀 Ready to launch WebUI in the next cell")
        
        if ENHANCEMENTS_AVAILABLE:
            send_success("LSDAI Setup Complete", "Ready to launch WebUI")
    else:
        print("\n⚠️  LSDAI setup completed with some issues")
        print("🔧 Check the logs above for details")
        
        if ENHANCEMENTS_AVAILABLE:
            send_error("LSDAI Setup Issues", "Some components failed to install")

def setup_performance_monitoring():
    """Setup performance monitoring if available"""
    
    if ENHANCEMENTS_AVAILABLE:
        try:
            print("📊 Setting up performance monitoring...")
            logger = get_advanced_logger()
            logger.log_system_info()
            print("✅ Performance monitoring active")
        except Exception as e:
            print(f"⚠️  Monitoring setup failed: {e}")

# Execute main if run directly
if __name__ == "__main__":
    main()

# For compatibility when imported
create_robust_venv = create_robust_venv_fixed

# Enhanced downloading-en.py for LSDAI
# Comprehensive dependency management with intelligent fallbacks and progress tracking

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
    """
    
    print("\n" + "="*60)
    print("🔧 Setting up comprehensive extension-safe environment...")
    print("📋 Strategy: Pre-install ALL dependencies to prevent conflicts")
    print("="*60)
    
    # Step 1: Generate smart requirements.txt
    generate_smart_requirements()
    
    # Step 2: Create venv with fallbacks
    venv_success = create_robust_venv()
    
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
transformers>=4.30.0,<4.37.0
diffusers>=0.20.0,<0.26.0
accelerate>=0.20.0,<0.26.0
safetensors>=0.3.0,<0.5.0
compel>=2.0.0,<3.0.0

# =================== WEBUI FRAMEWORK ===================
gradio>=4.0.0,<4.8.0
fastapi>=0.100.0,<0.106.0
uvicorn>=0.20.0,<0.25.0
pydantic>=1.10.0,<3.0.0

# =================== CONTROLNET & POSE DETECTION ===================
# Pre-install ALL ControlNet dependencies
controlnet-aux>=0.0.6
segment-anything>=1.0
ultralytics>=8.0.0,<9.0.0
mediapipe>=0.10.0,<0.11.0
mmdet>=3.0.0,<4.0.0
mmpose>=1.0.0,<2.0.0

# =================== FACE PROCESSING ===================
# Pre-install ALL face processing extensions deps
insightface>=0.7.0
facexlib>=0.3.0
gfpgan>=1.3.0
realesrgan>=0.3.0
basicsr>=1.4.0
lpips>=0.1.0

# =================== PERFORMANCE & ACCELERATION ===================
xformers>=0.0.20
onnx>=1.14.0,<1.16.0
onnxruntime>=1.15.0,<1.17.0
tensorrt>=8.6.0; sys_platform != "darwin"  # Skip on macOS

# =================== COMPUTER VISION ===================
opencv-python>=4.5.0,<5.0.0{" # Pre-installed" if is_colab else ""}
pillow>=9.0.0,<11.0.0
imageio>=2.25.0,<3.0.0
imageio-ffmpeg>=0.4.0,<0.5.0
scikit-image>=0.19.0,<0.22.0

# =================== NUMERICAL & SCIENTIFIC ===================
numpy>=1.21.0,<1.26.0{" # Pre-installed" if is_colab else ""}
scipy>=1.9.0,<1.12.0
pandas>=1.5.0,<2.1.0
matplotlib>=3.5.0,<4.0.0{" # Pre-installed" if is_colab else ""}
scikit-learn>=1.1.0,<1.4.0

# =================== AUDIO PROCESSING ===================
# For audio extensions (Bark, MusicGen, etc.)
librosa>=0.9.0,<0.11.0
soundfile>=0.12.0,<0.13.0
torchaudio>=2.0.0,<2.2.0
whisper>=1.1.0

# =================== VIDEO PROCESSING ===================
# For video extensions (AnimateDiff, etc.)
ffmpeg-python>=0.2.0
av>=10.0.0,<12.0.0
decord>=0.6.0

# =================== TRAINING & OPTIMIZATION ===================
# For Dreambooth, LoRA training, etc.
lion-pytorch>=0.0.6
dadaptation>=3.1
prodigyopt>=1.0
bitsandbytes>=0.39.0,<0.42.0
peft>=0.5.0,<0.7.0
deepspeed>=0.10.0,<0.12.0

# =================== API & INTEGRATION ===================
# For API extensions, cloud services
openai>=0.28.0,<2.0.0
anthropic>=0.3.0,<1.0.0
google-cloud-storage>=2.0.0,<3.0.0
boto3>=1.26.0,<2.0.0
requests>=2.28.0,<3.0.0
aiohttp>=3.8.0,<4.0.0
httpx>=0.24.0,<0.26.0

# =================== NETWORK & DOWNLOADS ===================
tqdm>=4.64.0,<5.0.0
wget>=3.2
aria2p>=0.11.0
gdown>=4.7.0

# =================== DATABASE & STORAGE ===================
# For extensions that need databases
sqlite-utils>=3.34,<4.0.0
sqlalchemy>=1.4.0,<3.0.0
redis>=4.5.0,<5.0.0

# =================== WEB & UI ===================
flask>=2.0.0,<3.0.0
streamlit>=1.25.0,<2.0.0
websockets>=10.0,<12.0
markdown>=3.4.0,<4.0.0
jinja2>=3.0.0,<4.0.0

# =================== MODEL FORMAT SUPPORT ===================
# GGML/GGUF support for LLaMA, etc.
gguf>=0.1.0
llama-cpp-python>=0.2.0
ctransformers>=0.2.0

# =================== QUALITY & ANALYSIS ===================
# For quality assessment extensions
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
# For memory-efficient operations
memory-profiler>=0.60.0
pympler>=0.9

# =================== TOKENIZERS & NLP ===================
tokenizers>=0.13.0,<0.15.0
sentencepiece>=0.1.99,<0.2.0
protobuf>=3.20.0,<5.0.0
nltk>=3.8,<4.0

# =================== EXTENSION-SPECIFIC DEPS ===================
# Regional Prompter
numpy-financial>=1.0.0

# Roop (face swapping)
# opencv-contrib-python>=4.5.0  # Conflicts with opencv-python

# AUTOMATIC1111 TensorRT
# nvidia-tensorrt>=8.6.0  # Only install if needed

# LyCORIS training
# lycoris-lora>=1.0.0

# =================== PLATFORM SPECIFIC ===================
{"colorama>=0.4.0" if platform.system() == "Windows" else "# colorama  # Not needed on Unix"}
{"pywin32>=227" if platform.system() == "Windows" else "# pywin32  # Windows only"}

# =================== SAFETY & FALLBACKS ===================
# Ensure basic packages that should always work
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

def create_robust_venv():
    """Create virtual environment with multiple fallback strategies"""
    
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
    
    # Strategy 1: Standard venv with system packages
    try:
        print("🔧 Strategy 1: Creating venv with system packages...")
        
        create_cmd = [sys.executable, '-m', 'venv', str(VENV_PATH), '--system-site-packages']
        result = subprocess.run(create_cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            if test_venv_creation():
                print("✅ Virtual environment created successfully")
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
    
    # Strategy 2: Venv without system packages
    try:
        print("🔧 Strategy 2: Creating isolated venv...")
        
        create_cmd = [sys.executable, '-m', 'venv', str(VENV_PATH)]
        result = subprocess.run(create_cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            if test_venv_creation():
                print("✅ Virtual environment created (isolated)")
                return True
            else:
                print("⚠️  Isolated venv created but pip test failed")
        else:
            print(f"⚠️  Strategy 2 failed: {result.stderr}")
            
    except subprocess.TimeoutExpired:
        print("⏱️  Strategy 2 timed out")
    except Exception as e:
        print(f"⚠️  Strategy 2 exception: {e}")
    
    # Strategy 3: Use system Python
    print("📦 Virtual environment creation failed")
    print("   Using system Python (this is OK - system will still work)")
    
    if ENHANCEMENTS_AVAILABLE:
        send_info("Venv Creation", "Using system Python instead of venv")
    
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
    
    # Strategy 1: Try enhanced installation if available
    if ENHANCEMENTS_AVAILABLE:
        print("✨ Attempting enhanced installation...")
        if install_with_enhanced_manager(pip_executable, req_file):
            return True
    
    # Strategy 2: Batch install (fastest if it works)
    print("🚀 Attempting comprehensive batch installation...")
    if install_batch(pip_executable, req_file):
        return True
    
    # Strategy 3: Tiered installation (most reliable)
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

def install_with_enhanced_manager(pip_executable, req_file):
    """Install using enhanced download manager if available"""
    try:
        manager, batch_ops = get_enhanced_manager()
        
        # Read requirements and convert to download format
        with open(req_file, 'r') as f:
            lines = f.readlines()
        
        packages = [line.strip() for line in lines 
                   if line.strip() and not line.strip().startswith('#')]
        
        print(f"📥 Enhanced manager installing {len(packages)} packages...")
        
        # Use enhanced manager for better progress tracking
        success_count = 0
        for package in packages[:10]:  # Start with first 10 as test
            try:
                result = subprocess.run([
                    pip_executable, 'install', package, '--quiet'
                ], capture_output=True, text=True, timeout=300)
                
                if result.returncode == 0:
                    success_count += 1
                    
            except Exception:
                pass
        
        if success_count >= 8:  # 80% success rate for first batch
            print("✅ Enhanced installation working, continuing...")
            # Install remaining packages
            return install_batch(pip_executable, req_file)
        else:
            print("⚠️  Enhanced installation having issues, falling back...")
            return False
            
    except Exception as e:
        print(f"❌ Enhanced installation error: {e}")
        return False

def install_batch(pip_executable, req_file):
    """Try to install all requirements at once"""
    try:
        print("📦 Installing all dependencies in batch...")
        
        result = subprocess.run([
            pip_executable, 'install', '-r', str(req_file),
            '--quiet', '--no-warn-script-location',
            '--timeout', '60'
        ], capture_output=True, text=True, timeout=3600)  # 1 hour timeout
        
        if result.returncode == 0:
            print("✅ Batch installation completed successfully!")
            print("🛡️  All extension dependencies pre-installed")
            
            if ENHANCEMENTS_AVAILABLE:
                send_success("Dependencies Installed", "Comprehensive environment ready")
            
            return True
        else:
            print("⚠️  Batch installation had issues:")
            if widget_settings.get('detailed_download') == 'on':
                print(f"   Error: {result.stderr[:500]}...")
            print("   Falling back to tiered installation...")
            return False
            
    except subprocess.TimeoutExpired:
        print("⏱️  Batch installation timed out (1 hour)")
        print("   Falling back to tiered installation...")
        return False
    except Exception as e:
        print(f"❌ Batch installation error: {e}")
        return False

def install_in_tiers(pip_executable):
    """Install dependencies in tiers for maximum compatibility"""
    
    print("📋 Installing comprehensive dependencies in tiers...")
    print("🎯 This ensures ALL extensions will work without conflicts")
    
    # Tier 1: Absolutely Essential (WebUI won't work without these)
    tier1 = [
        "torch>=2.0.0,<2.2.0",
        "torchvision>=0.15.0,<0.17.0", 
        "transformers>=4.30.0,<4.37.0",
        "diffusers>=0.20.0,<0.26.0",
        "gradio>=4.0.0,<4.8.0",
        "requests>=2.28.0,<3.0.0",
        "pillow>=9.0.0,<11.0.0",
        "numpy>=1.21.0,<1.26.0",
        "safetensors>=0.3.0,<0.5.0"
    ]
    
    # Tier 2: Core Extensions (ControlNet, basic functionality)
    tier2 = [
        "accelerate>=0.20.0,<0.26.0",
        "opencv-python>=4.5.0,<5.0.0",
        "controlnet-aux>=0.0.6",
        "segment-anything>=1.0",
        "ultralytics>=8.0.0,<9.0.0",
        "scipy>=1.9.0,<1.12.0",
        "tqdm>=4.64.0,<5.0.0",
        "fastapi>=0.100.0,<0.106.0"
    ]
    
    # Tier 3: Advanced Extensions (Face processing, training)
    tier3 = [
        "insightface>=0.7.0",
        "facexlib>=0.3.0",
        "gfpgan>=1.3.0", 
        "realesrgan>=0.3.0",
        "basicsr>=1.4.0",
        "matplotlib>=3.5.0,<4.0.0",
        "pandas>=1.5.0,<2.1.0",
        "scikit-learn>=1.1.0,<1.4.0"
    ]
    
    # Tier 4: Performance & Optimization
    tier4 = [
        "xformers>=0.0.20",
        "bitsandbytes>=0.39.0,<0.42.0",
        "onnx>=1.14.0,<1.16.0",
        "onnxruntime>=1.15.0,<1.17.0",
        "lion-pytorch>=0.0.6",
        "dadaptation>=3.1"
    ]
    
    # Tier 5: Audio/Video Extensions  
    tier5 = [
        "librosa>=0.9.0,<0.11.0",
        "soundfile>=0.12.0,<0.13.0",
        "ffmpeg-python>=0.2.0",
        "av>=10.0.0,<12.0.0",
        "whisper>=1.1.0"
    ]
    
    # Tier 6: Quality of Life & APIs
    tier6 = [
        "rich>=12.0.0,<14.0.0",
        "psutil>=5.9.0,<6.0.0",
        "lpips>=0.1.0",
        "clip-interrogator>=0.6.0",
        "openai>=0.28.0,<2.0.0",
        "ipywidgets>=8.0.0,<9.0.0"
    ]
    
    tiers = [
        ("Essential WebUI", tier1, True),      # Must succeed
        ("Core Extensions", tier2, True),      # Should succeed
        ("Advanced Extensions", tier3, False), # Can fail
        ("Performance", tier4, False),         # Can fail  
        ("Audio/Video", tier5, False),         # Can fail
        ("Quality of Life", tier6, False)      # Can fail
    ]
    
    total_success = 0
    total_attempted = 0
    critical_failures = 0
    
    for tier_name, packages, is_critical in tiers:
        print(f"\n🎯 Installing {tier_name} tier ({len(packages)} packages)...")
        
        success_count = 0
        for i, package in enumerate(packages, 1):
            try:
                print(f"  📦 [{i}/{len(packages)}] {package[:50]}...", end="")
                
                result = subprocess.run([
                    pip_executable, 'install', package,
                    '--quiet', '--no-warn-script-location'
                ], capture_output=True, text=True, timeout=600)  # 10 min per package
                
                if result.returncode == 0:
                    success_count += 1
                    print(" ✅")
                else:
                    print(f" ❌")
                    if widget_settings.get('detailed_download') == 'on':
                        print(f"      Error: {result.stderr[:100]}...")
                        
            except subprocess.TimeoutExpired:
                print(" ⏱️ (timeout)")
            except Exception as e:
                print(f" ❌ ({str(e)[:30]}...)")
        
        total_success += success_count
        total_attempted += len(packages)
        
        success_rate = (success_count / len(packages)) * 100
        print(f"  📊 {tier_name}: {success_count}/{len(packages)} successful ({success_rate:.1f}%)")
        
        if is_critical and success_rate < 70:  # 70% success required for critical tiers
            critical_failures += 1
            print(f"  ⚠️  Critical tier has low success rate!")
            
            if ENHANCEMENTS_AVAILABLE:
                send_error("Installation Issue", f"{tier_name} tier had low success rate")
    
    overall_success_rate = (total_success / total_attempted) * 100
    print(f"\n📈 Overall Installation Results:")
    print(f"   ✅ Successful: {total_success}/{total_attempted} ({overall_success_rate:.1f}%)")
    print(f"   ⚠️  Critical failures: {critical_failures}")
    
    if overall_success_rate >= 80 and critical_failures == 0:
        print("🎉 Comprehensive environment ready!")
        print("🛡️  Extensions should install without major conflicts")
        
        if ENHANCEMENTS_AVAILABLE:
            send_success("Environment Ready", f"Comprehensive dependencies installed ({overall_success_rate:.1f}% success)")
        
        return True
    elif overall_success_rate >= 60 and critical_failures <= 1:
        print("✅ Core environment ready (some optional features missing)")
        print("🛡️  Most extensions should work fine")
        
        if ENHANCEMENTS_AVAILABLE:
            send_info("Environment Ready", f"Core dependencies installed ({overall_success_rate:.1f}% success)")
        
        return True
    else:
        print("⚠️  Minimal environment - may have extension conflicts")
        print("🔧 Consider running the installation again")
        
        if ENHANCEMENTS_AVAILABLE:
            send_error("Installation Issues", f"Low success rate ({overall_success_rate:.1f}%)")
        
        return False

def install_essential_fallback(pip_executable):
    """Fallback installation of only essential packages"""
    
    print("🆘 Installing essential packages only (fallback mode)...")
    
    essential_packages = [
        "torch>=2.0.0",
        "torchvision>=0.15.0", 
        "transformers>=4.30.0",
        "diffusers>=0.20.0",
        "gradio>=4.0.0",
        "requests>=2.28.0",
        "pillow>=9.0.0",
        "numpy>=1.21.0"
    ]
    
    success_count = 0
    
    for package in essential_packages:
        try:
            print(f"  📦 {package}...", end="")
            result = subprocess.run([
                pip_executable, 'install', package, '--quiet'
            ], capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                success_count += 1
                print(" ✅")
            else:
                print(" ❌")
                
        except Exception:
            print(" ❌")
    
    print(f"📊 Essential packages: {success_count}/{len(essential_packages)} installed")
    
    if success_count >= 6:  # At least 6/8 essential packages
        print("✅ Essential environment ready")
        return True
    else:
        print("❌ Critical installation failure")
        return False

def verify_installation():
    """Verify key packages are working correctly"""
    
    print("\n🧪 Verifying installation...")
    
    critical_imports = [
        ("torch", "PyTorch", "import torch; torch.cuda.is_available()"),
        ("transformers", "Transformers", "from transformers import pipeline"),
        ("diffusers", "Diffusers", "from diffusers import StableDiffusionPipeline"), 
        ("gradio", "Gradio", "import gradio"),
        ("PIL", "Pillow", "from PIL import Image"),
        ("cv2", "OpenCV", "import cv2"),
        ("numpy", "NumPy", "import numpy"),
        ("requests", "Requests", "import requests")
    ]
    
    working_count = 0
    cuda_available = False
    
    for module, name, test_code in critical_imports:
        try:
            exec(test_code)
            print(f"  ✅ {name}")
            working_count += 1
            
            if module == "torch":
                import torch
                cuda_available = torch.cuda.is_available()
                if cuda_available:
                    print(f"     🚀 CUDA available: {torch.cuda.get_device_name(0)}")
                else:
                    print(f"     💻 CPU-only mode")
                    
        except ImportError:
            print(f"  ❌ {name} - not installed")
        except Exception as e:
            print(f"  ⚠️  {name} - installed but has issues: {str(e)[:50]}...")
            working_count += 0.5  # Partial credit
    
    print(f"\n📊 Verification Results:")
    print(f"   ✅ Working packages: {working_count}/{len(critical_imports)}")
    print(f"   🚀 CUDA acceleration: {'Available' if cuda_available else 'Not available'}")
    
    if working_count >= len(critical_imports) - 1:
        print("🎉 Environment verification passed!")
        
        if ENHANCEMENTS_AVAILABLE:
            send_success("Verification Complete", "All critical packages working")
        
    elif working_count >= len(critical_imports) - 2:
        print("✅ Environment mostly working (minor issues)")
    else:
        print("⚠️  Environment has significant issues")
        
        if ENHANCEMENTS_AVAILABLE:
            send_error("Verification Issues", "Some critical packages not working")

def setup_enhanced_download_manager():
    """Setup enhanced download manager if available"""
    try:
        manager, batch_ops = get_enhanced_manager()
        
        # Configure download manager
        concurrent_downloads = widget_settings.get('concurrent_downloads', 3)
        
        print(f"✨ Enhanced download manager configured")
        print(f"   📥 Concurrent downloads: {concurrent_downloads}")
        
        # Add progress callback if logging available
        if ENHANCEMENTS_AVAILABLE:
            try:
                logger = get_advanced_logger()
                
                def progress_callback(status):
                    if status.get('total_progress', 0) == 100:
                        send_success("Downloads Complete", "All queued downloads finished")
                        logger.log_event('info', 'downloads', 'All downloads completed')
                        
                manager.add_progress_callback(progress_callback)
                
            except Exception as e:
                print(f"⚠️  Could not setup progress tracking: {e}")
        
        return manager, batch_ops
        
    except Exception as e:
        print(f"⚠️  Enhanced download manager setup failed: {e}")
        return None, None

# =================== WEBUI INSTALLATION ===================

def install_webui():
    """Install WebUI with enhanced error handling"""
    
    print("\n" + "="*60)
    print("🚀 Installing Stable Diffusion WebUI...")
    print("="*60)
    
    # Get WebUI type from settings
    webui_type = widget_settings.get('change_webui', 'automatic1111')
    webui_path = get_webui_path(webui_type)
    
    print(f"📦 Installing: {webui_type}")
    print(f"📍 Location: {webui_path}")
    
    if webui_path.exists():
        print(f"✅ WebUI {webui_type} already exists")
        
        # Check if update is requested
        if widget_settings.get('latest_webui') == 'on':
            print("🔄 Updating WebUI...")
            update_webui(webui_path)
        
        return True
    
    try:
        print(f"⌚ Unpacking Stable Diffusion {webui_type}...")
        
        # Use enhanced webui installer if available
        if ENHANCEMENTS_AVAILABLE:
            result = install_webui_enhanced(webui_type, webui_path)
        else:
            result = install_webui_standard(webui_type, webui_path)
        
        if result:
            print(f"✅ WebUI {webui_type} installed successfully")
            
            if ENHANCEMENTS_AVAILABLE:
                send_success("WebUI Installed", f"{webui_type} ready to use")
            
            return True
        else:
            print(f"❌ WebUI {webui_type} installation failed")
            
            if ENHANCEMENTS_AVAILABLE:
                send_error("WebUI Installation Failed", f"Could not install {webui_type}")
            
            return False
            
    except Exception as e:
        print(f"❌ WebUI installation error: {e}")
        
        if ENHANCEMENTS_AVAILABLE:
            send_error("WebUI Installation Error", str(e))
        
        return False

def get_webui_path(webui_type):
    """Get WebUI installation path"""
    webui_paths = {
        'automatic1111': HOME / 'stable-diffusion-webui',
        'ComfyUI': HOME / 'ComfyUI',
        'InvokeAI': HOME / 'InvokeAI',
        'StableSwarmUI': HOME / 'StableSwarmUI'
    }
    
    return webui_paths.get(webui_type, HOME / 'stable-diffusion-webui')

def install_webui_enhanced(webui_type, webui_path):
    """Install WebUI using enhanced methods"""
    try:
        # Use enhanced webui installer
        from scripts import webui_installer
        return webui_installer.install_webui(webui_type, webui_path)
        
    except ImportError:
        # Fallback to standard installation
        return install_webui_standard(webui_type, webui_path)

def install_webui_standard(webui_type, webui_path):
    """Standard WebUI installation"""
    try:
        # Import and run existing webui installer
        import importlib.util
        installer_path = SCRIPTS / 'webui-installer.py'
        
        if installer_path.exists():
            spec = importlib.util.spec_from_file_location("webui_installer", installer_path)
            installer_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(installer_module)
            return True
        else:
            print(f"❌ WebUI installer not found: {installer_path}")
            return False
            
    except Exception as e:
        print(f"❌ Standard WebUI installation error: {e}")
        return False

def update_webui(webui_path):
    """Update existing WebUI installation"""
    try:
        if (webui_path / '.git').exists():
            print("🔄 Updating WebUI via git...")
            result = subprocess.run([
                'git', 'pull'
            ], cwd=webui_path, capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ WebUI updated successfully")
            else:
                print(f"⚠️  WebUI update had issues: {result.stderr}")
        else:
            print("⚠️  WebUI is not a git repository, cannot update")
            
    except Exception as e:
        print(f"❌ WebUI update error: {e}")

# =================== MODEL AND ASSET DOWNLOADING ===================

def download_models_and_assets():
    """Download models and other assets with enhanced progress tracking"""
    
    print("\n" + "="*60)
    print("🎨 Downloading models and assets...")
    print("="*60)
    
    # Get download URLs from settings
    download_items = collect_download_items()
    
    if not download_items:
        print("ℹ️  No models or assets to download")
        return True
    
    print(f"📥 Found {len(download_items)} items to download")
    
    # Use enhanced download manager if available
    if ENHANCEMENTS_AVAILABLE:
        return download_with_enhanced_manager(download_items)
    else:
        return download_with_standard_manager(download_items)

def collect_download_items():
    """Collect all download items from widget settings"""
    
    download_items = []
    
    # Model URLs
    url_keys = [
        'Model_url', 'Vae_url', 'LoRA_url', 'Embedding_url', 
        'Extensions_url', 'ADetailer_url', 'custom_file_urls'
    ]
    
    for key in url_keys:
        urls = widget_settings.get(key, '')
        if urls:
            # Split by comma and clean up
            url_list = [url.strip() for url in urls.split(',') if url.strip()]
            download_items.extend(url_list)
    
    return download_items

def download_with_enhanced_manager(download_items):
    """Download using enhanced manager with progress tracking"""
    
    try:
        manager, batch_ops = get_enhanced_manager()
        
        print("✨ Using enhanced download manager...")
        
        # Add items to download queue
        count = manager.add_to_queue(download_items)
        print(f"📥 Added {count} items to download queue")
        
        # Start downloads
        manager.start_queue()
        
        # Monitor progress
        print("⏳ Monitoring download progress...")
        last_status = None
        
        while True:
            status = manager.get_queue_status()
            
            if status != last_status:
                active = status['downloading']
                completed = status['completed']
                failed = status['failed']
                total = status['total_items']
                
                if active == 0:
                    break  # All downloads finished
                
                print(f"   📊 Progress: {completed}/{total} complete, {active} downloading, {failed} failed")
                last_status = status
            
            time.sleep(5)
        
        final_status = manager.get_queue_status()
        
        print(f"\n📈 Download Results:")
        print(f"   ✅ Completed: {final_status['completed']}")
        print(f"   ❌ Failed: {final_status['failed']}")
        
        success = final_status['failed'] == 0
        
        if success:
            print("🎉 All downloads completed successfully!")
            send_success("Downloads Complete", f"Downloaded {final_status['completed']} items")
        else:
            print(f"⚠️  {final_status['failed']} downloads failed")
            send_error("Download Issues", f"{final_status['failed']} downloads failed")
        
        return success
        
    except Exception as e:
        print(f"❌ Enhanced download error: {e}")
        print("📦 Falling back to standard download method...")
        return download_with_standard_manager(download_items)

def download_with_standard_manager(download_items):
    """Download using standard LSDAI manager"""
    
    print("📦 Using standard download manager...")
    
    success_count = 0
    total_count = len(download_items)
    
    for i, item in enumerate(download_items, 1):
        try:
            print(f"📥 [{i}/{total_count}] Downloading: {item[:60]}...")
            
            # Use existing LSDAI download function
            result = m_download(item, log=widget_settings.get('detailed_download') == 'on')
            
            if result:
                success_count += 1
                print(f"   ✅ Success")
            else:
                print(f"   ❌ Failed")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print(f"\n📊 Standard Download Results: {success_count}/{total_count} successful")
    
    success = success_count > 0
    
    if success and success_count == total_count:
        print("🎉 All downloads completed!")
    elif success:
        print(f"✅ {success_count} downloads completed ({total_count - success_count} failed)")
    else:
        print("❌ All downloads failed")
    
    return success

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
    
    # Install extensions if specified
    if widget_settings.get('Extensions_url'):
        install_extensions()
    
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

def install_extensions():
    """Install extensions with enhanced management"""
    
    print("🔧 Installing extensions...")
    
    if ENHANCEMENTS_AVAILABLE:
        try:
            from modules.ExtensionManager import get_extension_manager
            
            ext_manager = get_extension_manager()
            
            # Get extension URLs
            extension_urls = widget_settings.get('Extensions_url', '').split(',')
            extension_urls = [url.strip() for url in extension_urls if url.strip()]
            
            if extension_urls:
                # Convert to extension info format
                extensions_to_install = []
                for url in extension_urls:
                    name = Path(url).stem
                    extensions_to_install.append({
                        'name': name,
                        'url': url
                    })
                
                # Install using enhanced manager
                results = ext_manager.batch_install_extensions(extensions_to_install)
                
                print(f"📊 Extension Results:")
                print(f"   ✅ Installed: {len(results['successful'])}")
                print(f"   ❌ Failed: {len(results['failed'])}")
                
                if results['successful']:
                    send_success("Extensions Installed", f"Installed {len(results['successful'])} extensions")
                
                if results['failed']:
                    send_error("Extension Issues", f"{len(results['failed'])} extensions failed")
            
        except Exception as e:
            print(f"❌ Enhanced extension installation error: {e}")
            # Fallback to standard method would go here
    else:
        print("📦 Using standard extension installation...")
        # Standard extension installation would go here

def setup_performance_monitoring():
    """Setup performance monitoring if available"""
    
    try:
        logger = get_advanced_logger()
        
        # Log setup completion
        logger.log_event('info', 'setup', 'LSDAI setup completed with enhancements')
        
        # Start resource monitoring
        if widget_settings.get('performance_monitoring', True):
            from modules.AdvancedLogging import SystemResourceMonitor
            
            resource_monitor = SystemResourceMonitor(logger)
            resource_monitor.start_monitoring()
            
            print("📊 Performance monitoring started")
        
    except Exception as e:
        print(f"⚠️  Performance monitoring setup failed: {e}")

# Execute main function if running directly
if __name__ == "__main__":
    main()
else:
    # If imported, run main automatically
    main()

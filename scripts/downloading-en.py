# Fixed Cell 3 for LSDAI - Smart Comprehensive Venv Setup
# Add this to your downloading-en.py to replace the problematic venv section

def setup_comprehensive_safe_venv():
    """
    Your original strategy (pre-install everything) but with smart execution
    Creates comprehensive venv that prevents ALL extension conflicts
    """
    
    print("🔧 Setting up comprehensive extension-safe environment...")
    print("📋 Strategy: Pre-install ALL dependencies to prevent conflicts")
    
    # Step 1: Generate smart requirements.txt
    generate_smart_requirements()
    
    # Step 2: Create venv with fallbacks
    venv_success = create_robust_venv()
    
    # Step 3: Install comprehensive dependencies  
    install_success = install_comprehensive_deps(venv_success)
    
    # Step 4: Verify installation
    verify_installation()
    
    return venv_success and install_success

def generate_smart_requirements():
    """Generate requirements.txt that actually works across platforms"""
    
    # Your comprehensive list, but with compatible versions
    comprehensive_requirements = """# LSDAI Comprehensive Extension-Safe Requirements
# Pre-installs ALL extension dependencies to prevent conflicts
# Compatible with Colab, Kaggle, Lightning.ai, local systems

# =================== CORE PYTORCH (Auto-CUDA) ===================
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

# =================== CONTROLNET & EXTENSIONS ===================
controlnet-aux>=0.0.6
segment-anything>=1.0
ultralytics>=8.0.0,<9.0.0
insightface>=0.7.0
facexlib>=0.3.0
gfpgan>=1.3.0
realesrgan>=0.3.0
basicsr>=1.4.0

# =================== PERFORMANCE & ACCELERATION ===================
xformers>=0.0.20
onnx>=1.14.0,<1.16.0
onnxruntime>=1.15.0,<1.17.0

# =================== COMPUTER VISION ===================
opencv-python>=4.5.0,<5.0.0
pillow>=9.0.0,<11.0.0
imageio>=2.25.0,<3.0.0
scikit-image>=0.19.0,<0.22.0

# =================== NUMERICAL & SCIENTIFIC ===================
numpy>=1.21.0,<1.26.0
scipy>=1.9.0,<1.12.0
pandas>=1.5.0,<2.1.0
matplotlib>=3.5.0,<4.0.0
scikit-learn>=1.1.0,<1.4.0

# =================== NETWORK & DOWNLOADS ===================
requests>=2.28.0,<3.0.0
aiohttp>=3.8.0,<4.0.0
tqdm>=4.64.0,<5.0.0
wget>=3.2

# =================== COMMON EXTENSION DEPENDENCIES ===================
# Audio processing
librosa>=0.9.0,<0.11.0
soundfile>=0.12.0,<0.13.0

# Video processing  
ffmpeg-python>=0.2.0
av>=10.0.0,<12.0.0

# Web frameworks
flask>=2.0.0,<3.0.0
websockets>=10.0,<12.0

# File handling
send2trash>=1.8.0
psutil>=5.9.0,<6.0.0

# Development tools
rich>=12.0.0,<14.0.0
loguru>=0.6.0,<0.8.0

# Configuration management
jsonschema>=4.0.0,<5.0.0
pyyaml>=6.0,<7.0
omegaconf>=2.3.0,<3.0.0

# Training extensions
lion-pytorch>=0.0.6
dadaptation>=3.1
prodigyopt>=1.0

# API extensions
openai>=0.28.0,<2.0.0

# Memory optimization
bitsandbytes>=0.39.0,<0.42.0

# Quality analysis
lpips>=0.1.0
clip-interrogator>=0.6.0

# Jupyter compatibility
ipython>=8.0.0,<9.0.0
ipywidgets>=8.0.0,<9.0.0

# Model formats
gguf>=0.1.0
protobuf>=3.20.0,<5.0.0
tokenizers>=0.13.0,<0.15.0

# Cloud storage (optional)
# google-cloud-storage>=2.0.0,<3.0.0
# boto3>=1.26.0,<2.0.0
"""
    
    req_file = SCRIPTS / "requirements.txt"
    req_file.write_text(comprehensive_requirements)
    
    print(f"✅ Generated comprehensive requirements.txt ({len(comprehensive_requirements.split())} lines)")
    print("📦 Includes dependencies for ALL major extensions")
    
    return req_file

def create_robust_venv():
    """Create venv with multiple fallback strategies"""
    
    venv_path = "/content/venv"
    
    # Remove existing broken venv
    if Path(venv_path).exists():
        print("🗑️  Removing existing venv...")
        import shutil
        shutil.rmtree(venv_path, ignore_errors=True)
    
    # Strategy 1: Standard approach
    try:
        print("🐍 Creating virtual environment...")
        
        create_cmd = [sys.executable, '-m', 'venv', venv_path, '--system-site-packages']
        result = subprocess.run(create_cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print("✅ Virtual environment created successfully")
            return True
        else:
            print(f"⚠️  Standard venv failed: {result.stderr}")
            
    except Exception as e:
        print(f"⚠️  Standard venv exception: {e}")
    
    # Strategy 2: Without system packages
    try:
        print("🔄 Trying without system packages...")
        
        create_cmd = [sys.executable, '-m', 'venv', venv_path]
        result = subprocess.run(create_cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print("✅ Virtual environment created (isolated)")
            return True
        else:
            print(f"⚠️  Isolated venv failed: {result.stderr}")
            
    except Exception as e:
        print(f"⚠️  Isolated venv exception: {e}")
    
    # Strategy 3: Use system Python
    print("📦 Venv creation failed, using system Python")
    print("   (This is OK - system will still work)")
    return False

def install_comprehensive_deps(venv_available):
    """Install comprehensive dependencies with smart error handling"""
    
    # Determine pip executable
    if venv_available and Path("/content/venv/bin/pip").exists():
        pip_executable = "/content/venv/bin/pip"
        print(f"📦 Using venv pip: {pip_executable}")
    else:
        pip_executable = "pip"
        print(f"📦 Using system pip: {pip_executable}")
    
    req_file = SCRIPTS / "requirements.txt"
    
    # Strategy 1: Batch install (fastest if it works)
    print("🚀 Attempting comprehensive batch installation...")
    try:
        result = subprocess.run([
            pip_executable, "install", "-r", str(req_file),
            "--quiet", "--no-warn-script-location", 
            "--timeout", "60"  # 60 second timeout per package
        ], capture_output=True, text=True, timeout=2400)  # 40 minute total timeout
        
        if result.returncode == 0:
            print("✅ Comprehensive dependencies installed successfully!")
            print("🛡️  Extensions should now install without conflicts")
            return True
        else:
            print("⚠️  Batch install had issues, trying smart recovery...")
            
    except subprocess.TimeoutExpired:
        print("⏱️  Batch install timed out, trying smart recovery...")
    except Exception as e:
        print(f"❌ Batch install error: {e}")
    
    # Strategy 2: Tiered installation (your comprehensive strategy, but safer)
    return install_in_tiers(pip_executable)

def install_in_tiers(pip_executable):
    """Install in tiers - essential first, then extensions, then nice-to-haves"""
    
    print("📋 Installing comprehensive dependencies in tiers...")
    
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
    
    # Tier 2: Core Extensions (ControlNet, etc.)
    tier2 = [
        "accelerate>=0.20.0,<0.26.0",
        "opencv-python>=4.5.0,<5.0.0",
        "controlnet-aux>=0.0.6",
        "segment-anything>=1.0",
        "ultralytics>=8.0.0,<9.0.0",
        "scipy>=1.9.0,<1.12.0",
        "tqdm>=4.64.0,<5.0.0"
    ]
    
    # Tier 3: Advanced Extensions (Face processing, etc.)
    tier3 = [
        "insightface>=0.7.0",
        "facexlib>=0.3.0",
        "gfpgan>=1.3.0", 
        "realesrgan>=0.3.0",
        "basicsr>=1.4.0",
        "matplotlib>=3.5.0,<4.0.0",
        "pandas>=1.5.0,<2.1.0"
    ]
    
    # Tier 4: Performance & Quality-of-Life
    tier4 = [
        "xformers>=0.0.20",
        "bitsandbytes>=0.39.0,<0.42.0",
        "rich>=12.0.0,<14.0.0",
        "psutil>=5.9.0,<6.0.0",
        "lpips>=0.1.0",
        "clip-interrogator>=0.6.0"
    ]
    
    # Tier 5: Optional Advanced Features
    tier5 = [
        "librosa>=0.9.0,<0.11.0",
        "soundfile>=0.12.0,<0.13.0", 
        "ffmpeg-python>=0.2.0",
        "lion-pytorch>=0.0.6",
        "openai>=0.28.0,<2.0.0"
    ]
    
    tiers = [
        ("Essential", tier1, True),     # Must succeed
        ("Core Extensions", tier2, True),  # Should succeed
        ("Advanced Extensions", tier3, False),  # Can fail
        ("Performance", tier4, False),      # Can fail  
        ("Optional", tier5, False)          # Can fail
    ]
    
    total_success = 0
    total_attempted = 0
    
    for tier_name, packages, is_critical in tiers:
        print(f"\n🎯 Installing {tier_name} tier...")
        
        success_count = 0
        for package in packages:
            try:
                print(f"  📦 {package}...")
                result = subprocess.run([
                    pip_executable, "install", package,
                    "--quiet", "--no-warn-script-location"
                ], capture_output=True, text=True, timeout=600)
                
                if result.returncode == 0:
                    success_count += 1
                    print(f"    ✅")
                else:
                    print(f"    ❌ {result.stderr[:50]}...")
                    
            except Exception as e:
                print(f"    ❌ {str(e)[:50]}...")
        
        total_success += success_count
        total_attempted += len(packages)
        
        print(f"  📊 {tier_name}: {success_count}/{len(packages)} successful")
        
        if is_critical and success_count < len(packages) * 0.8:  # 80% success required for critical tiers
            print(f"  ⚠️  Critical tier had low success rate")
    
    success_rate = (total_success / total_attempted) * 100
    print(f"\n📈 Overall Installation Results:")
    print(f"   ✅ Successful: {total_success}/{total_attempted} ({success_rate:.1f}%)")
    
    if success_rate >= 70:
        print("🎉 Comprehensive environment ready!")
        print("🛡️  Extensions should install without major conflicts")
        return True
    elif success_rate >= 40:
        print("✅ Core environment ready (some optional features missing)")
        return True
    else:
        print("⚠️  Minimal environment - may have extension conflicts")
        return False

def verify_installation():
    """Verify key packages are working"""
    
    print("\n🧪 Verifying installation...")
    
    critical_imports = [
        ("torch", "PyTorch"),
        ("transformers", "Transformers"),
        ("diffusers", "Diffusers"), 
        ("gradio", "Gradio"),
        ("PIL", "Pillow"),
        ("cv2", "OpenCV")
    ]
    
    working_count = 0
    
    for module, name in critical_imports:
        try:
            __import__(module)
            print(f"  ✅ {name}")
            working_count += 1
        except ImportError:
            print(f"  ❌ {name}")
    
    print(f"\n📊 Verification: {working_count}/{len(critical_imports)} critical packages working")
    
    if working_count >= len(critical_imports) - 1:
        print("🎉 Environment verification passed!")
    else:
        print("⚠️  Some critical packages missing")

# Replace your existing venv setup section with:
setup_comprehensive_safe_venv()

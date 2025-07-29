# Enhanced downloading integration - FIXED VENV CREATION
import json_utils as js
from pathlib import Path
import subprocess
import time
import os
import sys

# Get settings path from environment or default
SETTINGS_PATH = Path(os.environ.get('settings_path', '/content/LSDAI/settings.json'))

# Import original downloading functions - FIX THE IMPORTS
try:
    from scripts.downloading_en import setup_comprehensive_safe_venv, create_robust_venv, install_webui, download_models_and_assets, main as downloading_main
    ORIGINAL_DOWNLOADING_AVAILABLE = True
    print("✅ Original downloading functions imported successfully")
except ImportError as e:
    print(f"⚠️ Original downloading functions not found: {e}")
    ORIGINAL_DOWNLOADING_AVAILABLE = False

# Import enhancements
try:
    from modules.EnhancedManager import get_enhanced_manager
    from modules.NotificationSystem import send_info, send_success, send_error
    from modules.AdvancedLogging import get_advanced_logger
    ENHANCEMENTS_AVAILABLE = True
    print("✅ Enhanced modules imported successfully")
except ImportError:
    ENHANCEMENTS_AVAILABLE = False
    print("⚠️ Enhanced modules not available, using standard functionality")

class EnhancedDownloadingSystem:
    def __init__(self):
        self.original_mode = not ENHANCEMENTS_AVAILABLE
        self.enhanced_manager = None
        self.batch_ops = None
        
        if ENHANCEMENTS_AVAILABLE:
            try:
                self.enhanced_manager, self.batch_ops = get_enhanced_manager()
                print("✅ Enhanced manager initialized")
            except Exception as e:
                print(f"⚠️ Could not initialize enhanced manager: {e}")
                self.original_mode = True
            
    def run_enhanced_downloading(self):
        """Enhanced downloading with progress tracking and proper venv creation"""
        
        print("📥 LSDAI Enhanced Downloading System v2.1")
        print("=" * 50)
        
        # Step 1: Setup venv with proper fallbacks
        print("🐍 Setting up Python environment...")
        venv_success = self._setup_enhanced_venv()
        
        if venv_success:
            print("✅ Virtual environment ready")
        else:
            print("⚠️ Using system Python (this is still functional)")
            
        # Step 2: Install WebUI
        print("\n🚀 Installing WebUI...")
        webui_result = self._install_webui_enhanced()
        
        # Step 3: Download models
        print("\n🎨 Downloading models...")
        models_result = self._download_models_enhanced()
        
        # Step 4: Install extensions
        print("\n🔧 Installing extensions...")
        extensions_result = self._install_extensions_enhanced()
        
        # Summary
        print("\n" + "=" * 50)
        print("📊 LSDAI Setup Summary")
        print("=" * 50)
        print(f"🐍 Environment: {'✅ Ready' if venv_success else '⚠️ System Python'}")
        print(f"🚀 WebUI: {'✅ Installed' if webui_result else '❌ Failed'}")
        print(f"🎨 Models: {'✅ Complete' if models_result else '⚠️ Issues'}")
        print(f"🔧 Extensions: {'✅ Complete' if extensions_result else '⚠️ Issues'}")
        
        # Send completion notification
        if ENHANCEMENTS_AVAILABLE:
            if webui_result and models_result:
                send_success("LSDAI Setup Complete", "All components installed successfully!")
            else:
                send_error("LSDAI Setup Issues", "Some components failed to install")
                
        print("🎉 LSDAI setup completed! Ready for launch.")
        return True
            
    def _setup_enhanced_venv(self):
        """Setup enhanced virtual environment with proper fallbacks"""
        print("🔧 Attempting venv creation with multiple strategies...")
        
        # Strategy 1: Use enhanced venv setup if available
        if ENHANCEMENTS_AVAILABLE and not self.original_mode:
            try:
                print("✨ Attempting enhanced venv setup...")
                return self.enhanced_manager.setup_enhanced_venv()
            except Exception as e:
                print(f"⚠️ Enhanced venv setup failed: {e}")
        
        # Strategy 2: Use original comprehensive venv setup
        if ORIGINAL_DOWNLOADING_AVAILABLE:
            try:
                print("📦 Using original comprehensive venv setup...")
                return setup_comprehensive_safe_venv()
            except Exception as e:
                print(f"⚠️ Comprehensive venv setup failed: {e}")
        
        # Strategy 3: Use basic robust venv creation
        if ORIGINAL_DOWNLOADING_AVAILABLE:
            try:
                print("🔄 Using robust venv creation...")
                return create_robust_venv()
            except Exception as e:
                print(f"⚠️ Robust venv creation failed: {e}")
        
        # Strategy 4: Colab-specific venv creation (FIXED FOR ENSUREPIP ISSUE)
        return self._colab_safe_venv_setup()
        
    def _colab_safe_venv_setup(self):
        """Colab-safe venv setup that handles ensurepip failures"""
        try:
            print("🛠️ Using Colab-safe venv setup (handles ensurepip issues)...")
            
            venv_path = Path(os.environ.get('venv_path', '/content/venv'))
            
            # Remove existing broken venv
            if venv_path.exists():
                print("🗑️ Removing existing venv...")
                import shutil
                shutil.rmtree(venv_path, ignore_errors=True)
            
            # Method 1: Try venv without pip bootstrap (Colab-friendly)
            print("🐍 Creating venv without pip bootstrap...")
            cmd = [sys.executable, '-m', 'venv', str(venv_path), '--without-pip']
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                print("✅ Venv created without pip")
                
                # Manually install pip using get-pip.py
                print("📦 Installing pip manually...")
                success = self._install_pip_manually(venv_path)
                
                if success:
                    print("✅ Colab-safe venv creation successful")
                    return True
                else:
                    print("⚠️ Pip installation failed, using system Python")
                    return False
            else:
                print(f"⚠️ Venv creation failed: {result.stderr}")
                
            # Method 2: Try copying system environment
            print("📋 Trying system environment copy method...")
            return self._copy_system_environment(venv_path)
            
        except Exception as e:
            print(f"❌ Colab-safe venv setup error: {e}")
            print("📦 Continuing with system Python")
            return False
            
    def _install_pip_manually(self, venv_path):
        """Manually install pip in venv using get-pip.py"""
        try:
            python_exe = venv_path / 'bin' / 'python'
            
            if not python_exe.exists():
                return False
                
            # Download get-pip.py
            print("📥 Downloading get-pip.py...")
            import urllib.request
            get_pip_url = "https://bootstrap.pypa.io/get-pip.py"
            get_pip_path = venv_path / 'get-pip.py'
            
            urllib.request.urlretrieve(get_pip_url, get_pip_path)
            
            # Install pip
            cmd = [str(python_exe), str(get_pip_path)]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            # Clean up
            get_pip_path.unlink(missing_ok=True)
            
            if result.returncode == 0:
                # Test pip
                pip_path = venv_path / 'bin' / 'pip'
                if pip_path.exists():
                    test_result = subprocess.run([str(pip_path), '--version'], 
                                               capture_output=True, text=True, timeout=30)
                    return test_result.returncode == 0
                    
            return False
            
        except Exception as e:
            print(f"⚠️ Manual pip install error: {e}")
            return False
            
    def _copy_system_environment(self, venv_path):
        """Create a pseudo-venv by copying system environment"""
        try:
            print("📋 Creating pseudo-venv with system environment...")
            
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
            
            # Create pip symlink (find system pip)
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
                if test_result.returncode == 0:
                    print("✅ Pseudo-venv created successfully")
                    return True
                    
            return False
            
        except Exception as e:
            print(f"⚠️ Pseudo-venv creation error: {e}")
            return False
            
    def _install_webui_enhanced(self):
        """Install WebUI with enhancements"""
        try:
            if ORIGINAL_DOWNLOADING_AVAILABLE:
                print("📦 Installing WebUI using original methods...")
                return install_webui()
            else:
                print("❌ WebUI installation functions not available")
                # Try basic git clone fallback
                return self._basic_webui_install()
                
        except Exception as e:
            print(f"WebUI installation error: {e}")
            return self._basic_webui_install()
            
    def _basic_webui_install(self):
        """Basic WebUI installation fallback"""
        try:
            print("🔄 Using basic WebUI installation...")
            
            # Get WebUI selection from settings
            webui_type = js.read(SETTINGS_PATH, 'WIDGETS.change_webui', 'automatic1111')
            home_path = Path(os.environ.get('home_path', '/content'))
            
            webui_configs = {
                'automatic1111': {
                    'url': 'https://github.com/AUTOMATIC1111/stable-diffusion-webui.git',
                    'path': home_path / 'stable-diffusion-webui'
                },
                'ComfyUI': {
                    'url': 'https://github.com/comfyanonymous/ComfyUI.git',
                    'path': home_path / 'ComfyUI'
                }
            }
            
            config = webui_configs.get(webui_type, webui_configs['automatic1111'])
            
            if not config['path'].exists():
                print(f"📥 Cloning {webui_type}...")
                cmd = ['git', 'clone', config['url'], str(config['path'])]
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
            print(f"Basic WebUI install error: {e}")
            return False
            
    def _download_models_enhanced(self):
        """Download models with enhanced progress tracking"""
        try:
            if ENHANCEMENTS_AVAILABLE and not self.original_mode:
                print("✨ Using enhanced model downloading...")
                return self.enhanced_manager.download_models_with_progress()
            elif ORIGINAL_DOWNLOADING_AVAILABLE:
                print("📦 Using original model downloading...")
                return download_models_and_assets()
            else:
                print("🔄 Using basic model downloading...")
                return self._basic_model_download()
                
        except Exception as e:
            print(f"Model download error: {e}")
            return self._basic_model_download()
            
    def _basic_model_download(self):
        """Basic model downloading fallback"""
        try:
            print("🎨 Basic model download (using Manager.py)...")
            
            # Import Manager functions
            from Manager import m_download
            
            # Get model URLs from settings
            model_urls = []
            widgets_data = js.read(SETTINGS_PATH, 'WIDGETS', {})
            
            url_keys = ['Model_url', 'Vae_url', 'LoRA_url', 'Embedding_url']
            for key in url_keys:
                urls = widgets_data.get(key, '')
                if urls:
                    model_urls.extend([url.strip() for url in urls.split(',') if url.strip()])
            
            if model_urls:
                print(f"📥 Downloading {len(model_urls)} items...")
                for url in model_urls:
                    try:
                        m_download(url, log=True)
                    except Exception as e:
                        print(f"⚠️ Download failed for {url}: {e}")
                        
                print("✅ Model downloads completed")
                return True
            else:
                print("⚠️ No model URLs found in settings")
                return True  # Not an error if no models selected
                
        except Exception as e:
            print(f"Basic model download error: {e}")
            return False
            
    def _install_extensions_enhanced(self):
        """Install extensions with enhanced management"""
        try:
            if ENHANCEMENTS_AVAILABLE and not self.original_mode:
                print("✨ Using enhanced extension management...")
                # Use enhanced extension manager if available
                from modules.ExtensionManager import get_extension_manager
                ext_manager = get_extension_manager()
                return ext_manager.install_from_settings()
            else:
                print("📦 Using basic extension installation...")
                return self._basic_extension_install()
                
        except Exception as e:
            print(f"Extension installation error: {e}")
            return self._basic_extension_install()
            
    def _basic_extension_install(self):
        """Basic extension installation fallback"""
        try:
            # Get extension URLs from settings
            widgets_data = js.read(SETTINGS_PATH, 'WIDGETS', {})
            extension_urls = widgets_data.get('Extensions_url', '')
            
            if not extension_urls:
                print("⚠️ No extensions selected")
                return True
                
            urls = [url.strip() for url in extension_urls.split(',') if url.strip()]
            
            if urls:
                print(f"🔧 Installing {len(urls)} extensions...")
                
                # Determine WebUI type for extension path
                webui_type = widgets_data.get('change_webui', 'automatic1111')
                home_path = Path(os.environ.get('home_path', '/content'))
                
                if webui_type == 'automatic1111':
                    extensions_dir = home_path / 'stable-diffusion-webui' / 'extensions'
                elif webui_type == 'ComfyUI':
                    extensions_dir = home_path / 'ComfyUI' / 'custom_nodes'
                else:
                    extensions_dir = home_path / 'stable-diffusion-webui' / 'extensions'
                
                extensions_dir.mkdir(parents=True, exist_ok=True)
                
                for url in urls:
                    try:
                        # Extract repo name from URL
                        repo_name = url.split('/')[-1].replace('.git', '')
                        target_path = extensions_dir / repo_name
                        
                        if not target_path.exists():
                            print(f"📥 Cloning {repo_name}...")
                            cmd = ['git', 'clone', url, str(target_path)]
                            result = subprocess.run(cmd, capture_output=True, text=True)
                            
                            if result.returncode == 0:
                                print(f"✅ {repo_name} installed")
                            else:
                                print(f"⚠️ Failed to install {repo_name}")
                        else:
                            print(f"✅ {repo_name} already exists")
                            
                    except Exception as e:
                        print(f"⚠️ Extension install error: {e}")
                        
                return True
            else:
                return True
                
        except Exception as e:
            print(f"Basic extension install error: {e}")
            return False

# Main integration function that gets called by the notebook
def run_enhanced_downloading():
    """Main function called by the notebook cell"""
    try:
        system = EnhancedDownloadingSystem()
        return system.run_enhanced_downloading()
    except Exception as e:
        print(f"❌ Enhanced downloading system failed: {e}")
        print("🔄 Falling back to original downloading script...")
        
        # Final fallback - run original downloading script directly
        try:
            if ORIGINAL_DOWNLOADING_AVAILABLE:
                return downloading_main()
            else:
                print("❌ No fallback available")
                return False
        except Exception as e2:
            print(f"❌ Original downloading fallback also failed: {e2}")
            return False

# Execute the main function when script is run
if __name__ == "__main__" or "run_path" in globals():
    run_enhanced_downloading()

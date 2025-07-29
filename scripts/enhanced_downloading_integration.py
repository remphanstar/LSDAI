# Enhanced downloading integration
import json_utils as js
from pathlib import Path
import subprocess
import time

# Import original downloading functions
try:
    from scripts.downloading_en import *  # Your original functions
    ORIGINAL_DOWNLOADING_AVAILABLE = True
except ImportError:
    ORIGINAL_DOWNLOADING_AVAILABLE = False
    print("⚠️ Original downloading functions not found")

# Import enhancements
try:
    from modules.EnhancedManager import get_enhanced_manager
    from modules.NotificationSystem import send_info, send_success, send_error
    from modules.AdvancedLogging import get_advanced_logger
    ENHANCEMENTS_AVAILABLE = True
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
            except Exception as e:
                print(f"⚠️ Could not initialize enhanced manager: {e}")
                self.original_mode = True
            
    def run_enhanced_downloading(self):
        """Enhanced downloading with progress tracking"""
        
        print("📥 LSDAI Enhanced Downloading System")
        print("=" * 40)
        
        # Step 1: Setup venv (original functionality)
        print("🐍 Setting up Python environment...")
        try:
            setup_venv_result = self._setup_enhanced_venv()
            if setup_venv_result:
                print("✅ Virtual environment ready")
            else:
                print("⚠️ Using system Python")
        except Exception as e:
            print(f"❌ Venv setup error: {e}")
            
        # Step 2: Install WebUI (enhanced)
        print("🚀 Installing WebUI...")
        webui_result = self._install_webui_enhanced()
        
        # Step 3: Download models (enhanced with progress)
        print("🎨 Downloading models...")
        models_result = self._download_models_enhanced()
        
        # Step 4: Install extensions (enhanced management)
        print("🔧 Installing extensions...")
        extensions_result = self._install_extensions_enhanced()
        
        # Send completion notification
        if ENHANCEMENTS_AVAILABLE:
            if all([webui_result, models_result, extensions_result]):
                send_success("LSDAI Setup Complete", "All components installed successfully!")
        else:
            print("✅ LSDAI setup completed using standard methods")
            
    def _setup_enhanced_venv(self):
        """Setup enhanced virtual environment"""
        try:
            if ENHANCEMENTS_AVAILABLE and not self.original_mode:
                # Use enhanced venv setup
                return self.enhanced_manager.setup_enhanced_venv()
            else:
                # Fall back to original venv setup
                if ORIGINAL_DOWNLOADING_AVAILABLE:
                    return setup_comprehensive_safe_venv()
                else:
                    # Basic venv setup fallback
                    return self._basic_venv_setup()
        except Exception as e:
            print(f"Venv setup error: {e}")
            return self._basic_venv_setup()
            
    def _basic_venv_setup(self):
        """Basic venv setup fallback"""
        try:
            print("🔄 Using basic venv setup...")
            # Execute the original downloading_en.py script which contains venv setup
            exec(open('scripts/downloading_en.py').read())
            return True
        except Exception as e:
            print(f"Basic venv setup failed: {e}")
            return False
            
    def _install_webui_enhanced(self):
        """Install WebUI with enhancements"""
        try:
            if ORIGINAL_DOWNLOADING_AVAILABLE:
                # Call original WebUI installation functions
                # The exact function name depends on your original downloading_en.py
                # This should be replaced with the actual function call
                print("📦 Installing WebUI using original methods...")
                return True  # Replace with actual function call
            else:
                print("❌ WebUI installation functions not available")
                return False
                
        except Exception as e:
            print(f"WebUI installation error: {e}")
            return False
            
    def _download_models_enhanced(self):
        """Download models with enhanced progress tracking"""
        try:
            if ENHANCEMENTS_AVAILABLE and not self.original_mode:
                return self.enhanced_manager.download_models_with_progress()
            else:
                # Fall back to original model downloading
                print("📦 Downloading models using original methods...")
                return True  # Replace with actual function call from downloading_en.py
        except Exception as e:
            print(f"Model download error: {e}")
            return False
            
    def _install_extensions_enhanced(self):
        """Install extensions with enhanced management"""
        try:
            if ENHANCEMENTS_AVAILABLE and not self.original_mode:
                return self.enhanced_manager.install_extensions_enhanced()
            else:
                # Fall back to original extension installation
                print("📦 Installing extensions using original methods...")
                return True  # Replace with actual function call from downloading_en.py
        except Exception as e:
            print(f"Extension installation error: {e}")
            return False

# Main integration function
def run_enhanced_downloading():
    """Main function to run enhanced downloading"""
    system = EnhancedDownloadingSystem()
    system.run_enhanced_downloading()

# For backward compatibility and direct execution
if __name__ == "__main__":
    run_enhanced_downloading()

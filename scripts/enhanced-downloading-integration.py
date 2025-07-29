# Enhanced downloading integration
import json_utils as js
from pathlib import Path
import subprocess
import time

# Import original downloading functions
from scripts.downloading_en import *  # Your original functions

# Import enhancements
try:
    from modules.EnhancedManager import get_enhanced_manager
    from modules.NotificationSystem import send_info, send_success, send_error
    ENHANCEMENTS_AVAILABLE = True
except ImportError:
    ENHANCEMENTS_AVAILABLE = False

class EnhancedDownloadingSystem:
    def __init__(self):
        self.original_mode = not ENHANCEMENTS_AVAILABLE
        self.enhanced_manager = None
        self.batch_ops = None
        
        if ENHANCEMENTS_AVAILABLE:
            self.enhanced_manager, self.batch_ops = get_enhanced_manager()
            
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
                print("⚠️  Using system Python")
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
                send_error("LSDAI Setup Issues", "Some components failed to install")
                
    def _setup_enhanced_venv(self):
        """Enhanced venv setup with better error handling"""
        
        if ENHANCEMENTS_AVAILABLE:
            # Use enhanced venv management
            try:
                from modules.EnhancedManager import VenvManager
                venv_manager = VenvManager()
                return venv_manager.setup_venv()
            except ImportError:
                pass
                
        # Fallback to original venv setup
        try:
            # Your original venv setup code here
            return setup_original_venv()  # Call your existing function
        except Exception as e:
            print(f"Venv setup error: {e}")
            return False
            
    def _install_webui_enhanced(self):
        """Enhanced WebUI installation"""
        
        try:
            # Get WebUI selection from settings
            webui_type = js.read_key('change_webui', 'automatic1111')
            
            print(f"📦 Installing {webui_type}...")
            
            # Original WebUI installation logic
            webui_result = install_original_webui(webui_type)  # Your existing function
            
            # Enhanced post-installation setup
            if ENHANCEMENTS_AVAILABLE and webui_result:
                self._setup_webui_enhancements(webui_type)
                
            return webui_result
            
        except Exception as e:
            print(f"WebUI installation error: {e}")
            if ENHANCEMENTS_AVAILABLE:
                send_error("WebUI Installation Failed", str(e))
            return False
            
    def _download_models_enhanced(self):
        """Enhanced model downloading with progress tracking"""
        
        try:
            # Get model URLs from settings
            model_urls = []
            
            # Collect URLs from various sources
            if js.read_key('Model_url'):
                model_urls.extend(js.read_key('Model_url').split(','))
            if js.read_key('Vae_url'):
                model_urls.extend(js.read_key('Vae_url').split(','))
            if js.read_key('LoRA_url'):
                model_urls.extend(js.read_key('LoRA_url').split(','))
                
            if not model_urls:
                print("ℹ️  No models to download")
                return True
                
            if ENHANCEMENTS_AVAILABLE:
                print(f"📥 Downloading {len(model_urls)} models with enhanced manager...")
                
                # Use enhanced download manager
                count = self.enhanced_manager.add_to_queue(model_urls)
                self.enhanced_manager.start_queue()
                
                # Monitor progress
                while self.enhanced_manager.get_queue_status()['downloading'] > 0:
                    status = self.enhanced_manager.get_queue_status()
                    print(f"⏳ Progress: {status['completed']}/{status['total_items']} completed")
                    time.sleep(5)
                    
                final_status = self.enhanced_manager.get_queue_status()
                success = final_status['failed'] == 0
                
                if success:
                    send_success("Model Downloads", f"Downloaded {final_status['completed']} models")
                else:
                    send_error("Download Issues", f"{final_status['failed']} downloads failed")
                    
                return success
                
            else:
                # Fallback to original downloading
                print("📥 Using original download method...")
                return download_models_original(model_urls)  # Your existing function
                
        except Exception as e:
            print(f"Model download error: {e}")
            if ENHANCEMENTS_AVAILABLE:
                send_error("Model Download Failed", str(e))
            return False
            
    def _install_extensions_enhanced(self):
        """Enhanced extension installation"""
        
        try:
            # Get extension URLs
            extension_urls = []
            if js.read_key('Extensions_url'):
                extension_urls.extend(js.read_key('Extensions_url').split(','))
                
            if not extension_urls:
                print("ℹ️  No extensions to install")
                return True
                
            if ENHANCEMENTS_AVAILABLE:
                print(f"🔧 Installing {len(extension_urls)} extensions with enhanced manager...")
                
                from modules.ExtensionManager import get_extension_manager
                ext_manager = get_extension_manager()
                
                # Convert URLs to extension info
                extensions_to_install = []
                for url in extension_urls:
                    if url.strip():
                        name = Path(url).stem
                        extensions_to_install.append({
                            'name': name,
                            'url': url.strip()
                        })
                        
                # Install extensions
                results = ext_manager.batch_install_extensions(extensions_to_install)
                
                success = len(results['failed']) == 0
                if success:
                    send_success("Extensions Installed", f"Installed {len(results['successful'])} extensions")
                else:
                    send_error("Extension Issues", f"{len(results['failed'])} extensions failed")
                    
                return success
                
            else:
                # Fallback to original extension installation
                return install_extensions_original(extension_urls)  # Your existing function
                
        except Exception as e:
            print(f"Extension installation error: {e}")
            if ENHANCEMENTS_AVAILABLE:
                send_error("Extension Installation Failed", str(e))
            return False
            
    def _setup_webui_enhancements(self, webui_type):
        """Setup enhancements for installed WebUI"""
        
        try:
            print("✨ Setting up WebUI enhancements...")
            
            # Initialize performance monitoring
            from modules.AdvancedLogging import get_advanced_logger
            logger = get_advanced_logger()
            logger.log_event('info', 'setup', f'WebUI {webui_type} installed with enhancements')
            
            # Setup cloud sync if configured
            if js.read_key('cloud_sync_enabled', False):
                from modules.CloudSync import get_cloud_sync_manager
                sync_manager = get_cloud_sync_manager()
                sync_manager.sync_all_data()
                
            print("✅ WebUI enhancements configured")
            
        except Exception as e:
            print(f"Enhancement setup error: {e}")

# Main integration function
def run_enhanced_downloading():
    """Main function for enhanced downloading"""
    enhanced_system = EnhancedDownloadingSystem()
    enhanced_system.run_enhanced_downloading()

# For backward compatibility
if __name__ == "__main__":
    run_enhanced_downloading()

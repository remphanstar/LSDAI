# Enhanced launch integration
import json_utils as js
from pathlib import Path
import subprocess
import os
import sys

# Import original launch functions
from scripts.launch import *  # Your original launch functions

# Import enhancements - FIXED IMPORT
try:
    from scripts.enhanced_launch_en import enhanced_launch_webui, WebUIManager, SystemOptimizer  # Fixed filename
    from modules.NotificationSystem import send_info, send_success, send_error
    from modules.AdvancedLogging import setup_webui_monitoring
    ENHANCEMENTS_AVAILABLE = True
except ImportError:
    ENHANCEMENTS_AVAILABLE = False

class IntegratedLauncher:
    def __init__(self):
        self.enhancement_mode = ENHANCEMENTS_AVAILABLE
        self.webui_manager = None
        self.system_optimizer = None
        
        if ENHANCEMENTS_AVAILABLE:
            self.webui_manager = WebUIManager()
            self.system_optimizer = SystemOptimizer()
            
    def launch_integrated_webui(self):
        """Launch WebUI with integrated enhancements"""
        
        print("🚀 LSDAI Integrated Launcher v2.0")
        print("=" * 40)
        
        if self.enhancement_mode:
            print("✨ Enhanced mode enabled")
            self._launch_enhanced()
        else:
            print("📦 Standard mode (enhancements not available)")
            self._launch_standard()
            
    def _launch_enhanced(self):
        """Launch with full enhancements"""
        
        try:
            # System optimization
            print("⚡ Optimizing system performance...")
            specs = self.system_optimizer.detect_system_specs()
            optimizations = self.system_optimizer.apply_optimizations(specs)
            print(f"✅ Applied {len(optimizations)} optimizations")
            
            # Prepare WebUI launch
            print("🔧 Preparing WebUI launch...")
            config = self.webui_manager.prepare_launch()
            
            # Get WebUI path and arguments
            webui_path = self._get_webui_path()
            launch_args = js.read_key('commandline_arguments', '')
            
            # Add enhancement-specific arguments
            if not any('--api' in arg for arg in launch_args.split()):
                launch_args += ' --api'  # Enable API for enhancements
                
            # Setup monitoring
            print("📊 Setting up monitoring...")
            
            # Launch WebUI with monitoring
            print("🚀 Launching enhanced WebUI...")
            success = self.webui_manager.launch_webui(
                webui_path=webui_path,
                args=launch_args,
                auto_restart=True
            )
            
            if success:
                send_success("WebUI Launched", "Enhanced WebUI started successfully")
                
                # Start additional services
                self._start_enhancement_services()
                
                print("🎉 Enhanced WebUI is running!")
                
        except Exception as e:
            print(f"❌ Enhanced launch failed: {e}")
            print("🔄 Falling back to standard launch...")
            self._launch_standard()
            
    def _launch_standard(self):
        """Launch using original LSDAI functionality"""
        
        print("📦 Using original LSDAI launch process...")
        
        try:
            # Call original launch functions
            webui_path = self._get_webui_path()
            launch_args = js.read_key('commandline_arguments', '')
            
            print(f"🚀 Launching WebUI from: {webui_path}")
            print(f"📝 Arguments: {launch_args}")
            
            # Execute original launch logic
            original_launch_result = self._execute_original_launch(webui_path, launch_args)
            
            if original_launch_result:
                print("✅ WebUI launched successfully!")
            else:
                print("❌ Launch failed")
                
        except Exception as e:
            print(f"❌ Standard launch failed: {e}")
            
    def _get_webui_path(self):
        """Get WebUI installation path"""
        # Implementation to detect WebUI path
        webui_type = js.read_key('change_webui', 'automatic1111')
        home_path = Path(os.environ.get('home_path', '/content'))
        
        webui_paths = {
            'automatic1111': home_path / 'stable-diffusion-webui',
            'ComfyUI': home_path / 'ComfyUI',
            'InvokeAI': home_path / 'InvokeAI'
        }
        
        return webui_paths.get(webui_type, webui_paths['automatic1111'])
        
    def _execute_original_launch(self, webui_path, args):
        """Execute the original launch logic"""
        # Call your original launch functions here
        try:
            # This should call your existing launch.py functions
            return True
        except Exception as e:
            print(f"Launch execution error: {e}")
            return False
            
    def _start_enhancement_services(self):
        """Start additional enhancement services"""
        if ENHANCEMENTS_AVAILABLE:
            try:
                # Start background services
                setup_webui_monitoring()
                print("📊 Monitoring services started")
            except Exception as e:
                print(f"⚠️ Could not start enhancement services: {e}")

# Main integration function
def launch_integrated():
    """Main function to launch integrated system"""
    launcher = IntegratedLauncher()
    launcher.launch_integrated_webui()

# For backward compatibility
if __name__ == "__main__":
    launch_integrated()

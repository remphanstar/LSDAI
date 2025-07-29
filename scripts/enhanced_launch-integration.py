# Enhanced launch integration
import json_utils as js
from pathlib import Path
import subprocess
import os
import sys

# Import original launch functions
from scripts.launch import *  # Your original launch functions

# Import enhancements
try:
    from scripts.enhanced_launch import enhanced_launch_webui, WebUIManager, SystemOptimizer
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
                print("📱 Access the enhanced interface in your browser")
                
                # Keep launcher running
                self._monitor_webui()
                
            else:
                send_error("Launch Failed", "Enhanced WebUI failed to start")
                print("❌ Launch failed, falling back to standard mode")
                self._launch_standard()
                
        except Exception as e:
            print(f"❌ Enhanced launch error: {e}")
            send_error("Launch Error", str(e))
            print("📦 Falling back to standard launch...")
            self._launch_standard()
            
    def _launch_standard(self):
        """Fallback to original launch method"""
        
        try:
            print("📦 Using original LSDAI launch method...")
            
            # Apply matplotlib fixes (from your original launch.py)
            apply_matplotlib_fixes()  # Your existing function
            
            # Activate custom venv
            activate_custom_venv()  # Your existing function
            
            # Launch WebUI
            webui_path = self._get_webui_path()
            launch_args = js.read_key('commandline_arguments', '')
            
            # Use your original launch method
            launch_result = launch_original_webui(webui_path, launch_args)  # Your existing function
            
            if launch_result:
                print("✅ Standard WebUI launched successfully")
            else:
                print("❌ WebUI launch failed")
                
        except Exception as e:
            print(f"❌ Standard launch error: {e}")
            
    def _get_webui_path(self):
        """Get WebUI installation path"""
        
        webui_type = js.read_key('change_webui', 'automatic1111')
        
        webui_paths = {
            'automatic1111': Path('stable-diffusion-webui'),
            'ComfyUI': Path('ComfyUI'),
            'InvokeAI': Path('InvokeAI'),
            'StableSwarmUI': Path('StableSwarmUI')
        }
        
        webui_path = webui_paths.get(webui_type, Path('stable-diffusion-webui'))
        
        if not webui_path.exists():
            # Try alternative locations
            alternative_paths = [
                Path.cwd() / webui_path.name,
                Path.home() / webui_path.name,
                Path('/content') / webui_path.name  # Colab
            ]
            
            for alt_path in alternative_paths:
                if alt_path.exists():
                    webui_path = alt_path
                    break
                    
        return webui_path
        
    def _start_enhancement_services(self):
        """Start additional enhancement services"""
        
        try:
            # Start cloud sync if enabled
            if js.read_key('cloud_sync_enabled', False):
                from modules.CloudSync import get_cloud_sync_manager
                sync_manager = get_cloud_sync_manager()
                
                auto_sync_interval = js.read_key('auto_sync_interval', 3600)
                sync_manager.start_auto_sync(auto_sync_interval)
                print("☁️  Cloud sync service started")
                
            # Start model discovery if enabled
            if js.read_key('auto_discovery', True):
                from modules.EnhancedModelManager import get_enhanced_model_manager
                model_manager = get_enhanced_model_manager()
                
                # Schedule periodic model discovery
                import threading
                def discover_models():
                    try:
                        discovered = model_manager.discovery.discover_models(limit_per_source=5)
                        if discovered:
                            send_info("New Models", f"Discovered {len(discovered)} new models")
                    except Exception as e:
                        print(f"Model discovery error: {e}")
                        
                discovery_thread = threading.Thread(target=discover_models, daemon=True)
                discovery_thread.start()
                print("🔍 Model discovery service started")
                
            # Start performance monitoring
            performance_monitoring = js.read_key('performance_monitoring', True)
            if performance_monitoring:
                from modules.AdvancedLogging import SystemResourceMonitor, get_advanced_logger
                
                logger = get_advanced_logger()
                resource_monitor = SystemResourceMonitor(logger)
                resource_monitor.start_monitoring()
                print("📊 Performance monitoring started")
                
        except Exception as e:
            print(f"⚠️  Error starting enhancement services: {e}")
            
    def _monitor_webui(self):
        """Monitor WebUI process"""
        
        try:
            # Keep launcher running and monitor WebUI
            import time
            
            while self.webui_manager.get_status() == 'running':
                time.sleep(10)
                
                # Periodic health check
                if hasattr(self.webui_manager, 'process') and self.webui_manager.process:
                    if self.webui_manager.process.poll() is not None:
                        # Process ended
                        exit_code = self.webui_manager.process.poll()
                        if exit_code != 0:
                            send_error("WebUI Crashed", f"WebUI exited with code {exit_code}")
                        break
                        
        except KeyboardInterrupt:
            print("\n🛑 Shutdown requested...")
            if self.webui_manager:
                self.webui_manager.stop_webui()
            send_info("WebUI Shutdown", "WebUI stopped by user")

# Main integration function
def launch_integrated():
    """Main function for integrated launch"""
    launcher = IntegratedLauncher()
    launcher.launch_integrated_webui()

# For backward compatibility
if __name__ == "__main__":
    launch_integrated()

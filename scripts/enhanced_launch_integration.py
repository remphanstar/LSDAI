# Enhanced launch integration
import json_utils as js
from pathlib import Path
import subprocess
import os
import sys

# Import original launch functions
try:
    from scripts.launch import *  # Your original launch functions
    ORIGINAL_LAUNCH_AVAILABLE = True
except ImportError:
    ORIGINAL_LAUNCH_AVAILABLE = False
    print("⚠️ Original launch functions not found")

# Import enhancements - FIXED IMPORT
try:
    from scripts.enhanced_launch_en import enhanced_launch_webui, WebUIManager, SystemOptimizer  # Fixed filename
    from modules.NotificationSystem import send_info, send_success, send_error
    from modules.AdvancedLogging import setup_webui_monitoring
    ENHANCEMENTS_AVAILABLE = True
except ImportError:
    ENHANCEMENTS_AVAILABLE = False
    print("⚠️ Enhanced launch modules not available")

class IntegratedLauncher:
    def __init__(self):
        self.enhancement_mode = ENHANCEMENTS_AVAILABLE
        self.webui_manager = None
        self.system_optimizer = None
        
        if ENHANCEMENTS_AVAILABLE:
            try:
                self.webui_manager = WebUIManager()
                self.system_optimizer = SystemOptimizer()
            except Exception as e:
                print(f"⚠️ Could not initialize enhanced components: {e}")
                self.enhancement_mode = False
            
    def launch_integrated_webui(self):
        """Launch WebUI with integrated enhancements"""
        
        print("🚀 LSDAI Integrated Launcher v2.0")
        print("=" * 40)
        
        if self.enhancement_mode:
            print("✨ Enhanced mode enabled")
            try:
                self._launch_enhanced()
            except Exception as e:
                print(f"❌ Enhanced launch failed: {e}")
                print("🔄 Falling back to standard launch...")
                self._launch_standard()
        else:
            print("📦 Standard mode (enhancements not available)")
            self._launch_standard()
            
    def _launch_enhanced(self):
        """Launch with full enhancements"""
        
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
        
        try:
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
                return True
                
        except Exception as e:
            print(f"❌ Enhanced launch execution failed: {e}")
            raise
            
    def _launch_standard(self):
        """Launch using original LSDAI functionality"""
        
        print("📦 Using original LSDAI launch process...")
        
        try:
            # Get WebUI path and arguments
            webui_path = self._get_webui_path()
            launch_args = js.read_key('commandline_arguments', '')
            
            print(f"🚀 Launching WebUI from: {webui_path}")
            print(f"📝 Arguments: {launch_args}")
            
            # Execute original launch logic
            if ORIGINAL_LAUNCH_AVAILABLE:
                # Call original launch functions if available
                original_launch_result = self._execute_original_launch(webui_path, launch_args)
            else:
                # Basic launch fallback
                original_launch_result = self._execute_basic_launch(webui_path, launch_args)
            
            if original_launch_result:
                print("✅ WebUI launched successfully!")
            else:
                print("❌ Launch failed")
                
        except Exception as e:
            print(f"❌ Standard launch failed: {e}")
            
    def _get_webui_path(self):
        """Get WebUI installation path"""
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
        try:
            # Try to execute the original launch.py script
            exec(open('scripts/launch.py').read())
            return True
        except Exception as e:
            print(f"Original launch execution error: {e}")
            return self._execute_basic_launch(webui_path, args)
            
    def _execute_basic_launch(self, webui_path, args):
        """Basic launch fallback"""
        try:
            # Get venv path
            venv_path = Path(os.environ.get('venv_path', '/content/venv'))
            python_path = venv_path / 'bin' / 'python'
            
            # Check if webui exists
            if not webui_path.exists():
                print(f"❌ WebUI not found at: {webui_path}")
                return False
                
            # Find the main script
            main_scripts = ['webui.py', 'launch.py', 'main.py']
            main_script = None
            
            for script in main_scripts:
                script_path = webui_path / script
                if script_path.exists():
                    main_script = script_path
                    break
                    
            if not main_script:
                print(f"❌ No main script found in {webui_path}")
                return False
                
            # Build launch command
            cmd = [str(python_path), str(main_script)]
            if args.strip():
                cmd.extend(args.split())
                
            print(f"📋 Launch command: {' '.join(cmd)}")
            
            # Change to webui directory and launch
            os.chdir(webui_path)
            
            # Launch in background (non-blocking)
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            
            print("🚀 WebUI process started!")
            print("📝 Monitor the output above for the WebUI URL")
            
            # Print first few lines of output
            for i, line in enumerate(process.stdout):
                print(line.strip())
                if i > 10:  # Show first 10 lines then continue in background
                    break
                    
            return True
            
        except Exception as e:
            print(f"Basic launch error: {e}")
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

# For backward compatibility and direct execution
if __name__ == "__main__":
    launch_integrated()

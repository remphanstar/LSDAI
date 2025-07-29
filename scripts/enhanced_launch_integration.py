# Enhanced launch integration - FIXED AND COMPREHENSIVE
import json_utils as js
from pathlib import Path
import subprocess
import os
import sys
import time

# Get settings path from environment or default
SETTINGS_PATH = Path(os.environ.get('settings_path', '/content/LSDAI/settings.json'))

# Import original launch functions
try:
    from scripts.launch import *  # Your original launch functions
    ORIGINAL_LAUNCH_AVAILABLE = True
    print("✅ Original launch functions imported successfully")
except ImportError:
    ORIGINAL_LAUNCH_AVAILABLE = False
    print("⚠️ Original launch functions not found")

# Import enhancements - with better error handling
try:
    from modules.NotificationSystem import send_info, send_success, send_error
    from modules.AdvancedLogging import setup_webui_monitoring
    ENHANCEMENTS_AVAILABLE = True
    print("✅ Enhanced launch modules imported successfully")
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
                # Import enhanced components
                from scripts.enhanced_launch_en import enhanced_launch_webui, WebUIManager, SystemOptimizer
                self.webui_manager = WebUIManager()
                self.system_optimizer = SystemOptimizer()
                print("✅ Enhanced components initialized")
            except Exception as e:
                print(f"⚠️ Could not initialize enhanced components: {e}")
                self.enhancement_mode = False
            
    def launch_integrated_webui(self):
        """Launch WebUI with integrated enhancements"""
        
        print("🚀 LSDAI Integrated Launcher v2.1")
        print("=" * 50)
        
        if self.enhancement_mode:
            print("✨ Enhanced mode enabled")
            try:
                success = self._launch_enhanced()
                if success:
                    return True
            except Exception as e:
                print(f"❌ Enhanced launch failed: {e}")
                
            print("🔄 Falling back to standard launch...")
            
        print("📦 Standard mode")
        return self._launch_standard()
            
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
            launch_args = js.read(SETTINGS_PATH, 'WIDGETS.commandline_arguments', '')
            
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
                return True
            else:
                send_error("WebUI Launch Failed", "Failed to start Enhanced WebUI")
                print("❌ Enhanced WebUI launch failed")
                
            return success
            
        except ImportError:
            print("⚠️  Enhanced launcher not available, falling back to standard launch")
            return False
            
    def _launch_standard(self):
        """Launch using original LSDAI functionality"""
        
        print("📦 Using original LSDAI launch process...")
        
        try:
            # Get WebUI path and arguments
            webui_path = self._get_webui_path()
            launch_args = js.read(SETTINGS_PATH, 'WIDGETS.commandline_arguments', '')
            
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
                return True
            else:
                print("❌ Launch failed")
                return False
                
        except Exception as e:
            print(f"❌ Standard launch failed: {e}")
            return False
            
    def _get_webui_path(self):
        """Get WebUI installation path"""
        webui_type = js.read(SETTINGS_PATH, 'WIDGETS.change_webui', 'automatic1111')
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
            # Import and run the original launch script's main function
            if 'get_launch_command_str' in globals():
                # Use the original launch.py functionality
                print("📋 Using original launch.py functionality...")
                
                # Change to WebUI directory
                original_cwd = os.getcwd()
                if webui_path.exists():
                    os.chdir(webui_path)
                
                # Execute the launch command
                launch_cmd = get_launch_command_str()
                print(f"📋 Launch command: {launch_cmd}")
                
                # Start the WebUI process
                process = subprocess.Popen(
                    launch_cmd,
                    shell=True,
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
                    if i > 15:  # Show first 15 lines then continue in background
                        break
                
                # Restore original directory
                os.chdir(original_cwd)
                return True
                
            else:
                # Try executing the original launch.py script directly
                return self._execute_basic_launch(webui_path, args)
                
        except Exception as e:
            print(f"Original launch execution error: {e}")
            return self._execute_basic_launch(webui_path, args)
            
    def _execute_basic_launch(self, webui_path, args):
        """Basic launch fallback"""
        try:
            # Get venv path
            venv_path = Path(os.environ.get('venv_path', '/content/venv'))
            
            # Determine python executable
            python_paths = [
                venv_path / 'bin' / 'python',
                Path('/usr/bin/python3'),
                Path('/usr/bin/python')
            ]
            
            python_exe = None
            for path in python_paths:
                if path.exists():
                    python_exe = str(path)
                    break
            
            if not python_exe:
                print("❌ No Python executable found")
                return False
            
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
            cmd = [python_exe, str(main_script)]
            
            # Add arguments
            if args.strip():
                # Parse arguments properly
                import shlex
                parsed_args = shlex.split(args)
                cmd.extend(parsed_args)
                
            print(f"📋 Launch command: {' '.join(cmd)}")
            
            # Change to webui directory and launch
            original_cwd = os.getcwd()
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
                if i > 15:  # Show first 15 lines then continue in background
                    break
            
            # Restore original directory
            os.chdir(original_cwd)
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

class LauncherHealth:
    """Health check and diagnostics for the launcher"""
    
    @staticmethod
    def check_system_health():
        """Perform system health checks before launch"""
        
        print("🔍 Performing system health checks...")
        
        checks = {
            'WebUI Installation': LauncherHealth._check_webui_installation(),
            'Python Environment': LauncherHealth._check_python_environment(),
            'Required Modules': LauncherHealth._check_required_modules(),
            'Settings File': LauncherHealth._check_settings_file()
        }
        
        passed_checks = sum(checks.values())
        total_checks = len(checks)
        
        print(f"📊 Health Check Results: {passed_checks}/{total_checks} passed")
        
        for check_name, result in checks.items():
            status = "✅" if result else "❌"
            print(f"   {status} {check_name}")
        
        return passed_checks >= total_checks * 0.75  # Need 75% to pass
    
    @staticmethod
    def _check_webui_installation():
        """Check if WebUI is installed"""
        try:
            webui_type = js.read(SETTINGS_PATH, 'WIDGETS.change_webui', 'automatic1111')
            home_path = Path(os.environ.get('home_path', '/content'))
            
            if webui_type == 'automatic1111':
                webui_path = home_path / 'stable-diffusion-webui'
                return (webui_path / 'webui.py').exists()
            elif webui_type == 'ComfyUI':
                webui_path = home_path / 'ComfyUI'
                return (webui_path / 'main.py').exists()
            
            return False
        except:
            return False
    
    @staticmethod
    def _check_python_environment():
        """Check Python environment"""
        try:
            import torch, transformers, diffusers
            return True
        except ImportError:
            return False
    
    @staticmethod
    def _check_required_modules():
        """Check if required modules are available"""
        try:
            import json_utils
            return True
        except ImportError:
            return False
    
    @staticmethod
    def _check_settings_file():
        """Check if settings file exists and is readable"""
        try:
            return SETTINGS_PATH.exists() and js.read(SETTINGS_PATH, 'WIDGETS', {})
        except:
            return False

# Main integration functions

def launch_integrated():
    """Main function to launch integrated system with health checks"""
    
    print("🚀 LSDAI Integrated Launch System")
    print("=" * 50)
    
    # Perform health checks
    if not LauncherHealth.check_system_health():
        print("\n⚠️ System health checks failed!")
        print("🔧 Please ensure Cell 2 (Widgets) and Cell 3 (Downloading) completed successfully")
        return False
    
    print("\n✅ System health checks passed")
    
    # Initialize and run launcher
    launcher = IntegratedLauncher()
    return launcher.launch_integrated_webui()

def quick_launch():
    """Quick launch without health checks (for advanced users)"""
    
    print("⚡ LSDAI Quick Launch")
    print("=" * 30)
    
    launcher = IntegratedLauncher()
    return launcher.launch_integrated_webui()

# For backward compatibility and direct execution
if __name__ == "__main__" or "run_path" in globals():
    launch_integrated()

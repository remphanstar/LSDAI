# ~ enhanced_launch_integration.py | True Blocking Launch System ~

from modules.widget_factory import WidgetFactory
from modules.webui_utils import update_current_webui
from modules import json_utils as js

# VERBOSITY SYSTEM IMPORT WITH FALLBACK
try:
    from modules.verbose_output_manager import (
        get_verbose_manager, VerbosityLevel, 
        vprint, vrun
    )
    VERBOSITY_AVAILABLE = True
    verbose_manager = get_verbose_manager()
    
    def log_msg(message: str, level: int = 2):
        vprint(message, level)
        
except ImportError:
    print("⚠️ Verbosity system not available - using fallback logging")
    VERBOSITY_AVAILABLE = False
    
    class VerbosityLevel:
        SILENT = 0
        MINIMAL = 1
        NORMAL = 2
        DETAILED = 3
        VERBOSE = 4
        RAW = 5
    
    def log_msg(message: str, level: int = 2):
        if level <= 2:
            print(message)

from IPython.display import display, Javascript, HTML, clear_output
import ipywidgets as widgets
from pathlib import Path
import json
import os
import sys
import subprocess
import threading
import time
import signal
import shlex

# --- ROBUST PATH RESOLUTION ---
def find_script_path():
    """Find the absolute path to the 'scripts' directory using multiple methods."""
    try: return Path(__file__).parent.resolve()
    except NameError: pass
    env_path = os.environ.get('scr_path')
    if env_path:
        scripts_dir = Path(env_path) / 'scripts'
        if scripts_dir.exists() and (scripts_dir / '_models_data.py').exists(): return scripts_dir
    cwd = Path.cwd()
    if (cwd / 'scripts' / '_models_data.py').exists(): return cwd / 'scripts'
    if cwd.name == 'scripts' and (cwd / '_models_data.py').exists(): return cwd
    hardcoded_path = Path('/content/LSDAI/scripts')
    if hardcoded_path.exists(): return hardcoded_path
    raise FileNotFoundError("Could not determine the script path. Please ensure you are running from the LSDAI directory.")

try:
    SCRIPTS = find_script_path()
    SCR_PATH = SCRIPTS.parent
    SETTINGS_PATH = SCR_PATH / 'settings.json'
    CSS = SCR_PATH / 'CSS'
    JS = SCR_PATH / 'JS'
except FileNotFoundError as e:
    print(f"FATAL ERROR: {e}")
    sys.exit(1)

# Conditional imports for platform-specific features
try:
    from google.colab import output, drive
    IN_COLAB = True
except ImportError:
    IN_COLAB = False

# --- GLOBAL STATE MANAGEMENT ---
class GlobalLaunchState:
    """Global state to coordinate between UI and blocking execution"""
    def __init__(self):
        self.launch_requested = False
        self.stop_requested = False
        self.restart_requested = False
        self.webui_process = None
        self.webui_running = False
        self.local_url = None
        self.public_url = None
        self.settings = {}
        self.lock = threading.Lock()
    
    def request_launch(self, settings):
        with self.lock:
            self.launch_requested = True
            self.stop_requested = False
            self.restart_requested = False
            self.settings = settings
    
    def request_stop(self):
        with self.lock:
            self.stop_requested = True
            self.launch_requested = False
            self.restart_requested = False
    
    def request_restart(self, settings):
        with self.lock:
            self.restart_requested = True
            self.stop_requested = False
            self.launch_requested = False
            self.settings = settings

# Global state instance
global_state = GlobalLaunchState()

# --- WEBUI PROCESS MANAGER ---
class WebUIProcessManager:
    """Manages WebUI subprocess with proper URL detection"""
    
    def __init__(self, state):
        self.state = state
        self.monitor_thread = None
        
    def find_webui_installation(self):
        """Find installed WebUI directory"""
        base_path = Path(os.environ.get('home_path', '/content'))
        
        webui_paths = [
            base_path / 'stable-diffusion-webui',
            base_path / 'ComfyUI',
            base_path / 'stable-diffusion-webui-forge',
            base_path / 'automatic1111',
            Path('/content/stable-diffusion-webui'),
            Path('/content/ComfyUI')
        ]
        
        for path in webui_paths:
            if path.exists() and (path / 'launch.py').exists():
                log_msg(f"✅ Found WebUI installation: {path}", VerbosityLevel.DETAILED)
                return path
                
        log_msg("❌ No WebUI installation found", VerbosityLevel.MINIMAL)
        return None
    
    def build_launch_command(self, webui_path, settings):
        """Build WebUI launch command from settings"""
        # Use virtual environment python if available
        venv_path = Path(os.environ.get('venv_path', '/content/venv'))
        if venv_path.exists():
            python_exe = venv_path / 'bin' / 'python'
            if not python_exe.exists():  # Windows
                python_exe = venv_path / 'Scripts' / 'python.exe'
        else:
            python_exe = sys.executable
            
        # Base command
        cmd = [str(python_exe), 'launch.py']
        
        # Add arguments from settings
        launch_settings = settings.get('LAUNCH', {})
        
        # Public link support
        if launch_settings.get('public_link', True):
            cmd.append('--share')
            
        # System optimization arguments
        if launch_settings.get('optimize_system', True):
            cmd.extend(['--xformers', '--no-half-vae'])
            
        # Memory optimization
        if launch_settings.get('low_memory_mode', False):
            cmd.extend(['--lowram', '--lowvram'])
            
        # Custom arguments
        custom_args = launch_settings.get('custom_args', '').strip()
        if custom_args:
            try:
                custom_list = shlex.split(custom_args)
                cmd.extend(custom_list)
            except ValueError:
                log_msg(f"⚠️ Invalid custom arguments: {custom_args}", VerbosityLevel.MINIMAL)
                
        return cmd
    
    def start_webui(self):
        """Start WebUI process"""
        webui_path = self.find_webui_installation()
        if not webui_path:
            return False
            
        try:
            cmd = self.build_launch_command(webui_path, self.state.settings)
            
            log_msg("🚀 Starting WebUI process...", VerbosityLevel.NORMAL)
            log_msg(f"🔧 Command: {' '.join(cmd)}", VerbosityLevel.DETAILED)
            log_msg(f"🔧 Working directory: {webui_path}", VerbosityLevel.DETAILED)
            
            # Start process
            self.state.webui_process = subprocess.Popen(
                cmd,
                cwd=webui_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            
            self.state.webui_running = True
            
            # Start monitoring in background
            self.monitor_thread = threading.Thread(target=self._monitor_output)
            self.monitor_thread.daemon = True
            self.monitor_thread.start()
            
            log_msg("✅ WebUI process started successfully", VerbosityLevel.NORMAL)
            log_msg(f"🔧 Process ID: {self.state.webui_process.pid}", VerbosityLevel.DETAILED)
            
            return True
            
        except Exception as e:
            log_msg(f"❌ Failed to start WebUI: {e}", VerbosityLevel.MINIMAL)
            return False
    
    def _monitor_output(self):
        """Monitor WebUI output and extract URLs"""
        while self.state.webui_running and self.state.webui_process:
            try:
                line = self.state.webui_process.stdout.readline()
                if not line:
                    break
                    
                line = line.strip()
                if line:
                    # Show output based on verbosity
                    if VERBOSITY_AVAILABLE:
                        if verbose_manager.verbosity_level >= VerbosityLevel.VERBOSE:
                            print(line)
                        elif any(keyword in line.lower() for keyword in 
                                ['running on', 'local url', 'public url', 'model loaded', 'error', 'warning']):
                            print(line)
                    else:
                        if any(keyword in line.lower() for keyword in 
                               ['running on', 'local url', 'public url', 'error', 'warning']):
                            print(line)
                    
                    # Extract URLs
                    if 'running on local url:' in line.lower():
                        url_part = line.split(':', 2)[-1].strip()
                        self.state.local_url = url_part
                        log_msg(f"🔗 Local URL detected: {url_part}", VerbosityLevel.NORMAL)
                    elif 'running on public url:' in line.lower():
                        url_part = line.split(':', 2)[-1].strip()
                        self.state.public_url = url_part
                        log_msg(f"🌐 Public URL detected: {url_part}", VerbosityLevel.NORMAL)
                        
            except Exception as e:
                log_msg(f"❌ Error monitoring output: {e}", VerbosityLevel.DETAILED)
                break
        
        # Process ended
        if self.state.webui_process:
            exit_code = self.state.webui_process.poll()
            if exit_code is not None and exit_code != 0:
                log_msg(f"❌ WebUI process ended with error code: {exit_code}", VerbosityLevel.MINIMAL)
        
        self.state.webui_running = False
    
    def stop_webui(self):
        """Stop WebUI process"""
        if not self.state.webui_process or not self.state.webui_running:
            return True
            
        log_msg("⏹️ Stopping WebUI process...", VerbosityLevel.NORMAL)
        
        try:
            self.state.webui_running = False
            self.state.webui_process.terminate()
            
            try:
                self.state.webui_process.wait(timeout=10)
                log_msg("✅ WebUI stopped gracefully", VerbosityLevel.NORMAL)
            except subprocess.TimeoutExpired:
                self.state.webui_process.kill()
                self.state.webui_process.wait()
                log_msg("✅ WebUI process force killed", VerbosityLevel.NORMAL)
                
            self.state.webui_process = None
            self.state.local_url = None
            self.state.public_url = None
            
            return True
            
        except Exception as e:
            log_msg(f"❌ Error stopping WebUI: {e}", VerbosityLevel.MINIMAL)
            return False

# --- LAUNCH WIDGET MANAGER ---
class LaunchWidgetManager:
    """Manages the launch interface"""
    
    def __init__(self, state):
        self.factory = WidgetFactory()
        self.widgets = {}
        self.state = state
        
        self.settings_keys = [
            'auto_launch', 'public_link', 'ngrok_tunnel', 'optimize_system',
            'low_memory_mode', 'precision_mode', 'custom_args',
            'monitor_performance', 'auto_restart', 'backup_before_launch'
        ]

    def build_ui(self):
        """Build launch interface"""
        log_msg("🎨 Building launch interface...", VerbosityLevel.DETAILED)
        
        # --- CONTROLS ---
        self.widgets['auto_launch'] = widgets.ToggleButton(value=False, description='Auto Launch', button_style='')
        self.widgets['public_link'] = widgets.ToggleButton(value=True, description='Public Link', button_style='')
        self.widgets['optimize_system'] = widgets.ToggleButton(value=True, description='Optimize System', button_style='')
        self.widgets['low_memory_mode'] = widgets.ToggleButton(value=False, description='Low Memory Mode', button_style='')
        
        self.widgets['precision_mode'] = self.factory.create_dropdown(
            options=['auto', 'fp16', 'fp32', 'bf16'],
            value='auto',
            description='Precision:'
        )
        
        self.widgets['backup_before_launch'] = self.factory.create_checkbox(
            value=True,
            description='Backup Settings Before Launch'
        )
        
        self.widgets['custom_args'] = self.factory.create_textarea(
            value='',
            description='Custom Arguments:',
            placeholder='Additional command line arguments...'
        )
        
        # Layout controls
        controls_left = self.factory.create_vbox([
            self.widgets['auto_launch'],
            self.widgets['public_link'],
            self.widgets['optimize_system']
        ])
        
        controls_right = self.factory.create_vbox([
            self.widgets['low_memory_mode'],
            self.widgets['precision_mode']
        ])
        
        controls_row = self.factory.create_hbox([controls_left, controls_right])
        
        # Configuration section
        config_section = self.factory.create_vbox([
            self.widgets['backup_before_launch'],
            self.widgets['custom_args']
        ])
        
        # --- BUTTONS ---
        launch_button = self.factory.create_button('🚀 Launch WebUI', button_style='success')
        launch_button.on_click(self.launch_webui)
        
        stop_button = self.factory.create_button('⏹️ Stop WebUI', button_style='danger')
        stop_button.on_click(self.stop_webui)
        
        restart_button = self.factory.create_button('🔄 Restart WebUI', button_style='warning')
        restart_button.on_click(self.restart_webui)
        
        button_row = self.factory.create_hbox([launch_button, stop_button, restart_button])
        
        # --- STATUS DISPLAY ---
        self.status_display = self.factory.create_html('<div>⏳ Ready to launch...</div>')
        
        # --- FINAL LAYOUT ---
        main_content = self.factory.create_vbox([
            controls_row,
            config_section,
            button_row,
            self.status_display
        ])
        
        return main_content

    def launch_webui(self, button):
        """Request WebUI launch"""
        try:
            log_msg("🚀 Launch requested...", VerbosityLevel.NORMAL)
            
            # Collect settings
            settings = {'LAUNCH': {}}
            for key in self.settings_keys:
                if key in self.widgets and hasattr(self.widgets[key], 'value'):
                    settings['LAUNCH'][key] = self.widgets[key].value
            
            # Backup settings if requested
            if hasattr(self.widgets['backup_before_launch'], 'value') and self.widgets['backup_before_launch'].value:
                js.save_settings(settings['LAUNCH'], section='LAUNCH')
                log_msg("💾 Settings backed up", VerbosityLevel.DETAILED)
            
            # Request launch
            self.state.request_launch(settings)
            
            # Update status
            self.status_display.value = '<div style="color: orange;">🚀 Launch requested - starting WebUI...</div>'
            
        except Exception as e:
            log_msg(f"❌ Launch request failed: {e}", VerbosityLevel.MINIMAL)

    def stop_webui(self, button):
        """Request WebUI stop"""
        log_msg("⏹️ Stop requested...", VerbosityLevel.NORMAL)
        self.state.request_stop()
        self.status_display.value = '<div style="color: red;">⏹️ Stop requested...</div>'

    def restart_webui(self, button):
        """Request WebUI restart"""
        log_msg("🔄 Restart requested...", VerbosityLevel.NORMAL)
        
        # Collect current settings
        settings = {'LAUNCH': {}}
        for key in self.settings_keys:
            if key in self.widgets and hasattr(self.widgets[key], 'value'):
                settings['LAUNCH'][key] = self.widgets[key].value
        
        self.state.request_restart(settings)
        self.status_display.value = '<div style="color: blue;">🔄 Restart requested...</div>'

    def update_status_display(self):
        """Update status display based on current state"""
        if self.state.webui_running:
            status_html = '<div style="color: green;">✅ WebUI Running</div>'
            
            if self.state.local_url:
                status_html += f'<div>🔗 <a href="{self.state.local_url}" target="_blank">Local URL</a></div>'
            
            if self.state.public_url:
                status_html += f'<div>🌐 <a href="{self.state.public_url}" target="_blank">Public URL</a></div>'
            
            self.status_display.value = status_html
        elif self.state.webui_process:
            self.status_display.value = '<div style="color: orange;">⏳ WebUI starting...</div>'
        else:
            self.status_display.value = '<div>⏸️ WebUI stopped</div>'

# --- MAIN BLOCKING EXECUTION LOOP ---
def main_execution_loop():
    """Main blocking execution loop that keeps cell alive"""
    log_msg("🔄 Entering main execution loop - cell will stay active", VerbosityLevel.NORMAL)
    log_msg("   Click Launch WebUI to start, or interrupt kernel to exit", VerbosityLevel.NORMAL)
    
    process_manager = WebUIProcessManager(global_state)
    
    try:
        while True:
            # Check for launch request
            if global_state.launch_requested:
                with global_state.lock:
                    global_state.launch_requested = False
                
                log_msg("🚀 Processing launch request...", VerbosityLevel.NORMAL)
                success = process_manager.start_webui()
                
                if success:
                    log_msg("✅ WebUI started successfully", VerbosityLevel.NORMAL)
                else:
                    log_msg("❌ WebUI start failed", VerbosityLevel.MINIMAL)
            
            # Check for stop request
            if global_state.stop_requested:
                with global_state.lock:
                    global_state.stop_requested = False
                
                log_msg("⏹️ Processing stop request...", VerbosityLevel.NORMAL)
                process_manager.stop_webui()
                log_msg("✅ WebUI stopped", VerbosityLevel.NORMAL)
            
            # Check for restart request
            if global_state.restart_requested:
                with global_state.lock:
                    global_state.restart_requested = False
                
                log_msg("🔄 Processing restart request...", VerbosityLevel.NORMAL)
                process_manager.stop_webui()
                time.sleep(2)
                success = process_manager.start_webui()
                
                if success:
                    log_msg("✅ WebUI restarted successfully", VerbosityLevel.NORMAL)
                else:
                    log_msg("❌ WebUI restart failed", VerbosityLevel.MINIMAL)
            
            # Update UI status if manager exists
            if 'manager' in globals():
                manager.update_status_display()
            
            # Sleep to prevent busy waiting
            time.sleep(1)
            
    except KeyboardInterrupt:
        log_msg("🛑 Execution interrupted by user", VerbosityLevel.NORMAL)
        if global_state.webui_running:
            log_msg("⏹️ Stopping WebUI before exit...", VerbosityLevel.NORMAL)
            process_manager.stop_webui()
    except Exception as e:
        log_msg(f"❌ Main loop error: {e}", VerbosityLevel.MINIMAL)
    finally:
        log_msg("🏁 Main execution loop ended", VerbosityLevel.NORMAL)

# --- EXECUTION ---
if __name__ == "__main__":
    log_msg("=" * 60, VerbosityLevel.NORMAL)
    log_msg("🔥 LSDAI True Blocking Launch System", VerbosityLevel.NORMAL)
    log_msg("=" * 60, VerbosityLevel.NORMAL)
    
    # Show verbosity system status
    if VERBOSITY_AVAILABLE:
        level_names = {
            VerbosityLevel.SILENT: "Silent",
            VerbosityLevel.MINIMAL: "Minimal",
            VerbosityLevel.NORMAL: "Normal", 
            VerbosityLevel.DETAILED: "Detailed",
            VerbosityLevel.VERBOSE: "Verbose",
            VerbosityLevel.RAW: "Raw Output"
        }
        current_level = level_names.get(verbose_manager.verbosity_level, "Unknown")
        log_msg(f"🔧 Verbosity system: Available (Level: {current_level})", VerbosityLevel.MINIMAL)
    else:
        log_msg("🔧 Verbosity system: Using fallback mode", VerbosityLevel.MINIMAL)

    # Create and display the launch interface
    manager = LaunchWidgetManager(global_state)
    main_container = manager.build_ui()
    
    log_msg("🎨 Launch interface created successfully", VerbosityLevel.NORMAL)
    
    display(main_container)
    
    log_msg("✅ Enhanced Launch System ready!", VerbosityLevel.NORMAL)
    
    # Check for auto-launch
    try:
        settings = js.load_settings(section='LAUNCH')
        if settings and settings.get('auto_launch', False):
            log_msg("🚀 Auto-launch enabled, requesting launch...", VerbosityLevel.NORMAL)
            global_state.request_launch({'LAUNCH': settings})
    except:
        pass
    
    # START THE BLOCKING MAIN LOOP - THIS KEEPS THE CELL ALIVE
    main_execution_loop()

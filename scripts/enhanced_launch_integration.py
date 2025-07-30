# ~ enhanced_launch_integration.py | True Blocking Launch System - FIXED ~

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
    try: 
        return Path(__file__).parent.resolve()
    except NameError: 
        pass
    env_path = os.environ.get('scr_path')
    if env_path:
        scripts_dir = Path(env_path) / 'scripts'
        if scripts_dir.exists() and (scripts_dir / '_models_data.py').exists(): 
            return scripts_dir
    cwd = Path.cwd()
    if (cwd / 'scripts' / '_models_data.py').exists(): 
        return cwd / 'scripts'
    if cwd.name == 'scripts' and (cwd / '_models_data.py').exists(): 
        return cwd
    hardcoded_path = Path('/content/LSDAI/scripts')
    if hardcoded_path.exists(): 
        return hardcoded_path
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
        self.status_widget = None
    
    def request_launch(self, settings):
        with self.lock:
            self.launch_requested = True
            self.stop_requested = False
            self.restart_requested = False
            self.settings = settings
            self._update_status("🚀 Launch requested - starting WebUI...", "orange")
    
    def request_stop(self):
        with self.lock:
            self.stop_requested = True
            self.launch_requested = False
            self.restart_requested = False
            self._update_status("⏹️ Stop requested...", "red")
    
    def request_restart(self, settings):
        with self.lock:
            self.restart_requested = True
            self.stop_requested = False
            self.launch_requested = False
            self.settings = settings
            self._update_status("🔄 Restart requested...", "blue")
    
    def _update_status(self, message, color="black"):
        if self.status_widget:
            self.status_widget.value = f'<div style="color: {color};">{message}</div>'

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
            
        # Precision mode
        precision = launch_settings.get('precision_mode', 'auto')
        if precision == 'fp16':
            cmd.extend(['--precision', 'half'])
        elif precision == 'fp32':
            cmd.extend(['--precision', 'full'])
        elif precision == 'bf16':
            cmd.extend(['--precision', 'bfloat16'])
            
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
            self.state._update_status("❌ No WebUI installation found", "red")
            return False
            
        if self.state.webui_running:
            log_msg("⚠️ WebUI already running", VerbosityLevel.NORMAL)
            return True
            
        try:
            cmd = self.build_launch_command(webui_path, self.state.settings)
            
            log_msg("🚀 Starting WebUI process...", VerbosityLevel.NORMAL)
            log_msg(f"🔧 Command: {' '.join(cmd)}", VerbosityLevel.DETAILED)
            log_msg(f"🔧 Working directory: {webui_path}", VerbosityLevel.DETAILED)
            
            # Change to WebUI directory
            original_cwd = os.getcwd()
            os.chdir(webui_path)
            
            # Start process
            self.state.webui_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            
            self.state.webui_running = True
            self.state._update_status("🟡 Starting WebUI...", "orange")
            
            # Start monitoring in separate thread
            self.monitor_thread = threading.Thread(target=self._monitor_output, daemon=True)
            self.monitor_thread.start()
            
            os.chdir(original_cwd)
            return True
            
        except Exception as e:
            log_msg(f"❌ Failed to start WebUI: {e}", VerbosityLevel.MINIMAL)
            self.state._update_status(f"❌ Launch failed: {e}", "red")
            if 'original_cwd' in locals():
                os.chdir(original_cwd)
            return False
    
    def _monitor_output(self):
        """Monitor WebUI process output for URLs and status"""
        if not self.state.webui_process:
            return
            
        try:
            while self.state.webui_running and self.state.webui_process:
                line = self.state.webui_process.stdout.readline()
                if not line:
                    break
                    
                line = line.strip()
                if line:
                    # Look for local URL
                    if 'running on local url:' in line.lower():
                        url_part = line.split(':', 2)[-1].strip()
                        self.state.local_url = url_part
                        self.state._update_status(f"🟢 WebUI running: {url_part}", "green")
                        log_msg(f"🌐 Local URL detected: {url_part}", VerbosityLevel.NORMAL)
                        
                    # Look for public URL
                    elif 'running on public url:' in line.lower():
                        url_part = line.split(':', 2)[-1].strip()
                        self.state.public_url = url_part
                        log_msg(f"🌐 Public URL detected: {url_part}", VerbosityLevel.NORMAL)
                        
                    # Log errors and important messages
                    if any(keyword in line.lower() for keyword in ['error', 'failed', 'exception']):
                        log_msg(f"⚠️ {line}", VerbosityLevel.MINIMAL)
                    elif VERBOSITY_AVAILABLE and verbose_manager.verbosity_level >= VerbosityLevel.RAW:
                        print(line)
                        
        except Exception as e:
            log_msg(f"❌ Error monitoring output: {e}", VerbosityLevel.DETAILED)
        
        # Process ended
        if self.state.webui_process:
            exit_code = self.state.webui_process.poll()
            if exit_code is not None and exit_code != 0:
                log_msg(f"❌ WebUI process ended with error code: {exit_code}", VerbosityLevel.MINIMAL)
                self.state._update_status(f"❌ WebUI stopped (exit code: {exit_code})", "red")
        
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
            self.state._update_status("⏹️ WebUI stopped", "red")
            
            return True
            
        except Exception as e:
            log_msg(f"❌ Error stopping WebUI: {e}", VerbosityLevel.MINIMAL)
            return False

# --- LAUNCH WIDGET MANAGER (STYLED TO MATCH EXISTING SYSTEM) ---
class LaunchWidgetManager:
    """Manages the launch interface with consistent styling"""
    
    def __init__(self, state):
        self.factory = WidgetFactory()
        self.state = state
        self.widgets = {}
        
        self.settings_keys = [
            'auto_launch', 'public_link', 'optimize_system',
            'low_memory_mode', 'precision_mode', 'custom_args',
            'backup_before_launch'
        ]

    def build_ui(self):
        """Build launch interface matching existing widget styling"""
        log_msg("🎨 Building launch interface...", VerbosityLevel.DETAILED)
        
        # --- LAUNCH SETTINGS (Match existing toggle button style) ---
        self.widgets['auto_launch'] = widgets.ToggleButton(
            value=False, 
            description='Auto Launch', 
            button_style='',
            tooltip='Automatically launch WebUI after setup'
        )
        self.widgets['public_link'] = widgets.ToggleButton(
            value=True, 
            description='Public Link', 
            button_style='',
            tooltip='Create public Gradio link for external access'
        )
        self.widgets['optimize_system'] = widgets.ToggleButton(
            value=True, 
            description='Optimize System', 
            button_style='',
            tooltip='Apply system optimizations (xformers, etc.)'
        )
        self.widgets['low_memory_mode'] = widgets.ToggleButton(
            value=False, 
            description='Low Memory Mode', 
            button_style='',
            tooltip='Enable low RAM/VRAM optimizations'
        )
        
        # Precision dropdown (match existing dropdown style)
        self.widgets['precision_mode'] = self.factory.create_dropdown(
            options=['auto', 'fp16', 'fp32', 'bf16'],
            value='auto',
            description='Precision:'
        )
        
        # Backup checkbox
        self.widgets['backup_before_launch'] = self.factory.create_checkbox(
            value=True,
            description='Backup Settings Before Launch'
        )
        
        # Custom arguments textarea
        self.widgets['custom_args'] = self.factory.create_textarea(
            value='',
            description='Custom Arguments:',
            placeholder='Additional command line arguments...',
            rows=3
        )
        
        # --- LAYOUT SECTIONS (Match existing header-group style) ---
        left_toggles = self.factory.create_hbox([
            self.widgets['auto_launch'],
            self.widgets['public_link']
        ], class_names=['header-group'])
        
        right_toggles = self.factory.create_hbox([
            self.widgets['optimize_system'],
            self.widgets['low_memory_mode']
        ], class_names=['header-group'])
        
        # Main controls row
        controls_row = self.factory.create_hbox([
            left_toggles,
            self.widgets['precision_mode'],
            right_toggles
        ], class_names=['header-controls'])
        
        # Configuration section  
        config_section = self.factory.create_vbox([
            self.widgets['backup_before_launch'],
            self.widgets['custom_args']
        ])
        
        # --- ACTION BUTTONS (Match existing button styling) ---
        self.launch_button = self.factory.create_button(
            '🚀 Launch WebUI',
            button_style='success',
            class_names=['enhanced-button', 'button-success']
        )
        self.launch_button.on_click(self._on_launch_click)
        
        self.stop_button = self.factory.create_button(
            '⏹️ Stop WebUI',
            button_style='danger', 
            class_names=['enhanced-button', 'button-error']
        )
        self.stop_button.on_click(self._on_stop_click)
        
        self.restart_button = self.factory.create_button(
            '🔄 Restart WebUI',
            button_style='warning',
            class_names=['enhanced-button', 'button-warning']
        )
        self.restart_button.on_click(self._on_restart_click)
        
        # Button row (match existing layout)
        button_row = self.factory.create_hbox([
            self.launch_button, 
            self.stop_button, 
            self.restart_button
        ], class_names=['header-group'])
        
        # --- STATUS DISPLAY ---
        self.status_display = self.factory.create_html(
            '<div style="text-align: center; padding: 10px; font-weight: bold;">⏳ Ready to launch...</div>'
        )
        
        # Connect status display to global state
        self.state.status_widget = self.status_display
        
        # --- FINAL LAYOUT (Match existing structure) ---
        main_content = self.factory.create_vbox([
            self.factory.create_html('<h3 style="text-align: center; margin: 10px 0;">🚀 WebUI Launch Control</h3>'),
            controls_row,
            config_section,
            button_row,
            self.status_display
        ], class_names=['main-content'])
        
        return main_content

    def _on_launch_click(self, button):
        """Handle launch button click"""
        try:
            log_msg("🚀 Launch button clicked", VerbosityLevel.NORMAL)
            
            # Collect settings
            settings = {'LAUNCH': {}}
            for key in self.settings_keys:
                if key in self.widgets:
                    widget = self.widgets[key]
                    if hasattr(widget, 'value'):
                        settings['LAUNCH'][key] = widget.value
            
            # Backup settings if requested
            if self.widgets['backup_before_launch'].value:
                try:
                    js.save_settings(settings['LAUNCH'], section='LAUNCH')
                    log_msg("💾 Settings backed up", VerbosityLevel.DETAILED)
                except Exception as e:
                    log_msg(f"⚠️ Settings backup failed: {e}", VerbosityLevel.MINIMAL)
            
            # Request launch
            self.state.request_launch(settings)
            
        except Exception as e:
            log_msg(f"❌ Launch request failed: {e}", VerbosityLevel.MINIMAL)
            self.state._update_status(f"❌ Launch failed: {e}", "red")

    def _on_stop_click(self, button):
        """Handle stop button click"""
        log_msg("⏹️ Stop button clicked", VerbosityLevel.NORMAL)
        self.state.request_stop()

    def _on_restart_click(self, button):
        """Handle restart button click"""
        log_msg("🔄 Restart button clicked", VerbosityLevel.NORMAL)
        
        # Collect current settings
        settings = {'LAUNCH': {}}
        for key in self.settings_keys:
            if key in self.widgets:
                widget = self.widgets[key]
                if hasattr(widget, 'value'):
                    settings['LAUNCH'][key] = widget.value
        
        self.state.request_restart(settings)

# --- MAIN EXECUTION CONTROLLER ---
class LaunchExecutionController:
    """Controls the main execution loop and state management"""
    
    def __init__(self, state):
        self.state = state
        self.process_manager = WebUIProcessManager(state)
        self.running = True
        
    def run(self):
        """Main blocking execution loop"""
        log_msg("🔄 Entering main execution loop - cell will stay active", VerbosityLevel.NORMAL)
        log_msg("   Click Launch WebUI to start, or interrupt kernel to exit", VerbosityLevel.NORMAL)
        
        try:
            while self.running:
                with self.state.lock:
                    # Handle launch request
                    if self.state.launch_requested:
                        self.state.launch_requested = False
                        log_msg("🚀 Processing launch request...", VerbosityLevel.NORMAL)
                        self.process_manager.start_webui()
                    
                    # Handle stop request  
                    elif self.state.stop_requested:
                        self.state.stop_requested = False
                        log_msg("⏹️ Processing stop request...", VerbosityLevel.NORMAL)
                        self.process_manager.stop_webui()
                    
                    # Handle restart request
                    elif self.state.restart_requested:
                        self.state.restart_requested = False
                        log_msg("🔄 Processing restart request...", VerbosityLevel.NORMAL)
                        if self.state.webui_running:
                            self.process_manager.stop_webui()
                            time.sleep(2)  # Brief pause between stop and start
                        self.process_manager.start_webui()
                
                # Brief pause to prevent excessive CPU usage
                time.sleep(0.5)
                
        except KeyboardInterrupt:
            log_msg("🛑 Keyboard interrupt received", VerbosityLevel.NORMAL)
            if self.state.webui_running:
                log_msg("🔄 Stopping WebUI before exit...", VerbosityLevel.NORMAL)
                self.process_manager.stop_webui()
        except Exception as e:
            log_msg(f"❌ Execution controller error: {e}", VerbosityLevel.MINIMAL)
        finally:
            self.running = False
            log_msg("✅ Launch controller stopped", VerbosityLevel.NORMAL)

# --- MAIN EXECUTION ---
def main():
    """Main function that sets up and runs the launch system"""
    print("============================================================")
    print("🔥 LSDAI True Blocking Launch System")
    print("============================================================")
    
    # Check verbosity system
    if VERBOSITY_AVAILABLE:
        print(f"🔧 Verbosity system: Available (Level: {verbose_manager.get_current_level_name()})")
    else:
        print("🔧 Verbosity system: Using fallback")
    
    # Create UI
    try:
        widget_manager = LaunchWidgetManager(global_state)
        ui = widget_manager.build_ui()
        
        print("🎨 Launch interface created successfully")
        display(ui)
        
        print("✅ Enhanced Launch System ready!")
        
        # Start execution controller
        controller = LaunchExecutionController(global_state)
        controller.run()
        
    except Exception as e:
        print(f"❌ Failed to create launch interface: {e}")
        import traceback
        traceback.print_exc()

# Execute main function
if __name__ == "__main__":
    main()

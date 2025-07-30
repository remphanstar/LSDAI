# ~ enhanced_launch_integration.py | Complete Launch System with Proper Blocking ~

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
        
    def run_cmd(cmd, **kwargs):
        return vrun(cmd, **kwargs)
        
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
    
    def run_cmd(cmd, **kwargs):
        try:
            result = subprocess.run(cmd, check=True, text=True, capture_output=True, **kwargs)
            return result
        except subprocess.CalledProcessError as e:
            print(f"❌ Command failed: {' '.join(cmd)}")
            print(f"Error: {e}")
            raise

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
    class DummyOutput:
        @staticmethod
        def register_callback(name, func): pass
    output = DummyOutput()

# --- WEBUI PROCESS MANAGER ---
class WebUIProcessManager:
    """Manages WebUI subprocess with monitoring and control"""
    
    def __init__(self):
        self.process = None
        self.monitor_thread = None
        self.running = False
        self.webui_path = None
        self.public_url = None
        self.local_url = None
        self.urls_found = False
        
    def find_webui_installation(self):
        """Find installed WebUI directory"""
        base_path = Path(os.environ.get('home_path', '/content'))
        
        # Common WebUI installation paths
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
    
    def build_launch_command(self, settings):
        """Build WebUI launch command from settings"""
        if not self.webui_path:
            self.webui_path = self.find_webui_installation()
            
        if not self.webui_path:
            raise FileNotFoundError("No WebUI installation found")
            
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
        
        # Add arguments from widgets
        widget_settings = settings.get('LAUNCH', {})
        
        # Public link support
        if widget_settings.get('public_link', True):
            cmd.append('--share')
            
        # System optimization arguments
        if widget_settings.get('optimize_system', True):
            cmd.extend(['--xformers', '--no-half-vae'])
            
        # Memory optimization
        if widget_settings.get('low_memory_mode', False):
            cmd.extend(['--lowram', '--lowvram'])
            
        # Precision mode
        precision = widget_settings.get('precision_mode', 'auto')
        if precision != 'auto':
            if precision == 'fp16':
                cmd.append('--precision=half')
            elif precision == 'fp32':
                cmd.append('--precision=full')
            elif precision == 'bf16':
                cmd.append('--precision=autocast')
                
        # Custom arguments
        custom_args = widget_settings.get('custom_args', '').strip()
        if custom_args:
            try:
                custom_list = shlex.split(custom_args)
                cmd.extend(custom_list)
            except ValueError:
                log_msg(f"⚠️ Invalid custom arguments: {custom_args}", VerbosityLevel.MINIMAL)
                
        return cmd
    
    def start_webui(self, settings):
        """Start WebUI process with monitoring"""
        try:
            # Build launch command
            cmd = self.build_launch_command(settings)
            
            log_msg("🚀 Starting WebUI process...", VerbosityLevel.NORMAL)
            log_msg(f"🔧 Working directory: {self.webui_path}", VerbosityLevel.DETAILED)
            log_msg(f"🔧 Command: {' '.join(cmd)}", VerbosityLevel.DETAILED)
            
            # Start process
            self.process = subprocess.Popen(
                cmd,
                cwd=self.webui_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            
            self.running = True
            self.urls_found = False
            
            # Start monitoring thread
            self.monitor_thread = threading.Thread(target=self._monitor_process)
            self.monitor_thread.daemon = True
            self.monitor_thread.start()
            
            log_msg("✅ WebUI process started successfully", VerbosityLevel.NORMAL)
            log_msg(f"🔧 Process ID: {self.process.pid}", VerbosityLevel.DETAILED)
            
            return True
            
        except Exception as e:
            log_msg(f"❌ Failed to start WebUI: {e}", VerbosityLevel.MINIMAL)
            return False
    
    def _monitor_process(self):
        """Monitor WebUI process output and extract URLs"""
        log_msg("📊 Starting WebUI output monitoring...", VerbosityLevel.DETAILED)
        
        while self.running and self.process:
            try:
                line = self.process.stdout.readline()
                if not line:
                    break
                    
                line = line.strip()
                if line:
                    # Show output based on verbosity level or fallback
                    show_line = False
                    if VERBOSITY_AVAILABLE:
                        if verbose_manager.verbosity_level >= VerbosityLevel.RAW:
                            show_line = True
                        elif verbose_manager.verbosity_level >= VerbosityLevel.VERBOSE:
                            if any(keyword in line.lower() for keyword in 
                                   ['running on', 'local url', 'public url', 'model loaded', 'error', 'warning']):
                                show_line = True
                    else:
                        # Fallback: show important lines
                        if any(keyword in line.lower() for keyword in 
                               ['running on', 'local url', 'public url', 'error', 'warning']):
                            show_line = True
                    
                    if show_line:
                        print(line)
                    
                    # Extract URLs
                    if 'running on local url:' in line.lower():
                        self.local_url = line.split(':', 2)[-1].strip()
                        log_msg(f"🔗 Local URL: {self.local_url}", VerbosityLevel.NORMAL)
                        self.urls_found = True
                    elif 'running on public url:' in line.lower():
                        self.public_url = line.split(':', 2)[-1].strip()
                        log_msg(f"🌐 Public URL: {self.public_url}", VerbosityLevel.NORMAL)
                        self.urls_found = True
                        
            except Exception as e:
                log_msg(f"❌ Error monitoring process: {e}", VerbosityLevel.DETAILED)
                break
                
        # Process ended
        if self.process:
            exit_code = self.process.poll()
            if exit_code is not None:
                if exit_code == 0:
                    log_msg("✅ WebUI process ended normally", VerbosityLevel.NORMAL)
                else:
                    log_msg(f"❌ WebUI process ended with error code: {exit_code}", VerbosityLevel.MINIMAL)
        
        self.running = False
    
    def wait_for_urls(self, timeout=180):
        """Wait for URLs to be detected"""
        log_msg("⏳ Waiting for WebUI to initialize and generate URLs...", VerbosityLevel.NORMAL)
        
        waited = 0
        while waited < timeout and self.running:
            if self.urls_found:
                return True
            time.sleep(2)
            waited += 2
            
            # Show progress every 15 seconds
            if waited % 15 == 0:
                log_msg(f"   Still waiting... ({waited}s elapsed)", VerbosityLevel.NORMAL)
        
        return False
    
    def stop_webui(self):
        """Stop WebUI process"""
        if not self.process or not self.running:
            log_msg("⚠️ No WebUI process running", VerbosityLevel.NORMAL)
            return True
            
        log_msg("⏹️ Stopping WebUI process...", VerbosityLevel.NORMAL)
        
        try:
            # Graceful termination
            self.running = False
            self.process.terminate()
            
            # Wait for termination
            try:
                self.process.wait(timeout=10)
                log_msg("✅ WebUI stopped gracefully", VerbosityLevel.NORMAL)
            except subprocess.TimeoutExpired:
                # Force kill if necessary
                log_msg("🔨 Force killing WebUI process...", VerbosityLevel.DETAILED)
                self.process.kill()
                self.process.wait()
                log_msg("✅ WebUI process killed", VerbosityLevel.NORMAL)
                
            self.process = None
            self.local_url = None
            self.public_url = None
            self.urls_found = False
            
            return True
            
        except Exception as e:
            log_msg(f"❌ Error stopping WebUI: {e}", VerbosityLevel.MINIMAL)
            return False
    
    def get_status(self):
        """Get current WebUI status"""
        if not self.process:
            return "stopped"
        elif self.process.poll() is None:
            return "running"
        else:
            return "crashed"

# --- LAUNCH WIDGET MANAGER ---
class LaunchWidgetManager:
    """Manages the launch interface with system optimizations and monitoring."""
    
    def __init__(self):
        self.factory = WidgetFactory()
        self.widgets = {}
        self.selection_containers = {}
        self.webui_manager = WebUIProcessManager()
        
        # Define widget keys for settings persistence
        self.settings_keys = [
            'auto_launch', 'public_link', 'ngrok_tunnel', 'optimize_system',
            'low_memory_mode', 'precision_mode', 'custom_args',
            'monitor_performance', 'auto_restart', 'backup_before_launch'
        ]

    def build_ui(self):
        """Build complete launch interface."""
        log_msg("🎨 Building enhanced launch interface...", VerbosityLevel.DETAILED)
        
        # --- HEADER CONTROLS ---
        self.widgets['auto_launch'] = widgets.ToggleButton(value=False, description='Auto Launch', button_style='')
        self.widgets['public_link'] = widgets.ToggleButton(value=True, description='Public Link', button_style='')
        self.widgets['ngrok_tunnel'] = widgets.ToggleButton(value=False, description='Ngrok Tunnel', button_style='')
        self.widgets['optimize_system'] = widgets.ToggleButton(value=True, description='Optimize System', button_style='')
        
        # System optimization toggles
        self.widgets['low_memory_mode'] = widgets.ToggleButton(value=False, description='Low Memory Mode', button_style='')
        self.widgets['precision_mode'] = self.factory.create_dropdown(
            options=['auto', 'fp16', 'fp32', 'bf16'],
            value='auto',
            description='Precision:'
        )
        
        # Monitoring and safety features
        self.widgets['monitor_performance'] = widgets.ToggleButton(value=True, description='Monitor Performance', button_style='')
        self.widgets['auto_restart'] = widgets.ToggleButton(value=False, description='Auto Restart on Crash', button_style='')
        
        # FIXED: Use proper widget attribute access with checkbox factory method
        self.widgets['backup_before_launch'] = self.factory.create_checkbox(
            value=True,
            description='Backup Settings Before Launch'
        )
        
        # Custom arguments
        self.widgets['custom_args'] = self.factory.create_textarea(
            value='',
            description='Custom Arguments:',
            placeholder='Additional command line arguments...'
        )
        
        # Header layout
        header_left = self.factory.create_vbox([
            self.widgets['auto_launch'],
            self.widgets['public_link'], 
            self.widgets['ngrok_tunnel']
        ], class_names=['launch-options'])
        
        header_right = self.factory.create_vbox([
            self.widgets['optimize_system'],
            self.widgets['low_memory_mode'],
            self.widgets['monitor_performance']
        ], class_names=['system-options'])
        
        header_controls = self.factory.create_hbox([header_left, header_right], class_names=['header-controls'])

        # --- SYSTEM CONFIGURATION ---
        system_config = self.factory.create_vbox([
            self.factory.create_hbox([
                self.widgets['precision_mode'], 
                self.widgets['auto_restart']
            ]),
            self.widgets['backup_before_launch'],
            self.widgets['custom_args']
        ], class_names=['system-config'])

        # --- LAUNCH BUTTONS ---
        launch_button = self.factory.create_button('🚀 Launch WebUI', class_names=['button', 'button_launch'], button_style='success')
        launch_button.on_click(self.launch_webui)
        
        stop_button = self.factory.create_button('⏹️ Stop WebUI', class_names=['button', 'button_stop'], button_style='danger')
        stop_button.on_click(self.stop_webui)
        
        restart_button = self.factory.create_button('🔄 Restart WebUI', class_names=['button', 'button_restart'], button_style='warning')
        restart_button.on_click(self.restart_webui)
        
        button_row = self.factory.create_hbox([launch_button, stop_button, restart_button], class_names=['launch-buttons'])

        # --- STATUS AND MONITORING ---
        self.status_display = self.factory.create_html('<div class="status-display">⏳ Ready to launch...</div>')
        
        # Performance monitoring output
        self.performance_monitor = self.factory.create_output()
        
        monitoring_section = self.factory.create_vbox([
            self.status_display,
            self.performance_monitor
        ], class_names=['monitoring-section'])

        # --- FINAL LAYOUT ---
        main_content = self.factory.create_vbox([
            header_controls, 
            system_config,
            button_row,
            monitoring_section
        ], class_names=['main-content'])
        
        return main_content

    def setup_callbacks(self):
        """Connect widget events to their handler functions."""
        log_msg("🔧 Setting up widget callbacks...", VerbosityLevel.DETAILED)
        
        # Auto-load settings
        self.load_settings()
            
        log_msg("✅ Widget callbacks configured", VerbosityLevel.DETAILED)

    # --- CORE LAUNCH FUNCTIONALITY ---
    def launch_webui(self, button):
        """Launch WebUI with complete process management and monitoring."""
        try:
            log_msg("🚀 Initiating WebUI launch sequence...", VerbosityLevel.NORMAL)
            
            # Update status
            self.status_display.value = '<div class="status-display starting">🚀 Starting WebUI...</div>'
            
            # Backup settings if requested
            # FIXED: Use .value instead of .get() for widget access
            if hasattr(self.widgets['backup_before_launch'], 'value') and self.widgets['backup_before_launch'].value:
                log_msg("💾 Backing up settings before launch...", VerbosityLevel.DETAILED)
                self.save_settings()
            
            # Load current settings
            settings = js.load_settings()
            if not settings:
                settings = {'LAUNCH': {}}
                
            # Add current widget values to settings
            launch_settings = {}
            for key in self.settings_keys:
                if key in self.widgets and hasattr(self.widgets[key], 'value'):
                    launch_settings[key] = self.widgets[key].value
                    
            settings['LAUNCH'] = launch_settings
            
            # Start WebUI process
            success = self.webui_manager.start_webui(settings)
            
            if success:
                self.status_display.value = '<div class="status-display starting">⏳ WebUI initializing...</div>'
                
                # Wait for URLs to be detected - THIS IS THE KEY BLOCKING CALL
                if self.webui_manager.wait_for_urls():
                    # URLs found - display them
                    status_html = f'''
                    <div class="status-display running">
                        ✅ WebUI Running<br>
                    '''
                    
                    if self.webui_manager.local_url:
                        status_html += f'🔗 <a href="{self.webui_manager.local_url}" target="_blank">Local URL</a><br>'
                    
                    if self.webui_manager.public_url:
                        status_html += f'🌐 <a href="{self.webui_manager.public_url}" target="_blank">Public URL</a><br>'
                    
                    status_html += '</div>'
                    self.status_display.value = status_html
                    
                    log_msg("✅ WebUI launched successfully!", VerbosityLevel.NORMAL)
                    
                    # NOW KEEP THE CELL RUNNING - Monitor continuously
                    self.monitor_webui_continuous()
                    
                else:
                    # Timeout waiting for URLs
                    self.status_display.value = '<div class="status-display warning">⚠️ WebUI startup timeout</div>'
                    log_msg("⚠️ WebUI startup took longer than expected, but may still be running", VerbosityLevel.NORMAL)
                    
                    # Still monitor even if URLs not detected
                    self.monitor_webui_continuous()
                
            else:
                self.status_display.value = '<div class="status-display error">❌ Launch Failed</div>'
                log_msg("❌ Failed to start WebUI. Check console for details.", VerbosityLevel.MINIMAL)
                
        except Exception as e:
            log_msg(f"❌ Launch failed: {e}", VerbosityLevel.MINIMAL)
            self.status_display.value = '<div class="status-display error">❌ Launch Failed</div>'

    def monitor_webui_continuous(self):
        """Continuously monitor WebUI and keep cell running"""
        log_msg("🔄 Entering continuous monitoring mode...", VerbosityLevel.NORMAL)
        log_msg("   WebUI is running. Use Stop button or interrupt kernel to stop.", VerbosityLevel.NORMAL)
        
        try:
            while self.webui_manager.running and self.webui_manager.process:
                # Check if process is still alive
                status = self.webui_manager.get_status()
                
                if status == "crashed":
                    self.status_display.value = '<div class="status-display error">❌ WebUI Crashed</div>'
                    log_msg("❌ WebUI process crashed", VerbosityLevel.MINIMAL)
                    break
                elif status == "stopped":
                    self.status_display.value = '<div class="status-display stopped">⏹️ WebUI Stopped</div>'
                    log_msg("⏹️ WebUI process stopped", VerbosityLevel.NORMAL)
                    break
                
                # Update status with current URLs if available
                if self.webui_manager.local_url or self.webui_manager.public_url:
                    status_html = f'''
                    <div class="status-display running">
                        ✅ WebUI Running (PID: {self.webui_manager.process.pid})<br>
                    '''
                    
                    if self.webui_manager.local_url:
                        status_html += f'🔗 <a href="{self.webui_manager.local_url}" target="_blank">Local URL</a><br>'
                    
                    if self.webui_manager.public_url:
                        status_html += f'🌐 <a href="{self.webui_manager.public_url}" target="_blank">Public URL</a><br>'
                    
                    status_html += f'<small>Running for {int(time.time() - getattr(self, "start_time", time.time()))}s</small></div>'
                    self.status_display.value = status_html
                
                # Sleep and continue monitoring
                time.sleep(10)  # Check every 10 seconds
                
        except KeyboardInterrupt:
            log_msg("🛑 User interrupted monitoring", VerbosityLevel.NORMAL)
            self.stop_webui(None)
        except Exception as e:
            log_msg(f"❌ Monitoring error: {e}", VerbosityLevel.MINIMAL)
        
        log_msg("🏁 Monitoring ended", VerbosityLevel.NORMAL)

    def stop_webui(self, button):
        """Stop the running WebUI."""
        try:
            log_msg("⏹️ Stopping WebUI...", VerbosityLevel.NORMAL)
            self.status_display.value = '<div class="status-display stopping">⏹️ Stopping WebUI...</div>'
            
            success = self.webui_manager.stop_webui()
            
            if success:
                self.status_display.value = '<div class="status-display stopped">⏹️ WebUI Stopped</div>'
                log_msg("✅ WebUI stopped successfully!", VerbosityLevel.NORMAL)
            else:
                self.status_display.value = '<div class="status-display error">❌ Stop Failed</div>'
                log_msg("❌ Failed to stop WebUI", VerbosityLevel.MINIMAL)
                
        except Exception as e:
            log_msg(f"❌ Stop failed: {e}", VerbosityLevel.MINIMAL)

    def restart_webui(self, button):
        """Restart the WebUI."""
        try:
            log_msg("🔄 Restarting WebUI...", VerbosityLevel.NORMAL)
            self.status_display.value = '<div class="status-display restarting">🔄 Restarting WebUI...</div>'
            
            # Stop current process
            self.webui_manager.stop_webui()
            time.sleep(2)
            
            # Restart
            self.launch_webui(button)
                
        except Exception as e:
            log_msg(f"❌ Restart failed: {e}", VerbosityLevel.MINIMAL)

    def save_settings(self):
        """Save all widget data to settings."""
        try:
            data = {}
            
            # Add all widget values using proper attribute access
            for key in self.settings_keys:
                if key in self.widgets:
                    widget = self.widgets[key]
                    if hasattr(widget, 'value'):
                        data[key] = widget.value
            
            # Save to settings
            js.save_settings(data, section='LAUNCH')
            log_msg("💾 Launch settings saved", VerbosityLevel.DETAILED)
            
        except Exception as e:
            log_msg(f"❌ Error saving launch settings: {e}", VerbosityLevel.MINIMAL)

    def load_settings(self):
        """Load settings from file."""
        try:
            settings = js.load_settings(section='LAUNCH')
            if settings:
                self.apply_settings(settings)
                log_msg("📂 Launch settings loaded", VerbosityLevel.DETAILED)
        except Exception as e:
            log_msg(f"❌ Error loading launch settings: {e}", VerbosityLevel.DETAILED)

    def apply_settings(self, settings):
        """Apply loaded settings to widgets."""
        # Apply to widgets using proper attribute access
        for key in self.settings_keys:
            if key in settings and key in self.widgets:
                try:
                    if hasattr(self.widgets[key], 'value'):
                        self.widgets[key].value = settings[key]
                except Exception as e:
                    log_msg(f"Warning: Could not apply setting {key}: {e}", VerbosityLevel.VERBOSE)

# --- EXECUTION ---
if __name__ == "__main__":
    log_msg("=" * 60, VerbosityLevel.NORMAL)
    log_msg("🔥 LSDAI Enhanced Launch System (Blocking Version)", VerbosityLevel.NORMAL)
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
    manager = LaunchWidgetManager()
    main_container = manager.build_ui()
    
    log_msg("🎨 Launch interface created successfully", VerbosityLevel.NORMAL)
    
    display(main_container)
    
    # Setup callbacks after display
    manager.setup_callbacks()
    
    # Record start time for monitoring
    manager.start_time = time.time()
    
    log_msg("✅ Enhanced Launch System ready!", VerbosityLevel.NORMAL)
    log_msg("   Click 'Launch WebUI' to start. Cell will stay running to monitor WebUI.", VerbosityLevel.NORMAL)
    
    # If auto-launch is enabled, start immediately
    try:
        settings = js.load_settings(section='LAUNCH')
        if settings and settings.get('auto_launch', False):
            log_msg("🚀 Auto-launch enabled, starting WebUI...", VerbosityLevel.NORMAL)
            manager.launch_webui(None)
    except:
        pass  # Auto-launch failed, ignore

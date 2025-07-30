# ~ enhanced_launch_integration.py | Complete Launch System with Verbosity Integration ~

from modules.widget_factory import WidgetFactory
from modules.webui_utils import update_current_webui
from modules import json_utils as js

# CRITICAL: Import verbosity system for complete integration
from modules.verbose_output_manager import (
    get_verbose_manager, VerbosityLevel, 
    vprint, vrun
)

from IPython.display import display, Javascript, HTML
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
        self.verbose_manager = get_verbose_manager()
        self.webui_path = None
        self.public_url = None
        self.local_url = None
        
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
                vprint(f"✅ Found WebUI installation: {path}", VerbosityLevel.DETAILED)
                return path
                
        vprint("❌ No WebUI installation found", VerbosityLevel.MINIMAL)
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
            # Parse custom arguments safely
            try:
                custom_list = shlex.split(custom_args)
                cmd.extend(custom_list)
            except ValueError:
                vprint(f"⚠️ Invalid custom arguments: {custom_args}", VerbosityLevel.MINIMAL)
                
        # Add verbosity flags based on current level
        if self.verbose_manager.verbosity_level >= VerbosityLevel.VERBOSE:
            cmd.append('--debug')
            
        return cmd
    
    def start_webui(self, settings):
        """Start WebUI process with monitoring"""
        try:
            # Build launch command
            cmd = self.build_launch_command(settings)
            
            vprint("🚀 Starting WebUI process...", VerbosityLevel.NORMAL)
            vprint(f"🔧 Working directory: {self.webui_path}", VerbosityLevel.DETAILED)
            vprint(f"🔧 Command: {' '.join(cmd)}", VerbosityLevel.DETAILED)
            
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
            
            # Start monitoring thread
            self.monitor_thread = threading.Thread(target=self._monitor_process)
            self.monitor_thread.daemon = True
            self.monitor_thread.start()
            
            vprint("✅ WebUI process started successfully", VerbosityLevel.NORMAL)
            vprint(f"🔧 Process ID: {self.process.pid}", VerbosityLevel.DETAILED)
            
            return True
            
        except Exception as e:
            vprint(f"❌ Failed to start WebUI: {e}", VerbosityLevel.MINIMAL)
            return False
    
    def _monitor_process(self):
        """Monitor WebUI process output and extract URLs"""
        vprint("📊 Starting WebUI output monitoring...", VerbosityLevel.DETAILED)
        
        while self.running and self.process:
            try:
                line = self.process.stdout.readline()
                if not line:
                    break
                    
                line = line.strip()
                if line:
                    # Show output based on verbosity level
                    if self.verbose_manager.verbosity_level >= VerbosityLevel.RAW:
                        print(line)
                    elif self.verbose_manager.verbosity_level >= VerbosityLevel.VERBOSE:
                        # Show important lines
                        if any(keyword in line.lower() for keyword in 
                               ['running on', 'local url', 'public url', 'model loaded', 'error', 'warning']):
                            print(line)
                    
                    # Extract URLs
                    if 'running on local url:' in line.lower():
                        self.local_url = line.split(':', 2)[-1].strip()
                        vprint(f"🔗 Local URL: {self.local_url}", VerbosityLevel.NORMAL)
                    elif 'running on public url:' in line.lower():
                        self.public_url = line.split(':', 2)[-1].strip()
                        vprint(f"🌐 Public URL: {self.public_url}", VerbosityLevel.NORMAL)
                        
            except Exception as e:
                vprint(f"❌ Error monitoring process: {e}", VerbosityLevel.DETAILED)
                break
                
        # Process ended
        if self.process:
            exit_code = self.process.poll()
            if exit_code is not None:
                if exit_code == 0:
                    vprint("✅ WebUI process ended normally", VerbosityLevel.NORMAL)
                else:
                    vprint(f"❌ WebUI process ended with error code: {exit_code}", VerbosityLevel.MINIMAL)
        
        self.running = False
    
    def stop_webui(self):
        """Stop WebUI process"""
        if not self.process or not self.running:
            vprint("⚠️ No WebUI process running", VerbosityLevel.NORMAL)
            return True
            
        vprint("⏹️ Stopping WebUI process...", VerbosityLevel.NORMAL)
        
        try:
            # Graceful termination
            self.running = False
            self.process.terminate()
            
            # Wait for termination
            try:
                self.process.wait(timeout=10)
                vprint("✅ WebUI stopped gracefully", VerbosityLevel.NORMAL)
            except subprocess.TimeoutExpired:
                # Force kill if necessary
                vprint("🔨 Force killing WebUI process...", VerbosityLevel.DETAILED)
                self.process.kill()
                self.process.wait()
                vprint("✅ WebUI process killed", VerbosityLevel.NORMAL)
                
            self.process = None
            self.local_url = None
            self.public_url = None
            
            return True
            
        except Exception as e:
            vprint(f"❌ Error stopping WebUI: {e}", VerbosityLevel.MINIMAL)
            return False
    
    def restart_webui(self, settings):
        """Restart WebUI process"""
        vprint("🔄 Restarting WebUI...", VerbosityLevel.NORMAL)
        
        # Stop current process
        if not self.stop_webui():
            return False
            
        # Wait a moment
        time.sleep(2)
        
        # Start again
        return self.start_webui(settings)
    
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
        self.verbose_manager = get_verbose_manager()
        
        # Define widget keys for settings persistence
        self.settings_keys = [
            'auto_launch', 'public_link', 'ngrok_tunnel', 'optimize_system',
            'low_memory_mode', 'precision_mode', 'custom_args',
            'monitor_performance', 'auto_restart', 'backup_before_launch'
        ]
        
        # WebUI command line argument templates
        self.WEBUI_SELECTION = {
            'A1111':   "--xformers --no-half-vae --share --lowram",
            'ComfyUI': "--dont-print-server",
            'Forge':   "--xformers --cuda-stream --pin-shared-memory",
            'Classic': "--persistent-patches --cuda-stream --pin-shared-memory",
            'ReForge': "--xformers --cuda-stream --pin-shared-memory",
            'SD-UX':   "--xformers --no-half-vae"
        }

    def read_model_data(self, file_path, data_type):
        """Read model data from the models data file."""
        try:
            with open(file_path, 'r') as file:
                exec(file.read(), globals())
                
            data_map = {
                'model': globals().get('model_list', {}),
                'vae': globals().get('vae_list', {}),
                'lora': globals().get('lora_list', {}),
                'cnet': globals().get('controlnet_list', {})
            }
            
            return data_map.get(data_type, {})
        except Exception as e:
            vprint(f"Error reading model data: {e}", VerbosityLevel.DETAILED)
            return {}

    def build_ui(self):
        """Build complete launch interface."""
        vprint("🎨 Building enhanced launch interface...", VerbosityLevel.DETAILED)
        
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
        
        # FIXED: Use proper widget attribute access
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

        # --- WEBUI SELECTION TABS ---
        webui_tabs = []
        webui_names = list(self.WEBUI_SELECTION.keys())
        
        for webui_name in webui_names:
            webui_content = self.factory.create_html(f"""
                <div class="webui-tab-content">
                    <h4>{webui_name} WebUI</h4>
                    <p>Default arguments: <code>{self.WEBUI_SELECTION[webui_name]}</code></p>
                </div>
            """)
            webui_tabs.append(webui_content)
        
        tab_widget = widgets.Tab()
        tab_widget.children = webui_tabs
        for i, name in enumerate(webui_names):
            tab_widget.set_title(i, name)

        # --- CONFIGURATION ACCORDION ---
        # Launch Configuration
        launch_config_vbox = self.factory.create_vbox([
            self.factory.create_html("<h4>🚀 Launch Configuration</h4>"),
            system_config
        ])

        # Custom Download / Empowerment  
        # FIXED: Proper parameter order for empowerment checkbox
        self.widgets['empowerment'] = self.factory.create_checkbox(
            value=False,
            description='Empowerment Mode'
        )
        self.widgets['empowerment_output'] = self.factory.create_textarea(
            value='',
            description='Use special tags like $ckpt, $lora, etc.'
        )
        self.widgets['Model_url'] = self.factory.create_text(description='Model URL:')
        self.widgets['Vae_url'] = self.factory.create_text(description='Vae URL:')
        self.widgets['LoRA_url'] = self.factory.create_text(description='LoRA URL:')
        self.widgets['Embedding_url'] = self.factory.create_text(description='Embedding URL:')
        self.widgets['Extensions_url'] = self.factory.create_text(description='Extensions URL:')
        self.widgets['ADetailer_url'] = self.factory.create_text(description='ADetailer URL:')
        self.widgets['custom_file_urls'] = self.factory.create_text(description='File (txt):')
        
        self.custom_dl_container = self.factory.create_vbox([
            self.widgets['Model_url'], self.widgets['Vae_url'], self.widgets['LoRA_url'],
            self.widgets['Embedding_url'], self.widgets['Extensions_url'], self.widgets['ADetailer_url'],
            self.widgets['custom_file_urls']
        ])
        custom_dl_vbox = self.factory.create_vbox([
            self.widgets['empowerment'], self.widgets['empowerment_output'], self.custom_dl_container
        ])
        
        accordion = widgets.Accordion(children=[launch_config_vbox, custom_dl_vbox])
        accordion.set_title(0, 'Launch Configuration & API Tokens')
        accordion.set_title(1, 'Custom Download / Empowerment')
        accordion.selected_index = None
        accordion.add_class('trimmed-box')

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

        # --- SIDEBAR FOR QUICK ACTIONS ---
        BTN_STYLE = {'width': '48px', 'height': '48px'}
        
        self.quick_launch_button = self.factory.create_button('⚡', layout=BTN_STYLE, class_names=['side-button'])
        self.quick_launch_button.tooltip = "Quick Launch with Default Settings"
        self.quick_launch_button.on_click(self.quick_launch)
        
        self.settings_button = self.factory.create_button('⚙️', layout=BTN_STYLE, class_names=['side-button'])
        self.settings_button.tooltip = "Open Settings"
        self.settings_button.on_click(self.open_settings)
        
        self.logs_button = self.factory.create_button('📋', layout=BTN_STYLE, class_names=['side-button'])
        self.logs_button.tooltip = "View Logs"
        self.logs_button.on_click(self.view_logs)

        self.notification_popup = self.factory.create_html('', class_names=['notification-popup', 'hidden'])
        
        sidebar = self.factory.create_vbox([
            self.quick_launch_button, 
            self.settings_button, 
            self.logs_button, 
            self.notification_popup
        ], class_names=['sidebar'])
        
        if not IN_COLAB:
            sidebar.layout.display = 'none'

        # --- FINAL LAYOUT ---
        main_content = self.factory.create_vbox([
            header_controls, 
            system_config,
            tab_widget, 
            accordion, 
            button_row,
            monitoring_section
        ], class_names=['main-content'])
        
        return self.factory.create_hbox([main_content, sidebar], class_names=['main-ui-container'])

    def setup_callbacks(self):
        """Connect widget events to their handler functions with verbosity integration."""
        vprint("🔧 Setting up widget callbacks...", VerbosityLevel.DETAILED)
        
        # Auto-load settings
        self.load_settings()
        
        # Start monitoring thread if needed
        if hasattr(self.widgets, 'monitor_performance') and self.widgets['monitor_performance'].value:
            self.start_performance_monitoring()
            
        vprint("✅ Widget callbacks configured", VerbosityLevel.DETAILED)

    # --- CORE LAUNCH FUNCTIONALITY ---
    def launch_webui(self, button):
        """Launch WebUI with complete process management and monitoring."""
        try:
            vprint("🚀 Initiating WebUI launch sequence...", VerbosityLevel.NORMAL)
            
            # Update status
            self.status_display.value = '<div class="status-display starting">🚀 Starting WebUI...</div>'
            
            # Backup settings if requested
            # FIXED: Use .value instead of .get() for widget access
            if hasattr(self.widgets['backup_before_launch'], 'value') and self.widgets['backup_before_launch'].value:
                vprint("💾 Backing up settings before launch...", VerbosityLevel.DETAILED)
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
                self.show_notification("WebUI starting up... This may take 1-2 minutes", "info")
                
                # Wait for URLs to be detected
                self.wait_for_webui_ready()
                
            else:
                self.status_display.value = '<div class="status-display error">❌ Launch Failed</div>'
                self.show_notification("Failed to start WebUI. Check console for details.", "error")
                
        except Exception as e:
            vprint(f"❌ Launch failed: {e}", VerbosityLevel.MINIMAL)
            self.show_notification(f"Launch failed: {e}", "error")
            self.status_display.value = '<div class="status-display error">❌ Launch Failed</div>'

    def wait_for_webui_ready(self):
        """Wait for WebUI to be ready and display URLs"""
        def check_ready():
            max_wait = 120  # 2 minutes
            waited = 0
            
            while waited < max_wait and self.webui_manager.running:
                status = self.webui_manager.get_status()
                
                if status == "crashed":
                    self.status_display.value = '<div class="status-display error">❌ WebUI Crashed</div>'
                    self.show_notification("WebUI crashed during startup", "error")
                    return
                
                # Check if we have URLs
                if self.webui_manager.local_url:
                    # WebUI is ready
                    status_html = f'''
                    <div class="status-display running">
                        ✅ WebUI Running<br>
                        🔗 <a href="{self.webui_manager.local_url}" target="_blank">Local URL</a>
                    '''
                    
                    if self.webui_manager.public_url:
                        status_html += f'<br>🌐 <a href="{self.webui_manager.public_url}" target="_blank">Public URL</a>'
                    
                    status_html += '</div>'
                    self.status_display.value = status_html
                    
                    self.show_notification("WebUI launched successfully!", "success")
                    
                    # Start performance monitoring if enabled
                    if hasattr(self.widgets['monitor_performance'], 'value') and self.widgets['monitor_performance'].value:
                        self.start_performance_monitoring()
                    
                    return
                
                time.sleep(2)
                waited += 2
            
            # Timeout
            if waited >= max_wait:
                self.status_display.value = '<div class="status-display warning">⚠️ WebUI startup timeout</div>'
                self.show_notification("WebUI startup took longer than expected", "warning")
        
        # Run check in background thread
        check_thread = threading.Thread(target=check_ready)
        check_thread.daemon = True
        check_thread.start()

    def stop_webui(self, button):
        """Stop the running WebUI."""
        try:
            vprint("⏹️ Stopping WebUI...", VerbosityLevel.NORMAL)
            self.status_display.value = '<div class="status-display stopping">⏹️ Stopping WebUI...</div>'
            
            success = self.webui_manager.stop_webui()
            
            if success:
                self.status_display.value = '<div class="status-display stopped">⏹️ WebUI Stopped</div>'
                self.show_notification("WebUI stopped successfully!", "success")
            else:
                self.status_display.value = '<div class="status-display error">❌ Stop Failed</div>'
                self.show_notification("Failed to stop WebUI", "error")
                
        except Exception as e:
            vprint(f"❌ Stop failed: {e}", VerbosityLevel.MINIMAL)
            self.show_notification(f"Stop failed: {e}", "error")

    def restart_webui(self, button):
        """Restart the WebUI."""
        try:
            vprint("🔄 Restarting WebUI...", VerbosityLevel.NORMAL)
            self.status_display.value = '<div class="status-display restarting">🔄 Restarting WebUI...</div>'
            
            # Load current settings
            settings = js.load_settings()
            if not settings:
                settings = {'LAUNCH': {}}
            
            success = self.webui_manager.restart_webui(settings)
            
            if success:
                self.show_notification("WebUI restarted successfully!", "success")
                self.wait_for_webui_ready()
            else:
                self.status_display.value = '<div class="status-display error">❌ Restart Failed</div>'
                self.show_notification("Failed to restart WebUI", "error")
                
        except Exception as e:
            vprint(f"❌ Restart failed: {e}", VerbosityLevel.MINIMAL)
            self.show_notification(f"Restart failed: {e}", "error")

    def quick_launch(self, button):
        """Quick launch with default optimized settings."""
        try:
            vprint("⚡ Quick launching with optimized settings...", VerbosityLevel.NORMAL)
            
            # Set optimal defaults
            if 'optimize_system' in self.widgets:
                self.widgets['optimize_system'].value = True
            if 'public_link' in self.widgets:
                self.widgets['public_link'].value = True
            if 'monitor_performance' in self.widgets:
                self.widgets['monitor_performance'].value = True
            
            self.show_notification("Quick launching with optimized settings...", "info")
            self.launch_webui(button)
            
        except Exception as e:
            vprint(f"❌ Quick launch failed: {e}", VerbosityLevel.MINIMAL)
            self.show_notification(f"Quick launch failed: {e}", "error")

    def start_performance_monitoring(self):
        """Start performance monitoring display"""
        def monitor_performance():
            while self.webui_manager.running:
                try:
                    import psutil
                    
                    # Get system stats
                    cpu_percent = psutil.cpu_percent(interval=1)
                    memory = psutil.virtual_memory()
                    
                    # GPU stats if available
                    gpu_info = "N/A"
                    try:
                        import GPUtil
                        gpus = GPUtil.getGPUs()
                        if gpus:
                            gpu = gpus[0]
                            gpu_info = f"{gpu.load*100:.1f}% ({gpu.memoryUsed}MB/{gpu.memoryTotal}MB)"
                    except:
                        pass
                    
                    # Update performance display
                    with self.performance_monitor:
                        perf_html = f"""
                        <div style="font-family: monospace; font-size: 12px; background: #f0f0f0; padding: 10px; border-radius: 5px;">
                            <strong>🖥️ System Performance</strong><br>
                            CPU: {cpu_percent:.1f}% | RAM: {memory.percent:.1f}% ({memory.used//1024//1024}MB/{memory.total//1024//1024}MB)<br>
                            GPU: {gpu_info}<br>
                            WebUI Status: {self.webui_manager.get_status().title()}
                        </div>
                        """
                        self.performance_monitor.clear_output(wait=True)
                        display(HTML(perf_html))
                    
                    time.sleep(5)
                    
                except Exception as e:
                    vprint(f"Performance monitoring error: {e}", VerbosityLevel.VERBOSE)
                    break
        
        monitor_thread = threading.Thread(target=monitor_performance)
        monitor_thread.daemon = True
        monitor_thread.start()

    def open_settings(self, button):
        """Open settings management interface."""
        self.show_notification("Settings interface coming soon!", "info")

    def view_logs(self, button):
        """Open log viewer interface."""
        self.show_notification("Log viewer coming soon!", "info")

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
            vprint("💾 Launch settings saved", VerbosityLevel.DETAILED)
            
        except Exception as e:
            vprint(f"❌ Error saving launch settings: {e}", VerbosityLevel.MINIMAL)

    def load_settings(self):
        """Load settings from file."""
        try:
            settings = js.load_settings(section='LAUNCH')
            if settings:
                self.apply_settings(settings)
                vprint("📂 Launch settings loaded", VerbosityLevel.DETAILED)
        except Exception as e:
            vprint(f"❌ Error loading launch settings: {e}", VerbosityLevel.DETAILED)

    def apply_settings(self, settings):
        """Apply loaded settings to widgets."""
        # Apply to widgets using proper attribute access
        for key in self.settings_keys:
            if key in settings and key in self.widgets:
                try:
                    if hasattr(self.widgets[key], 'value'):
                        self.widgets[key].value = settings[key]
                except Exception as e:
                    vprint(f"Warning: Could not apply setting {key}: {e}", VerbosityLevel.VERBOSE)

    def show_notification(self, message, type_="info"):
        """Show a notification popup."""
        if hasattr(self, 'notification_popup') and self.notification_popup:
            icons = {'success': '✅', 'error': '❌', 'warning': '⚠️', 'info': 'ℹ️'}
            icon = icons.get(type_, 'ℹ️')
            
            self.notification_popup.value = f'''
                <div class="notification {type_}" style="
                    background: {'#d4edda' if type_=='success' else '#f8d7da' if type_=='error' else '#fff3cd' if type_=='warning' else '#d1ecf1'};
                    border: 1px solid {'#c3e6cb' if type_=='success' else '#f5c6cb' if type_=='error' else '#faeeba' if type_=='warning' else '#bee5eb'};
                    color: {'#155724' if type_=='success' else '#721c24' if type_=='error' else '#856404' if type_=='warning' else '#0c5460'};
                    padding: 10px;
                    border-radius: 5px;
                    margin: 5px 0;
                ">
                    <span class="icon">{icon}</span> {message}
                </div>
            '''
            
            # Auto-hide after 5 seconds for non-error messages
            if type_ != 'error':
                def hide_notification():
                    time.sleep(5)
                    self.notification_popup.value = ''
                
                hide_thread = threading.Thread(target=hide_notification)
                hide_thread.daemon = True
                hide_thread.start()

# --- EXECUTION ---
if __name__ == "__main__":
    # Initialize verbosity system
    verbose_manager = get_verbose_manager()
    
    vprint("=" * 60, VerbosityLevel.NORMAL)
    vprint("🔥 LSDAI Enhanced Launch System with Full Verbosity Integration", VerbosityLevel.NORMAL)
    vprint("=" * 60, VerbosityLevel.NORMAL)
    
    # Show current verbosity level
    level_names = {
        VerbosityLevel.SILENT: "Silent",
        VerbosityLevel.MINIMAL: "Minimal",
        VerbosityLevel.NORMAL: "Normal", 
        VerbosityLevel.DETAILED: "Detailed",
        VerbosityLevel.VERBOSE: "Verbose",
        VerbosityLevel.RAW: "Raw Output"
    }
    current_level = level_names.get(verbose_manager.verbosity_level, "Unknown")
    vprint(f"🔧 Current verbosity level: {current_level}", VerbosityLevel.MINIMAL)
    
    # Load CSS and JS if available
    try:
        WidgetFactory().load_css(CSS / 'enhanced-widgets.css')
        vprint("🎨 Enhanced CSS loaded", VerbosityLevel.DETAILED)
    except:
        vprint("⚠️ Enhanced CSS not found, using default styles", VerbosityLevel.DETAILED)
        
    if IN_COLAB:
        try:
            WidgetFactory().load_js(JS / 'main-widgets.js')
            vprint("📜 Enhanced JavaScript loaded", VerbosityLevel.DETAILED)
        except:
            vprint("⚠️ Enhanced JavaScript not found", VerbosityLevel.DETAILED)

    # Create and display the launch interface
    manager = LaunchWidgetManager()
    main_container = manager.build_ui()
    
    vprint("🎨 Launch interface created successfully", VerbosityLevel.NORMAL)
    
    display(main_container)
    
    # Setup callbacks after display
    manager.setup_callbacks()
    
    vprint("✅ Enhanced Launch System ready!", VerbosityLevel.NORMAL)
    vprint("   Use the buttons above to launch, stop, or restart your WebUI", VerbosityLevel.NORMAL)
    
    # If auto-launch is enabled, start immediately
    try:
        settings = js.load_settings(section='LAUNCH')
        if settings and settings.get('auto_launch', False):
            vprint("🚀 Auto-launch enabled, starting WebUI...", VerbosityLevel.NORMAL)
            manager.launch_webui(None)
    except:
        pass  # Auto-launch failed, ignore

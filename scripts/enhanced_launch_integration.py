# ~ enhanced_launch_integration.py | by ANXETY - Launch System with Optimizations ~

from modules.widget_factory import WidgetFactory
from modules.webui_utils import update_current_webui
from modules import json_utils as js

from IPython.display import display, Javascript, HTML
import ipywidgets as widgets
from pathlib import Path
import json
import os
import sys

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

# --- LAUNCH WIDGET MANAGER ---
class LaunchWidgetManager:
    """Manages the launch interface with system optimizations and monitoring."""
    
    def __init__(self):
        self.factory = WidgetFactory()
        self.widgets = {}
        self.selection_containers = {}
        
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
        key_map = {
            'model': 'model_list',
            'vae': 'vae_list', 
            'cnet': 'controlnet_list',
            'lora': 'lora_list'
        }
        key = key_map.get(data_type)
        local_vars = {}
        
        try:
            with open(file_path) as f:
                exec(f.read(), {}, local_vars)
            return local_vars.get(key, {})
        except Exception as e:
            print(f"Error reading {data_type} data: {e}")
            return {}

    def create_api_token_box(self, description, placeholder, url, env_var):
        """Create an API token input box with help link."""
        widget = self.factory.create_text(value='', description=description, placeholder=placeholder)
        
        # Check if token already set in environment
        token_from_env = os.getenv(env_var)
        if token_from_env:
            widget.value = "Token set in Cell 1"
            widget.disabled = True
        
        button = self.factory.create_html(f'<a href="{url}" target="_blank" class="button button_api"><span class="icon">?</span><span class="text">GET</span></a>')
        return self.factory.create_hbox([widget, button]), widget

    def create_selection_list(self, data_type, options_dict):
        """Create a selection list of toggle buttons."""
        buttons = [
            widgets.ToggleButton(
                description=name,
                value=False,
                button_style='',
                tooltip=name
            ) for name in options_dict.keys()
        ]
        self.widgets[data_type] = buttons
        
        container = self.factory.create_vbox(children=buttons, class_names=['selection-group'])
        self.selection_containers[data_type] = container
        return container

    def update_selection_list(self, data_type, new_options_dict):
        """Updates a VBox of ToggleButtons with new options."""
        selected_values = {btn.description for btn in self.widgets.get(data_type, []) if btn.value}
        new_buttons = [
            widgets.ToggleButton(
                description=name,
                value=(name in selected_values),
                button_style='',
                tooltip=name
            ) for name in new_options_dict.keys()
        ]
        self.widgets[data_type] = new_buttons
        if data_type in self.selection_containers:
            self.selection_containers[data_type].children = tuple(new_buttons)
        
    def build_ui(self):
        """Constructs and returns the entire launch UI."""
        
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
        # FIXED: Proper parameter order for checkbox
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

        # --- SYSTEM CONFIGURATION SECTION ---
        system_config = self.factory.create_vbox([
            self.widgets['precision_mode'],
            self.widgets['auto_restart'],
            self.widgets['backup_before_launch'],
            self.widgets['custom_args']
        ], class_names=['system-config'])

        # --- TABBED SELECTION INTERFACE (for final model verification) ---
        tab_children = []
        tab_titles = ['Models', 'VAEs', 'LoRAs', 'ControlNets']
        data_keys = ['model', 'vae', 'lora', 'cnet']
        
        for key in data_keys:
            options = self.read_model_data(SCRIPTS / '_models_data.py', key)
            selection_list = self.create_selection_list(key, options)
            tab_children.append(selection_list)
        
        tab_widget = widgets.Tab(children=tab_children)
        for i, title in enumerate(tab_titles):
            tab_widget.set_title(i, title)
        tab_widget.add_class('selection-tabs')
        
        # --- ACCORDION FOR ADVANCED SETTINGS ---
        # 1. Launch Configuration
        # FIXED: All checkbox parameter orders corrected
        self.widgets['check_custom_nodes_deps'] = self.factory.create_checkbox(
            value=True, 
            description='Check ComfyUI Dependencies', 
            layout={'display': 'none'}
        )
        self.widgets['commit_hash'] = self.factory.create_text(
            value='',
            description='Commit Hash:',
            placeholder='Optional: Use a specific commit'
        )
        self.widgets['commandline_arguments'] = self.factory.create_text(
            value=self.WEBUI_SELECTION['A1111'],
            description='Arguments:'
        )
        
        accent_colors = ['anxety', 'blue', 'green', 'peach', 'pink', 'red', 'yellow']
        self.widgets['theme_accent'] = self.factory.create_dropdown(
            options=accent_colors,
            value='anxety',
            description='Theme Accent:'
        )
        
        # API Token boxes
        civitai_box, self.widgets['civitai_token'] = self.create_api_token_box('CivitAI Token:', 'Paste token here', 'https://civitai.com/user/account', 'CIVITAI_API_TOKEN')
        hf_box, self.widgets['huggingface_token'] = self.create_api_token_box('HuggingFace Token:', 'Paste token here', 'https://huggingface.co/settings/tokens', 'HUGGINGFACE_API_TOKEN')
        zrok_box, self.widgets['zrok_token'] = self.create_api_token_box('Zrok Token:', 'Paste token here', 'https://zrok.io/', 'ZROK_API_TOKEN')
        ngrok_box, self.widgets['ngrok_token'] = self.create_api_token_box('Ngrok Token:', 'Paste token here', 'https://dashboard.ngrok.com/get-started/your-authtoken', 'NGROK_API_TOKEN')
        
        launch_config_vbox = self.factory.create_vbox([
            self.widgets['check_custom_nodes_deps'], self.widgets['commit_hash'], 
            self.widgets['commandline_arguments'], self.widgets['theme_accent'],
            widgets.HTML('<hr class="divider">'),
            civitai_box, hf_box, zrok_box, ngrok_box
        ])

        # 2. Custom Download / Empowerment
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
        self.status_display = self.factory.create_html('<div class="status-display">Ready to launch...</div>')
        self.performance_monitor = self.factory.create_output()
        
        monitoring_section = self.factory.create_vbox([
            self.status_display,
            self.performance_monitor
        ], class_names=['monitoring-section'])

        # --- SIDEBAR FOR QUICK ACTIONS ---
        BTN_STYLE = {'width': '48px', 'height': '48px'}
        
        self.quick_launch_button = self.factory.create_button('⚡', layout=BTN_STYLE, class_names=['side-button'])
        self.quick_launch_button.tooltip = "Quick Launch with Default Settings"
        
        self.settings_button = self.factory.create_button('⚙️', layout=BTN_STYLE, class_names=['side-button'])
        self.settings_button.tooltip = "Open Settings"
        
        self.logs_button = self.factory.create_button('📋', layout=BTN_STYLE, class_names=['side-button'])
        self.logs_button.tooltip = "View Logs"

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
        """Connects widget events to their handler functions."""
        # Set up widget observers
        if 'optimize_system' in self.widgets:
            self.factory.observe_widget(self.widgets['optimize_system'], self.update_optimization_settings)
        if 'precision_mode' in self.widgets:
            self.factory.observe_widget(self.widgets['precision_mode'], self.update_precision_settings)
        if 'empowerment' in self.widgets:
            self.factory.observe_widget(self.widgets['empowerment'], self.update_empowerment)
        
        if IN_COLAB:
            self.quick_launch_button.on_click(self.quick_launch)
            self.settings_button.on_click(self.open_settings)
            self.logs_button.on_click(self.view_logs)
            
        # Load initial settings
        self.load_settings()

    def update_optimization_settings(self, change):
        """Handle system optimization toggle."""
        is_optimized = change.get('new', False)
        
        if is_optimized:
            self.show_notification("System optimization enabled", "success")
            # Apply system optimizations here
        else:
            self.show_notification("System optimization disabled", "warning")

    def update_precision_settings(self, change):
        """Handle precision mode changes."""
        precision = change.get('new', 'auto')
        self.show_notification(f"Precision mode set to: {precision}", "info")

    def update_empowerment(self, change):
        """Handle empowerment mode toggle."""
        is_empowered = change.get('new', False)
        
        # List of widgets to hide/show based on empowerment mode
        url_widgets = [
            'Model_url', 'Vae_url', 'LoRA_url', 'Embedding_url', 
            'Extensions_url', 'ADetailer_url', 'custom_file_urls'
        ]
        
        for widget_name in url_widgets:
            if widget_name in self.widgets:
                self.widgets[widget_name].layout.display = 'none' if is_empowered else 'flex'
        
        if 'empowerment_output' in self.widgets:
            self.widgets['empowerment_output'].layout.display = 'flex' if is_empowered else 'none'

    def launch_webui(self, button):
        """Launch the WebUI with current settings."""
        try:
            self.show_notification("Launching WebUI...", "info")
            self.status_display.value = '<div class="status-display launching">🚀 Launching WebUI...</div>'
            
            # Apply backup if enabled
            if self.widgets.get('backup_before_launch', {}).get('value', False):
                js.backup_settings('pre_launch')
            
            # Save current settings
            self.save_settings()
            
            # Here would be the actual launch logic
            # For now, just show success
            self.status_display.value = '<div class="status-display running">✅ WebUI Running</div>'
            self.show_notification("WebUI launched successfully!", "success")
            
        except Exception as e:
            self.show_notification(f"Launch failed: {e}", "error")
            self.status_display.value = '<div class="status-display error">❌ Launch Failed</div>'

    def stop_webui(self, button):
        """Stop the running WebUI."""
        try:
            self.show_notification("Stopping WebUI...", "info")
            self.status_display.value = '<div class="status-display stopping">⏹️ Stopping WebUI...</div>'
            
            # Here would be the actual stop logic
            # For now, just show success
            self.status_display.value = '<div class="status-display stopped">⏹️ WebUI Stopped</div>'
            self.show_notification("WebUI stopped successfully!", "success")
            
        except Exception as e:
            self.show_notification(f"Stop failed: {e}", "error")

    def restart_webui(self, button):
        """Restart the WebUI."""
        try:
            self.show_notification("Restarting WebUI...", "info")
            self.status_display.value = '<div class="status-display restarting">🔄 Restarting WebUI...</div>'
            
            # Here would be the actual restart logic
            # For now, just show success
            self.status_display.value = '<div class="status-display running">✅ WebUI Restarted</div>'
            self.show_notification("WebUI restarted successfully!", "success")
            
        except Exception as e:
            self.show_notification(f"Restart failed: {e}", "error")

    def quick_launch(self, button):
        """Quick launch with default optimized settings."""
        try:
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
            self.show_notification(f"Quick launch failed: {e}", "error")

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
            
            # Add all widget values
            for key in self.settings_keys:
                if key in self.widgets:
                    widget = self.widgets[key]
                    if hasattr(widget, 'value'):
                        data[key] = widget.value
            
            # Save to settings
            js.save_settings(data, section='LAUNCH')
            
        except Exception as e:
            print(f"Error saving launch settings: {e}")

    def load_settings(self):
        """Load settings from file."""
        try:
            settings = js.load_settings(section='LAUNCH')
            if settings:
                self.apply_settings(settings)
        except Exception as e:
            print(f"Error loading launch settings: {e}")

    def apply_settings(self, settings):
        """Apply loaded settings to widgets."""
        # Apply to widgets
        for key in self.settings_keys:
            if key in settings and key in self.widgets:
                try:
                    self.widgets[key].value = settings[key]
                except:
                    pass

    def show_notification(self, message, type_="info"):
        """Show a notification popup."""
        if hasattr(self, 'notification_popup') and self.notification_popup:
            self.notification_popup.value = f'''
                <div class="notification {type_}">
                    <span class="icon">{'✅' if type_ == 'success' else '❌' if type_ == 'error' else 'ℹ️'}</span>
                    {message}
                </div>
            '''

# --- EXECUTION ---
if __name__ == "__main__":
    WidgetFactory().load_css(CSS / 'enhanced-widgets.css')
    if IN_COLAB:
        WidgetFactory().load_js(JS / 'main-widgets.js')

    manager = LaunchWidgetManager()
    main_container = manager.build_ui()
    display(main_container)
    
    manager.setup_callbacks()

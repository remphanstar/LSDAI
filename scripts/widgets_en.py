# widgets-en.py | by ANXETY - IMPROVED VERSION MATCHING ORIGINAL SDAIGEN
# Original stable widget interface for LSDAI

from widget_factory import WidgetFactory
from webui_utils import update_current_webui
import json_utils as js

from IPython.display import display, Javascript, HTML
import ipywidgets as widgets
from pathlib import Path
import importlib.util
import json
import os

# Conditional imports for platform-specific features
try:
    from google.colab import output, drive
    IN_COLAB = True
except ImportError:
    IN_COLAB = False
    class DummyOutput:
        @staticmethod
        def register_callback(name, func):
            pass
    output = DummyOutput()

osENV = os.environ

# Constants
PATHS = {k: Path(v) for k, v in osENV.items() if k.endswith('_path')}
HOME = PATHS['home_path']
SCR_PATH = PATHS['scr_path']
SETTINGS_PATH = SCR_PATH / 'settings.json'
ENV_NAME = js.read(SETTINGS_PATH, 'ENVIRONMENT.env_name')
SCRIPTS = SCR_PATH / 'scripts'

CSS = SCR_PATH / 'CSS'
JS = SCR_PATH / 'JS'
widgets_css = CSS / 'main-widgets.css'
widgets_js = JS / 'main-widgets.js'

class WidgetManager:
    def __init__(self):
        self.factory = WidgetFactory()
        self.widgets = {}
        self.settings_keys = [
            'XL_models', 'model', 'model_num', 'inpainting_model', 'vae', 'vae_num', 'lora',
            'latest_webui', 'latest_extensions', 'check_custom_nodes_deps', 'change_webui', 'detailed_download',
            'controlnet', 'controlnet_num', 'commit_hash',
            'civitai_token', 'huggingface_token', 'zrok_token', 'ngrok_token', 'commandline_arguments', 'theme_accent',
            'empowerment', 'empowerment_output',
            'Model_url', 'Vae_url', 'LoRA_url', 'Embedding_url', 'Extensions_url', 'ADetailer_url',
            'custom_file_urls'
        ]

    def create_expandable_button(self, text, url):
        """Create expandable API token button like original."""
        return self.factory.create_html(f'''
        <a href="{url}" target="_blank" class="button button_api">
            <span class="icon">🔗</span>
            <span class="text">{text}</span>
        </a>
        ''')

    def read_model_data(self, file_path, data_type):
        """Read model data safely using importlib."""
        type_map = {
            'model': ('model_list', ['none']),
            'vae': ('vae_list', ['none', 'ALL']),
            'cnet': ('controlnet_list', ['none', 'ALL']),
            'lora': ('lora_list', ['none', 'ALL'])
        }
        key, prefixes = type_map[data_type]
        
        try:
            spec = importlib.util.spec_from_file_location("model_data", file_path)
            model_data_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(model_data_module)
            data_dict = getattr(model_data_module, key, {})
            if not isinstance(data_dict, dict):
                raise TypeError(f"Data for '{key}' is not a dictionary.")
            
            # Build options list
            options = list(prefixes)
            for category, items in data_dict.items():
                if isinstance(items, list):
                    options.extend(items)
                else:
                    options.append(category)
            
            return options
        except Exception as e:
            print(f"Error reading {data_type} data: {e}")
            return list(prefixes)

    def create_widgets(self):
        """Create all widgets for the interface."""
        
        # Model data file
        model_data_file = SCRIPTS / '_models_data.py'
        
        # --- WebUI Selection ---
        webui_options = ['automatic1111', 'ComfyUI']
        self.widgets['change_webui'] = self.factory.create_dropdown(
            webui_options, 'automatic1111', 'WebUI:'
        )
        
        # --- Model Selection ---
        xl_models_toggle = self.factory.create_checkbox(False, 'XL Models')
        self.widgets['XL_models'] = xl_models_toggle
        
        model_options = self.read_model_data(model_data_file, 'model')
        self.widgets['model'] = self.factory.create_dropdown_multiple(
            model_options, ['none'], 'Model:'
        )
        
        # --- VAE Selection ---
        vae_options = self.read_model_data(model_data_file, 'vae')
        self.widgets['vae'] = self.factory.create_dropdown_multiple(
            vae_options, ['none'], 'VAE:'
        )
        
        # --- LoRA Selection ---
        lora_options = self.read_model_data(model_data_file, 'lora')
        self.widgets['lora'] = self.factory.create_dropdown_multiple(
            lora_options, ['none'], 'LoRA:'
        )
        
        # --- ControlNet Selection ---
        controlnet_options = self.read_model_data(model_data_file, 'cnet')
        self.widgets['controlnet'] = self.factory.create_dropdown_multiple(
            controlnet_options, ['none'], 'ControlNet:'
        )
        
        # --- Installation Options ---
        self.widgets['latest_webui'] = self.factory.create_checkbox(True, 'Latest WebUI')
        self.widgets['latest_extensions'] = self.factory.create_checkbox(False, 'Latest Extensions')
        self.widgets['detailed_download'] = self.factory.create_checkbox(False, 'Detailed Download')
        
        # --- Custom URLs ---
        self.widgets['Model_url'] = self.factory.create_text('', 'Model URLs (comma-separated):')
        self.widgets['Vae_url'] = self.factory.create_text('', 'VAE URLs:')
        self.widgets['LoRA_url'] = self.factory.create_text('', 'LoRA URLs:')
        self.widgets['Embedding_url'] = self.factory.create_text('', 'Embedding URLs:')
        self.widgets['Extensions_url'] = self.factory.create_text('', 'Extension URLs:')
        
        # --- API Tokens ---
        self.widgets['civitai_token'] = self.factory.create_text('', 'CivitAI Token:')
        self.widgets['huggingface_token'] = self.factory.create_text('', 'HuggingFace Token:')
        
        # --- Launch Arguments ---
        self.widgets['commandline_arguments'] = self.factory.create_text(
            '', 'Launch Arguments:'
        )
        
        # --- Theme ---
        theme_options = ['anxety', 'light', 'dark']
        self.widgets['theme_accent'] = self.factory.create_dropdown(
            theme_options, 'anxety', 'Theme:'
        )
        
        # Load existing values from settings
        self.load_settings()
        
        # Setup callbacks
        self.setup_callbacks()

    def setup_callbacks(self):
        """Setup widget callbacks and interactions."""
        
        # XL models toggle callback
        def update_xl_options(change):
            if change['new']:
                # Switch to XL model options
                model_options = [opt for opt in self.widgets['model'].options if 'XL' in opt or opt in ['none']]
            else:
                # Switch to regular model options
                model_options = self.read_model_data(SCRIPTS / '_models_data.py', 'model')
            
            self.widgets['model'].options = model_options
            self.widgets['model'].value = ['none']
        
        self.widgets['XL_models'].observe(update_xl_options, names='value')
        
        # WebUI change callback
        def update_webui_options(change):
            update_current_webui(change['new'])
            
        self.widgets['change_webui'].observe(update_webui_options, names='value')

    def load_settings(self):
        """Load settings from JSON file."""
        try:
            for key in self.settings_keys:
                if key in self.widgets:
                    value = js.read(SETTINGS_PATH, f'WIDGETS.{key}')
                    if value is not None:
                        if hasattr(self.widgets[key], 'value'):
                            self.widgets[key].value = value
        except Exception as e:
            print(f"Warning: Could not load some settings: {e}")

    def save_settings(self):
        """Save current widget values to settings."""
        try:
            settings_data = {}
            for key in self.settings_keys:
                if key in self.widgets and hasattr(self.widgets[key], 'value'):
                    settings_data[key] = self.widgets[key].value
            
            js.write(SETTINGS_PATH, 'WIDGETS', settings_data)
            show_notification("Settings saved successfully!", "success")
            
        except Exception as e:
            show_notification(f"Error saving settings: {e}", "error")

    def create_layout(self):
        """Create the main widget layout."""
        
        # Header
        header = self.factory.create_header("LSDAI Configuration", ['main-header'])
        
        # WebUI Section
        webui_section = widgets.VBox([
            self.factory.create_header("WebUI Selection", ['section-header']),
            self.widgets['change_webui'],
            widgets.HBox([
                self.widgets['latest_webui'],
                self.widgets['latest_extensions'],
                self.widgets['detailed_download']
            ])
        ])
        
        # Model Section
        model_section = widgets.VBox([
            self.factory.create_header("Model Selection", ['section-header']),
            self.widgets['XL_models'],
            self.widgets['model'],
            self.widgets['vae'],
            self.widgets['lora'],
            self.widgets['controlnet']
        ])
        
        # Custom URLs Section
        urls_section = widgets.VBox([
            self.factory.create_header("Custom URLs", ['section-header']),
            self.widgets['Model_url'],
            self.widgets['Vae_url'],
            self.widgets['LoRA_url'],
            self.widgets['Embedding_url'],
            self.widgets['Extensions_url']
        ])
        
        # Configuration Section
        config_section = widgets.VBox([
            self.factory.create_header("Configuration", ['section-header']),
            self.widgets['civitai_token'],
            self.widgets['huggingface_token'],
            self.widgets['commandline_arguments'],
            self.widgets['theme_accent']
        ])
        
        # Control Buttons
        save_button = widgets.Button(
            description='💾 Save Settings',
            button_style='success',
            layout=widgets.Layout(width='200px')
        )
        save_button.on_click(lambda b: self.save_settings())
        
        export_button = widgets.Button(
            description='📤 Export Settings',
            button_style='info',
            layout=widgets.Layout(width='200px')
        )
        export_button.on_click(export_settings)
        
        import_button = widgets.Button(
            description='📥 Import Settings',
            button_style='warning',
            layout=widgets.Layout(width='200px')
        )
        import_button.on_click(import_settings)
        
        buttons_section = widgets.HBox([
            save_button, export_button, import_button
        ], layout=widgets.Layout(justify_content='center'))
        
        # Google Drive Mount (Colab only)
        if IN_COLAB:
            mount_button = widgets.Button(
                description='📂 Mount Google Drive',
                button_style='primary',
                layout=widgets.Layout(width='200px')
            )
            mount_button.on_click(mount_google_drive)
            buttons_section.children = buttons_section.children + (mount_button,)
        
        # Main layout
        main_layout = widgets.VBox([
            header,
            webui_section,
            model_section,
            urls_section,
            config_section,
            buttons_section,
            notification_popup
        ])
        
        return main_layout

# Initialize widget manager
wm = WidgetManager()
factory = wm.factory

# --- UTILITY FUNCTIONS ---
def mount_google_drive(button=None):
    """Mount Google Drive in Colab"""
    if IN_COLAB:
        try:
            drive.mount('/content/drive')
            show_notification("Google Drive mounted successfully!", "success")
        except Exception as e:
            show_notification(f"Failed to mount Google Drive: {e}", "error")

def export_settings(button=None):
    """Export settings to JSON"""
    try:
        # Save current settings first
        wm.save_settings()
        
        # Read all settings
        all_settings = js.read(SETTINGS_PATH)
        
        # Create export data
        export_data = {
            'widgets': all_settings.get('WIDGETS', {}),
            'timestamp': js.get_current_timestamp(),
            'version': '2.0'
        }
        
        # In Colab, trigger download
        if IN_COLAB:
            display(Javascript(f'''
                const data = {json.dumps(export_data)};
                const blob = new Blob([JSON.stringify(data, null, 2)], {{type: 'application/json'}});
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = 'lsdai_settings.json';
                a.click();
                URL.revokeObjectURL(url);
            '''))
        
        show_notification("Settings exported successfully!", "success")
    except Exception as e:
        show_notification(f"Export failed: {str(e)}", "error")

def import_settings(button=None):
    """Import settings from JSON"""
    if not IN_COLAB:
        return
    display(Javascript('openFilePicker();'))

def apply_imported_settings(data):
    """Apply imported settings data"""
    try:
        if 'widgets' in data:
            for key, value in data['widgets'].items():
                if key in wm.settings_keys and key in wm.widgets:
                    try:
                        wm.widgets[key].value = value
                    except Exception as e:
                        print(f"Warning: Could not set {key}: {e}")

        show_notification("Settings imported successfully!", "success")
    except Exception as e:
        show_notification(f"Import failed: {str(e)}", "error")

# --- NOTIFICATION SYSTEM ---
notification_popup = factory.create_html('', class_names=['notification-popup', 'hidden'])

def show_notification(message, message_type='info'):
    """Show notification popup"""
    icon_map = {
        'success': '✅',
        'error': '❌',
        'info': 'ℹ️',
        'warning': '⚠️'
    }
    icon = icon_map.get(message_type, 'ℹ️')

    notification_popup.value = f'''
    <div class="notification {message_type}">
        <span class="notification-icon">{icon}</span>
        <span class="notification-text">{message}</span>
    </div>
    '''

    notification_popup.remove_class('visible')
    notification_popup.remove_class('hidden')
    notification_popup.add_class('visible')

    if IN_COLAB:
        display(Javascript("hideNotification(delay = 2500);"))

# Register callbacks for Colab
if IN_COLAB:
    output.register_callback('importSettingsFromJS', apply_imported_settings)
    output.register_callback('showNotificationFromJS', show_notification)

# --- LOAD CSS/JS ---
try:
    factory.load_css(widgets_css)
    print("✅ CSS loaded successfully")
except Exception as e:
    print(f"⚠️ Warning: Could not load CSS: {e}")

if IN_COLAB:
    try:
        factory.load_js(widgets_js)
        print("✅ JavaScript loaded successfully")
    except Exception as e:
        print(f"⚠️ Warning: Could not load JavaScript: {e}")

# --- MAIN EXECUTION ---
def main():
    """Main function to create and display the widget interface"""
    
    print("🎯 LSDAI Widget Interface")
    print("=" * 30)
    
    try:
        # Create widgets
        wm.create_widgets()
        
        # Create and display layout
        layout = wm.create_layout()
        display(layout)
        
        print("✅ Widget interface loaded successfully!")
        
    except Exception as e:
        print(f"❌ Error creating widget interface: {e}")
        
        # Show error in HTML
        error_html = f"""
        <div style="border: 2px solid #ef4444; background-color: #fee2e2; padding: 1rem; border-radius: 0.5rem; color: #b91c1c;">
            <h3>❌ Widget Interface Error</h3>
            <p>Failed to load the widget interface. Error details:</p>
            <pre style="background: #fecaca; padding: 0.5rem; border-radius: 0.25rem;">{str(e)}</pre>
        </div>
        """
        display(HTML(error_html))

# Execute main function
if __name__ == "__main__" or "run_path" in globals():
    main()

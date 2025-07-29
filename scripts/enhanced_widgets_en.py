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
import time

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
        """Read model data safely, ensuring only strings are returned for widget options."""
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
            
            # CORRECTED LOGIC: This ensures only the string names (keys) are used as options,
            # which prevents the "unhashable type: dict" error.
            options = list(prefixes)
            options.extend(data_dict.keys())
            
            return options
        except Exception as e:
            print(f"Error reading {data_type} data: {e}")
            return list(prefixes)

    def create_widgets(self):
        """Create all widgets for the interface."""
        
        model_data_file = SCRIPTS / '_models_data.py'
        
        # --- WebUI Selection ---
        webui_options = ['automatic1111', 'ComfyUI']
        self.widgets['change_webui'] = self.factory.create_dropdown(
            options=webui_options, value='automatic1111', description='WebUI:'
        )
        
        # --- Model Selection ---
        self.widgets['XL_models'] = self.factory.create_checkbox(value=False, description='XL Models')
        
        model_options = self.read_model_data(model_data_file, 'model')
        self.widgets['model'] = self.factory.create_dropdown_multiple(
            options=model_options, value=['none'], description='Model:'
        )
        
        # --- VAE Selection ---
        vae_options = self.read_model_data(model_data_file, 'vae')
        self.widgets['vae'] = self.factory.create_dropdown_multiple(
            options=vae_options, value=['none'], description='VAE:'
        )
        
        # --- LoRA Selection ---
        lora_options = self.read_model_data(model_data_file, 'lora')
        self.widgets['lora'] = self.factory.create_dropdown_multiple(
            options=lora_options, value=['none'], description='LoRA:'
        )
        
        # --- ControlNet Selection ---
        controlnet_options = self.read_model_data(model_data_file, 'cnet')
        self.widgets['controlnet'] = self.factory.create_dropdown_multiple(
            options=controlnet_options, value=['none'], description='ControlNet:'
        )
        
        # --- Installation Options ---
        self.widgets['latest_webui'] = self.factory.create_checkbox(value=True, description='Latest WebUI')
        self.widgets['latest_extensions'] = self.factory.create_checkbox(value=False, description='Latest Extensions')
        self.widgets['detailed_download'] = self.factory.create_checkbox(value=False, description='Detailed Download')
        
        # --- Custom URLs ---
        self.widgets['Model_url'] = self.factory.create_text(description='Model URLs (comma-separated):')
        self.widgets['Vae_url'] = self.factory.create_text(description='VAE URLs:')
        self.widgets['LoRA_url'] = self.factory.create_text(description='LoRA URLs:')
        self.widgets['Embedding_url'] = self.factory.create_text(description='Embedding URLs:')
        self.widgets['Extensions_url'] = self.factory.create_text(description='Extension URLs:')
        
        # --- API Tokens ---
        self.widgets['civitai_token'] = self.factory.create_text(description='CivitAI Token:')
        self.widgets['huggingface_token'] = self.factory.create_text(description='HuggingFace Token:')
        
        # --- Launch Arguments ---
        self.widgets['commandline_arguments'] = self.factory.create_text(description='Launch Arguments:')
        
        # --- Theme ---
        theme_options = ['anxety', 'light', 'dark']
        self.widgets['theme_accent'] = self.factory.create_dropdown(
            options=theme_options, value='anxety', description='Theme:'
        )
        
        self.load_settings()
        self.setup_callbacks()

    def setup_callbacks(self):
        """Setup widget callbacks and interactions."""
        def update_xl_options(change):
            model_data_file = SCRIPTS / ('_xl_models_data.py' if change['new'] else '_models_data.py')
            self.widgets['model'].options = self.read_model_data(model_data_file, 'model')
            self.widgets['model'].value = ['none']
        
        self.widgets['XL_models'].observe(update_xl_options, names='value')
        
        def update_webui_options(change):
            update_current_webui(change['new'])
            
        self.widgets['change_webui'].observe(update_webui_options, names='value')

    def load_settings(self):
        """Load settings from JSON file."""
        try:
            widget_settings = js.read(SETTINGS_PATH, 'WIDGETS', {})
            for key in self.settings_keys:
                if key in self.widgets and key in widget_settings:
                    value = widget_settings[key]
                    if value is not None and hasattr(self.widgets[key], 'value'):
                        self.widgets[key].value = value
        except Exception as e:
            print(f"Warning: Could not load some settings: {e}")

    def save_settings(self, button=None):
        """Save current widget values to settings."""
        try:
            settings_data = {key: self.widgets[key].value for key in self.settings_keys if key in self.widgets and hasattr(self.widgets[key], 'value')}
            js.save(SETTINGS_PATH, 'WIDGETS', settings_data)
            show_notification("Settings saved successfully!", "success")
        except Exception as e:
            show_notification(f"Error saving settings: {e}", "error")

    def create_layout(self):
        """Create the main widget layout."""
        header = self.factory.create_header("LSDAI Configuration", ['main-header'])
        
        webui_section = widgets.VBox([
            self.factory.create_header("WebUI Selection", ['section-header']),
            self.widgets['change_webui'],
            widgets.HBox([self.widgets['latest_webui'], self.widgets['latest_extensions'], self.widgets['detailed_download']])
        ])
        
        model_section = widgets.VBox([
            self.factory.create_header("Model Selection", ['section-header']),
            self.widgets['XL_models'], self.widgets['model'], self.widgets['vae'],
            self.widgets['lora'], self.widgets['controlnet']
        ])
        
        urls_section = widgets.VBox([
            self.factory.create_header("Custom URLs", ['section-header']),
            self.widgets['Model_url'], self.widgets['Vae_url'], self.widgets['LoRA_url'],
            self.widgets['Embedding_url'], self.widgets['Extensions_url']
        ])
        
        config_section = widgets.VBox([
            self.factory.create_header("Configuration", ['section-header']),
            self.widgets['civitai_token'], self.widgets['huggingface_token'],
            self.widgets['commandline_arguments'], self.widgets['theme_accent']
        ])
        
        save_button = self.factory.create_button(description='💾 Save Settings', button_style='success', layout={'width': '200px'})
        save_button.on_click(self.save_settings)
        
        buttons = [save_button]
        if IN_COLAB:
            mount_button = self.factory.create_button(description='📂 Mount Google Drive', button_style='primary', layout={'width': '200px'})
            mount_button.on_click(mount_google_drive)
            buttons.append(mount_button)
        
        buttons_section = widgets.HBox(buttons, layout={'justify_content': 'center'})
        
        return widgets.VBox([header, webui_section, model_section, urls_section, config_section, buttons_section, notification_popup])

# Initialize widget manager and factory
wm = WidgetManager()
factory = wm.factory
notification_popup = factory.create_html('', class_names=['notification-popup', 'hidden'])

def show_notification(message, message_type='info'):
    """Show notification popup."""
    icon_map = {'success': '✅', 'error': '❌', 'info': 'ℹ️', 'warning': '⚠️'}
    icon = icon_map.get(message_type, 'ℹ️')
    notification_popup.value = f'<div class="notification {message_type}"><span class="notification-icon">{icon}</span><span class="notification-text">{message}</span></div>'
    if IN_COLAB:
        display(Javascript("document.querySelector('.notification-popup').classList.add('visible'); setTimeout(() => { document.querySelector('.notification-popup').classList.remove('visible'); }, 3000);"))

def mount_google_drive(button=None):
    """Mount Google Drive in Colab"""
    if IN_COLAB:
        try:
            drive.mount('/content/drive')
            show_notification("Google Drive mounted successfully!", "success")
        except Exception as e:
            show_notification(f"Failed to mount Google Drive: {e}", "error")

# --- MAIN EXECUTION ---
def main():
    """Main function to create and display the widget interface"""
    print("🎯 LSDAI Widget Interface")
    print("=" * 30)
    try:
        factory.load_css(widgets_css)
        if IN_COLAB: factory.load_js(widgets_js)
        wm.create_widgets()
        display(wm.create_layout())
        print("✅ Widget interface loaded successfully!")
    except Exception as e:
        print(f"❌ Error creating widget interface: {e}")
        display(HTML(f'<div style="color:red;"><h3>Widget Error</h3><pre>{e}</pre></div>'))

if __name__ == "__main__":
    main()

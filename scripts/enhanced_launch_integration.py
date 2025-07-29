# ~ enhanced_widgets_integration.py | Amalgamated Script ~
# This script combines the robust loader with the main UI builder to create a single,
# self-contained, and reliable widget interface for the LSDAI notebook.

from IPython.display import display, HTML, Javascript
import ipywidgets as widgets
from pathlib import Path
import json
import os
import sys

# --- Global Path Variables ---
# These will be populated by the main() function before widgets are built.
SCRIPTS = None
SCR_PATH = None
SETTINGS_PATH = None
CSS = None
JS = None
IN_COLAB = False

# --- Main UI Builder Class ---
class WidgetManager:
    """Manages the creation, layout, and logic of the UI widgets."""
    
    def __init__(self):
        self.factory = WidgetFactory()
        self.widgets = {}
        self.selection_containers = {}
        self.settings_keys = [
            'XL_models', 'model', 'inpainting_model', 'vae', 'lora', 'controlnet',
            'latest_webui', 'latest_extensions', 'check_custom_nodes_deps', 'change_webui', 'detailed_download',
            'commit_hash', 'civitai_token', 'huggingface_token', 'zrok_token', 'ngrok_token', 
            'commandline_arguments', 'theme_accent', 'empowerment', 'empowerment_output',
            'Model_url', 'Vae_url', 'LoRA_url', 'Embedding_url', 'Extensions_url', 'ADetailer_url',
            'custom_file_urls'
        ]
        self.WEBUI_SELECTION = {
            'A1111':   "--xformers --no-half-vae --share --lowram",
            'ComfyUI': "--dont-print-server",
            'Forge':   "--xformers --cuda-stream --pin-shared-memory",
            'Classic': "--persistent-patches --cuda-stream --pin-shared-memory",
            'ReForge': "--xformers --cuda-stream --pin-shared-memory",
            'SD-UX':   "--xformers --no-half-vae"
        }

    def read_model_data(self, file_path, data_type):
        """Reads model data from the specified file."""
        key_map = {'model': 'model_list', 'vae': 'vae_list', 'cnet': 'controlnet_list', 'lora': 'lora_list'}
        key = key_map.get(data_type)
        local_vars = {}
        try:
            with open(file_path) as f:
                exec(f.read(), {}, local_vars)
            return local_vars.get(key, {})
        except Exception as e:
            print(f"Warning: Could not load {data_type} data from {file_path}: {e}")
            return {}

    def create_api_token_box(self, description, placeholder, url, env_var):
        """Creates a consistent UI element for API tokens, checking for environment variables."""
        widget = self.factory.create_text(description, '', placeholder)
        token_from_env = os.getenv(env_var)
        if token_from_env:
            widget.value = "Token set in Cell 1"
            widget.disabled = True
        
        button = self.factory.create_html(f'''
            <a href="{url}" target="_blank" class="button button_api">
                <span class="icon">?</span><span class="text">GET</span>
            </a>
        ''')
        return self.factory.create_hbox([widget, button]), widget

    def create_selection_list(self, data_type, options_dict):
        """Creates a VBox of ToggleButtons for model selection."""
        buttons = [widgets.ToggleButton(description=name, value=False, button_style='', tooltip=name) for name in options_dict.keys()]
        self.widgets[data_type] = buttons
        
        container = self.factory.create_vbox(children=buttons, class_names=['selection-group'])
        self.selection_containers[data_type] = container
        return container

    def update_selection_list(self, data_type, new_options_dict):
        """Updates a VBox of ToggleButtons with new options."""
        selected_values = {btn.description for btn in self.widgets.get(data_type, []) if btn.value}
        new_buttons = [widgets.ToggleButton(description=name, value=(name in selected_values), button_style='', tooltip=name) for name in new_options_dict.keys()]
        self.widgets[data_type] = new_buttons
        if data_type in self.selection_containers:
            self.selection_containers[data_type].children = tuple(new_buttons)
        
    def build_ui(self):
        """Constructs and returns the entire widget UI."""
        
        # --- HEADER CONTROLS ---
        self.widgets['latest_webui'] = widgets.ToggleButton(value=True, description='Update WebUI', button_style='')
        self.widgets['latest_extensions'] = widgets.ToggleButton(value=True, description='Update Extensions', button_style='')
        self.widgets['inpainting_model'] = widgets.ToggleButton(value=False, description='Inpainting', button_style='')
        self.widgets['XL_models'] = widgets.ToggleButton(value=False, description='SDXL', button_style='')
        
        left_toggles = self.factory.create_hbox([self.widgets['latest_webui'], self.widgets['latest_extensions']], class_names=['header-group'])
        right_toggles = self.factory.create_hbox([self.widgets['inpainting_model'], self.widgets['XL_models']], class_names=['header-group'])
        
        self.widgets['change_webui'] = self.factory.create_dropdown(list(self.WEBUI_SELECTION.keys()), 'WebUI:', 'A1111')
        self.widgets['detailed_download'] = widgets.ToggleButton(value=False, description='Detailed Output', button_style='')
        
        header_controls = self.factory.create_hbox([
            left_toggles,
            self.widgets['change_webui'],
            self.widgets['detailed_download'],
            right_toggles
        ], class_names=['header-controls'])

        # --- TABBED SELECTION INTERFACE ---
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
        
        # --- ACCORDION FOR OTHER SETTINGS ---
        self.widgets['check_custom_nodes_deps'] = self.factory.create_checkbox('Check ComfyUI Dependencies', True, layout={'display': 'none'})
        self.widgets['commit_hash'] = self.factory.create_text('Commit Hash:', '', 'Optional: Use a specific commit')
        self.widgets['commandline_arguments'] = self.factory.create_text('Arguments:', self.WEBUI_SELECTION['A1111'])
        accent_colors = ['anxety', 'blue', 'green', 'peach', 'pink', 'red', 'yellow']
        self.widgets['theme_accent'] = self.factory.create_dropdown(accent_colors, 'Theme Accent:', 'anxety')
        
        civitai_box, self.widgets['civitai_token'] = self.create_api_token_box('CivitAI Token:', 'Paste token here', 'https://civitai.com/user/account', 'CIVITAI_API_TOKEN')
        hf_box, self.widgets['huggingface_token'] = self.create_api_token_box('HuggingFace Token:', 'Paste token here', 'https://huggingface.co/settings/tokens', 'HUGGINGFACE_API_TOKEN')
        zrok_box, self.widgets['zrok_token'] = self.create_api_token_box('Zrok Token:', 'Paste token here', 'https://zrok.io/', 'ZROK_API_TOKEN')
        ngrok_box, self.widgets['ngrok_token'] = self.create_api_token_box('Ngrok Token:', 'Paste token here', 'https://dashboard.ngrok.com/get-started/your-authtoken', 'NGROK_API_TOKEN')
        
        additional_vbox = self.factory.create_vbox([
            self.widgets['check_custom_nodes_deps'], self.widgets['commit_hash'], 
            self.widgets['commandline_arguments'], self.widgets['theme_accent'],
            widgets.HTML('<hr class="divider">'),
            civitai_box, hf_box, zrok_box, ngrok_box
        ])

        self.widgets['empowerment'] = self.factory.create_checkbox('Empowerment Mode', False)
        self.widgets['empowerment_output'] = self.factory.create_textarea('', '', 'Use special tags like $ckpt, $lora, etc.')
        self.widgets['Model_url'] = self.factory.create_text('Model URL:')
        self.widgets['Vae_url'] = self.factory.create_text('Vae URL:')
        self.widgets['LoRA_url'] = self.factory.create_text('LoRA URL:')
        self.widgets['Embedding_url'] = self.factory.create_text('Embedding URL:')
        self.widgets['Extensions_url'] = self.factory.create_text('Extensions URL:')
        self.widgets['ADetailer_url'] = self.factory.create_text('ADetailer URL:')
        self.widgets['custom_file_urls'] = self.factory.create_text('File (txt):')
        self.custom_dl_container = self.factory.create_vbox([
            self.widgets['Model_url'], self.widgets['Vae_url'], self.widgets['LoRA_url'],
            self.widgets['Embedding_url'], self.widgets['Extensions_url'], self.widgets['ADetailer_url'],
            self.widgets['custom_file_urls']
        ])
        custom_dl_vbox = self.factory.create_vbox([
            self.widgets['empowerment'], self.widgets['empowerment_output'], self.custom_dl_container
        ])
        
        accordion = widgets.Accordion(children=[additional_vbox, custom_dl_vbox])
        accordion.set_title(0, 'Advanced Configuration & API Tokens')
        accordion.set_title(1, 'Custom Download / Empowerment')
        accordion.selected_index = None
        accordion.add_class('trimmed-box')

        save_button = self.factory.create_button('Save Settings', class_names=['button', 'button_save'])
        save_button.on_click(self.save_data)

        BTN_STYLE = {'width': '48px', 'height': '48px'}
        TOOLTIPS = ("Disconnect Google Drive", "Connect Google Drive")
        GD_status = js.read(SETTINGS_PATH, 'mountGDrive', False) if SETTINGS_PATH else False
        self.gdrive_button = self.factory.create_button('📁', layout=BTN_STYLE, class_names=['side-button'])
        self.gdrive_button.tooltip = TOOLTIPS[not GD_status]
        self.export_button = self.factory.create_button('📤', layout=BTN_STYLE, class_names=['side-button'])
        self.export_button.tooltip = "Export settings to JSON"
        self.import_button = self.factory.create_button('📥', layout=BTN_STYLE, class_names=['side-button'])
        self.import_button.tooltip = "Import settings from JSON"
        self.notification_popup = self.factory.create_html('', class_names=['notification-popup', 'hidden'])
        sidebar = self.factory.create_vbox([self.gdrive_button, self.export_button, self.import_button, self.notification_popup], class_names=['sidebar'])
        if not IN_COLAB:
            sidebar.layout.display = 'none'

        main_content = self.factory.create_vbox([header_controls, tab_widget, accordion, save_button], class_names=['main-content'])
        self.main_container = self.factory.create_hbox([main_content, sidebar], class_names=['main-ui-container'])
        return self.main_container

    def setup_callbacks(self):
        """Connects widget events to their handler functions."""
        self.factory.connect_widgets([(self.widgets['change_webui'], 'value')], self.update_change_webui)
        self.factory.connect_widgets([(self.widgets['XL_models'], 'value')], self.update_xl_options)
        self.factory.connect_widgets([(self.widgets['empowerment'], 'value')], self.update_empowerment)
        self.factory.connect_widgets([(self.widgets['inpainting_model'], 'value')], self.filter_inpainting_models)
        
        if IN_COLAB:
            self.gdrive_button.on_click(self.handle_gdrive_toggle)
            self.export_button.on_click(self.export_settings)
            self.import_button.on_click(self.import_settings)
            output.register_callback('importSettingsFromJS', self.apply_imported_settings)

        self.update_empowerment({'new': self.widgets['empowerment'].value}, None)
        self.update_change_webui({'new': self.widgets['change_webui'].value}, None)

    def update_xl_options(self, change, widget):
        is_xl = change['new']
        data_file = SCRIPTS / ('_xl_models_data.py' if is_xl else '_models_data.py')
        self.update_selection_list('model', self.read_model_data(data_file, 'model'))
        self.update_selection_list('vae', self.read_model_data(data_file, 'vae'))
        self.update_selection_list('lora', self.read_model_data(data_file, 'lora'))
        self.update_selection_list('cnet', self.read_model_data(data_file, 'cnet'))
        self.widgets['inpainting_model'].value = False
        self.widgets['inpainting_model'].disabled = is_xl
        self.filter_inpainting_models({'new': False}, None)

    def update_change_webui(self, change, widget):
        webui = change['new']
        self.widgets['commandline_arguments'].value = self.WEBUI_SELECTION.get(webui, '')
        is_comfy = webui == 'ComfyUI'
        self.widgets['latest_extensions'].layout.display = 'none' if is_comfy else 'flex'
        self.widgets['check_custom_nodes_deps'].layout.display = 'flex' if is_comfy else 'none'
        self.widgets['theme_accent'].layout.display = 'none' if is_comfy else 'flex'
        self.widgets['Extensions_url'].description = 'Custom Nodes:' if is_comfy else 'Extensions:'

    def update_empowerment(self, change, widget):
        self.custom_dl_container.layout.display = 'none' if change['new'] else 'flex'
        self.widgets['empowerment_output'].layout.display = 'flex' if change['new'] else 'none'

    def filter_inpainting_models(self, change, widget):
        is_inpainting = change.get('new', False)
        if self.widgets['XL_models'].value: return
        data_file = SCRIPTS / '_models_data.py'
        full_model_dict = self.read_model_data(data_file, 'model')
        options = {name: data for name, data in full_model_dict.items() if data.get('inpainting')} if is_inpainting else {name: data for name, data in full_model_dict.items() if not data.get('inpainting')}
        self.update_selection_list('model', options)

    def handle_gdrive_toggle(self, btn):
        btn.toggle = not getattr(btn, 'toggle', False)
        btn.tooltip = ("Disconnect Google Drive", "Connect Google Drive")[not btn.toggle]
        btn.remove_class('active') if not btn.toggle else btn.add_class('active')

    def show_notification(self, message, message_type='info'):
        icon_map = {'success': '✅', 'error': '❌', 'info': 'ℹ️', 'warning': '⚠️'}
        icon = icon_map.get(message_type, 'ℹ️')
        self.notification_popup.value = f'<div class="notification {message_type}"><span class="icon">{icon}</span>{message}</div>'
        self.notification_popup.remove_class('hidden')
        display(Javascript("setTimeout(() => { document.querySelector('.notification-popup').classList.add('hidden'); }, 3000)"))

    def export_settings(self, btn):
        widgets_data = self.save_settings_to_dict()
        settings_data = {'widgets': widgets_data, 'mountGDrive': getattr(self.gdrive_button, 'toggle', False)}
        display(Javascript(f'downloadJson({json.dumps(settings_data)});'))
        self.show_notification("Settings exported!", "success")

    def import_settings(self, btn):
        display(Javascript('openFilePicker();'))

    def apply_imported_settings(self, data):
        try:
            if 'widgets' in data: self.load_settings_data(data['widgets'])
            if 'mountGDrive' in data:
                self.gdrive_button.toggle = data['mountGDrive']
                self.gdrive_button.remove_class('active') if not data['mountGDrive'] else self.gdrive_button.add_class('active')
            self.show_notification("Settings imported!", "success")
        except Exception as e:
            self.show_notification(f"Import failed: {e}", "error")

    def get_selected_toggles(self, data_type):
        if data_type in self.widgets and isinstance(self.widgets[data_type], list):
            return [btn.description for btn in self.widgets[data_type] if btn.value]
        return []

    def save_settings_to_dict(self):
        widgets_values = {}
        for key in self.settings_keys:
            if key in ['model', 'vae', 'lora', 'controlnet']:
                widgets_values[key] = self.get_selected_toggles(key)
            elif key in self.widgets:
                if isinstance(self.widgets[key], widgets.ToggleButton):
                     widgets_values[key] = 'on' if self.widgets[key].value else 'off'
                else:
                    widgets_values[key] = self.widgets[key].value
        return widgets_values

    def save_settings(self):
        widgets_values = self.save_settings_to_dict()
        js.save(SETTINGS_PATH, 'WIDGETS', widgets_values)
        js.save(SETTINGS_PATH, 'mountGDrive', getattr(self.gdrive_button, 'toggle', False))
        update_current_webui(self.widgets['change_webui'].value)

    def load_settings_data(self, widget_data):
        for key in self.settings_keys:
            if key in widget_data and key in self.widgets:
                try:
                    if key in ['civitai_token', 'huggingface_token', 'zrok_token', 'ngrok_token'] and self.widgets[key].disabled: continue
                    if key in ['model', 'vae', 'lora', 'controlnet']:
                        selected_names = widget_data.get(key, [])
                        for btn in self.widgets[key]:
                            btn.value = btn.description in selected_names
                    elif isinstance(self.widgets[key], widgets.ToggleButton):
                        self.widgets[key].value = widget_data.get(key) == 'on'
                    else:
                        self.widgets[key].value = widget_data.get(key, self.widgets[key].value)
                except Exception as e:
                    print(f"Warning: could not load setting for {key}: {e}")

    def load_settings(self):
        if js.key_exists(SETTINGS_PATH, 'WIDGETS'):
            self.load_settings_data(js.read(SETTINGS_PATH, 'WIDGETS'))
        if IN_COLAB:
            gdrive_status = js.read(SETTINGS_PATH, 'mountGDrive', False)
            self.gdrive_button.toggle = gdrive_status
            self.gdrive_button.remove_class('active') if not gdrive_status else self.gdrive_button.add_class('active')

    def save_data(self, button):
        self.save_settings()
        self.show_notification("Settings Saved!", "success")
        self.factory.close(self.main_container, class_names=['hide'], delay=0.5)

# --- Loader Functions ---
def show_error_message(error_details):
    """Display a styled error message in the notebook"""
    display(HTML(f"""
    <div style="border: 2px solid #ef4444; background-color: #fee2e2; padding: 1rem; border-radius: 0.5rem; color: #b91c1c; margin: 10px 0;">
        <h3 style="margin-top: 0;">⚠️ Enhanced Widgets Loading Error</h3>
        <p>The enhanced UI script failed to load. Falling back to the original, stable widget interface.</p>
        <details style="margin-top: 10px;">
            <summary><b>Error Details (click to expand)</b></summary>
            <pre style="white-space: pre-wrap; word-wrap: break-word; background: #fecaca; padding: 0.5rem; border-radius: 0.25rem; margin-top: 5px; font-size: 12px;">{error_details}</pre>
        </details>
    </div>
    """))

def load_widgets():
    """Loads and displays the widget UI."""
    global main_container
    
    WidgetFactory().load_css(CSS / 'enhanced-widgets.css')
    if IN_COLAB:
        WidgetFactory().load_js(JS / 'main-widgets.js')

    manager = WidgetManager()
    main_container = manager.build_ui()
    display(main_container)
    
    manager.load_settings()
    manager.setup_callbacks()
    return True

def main():
    """Main widget loading function"""
    global SCRIPTS, SCR_PATH, SETTINGS_PATH, CSS, JS, IN_COLAB, main_container
    
    print("🎯 LSDAI Widget Interface Loader")
    print("=" * 40)
    
    try:
        SCRIPTS = find_script_path()
        SCR_PATH = SCRIPTS.parent
        SETTINGS_PATH = SCR_PATH / 'settings.json'
        CSS = SCR_PATH / 'CSS'
        JS = SCR_PATH / 'JS'
        IN_COLAB = 'google.colab' in sys.modules
        
        modules_path = SCR_PATH / 'modules'
        if modules_path.exists() and str(modules_path) not in sys.path:
            sys.path.insert(0, str(modules_path))
            print(f"🐍 Added {modules_path} to Python path")
        
        from modules.widget_factory import WidgetFactory
        from modules.webui_utils import update_current_webui
        from modules import json_utils as js

    except Exception as e:
        show_error_message(f"Initialization failed: {e}")
        return

    try:
        print("✅ Attempting to load Enhanced Widget UI...")
        if not load_widgets():
             raise RuntimeError("load_widgets returned False")
        print("✅ Enhanced Widget UI loaded successfully.")
    except Exception as e:
        show_error_message(e)
        print("📦 Falling back to Original Widget UI...")
        try:
            original_script = SCRIPTS / 'widgets_en.py'
            if original_script.exists():
                with open(original_script, 'r', encoding='utf-8') as f:
                    exec(f.read(), globals())
            else:
                print("❌ Original widget script not found. Cannot fall back.")
        except Exception as final_e:
            show_error_message(f"Fallback also failed: {final_e}")

# --- SCRIPT EXECUTION ---
if __name__ == "__main__" or "run_path" in globals():
    main()

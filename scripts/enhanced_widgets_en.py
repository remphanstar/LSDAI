# ~ enhanced_widgets_en.py | by ANXETY - Refactored for Tabbed UI & Enhanced UX ~

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
# --- END OF FIX ---

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

# --- WIDGET MANAGER ---
class WidgetManager:
    """Manages the creation, layout, and logic of the UI widgets."""
    
    def __init__(self):
        self.factory = WidgetFactory()
        self.widgets = {}
        self.selection_containers = {}
        
        # Define widget keys for settings persistence
        self.settings_keys = [
            'latest_webui', 'latest_extensions', 'change_webui', 'detailed_download', 
            'XL_models', 'inpainting_model', 'commit_hash', 'check_custom_nodes_deps',
            'civitai_token', 'huggingface_token', 'zrok_token', 'ngrok_token', 
            'commandline_arguments', 'theme_accent', 'empowerment', 'empowerment_output',
            'Model_url', 'Vae_url', 'LoRA_url', 'Embedding_url', 'Extensions_url', 'ADetailer_url',
            'custom_file_urls'
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
        """Constructs and returns the entire widget UI."""
        
        # --- HEADER CONTROLS (Single Line Layout using ToggleButtons) ---
        self.widgets['latest_webui'] = widgets.ToggleButton(value=True, description='Update WebUI', button_style='')
        self.widgets['latest_extensions'] = widgets.ToggleButton(value=True, description='Update Extensions', button_style='')
        self.widgets['inpainting_model'] = widgets.ToggleButton(value=False, description='Inpainting', button_style='')
        self.widgets['XL_models'] = widgets.ToggleButton(value=False, description='SDXL', button_style='')
        self.widgets['detailed_download'] = widgets.ToggleButton(value=False, description='Detailed Output', button_style='')
        
        # Create WebUI dropdown - FIXED: Correct parameter order
        self.widgets['change_webui'] = self.factory.create_dropdown(
            options=list(self.WEBUI_SELECTION.keys()),
            value='A1111',
            description='WebUI:'
        )
        
        # Header layout
        left_toggles = self.factory.create_hbox([self.widgets['latest_webui'], self.widgets['latest_extensions']], class_names=['header-group'])
        right_toggles = self.factory.create_hbox([self.widgets['inpainting_model'], self.widgets['XL_models']], class_names=['header-group'])
        
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
        # 1. Additional Configuration (Now includes API Tokens)
        # FIXED: Proper parameter order for checkboxes
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
        
        accordion = widgets.Accordion(children=[additional_vbox, custom_dl_vbox])
        accordion.set_title(0, 'Advanced Configuration & API Tokens')
        accordion.set_title(1, 'Custom Download / Empowerment')
        accordion.selected_index = None
        accordion.add_class('trimmed-box')

        # --- SAVE BUTTON ---
        save_button = self.factory.create_button('Save Settings', class_names=['button', 'button_save'])
        save_button.on_click(self.save_data)

        # --- SIDEBAR FOR G-DRIVE, IMPORT/EXPORT ---
        BTN_STYLE = {'width': '48px', 'height': '48px'}
        TOOLTIPS = ("Disconnect Google Drive", "Connect Google Drive")
        GD_status = js.read(SETTINGS_PATH, 'mountGDrive', False)
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

        # --- FINAL LAYOUT ---
        main_content = self.factory.create_vbox([header_controls, tab_widget, accordion, save_button], class_names=['main-content'])
        return self.factory.create_hbox([main_content, sidebar], class_names=['main-ui-container'])

    def setup_callbacks(self):
        """Connects widget events to their handler functions."""
        # Set up widget observers
        self.factory.observe_widget(self.widgets['change_webui'], self.update_change_webui)
        self.factory.observe_widget(self.widgets['XL_models'], self.update_xl_options)
        self.factory.observe_widget(self.widgets['empowerment'], self.update_empowerment)
        self.factory.observe_widget(self.widgets['inpainting_model'], self.filter_inpainting_models)
        
        if IN_COLAB:
            self.gdrive_button.on_click(self.handle_gdrive_toggle)
            self.export_button.on_click(self.export_settings)
            self.import_button.on_click(self.import_settings)
            output.register_callback('importSettingsFromJS', self.apply_imported_settings)
            
        # Update empowerment and webui on initial load
        self.update_empowerment({'new': self.widgets['empowerment'].value})
        self.update_change_webui({'new': self.widgets['change_webui'].value})

    def update_xl_options(self, change):
        """Handle SDXL model filtering."""
        self.filter_models(is_xl=change.get('new'))
        
    def update_change_webui(self, change):
        """Handle WebUI change updates."""
        webui = change.get('new', 'A1111')
        self.widgets['commandline_arguments'].value = self.WEBUI_SELECTION.get(webui, '')
        
        is_comfy = webui == 'ComfyUI'
        
        # Show/hide widgets based on WebUI selection
        widget_visibility = [
            ('latest_extensions', not is_comfy),
            ('check_custom_nodes_deps', is_comfy),
            ('theme_accent', not is_comfy)
        ]
        
        for widget_name, should_display in widget_visibility:
            self.widgets[widget_name].layout.display = 'flex' if should_display else 'none'
        
        # Update Extensions URL description
        self.widgets['Extensions_url'].description = 'Custom Nodes:' if is_comfy else 'Extensions:'

    def update_empowerment(self, change):
        """Handle empowerment mode toggle."""
        is_empowered = change.get('new', False)
        
        # List of widgets to hide/show based on empowerment mode
        url_widgets = [
            'Model_url', 'Vae_url', 'LoRA_url', 'Embedding_url', 
            'Extensions_url', 'ADetailer_url', 'custom_file_urls'
        ]
        
        for widget_name in url_widgets:
            self.widgets[widget_name].layout.display = 'none' if is_empowered else 'flex'
        
        self.widgets['empowerment_output'].layout.display = 'flex' if is_empowered else 'none'

    def filter_inpainting_models(self, change):
        """Handle inpainting model filtering."""
        self.filter_models(is_inpainting=change.get('new'))

    def filter_models(self, is_xl=None, is_inpainting=None):
        """Filter models based on XL and inpainting options."""
        if is_xl is None:
            is_xl = self.widgets['XL_models'].value
        if is_inpainting is None:
            is_inpainting = self.widgets['inpainting_model'].value

        # Read current model data
        all_models = self.read_model_data(SCRIPTS / '_models_data.py', 'model')
        
        if is_xl or is_inpainting:
            filtered_models = {}
            for name, url in all_models.items():
                name_lower = name.lower()
                
                if is_xl and is_inpainting:
                    # Must be both XL and inpainting
                    if ('xl' in name_lower or 'sdxl' in name_lower) and 'inpaint' in name_lower:
                        filtered_models[name] = url
                elif is_xl:
                    # Must be XL
                    if 'xl' in name_lower or 'sdxl' in name_lower:
                        filtered_models[name] = url
                elif is_inpainting:
                    # Must be inpainting
                    if 'inpaint' in name_lower:
                        filtered_models[name] = url
            
            self.update_selection_list('model', filtered_models)
        else:
            # Show all models
            self.update_selection_list('model', all_models)

    def save_data(self, button):
        """Save all widget data to settings."""
        try:
            data = {
                'model': [btn.description for btn in self.widgets.get('model', []) if btn.value],
                'vae': [btn.description for btn in self.widgets.get('vae', []) if btn.value],
                'lora': [btn.description for btn in self.widgets.get('lora', []) if btn.value],
                'cnet': [btn.description for btn in self.widgets.get('cnet', []) if btn.value],
            }
            
            # Add all other widget values
            for key in self.settings_keys:
                if key in self.widgets:
                    widget = self.widgets[key]
                    if hasattr(widget, 'value'):
                        data[key] = widget.value
            
            # Save to settings
            js.save_settings(data, section='WIDGETS')
            self.show_notification("Settings saved successfully!", "success")
                
        except Exception as e:
            print(f"Error saving settings: {e}")
            self.show_notification(f"Error saving settings: {e}", "error")

    def load_settings(self):
        """Load settings from file."""
        try:
            settings = js.load_settings(section='WIDGETS')
            if settings:
                self.apply_settings(settings)
        except Exception as e:
            print(f"Error loading settings: {e}")

    def apply_settings(self, settings):
        """Apply loaded settings to widgets."""
        # Apply to selection buttons
        for data_type in ['model', 'vae', 'lora', 'cnet']:
            selected_items = settings.get(data_type, [])
            for btn in self.widgets.get(data_type, []):
                btn.value = btn.description in selected_items
        
        # Apply to other widgets
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

    def handle_gdrive_toggle(self, button):
        """Handle Google Drive connection toggle."""
        self.show_notification("Google Drive functionality coming soon!", "info")

    def export_settings(self, button):
        """Export settings to JSON file."""
        try:
            settings = js.load_settings()
            if settings:
                import json
                settings_json = json.dumps(settings, indent=2)
                self.show_notification("Settings exported successfully!", "success")
                print("Settings JSON:", settings_json)
        except Exception as e:
            self.show_notification(f"Export failed: {e}", "error")

    def import_settings(self, button):
        """Import settings from JSON file."""
        self.show_notification("Import functionality coming soon!", "info")

    def apply_imported_settings(self, settings_str):
        """Apply imported settings from JavaScript."""
        try:
            import json
            settings = json.loads(settings_str)
            if 'WIDGETS' in settings:
                self.apply_settings(settings['WIDGETS'])
                self.show_notification("Settings imported successfully!", "success")
        except Exception as e:
            self.show_notification(f"Import failed: {e}", "error")

# --- EXECUTION ---
if __name__ == "__main__":
    WidgetFactory().load_css(CSS / 'enhanced-widgets.css')
    if IN_COLAB:
        WidgetFactory().load_js(JS / 'main-widgets.js')

    manager = WidgetManager()
    main_container = manager.build_ui()
    display(main_container)
    
    manager.load_settings()
    manager.setup_callbacks()

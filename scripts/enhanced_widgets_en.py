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

    def create_api_token_box(self, description, placeholder, url):
        """Creates a consistent UI element for API tokens."""
        widget = self.factory.create_text(description, '', placeholder)
        button = self.factory.create_html(f'''
            <a href="{url}" target="_blank" class="button button_api">
                <span class="icon">?</span><span class="text">GET</span>
            </a>
        ''')
        return self.factory.create_hbox([widget, button]), widget

    def create_selection_list(self, data_type, options_dict):
        """Creates a VBox of Checkboxes for model selection."""
        checkboxes = [self.factory.create_checkbox(name, value=False) for name in options_dict.keys()]
        self.widgets[data_type] = checkboxes
        
        container = self.factory.create_vbox(children=checkboxes, class_names=['checkbox-group'])
        self.selection_containers[data_type] = container
        return container

    def update_selection_list(self, data_type, new_options_dict):
        """Updates a VBox of Checkboxes with new options."""
        selected_values = {cb.description for cb in self.widgets.get(data_type, []) if cb.value}
        new_checkboxes = [self.factory.create_checkbox(name, value=(name in selected_values)) for name in new_options_dict.keys()]
        self.widgets[data_type] = new_checkboxes
        if data_type in self.selection_containers:
            self.selection_containers[data_type].children = tuple(new_checkboxes)
        
    def build_ui(self):
        """Constructs and returns the entire widget UI."""
        
        # --- HEADER CONTROLS ---
        self.widgets['XL_models'] = self.factory.create_checkbox('SDXL', False, class_names=['header-toggle'])
        self.widgets['inpainting_model'] = self.factory.create_checkbox('Inpainting', False, class_names=['header-toggle'])
        self.widgets['latest_webui'] = self.factory.create_checkbox('Update WebUI', True, class_names=['header-toggle'])
        self.widgets['latest_extensions'] = self.factory.create_checkbox('Update Extensions', True, class_names=['header-toggle'])
        
        left_toggles = self.factory.create_hbox([self.widgets['XL_models'], self.widgets['inpainting_model']], class_names=['header-left-group'])
        right_toggles = self.factory.create_hbox([self.widgets['latest_webui'], self.widgets['latest_extensions']], class_names=['header-right-group'])
        
        self.widgets['change_webui'] = self.factory.create_dropdown(list(self.WEBUI_SELECTION.keys()), 'WebUI:', 'A1111')
        self.widgets['detailed_download'] = widgets.ToggleButton(value=False, description='Detailed Output', button_style='', tooltip='Toggle detailed download logs')
        
        header_controls = self.factory.create_hbox([
            left_toggles,
            self.factory.create_vbox([self.widgets['change_webui'], self.widgets['detailed_download']], class_names=['header-center-group']),
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
        tab_widget.add_class('trimmed-box')
        
        # --- ACCORDION FOR OTHER SETTINGS ---
        # 1. Additional Configuration
        self.widgets['check_custom_nodes_deps'] = self.factory.create_checkbox('Check ComfyUI Dependencies', True, layout={'display': 'none'})
        self.widgets['commit_hash'] = self.factory.create_text('Commit Hash:', '', 'Optional: Use a specific commit')
        self.widgets['commandline_arguments'] = self.factory.create_text('Arguments:', self.WEBUI_SELECTION['A1111'])
        accent_colors = ['anxety', 'blue', 'green', 'peach', 'pink', 'red', 'yellow']
        self.widgets['theme_accent'] = self.factory.create_dropdown(accent_colors, 'Theme Accent:', 'anxety')
        additional_vbox = self.factory.create_vbox([
            self.widgets['check_custom_nodes_deps'], self.widgets['commit_hash'], self.widgets['commandline_arguments'], self.widgets['theme_accent']
        ])

        # 2. API Tokens
        civitai_box, self.widgets['civitai_token'] = self.create_api_token_box('CivitAI Token:', 'Paste your CivitAI API token here', 'https://civitai.com/user/account')
        hf_box, self.widgets['huggingface_token'] = self.create_api_token_box('HuggingFace Token:', 'Paste your HuggingFace token here', 'https://huggingface.co/settings/tokens')
        zrok_box, self.widgets['zrok_token'] = self.create_api_token_box('Zrok Token:', 'Paste your Zrok token here', 'https://zrok.io/')
        ngrok_box, self.widgets['ngrok_token'] = self.create_api_token_box('Ngrok Token:', 'Paste your Ngrok token here', 'https://dashboard.ngrok.com/get-started/your-authtoken')
        tokens_vbox = self.factory.create_vbox([civitai_box, hf_box, zrok_box, ngrok_box])

        # 3. Custom Download
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
        
        accordion = widgets.Accordion(children=[additional_vbox, tokens_vbox, custom_dl_vbox])
        accordion.set_title(0, 'Additional Configuration')
        accordion.set_title(1, 'API Tokens')
        accordion.set_title(2, 'Custom Download / Empowerment')
        accordion.selected_index = None
        accordion.add_class('trimmed-box')

        # --- SAVE BUTTON ---
        save_button = self.factory.create_button('Save Settings', class_names=['button', 'button_save'])
        save_button.on_click(self.save_data)

        # --- FINAL LAYOUT ---
        return self.factory.create_vbox([header_controls, tab_widget, accordion, save_button], class_names=['main-ui-container'])

    def setup_callbacks(self):
        """Connects widget events to their handler functions."""
        self.factory.connect_widgets([(self.widgets['change_webui'], 'value')], self.update_change_webui)
        self.factory.connect_widgets([(self.widgets['XL_models'], 'value')], self.update_xl_options)
        self.factory.connect_widgets([(self.widgets['empowerment'], 'value')], self.update_empowerment)
        self.factory.connect_widgets([(self.widgets['inpainting_model'], 'value')], self.filter_inpainting_models)
        self.update_empowerment({'new': self.widgets['empowerment'].value}, None)
        self.update_change_webui({'new': self.widgets['change_webui'].value}, None)

    # --- CALLBACK FUNCTIONS ---
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

        if is_inpainting:
            options = {name: data for name, data in full_model_dict.items() if data.get('inpainting')}
        else:
            options = {name: data for name, data in full_model_dict.items() if not data.get('inpainting')}
        
        self.update_selection_list('model', options)

    # --- DATA HANDLING ---
    def get_selected_checkboxes(self, data_type):
        """Helper to get the names of selected checkboxes for a given type."""
        if data_type in self.widgets and isinstance(self.widgets[data_type], list):
            return [cb.description for cb in self.widgets[data_type] if cb.value]
        return []

    def save_settings(self):
        """Saves the current state of all widgets to the settings file."""
        widgets_values = {}
        for key in self.settings_keys:
            if key in ['model', 'vae', 'lora', 'controlnet']:
                widgets_values[key] = self.get_selected_checkboxes(key)
            elif key in self.widgets:
                # Special handling for ToggleButton
                if isinstance(self.widgets[key], widgets.ToggleButton):
                     widgets_values[key] = 'on' if self.widgets[key].value else 'off'
                else:
                    widgets_values[key] = self.widgets[key].value
        
        js.save(SETTINGS_PATH, 'WIDGETS', widgets_values)
        update_current_webui(self.widgets['change_webui'].value)

    def load_settings(self):
        """Loads widget states from the settings file."""
        if not js.key_exists(SETTINGS_PATH, 'WIDGETS'): return
        
        widget_data = js.read(SETTINGS_PATH, 'WIDGETS')
        for key in self.settings_keys:
            if key in widget_data and key in self.widgets:
                try:
                    if key in ['model', 'vae', 'lora', 'controlnet']:
                        selected_names = widget_data.get(key, [])
                        for cb in self.widgets[key]:
                            if cb.description in selected_names:
                                cb.value = True
                    # Special handling for ToggleButton
                    elif isinstance(self.widgets[key], widgets.ToggleButton):
                        self.widgets[key].value = widget_data.get(key) == 'on'
                    else:
                        self.widgets[key].value = widget_data.get(key, self.widgets[key].value)
                except Exception as e:
                    print(f"Warning: could not load setting for {key}: {e}")

    def save_data(self, button):
        self.save_settings()
        self.factory.close(main_container, class_names=['hide'], delay=0.5)

# --- EXECUTION ---
if __name__ == "__main__":
    WidgetFactory().load_css(CSS / 'enhanced-widgets.css')
    if IN_COLAB:
        WidgetFactory().load_js(JS / 'enhanced-widgets.js')

    manager = WidgetManager()
    main_container = manager.build_ui()
    display(main_container)
    
    manager.load_settings()
    manager.setup_callbacks()

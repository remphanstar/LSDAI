# ~ enhanced_widgets_en.py | by ANXETY - Refactored for Stability & Functionality ~

from modules.widget_factory import WidgetFactory
from modules.webui_utils import update_current_webui
from modules import json_utils as js

from IPython.display import display, Javascript
import ipywidgets as widgets
from pathlib import Path
import json
import os
import sys

# --- ROBUST PATH RESOLUTION (FIX V2) ---
# This block makes the script self-sufficient and fixes the "FileNotFoundError".
# It uses a multi-layered approach to reliably find its path, making it
# immune to kernel restarts and execution context issues.
def find_script_path():
    """Find the absolute path to the 'scripts' directory using multiple methods."""
    # Method 1: __file__ (most reliable for standard .py execution)
    try:
        return Path(__file__).parent.resolve()
    except NameError:
        pass  # __file__ is not defined in notebook %run context

    # Method 2: Environment variable (set by Cell 1, reliable in the user's workflow)
    env_path = os.environ.get('scr_path')
    if env_path:
        scripts_dir = Path(env_path) / 'scripts'
        if scripts_dir.exists() and (scripts_dir / '_models-data.py').exists():
            return scripts_dir

    # Method 3: Current Working Directory (fallback for interactive sessions)
    cwd = Path.cwd()
    if (cwd / 'scripts' / '_models-data.py').exists():
        return cwd / 'scripts'
    if cwd.name == 'scripts' and (cwd / '_models-data.py').exists():
        return cwd

    # Final fallback: Hardcoded path for common cloud environments
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
    # Exit gracefully if paths can't be found, to avoid further errors.
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
        self.settings_keys = [
            'XL_models', 'model', 'model_num', 'inpainting_model', 'vae', 'vae_num', 'lora',
            'latest_webui', 'latest_extensions', 'check_custom_nodes_deps', 'change_webui', 'detailed_download',
            'controlnet', 'controlnet_num', 'commit_hash',
            'civitai_token', 'huggingface_token', 'zrok_token', 'ngrok_token', 'commandline_arguments', 'theme_accent',
            'empowerment', 'empowerment_output',
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
        """Reads model, VAE, or ControlNet data from the specified file."""
        type_map = {
            'model': ('model_list', ['none']),
            'vae': ('vae_list', ['none', 'ALL']),
            'cnet': ('controlnet_list', ['none', 'ALL']),
            'lora': ('lora_list', ['none', 'ALL'])
        }
        key, prefixes = type_map[data_type]
        local_vars = {}
        try:
            with open(file_path) as f:
                exec(f.read(), {}, local_vars)
            # Return the full dictionary for filtering, not just keys
            if data_type == 'model':
                return local_vars.get(key, {})
            names = list(local_vars.get(key, {}).keys())
            return prefixes + names
        except Exception as e:
            print(f"Warning: Could not load {data_type} data from {file_path}: {e}")
            return prefixes if data_type != 'model' else {}

    def get_safe_default(self, options, preferred_defaults):
        """Gets the first available option from a list of preferred defaults."""
        for default in preferred_defaults:
            if default in options:
                return default
        return options[0] if options else None

    def create_api_token_box(self, description, placeholder, url):
        """Creates a consistent UI element for API tokens."""
        widget = self.factory.create_text(description, '', placeholder)
        button = self.factory.create_html(f'''
            <a href="{url}" target="_blank" class="button button_api">
                <span class="icon">?</span><span class="text">GET</span>
            </a>
        ''')
        return self.factory.create_hbox([widget, button]), widget

    def build_ui(self):
        """Constructs and returns the entire widget UI."""
        # --- MODEL SELECTION ---
        model_header = self.factory.create_header('Model Selection')
        model_dict = self.read_model_data(SCRIPTS / '_models-data.py', 'model')
        model_options = ['none'] + list(model_dict.keys())
        model_default = self.get_safe_default(model_options, ['D5K6.0'])
        self.widgets['model'] = self.factory.create_select_multiple(model_options, 'Model:', (model_default,))
        self.widgets['model_num'] = self.factory.create_text('Model Number:', '', 'e.g., 1, 5-10')
        self.widgets['inpainting_model'] = self.factory.create_checkbox('Inpainting Models', False, class_names=['inpaint'])
        self.widgets['XL_models'] = self.factory.create_checkbox('SDXL', False, class_names=['sdxl'])
        model_box = self.factory.create_vbox([
            model_header, self.widgets['model'], self.widgets['model_num'],
            self.factory.create_hbox([self.widgets['inpainting_model'], self.widgets['XL_models']])
        ], class_names=['container'])

        # --- VAE SELECTION ---
        vae_header = self.factory.create_header('VAE Selection')
        vae_options = self.read_model_data(SCRIPTS / '_models-data.py', 'vae')
        vae_default = self.get_safe_default(vae_options, ['vae-ft-mse-840000-ema-pruned'])
        self.widgets['vae'] = self.factory.create_dropdown(vae_options, 'Vae:', vae_default)
        self.widgets['vae_num'] = self.factory.create_text('Vae Number:', '', 'e.g., 1, 2')
        vae_box = self.factory.create_vbox([vae_header, self.widgets['vae'], self.widgets['vae_num']], class_names=['container'])

        # --- LORA SELECTION ---
        lora_header = self.factory.create_header('LoRA Selection')
        lora_options = self.read_model_data(SCRIPTS / '_models-data.py', 'lora')
        self.widgets['lora'] = self.factory.create_select_multiple(lora_options, 'LoRA:', ('none',))
        lora_box = self.factory.create_vbox([lora_header, self.widgets['lora']], class_names=['container'])
        
        # --- ACCORDION SECTIONS ---
        
        # 1. Additional Configuration
        self.widgets['latest_webui'] = self.factory.create_checkbox('Update WebUI', True)
        self.widgets['latest_extensions'] = self.factory.create_checkbox('Update Extensions', True)
        self.widgets['check_custom_nodes_deps'] = self.factory.create_checkbox('Check ComfyUI Dependencies', True, layout={'display': 'none'})
        self.widgets['change_webui'] = self.factory.create_dropdown(list(self.WEBUI_SELECTION.keys()), 'WebUI:', 'A1111')
        self.widgets['detailed_download'] = self.factory.create_dropdown(['off', 'on'], 'Detailed Log:', 'off')
        controlnet_options = self.read_model_data(SCRIPTS / '_models-data.py', 'cnet')
        self.widgets['controlnet'] = self.factory.create_select_multiple(controlnet_options, 'ControlNet:', ('none',))
        self.widgets['controlnet_num'] = self.factory.create_text('ControlNet Number:', '', 'e.g., 1, 3-5')
        self.widgets['commit_hash'] = self.factory.create_text('Commit Hash:', '', 'Optional: Use a specific commit')
        self.widgets['commandline_arguments'] = self.factory.create_text('Arguments:', self.WEBUI_SELECTION['A1111'])
        accent_colors = ['anxety', 'blue', 'green', 'peach', 'pink', 'red', 'yellow']
        self.widgets['theme_accent'] = self.factory.create_dropdown(accent_colors, 'Theme Accent:', 'anxety')
        
        additional_vbox = self.factory.create_vbox([
            self.factory.create_hbox([self.widgets['latest_webui'], self.widgets['latest_extensions'], self.widgets['check_custom_nodes_deps']]),
            self.factory.create_hbox([self.widgets['change_webui'], self.widgets['detailed_download']]),
            widgets.HTML('<hr>'),
            self.widgets['controlnet'], self.widgets['controlnet_num'], self.widgets['commit_hash'],
            widgets.HTML('<hr>'),
            self.factory.create_hbox([self.widgets['commandline_arguments'], self.widgets['theme_accent']])
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
        
        # Create Accordion
        accordion = widgets.Accordion(children=[additional_vbox, tokens_vbox, custom_dl_vbox])
        accordion.set_title(0, 'Additional Configuration')
        accordion.set_title(1, 'API Tokens')
        accordion.set_title(2, 'Custom Download / Empowerment')
        accordion.selected_index = None # Start collapsed

        # --- SAVE BUTTON ---
        save_button = self.factory.create_button('Save Settings', class_names=['button', 'button_save'])
        save_button.on_click(self.save_data)

        # --- FINAL LAYOUT ---
        model_vae_lora_box = self.factory.create_hbox([model_box, vae_box, lora_box])
        
        widget_container = self.factory.create_vbox(
            [model_vae_lora_box, accordion, save_button],
            layout={'width': '100%'}
        )
        
        return widget_container

    def setup_callbacks(self):
        """Connects widget events to their handler functions."""
        self.factory.connect_widgets([(self.widgets['change_webui'], 'value')], self.update_change_webui)
        self.factory.connect_widgets([(self.widgets['XL_models'], 'value')], self.update_xl_options)
        self.factory.connect_widgets([(self.widgets['empowerment'], 'value')], self.update_empowerment)
        self.factory.connect_widgets([(self.widgets['inpainting_model'], 'value')], self.filter_inpainting_models)
        # Initial state update
        self.update_empowerment({'new': self.widgets['empowerment'].value}, None)
        self.update_change_webui({'new': self.widgets['change_webui'].value}, None)

    # --- CALLBACK FUNCTIONS ---
    def update_xl_options(self, change, widget):
        is_xl = change['new']
        data_file = SCRIPTS / ('_xl-models-data.py' if is_xl else '_models-data.py')
        
        model_dict = self.read_model_data(data_file, 'model')
        self.widgets['model'].options = ['none'] + list(model_dict.keys())
        self.widgets['vae'].options = self.read_model_data(data_file, 'vae')
        self.widgets['lora'].options = self.read_model_data(data_file, 'lora')
        self.widgets['controlnet'].options = self.read_model_data(data_file, 'cnet')

        if is_xl:
            self.widgets['model'].value = (self.get_safe_default(self.widgets['model'].options, ['uberRealisticPornMerge-xlV6Final-inpainting']),)
            self.widgets['vae'].value = self.get_safe_default(self.widgets['vae'].options, ['Pony Standard VAE'])
            self.widgets['lora'].value = ('none',)
            self.widgets['controlnet'].value = ('none',)
            self.widgets['inpainting_model'].value = False
            self.widgets['inpainting_model'].disabled = True
        else:
            self.widgets['model'].value = (self.get_safe_default(self.widgets['model'].options, ['D5K6.0']),)
            self.widgets['vae'].value = self.get_safe_default(self.widgets['vae'].options, ['vae-ft-mse-840000-ema-pruned'])
            self.widgets['lora'].value = ('none',)
            self.widgets['controlnet'].value = ('none',)
            self.widgets['inpainting_model'].disabled = False
        
        # After changing options, re-apply inpainting filter if it's active
        self.filter_inpainting_models({'new': self.widgets['inpainting_model'].value}, None)

    def update_change_webui(self, change, widget):
        webui = change['new']
        self.widgets['commandline_arguments'].value = self.WEBUI_SELECTION.get(webui, '')
        is_comfy = webui == 'ComfyUI'
        self.widgets['latest_extensions'].layout.display = 'none' if is_comfy else 'flex'
        self.widgets['check_custom_nodes_deps'].layout.display = 'flex' if is_comfy else 'none'
        self.widgets['theme_accent'].layout.display = 'none' if is_comfy else 'flex'
        self.widgets['Extensions_url'].description = 'Custom Nodes:' if is_comfy else 'Extensions:'

    def update_empowerment(self, change, widget):
        if change['new']:
            self.custom_dl_container.layout.display = 'none'
            self.widgets['empowerment_output'].layout.display = 'flex'
        else:
            self.custom_dl_container.layout.display = 'flex'
            self.widgets['empowerment_output'].layout.display = 'none'

    def filter_inpainting_models(self, change, widget):
        is_inpainting = change.get('new', False) # Safely get value
        # Do not run if in SDXL mode, as it's disabled
        if self.widgets['XL_models'].value:
            return

        data_file = SCRIPTS / '_models-data.py'
        full_model_dict = self.read_model_data(data_file, 'model')

        if is_inpainting:
            options = ['none'] + [name for name, data in full_model_dict.items() if data.get('inpainting')]
        else:
            options = ['none'] + list(full_model_dict.keys())
        
        # Preserve current selection if possible
        current_selection = self.widgets['model'].value
        new_selection = tuple(s for s in current_selection if s in options)
        
        self.widgets['model'].options = options
        self.widgets['model'].value = new_selection if new_selection else (options[0] if options else ('none',))

    # --- DATA HANDLING ---
    def save_settings(self):
        widgets_values = {key: self.widgets[key].value for key in self.settings_keys if key in self.widgets}
        js.save(SETTINGS_PATH, 'WIDGETS', widgets_values)
        update_current_webui(self.widgets['change_webui'].value)

    def load_settings(self):
        if js.key_exists(SETTINGS_PATH, 'WIDGETS'):
            widget_data = js.read(SETTINGS_PATH, 'WIDGETS')
            for key in self.settings_keys:
                if key in widget_data and key in self.widgets:
                    try:
                        self.widgets[key].value = widget_data.get(key, self.widgets[key].value)
                    except Exception as e:
                        print(f"Warning: could not load setting for {key}: {e}")

    def save_data(self, button):
        self.save_settings()
        # Close the entire container when saved
        self.factory.close(main_container, class_names=['hide'], delay=0.5)

# --- EXECUTION ---
if __name__ == "__main__":
    # Load CSS and JS
    WidgetFactory().load_css(CSS / 'enhanced-widgets.css')
    if IN_COLAB:
        WidgetFactory().load_js(JS / 'enhanced-widgets.js')

    # Create and display UI
    manager = WidgetManager()
    main_container = manager.build_ui()
    display(main_container)
    
    # Load saved settings and setup interactions
    manager.load_settings()
    manager.setup_callbacks()

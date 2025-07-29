# /content/LSDAI/scripts/enhanced_widgets_en.py

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
    try: return Path(__file__).parent.resolve()
    except NameError: pass
    env_path = os.environ.get('scr_path')
    if env_path and (Path(env_path) / 'scripts').exists(): return Path(env_path) / 'scripts'
    cwd = Path.cwd()
    if (cwd / 'scripts').exists(): return cwd / 'scripts'
    if cwd.name == 'scripts': return cwd
    return Path('/content/LSDAI/scripts')

SCRIPTS = find_script_path()
SCR_PATH = SCRIPTS.parent
SETTINGS_PATH = SCR_PATH / 'settings.json'
CSS = SCR_PATH / 'CSS'
JS = SCR_PATH / 'JS'

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
        key_map = {'model': 'model_list', 'vae': 'vae_list', 'cnet': 'controlnet_list', 'lora': 'lora_list'}
        key = key_map.get(data_type)
        local_vars = {}
        try:
            with open(file_path) as f:
                exec(f.read(), {}, local_vars)
            return local_vars.get(key, {})
        except Exception as e:
            return {}

    def create_api_token_box(self, description, placeholder, url, env_var):
        widget = self.factory.create_text(description, '', placeholder)
        token_from_env = os.getenv(env_var)
        if token_from_env:
            widget.value = "Token set in Cell 1"
            widget.disabled = True
        
        button = self.factory.create_html(f'<a href="{url}" target="_blank" class="button button_api"><span class="icon">?</span><span class="text">GET</span></a>')
        return self.factory.create_hbox([widget, button]), widget

    def create_selection_list(self, data_type, options_dict):
        buttons = [widgets.ToggleButton(description=name, value=False, button_style='', tooltip=name) for name in options_dict.keys()]
        self.widgets[data_type] = buttons
        container = self.factory.create_vbox(children=buttons, class_names=['selection-group'])
        self.selection_containers[data_type] = container
        return container

    def update_selection_list(self, data_type, new_options_dict):
        selected_values = {btn.description for btn in self.widgets.get(data_type, []) if btn.value}
        new_buttons = [widgets.ToggleButton(description=name, value=(name in selected_values), button_style='', tooltip=name) for name in new_options_dict.keys()]
        self.widgets[data_type] = new_buttons
        if data_type in self.selection_containers:
            self.selection_containers[data_type].children = tuple(new_buttons)
        
    def build_ui(self):
        self.widgets.update({
            'latest_webui': widgets.ToggleButton(value=True, description='Update WebUI'),
            'latest_extensions': widgets.ToggleButton(value=True, description='Update Extensions'),
            'inpainting_model': widgets.ToggleButton(value=False, description='Inpainting'),
            'XL_models': widgets.ToggleButton(value=False, description='SDXL'),
            'detailed_download': widgets.ToggleButton(value=False, description='Detailed Output'),
            'change_webui': self.factory.create_dropdown(list(self.WEBUI_SELECTION.keys()), 'A1111', 'WebUI:')
        })
        
        header_controls = self.factory.create_hbox([
            self.factory.create_hbox([self.widgets['latest_webui'], self.widgets['latest_extensions']], class_names=['header-group']),
            self.widgets['change_webui'], self.widgets['detailed_download'],
            self.factory.create_hbox([self.widgets['inpainting_model'], self.widgets['XL_models']], class_names=['header-group'])
        ], class_names=['header-controls'])

        tab_children, tab_titles, data_keys = [], ['Models', 'VAEs', 'LoRAs', 'ControlNets'], ['model', 'vae', 'lora', 'cnet']
        for key in data_keys:
            tab_children.append(self.create_selection_list(key, self.read_model_data(SCRIPTS / '_models_data.py', key)))
        
        tab_widget = widgets.Tab(children=tab_children)
        for i, title in enumerate(tab_titles): tab_widget.set_title(i, title)
        tab_widget.add_class('selection-tabs')
        
        self.widgets.update({
            'check_custom_nodes_deps': self.factory.create_checkbox(description='Check ComfyUI Dependencies', value=True, layout={'display': 'none'}),
            'commit_hash': self.factory.create_text('Commit Hash:', '', 'Optional: Use a specific commit'),
            'commandline_arguments': self.factory.create_text('Arguments:', self.WEBUI_SELECTION['A1111']),
            'theme_accent': self.factory.create_dropdown(['anxety', 'blue', 'green', 'peach', 'pink', 'red', 'yellow'], 'anxety', 'Theme Accent:'),
            'empowerment': self.factory.create_checkbox('Empowerment Mode', False),
            'empowerment_output': self.factory.create_textarea('', 'Use special tags like $ckpt, $lora, etc.'),
            'Model_url': self.factory.create_text('Model URL:'),
            'Vae_url': self.factory.create_text('Vae URL:'),
            'LoRA_url': self.factory.create_text('LoRA URL:'),
            'Embedding_url': self.factory.create_text('Embedding URL:'),
            'Extensions_url': self.factory.create_text('Extensions URL:'),
            'ADetailer_url': self.factory.create_text('ADetailer URL:'),
            'custom_file_urls': self.factory.create_text('File (txt):')
        })
        civitai_box, self.widgets['civitai_token'] = self.create_api_token_box('CivitAI Token:', 'Paste token here', 'https://civitai.com/user/account', 'CIVITAI_API_TOKEN')
        hf_box, self.widgets['huggingface_token'] = self.create_api_token_box('HuggingFace Token:', 'Paste token here', 'https://huggingface.co/settings/tokens', 'HUGGINGFACE_API_TOKEN')
        zrok_box, self.widgets['zrok_token'] = self.create_api_token_box('Zrok Token:', 'Paste token here', 'https://zrok.io/', 'ZROK_API_TOKEN')
        ngrok_box, self.widgets['ngrok_token'] = self.create_api_token_box('Ngrok Token:', 'Paste token here', 'https://dashboard.ngrok.com/get-started/your-authtoken', 'NGROK_API_TOKEN')

        accordion = widgets.Accordion(children=[
            self.factory.create_vbox([self.widgets[k] for k in ['check_custom_nodes_deps', 'commit_hash', 'commandline_arguments', 'theme_accent']] + [widgets.HTML('<hr class="divider">'), civitai_box, hf_box, zrok_box, ngrok_box]),
            self.factory.create_vbox([self.widgets['empowerment'], self.widgets['empowerment_output']] + [self.widgets[k] for k in ['Model_url', 'Vae_url', 'LoRA_url', 'Embedding_url', 'Extensions_url', 'ADetailer_url', 'custom_file_urls']])
        ])
        accordion.set_title(0, 'Advanced Configuration & API Tokens'); accordion.set_title(1, 'Custom Download / Empowerment')
        accordion.add_class('trimmed-box')

        save_button = self.factory.create_button('Save Settings', class_names=['button', 'button_save']); save_button.on_click(self.save_data)
        self.gdrive_button = self.factory.create_button('📁', layout={'width': '48px', 'height': '48px'}, class_names=['side-button'])
        self.export_button = self.factory.create_button('📤', layout={'width': '48px', 'height': '48px'}, class_names=['side-button'], tooltip="Export settings")
        self.import_button = self.factory.create_button('📥', layout={'width': '48px', 'height': '48px'}, class_names=['side-button'], tooltip="Import settings")
        self.notification_popup = self.factory.create_html('', class_names=['notification-popup', 'hidden'])

        sidebar = self.factory.create_vbox([self.gdrive_button, self.export_button, self.import_button, self.notification_popup], class_names=['sidebar'])
        if not IN_COLAB: sidebar.layout.display = 'none'

        return self.factory.create_hbox([self.factory.create_vbox([header_controls, tab_widget, accordion, save_button], class_names=['main-content']), sidebar], class_names=['main-ui-container'])

    def setup_callbacks(self):
        self.factory.observe_widget(self.widgets['change_webui'], self.update_change_webui)
        self.factory.observe_widget(self.widgets['XL_models'], self.update_xl_options)
        self.factory.observe_widget(self.widgets['empowerment'], self.update_empowerment)
        self.factory.observe_widget(self.widgets['inpainting_model'], self.filter_inpainting_models)
        if IN_COLAB:
            self.gdrive_button.on_click(self.handle_gdrive_toggle)
            self.export_button.on_click(self.export_settings)
            self.import_button.on_click(self.import_settings)
            output.register_callback('importSettingsFromJS', self.apply_imported_settings)
        self.update_empowerment({'new': self.widgets['empowerment'].value})
        self.update_change_webui({'new': self.widgets['change_webui'].value})

    def update_xl_options(self, change): self.filter_models(is_xl=change.get('new'))
    def update_change_webui(self, change):
        webui = change.get('new', 'A1111')
        self.widgets['commandline_arguments'].value = self.WEBUI_SELECTION.get(webui, '')
        is_comfy = webui == 'ComfyUI'
        for w_name, display_status in [('latest_extensions', not is_comfy), ('check_custom_nodes_deps', is_comfy), ('theme_accent', not is_comfy)]:
            self.widgets[w_name].layout.display = 'flex' if display_status else 'none'
        self.widgets['Extensions_url'].description = 'Custom Nodes:' if is_comfy else 'Extensions:'
    def update_empowerment(self, change):
        is_empowered = change.get('new', False)
        for w in [self.widgets[k] for k in ['Model_url', 'Vae_url', 'LoRA_url', 'Embedding_url', 'Extensions_url', 'ADetailer_url', 'custom_file_urls']]:
            w.layout.display = 'none' if is_empowered else 'flex'
        self.widgets['empowerment_output'].layout.display = 'flex' if is_empowered else 'none'
    def filter_inpainting_models(self, change): self.filter_models(is_inpainting=change.get('new'))
    def filter_models(self, is_xl=None, is_inpainting=None):
        if is_xl is None: is_xl = self.widgets['XL_models'].value
        if is_inpainting is None: is_inpainting = self.widgets['inpainting_model'].value
        if is_xl: is_inpainting = False; self.widgets['inpainting_model'].value = False; self.widgets['inpainting_model'].disabled = True
        else: self.widgets['inpainting_model'].disabled = False
        data_file = SCRIPTS / ('_xl_models_data.py' if is_xl else '_models_data.py')
        for key in ['model', 'vae', 'lora', 'cnet']:
            full_dict = self.read_model_data(data_file, key)
            if key == 'model':
                options = {n: d for n, d in full_dict.items() if d.get('inpainting', False) == is_inpainting}
            else:
                options = full_dict
            self.update_selection_list(key, options)

    def handle_gdrive_toggle(self, btn):
        btn.toggle = not getattr(btn, 'toggle', False)
        btn.tooltip = ("Disconnect", "Connect")[not btn.toggle]
        btn.remove_class('active') if not btn.toggle else btn.add_class('active')
    def show_notification(self, message, m_type='info'):
        icon = {'success': '✅', 'error': '❌', 'info': 'ℹ️', 'warning': '⚠️'}.get(m_type, 'ℹ️')
        self.notification_popup.value = f'<div class="notification {m_type}"><span class="icon">{icon}</span>{message}</div>'
        self.notification_popup.remove_class('hidden')
        display(Javascript("setTimeout(() => { document.querySelector('.notification-popup').classList.add('hidden'); }, 3000)"))
    def export_settings(self, btn):
        settings_data = {'widgets': self.save_settings_to_dict(), 'mountGDrive': getattr(self.gdrive_button, 'toggle', False)}
        display(Javascript(f'downloadJson({json.dumps(settings_data)});'))
        self.show_notification("Settings exported!", "success")
    def import_settings(self, btn): display(Javascript('openFilePicker();'))
    def apply_imported_settings(self, data):
        try:
            if 'widgets' in data: self.load_settings_data(data['widgets'])
            if 'mountGDrive' in data: self.gdrive_button.toggle = data['mountGDrive']
            self.show_notification("Settings imported!", "success")
        except Exception as e: self.show_notification(f"Import failed: {e}", "error")

    def get_selected_toggles(self, data_type): return [btn.description for btn in self.widgets.get(data_type, []) if btn.value]
    def save_settings_to_dict(self):
        vals = {}
        for key in self.settings_keys:
            if key in ['model', 'vae', 'lora', 'controlnet']:
                vals[key] = self.get_selected_toggles(key)
            elif key in self.widgets:
                vals[key] = 'on' if isinstance(self.widgets[key], widgets.ToggleButton) and self.widgets[key].value else self.widgets[key].value
        return vals
    def save_settings(self):
        js.save(SETTINGS_PATH, 'WIDGETS', self.save_settings_to_dict())
        js.save(SETTINGS_PATH, 'mountGDrive', getattr(self.gdrive_button, 'toggle', False))
        update_current_webui(self.widgets['change_webui'].value)
    def load_settings_data(self, widget_data):
        for key in self.settings_keys:
            if key in widget_data and key in self.widgets:
                try:
                    if key in ['civitai_token', 'huggingface_token', 'zrok_token', 'ngrok_token'] and self.widgets[key].disabled: continue
                    if key in ['model', 'vae', 'lora', 'controlnet']:
                        for btn in self.widgets[key]: btn.value = btn.description in widget_data.get(key, [])
                    elif isinstance(self.widgets[key], widgets.ToggleButton): self.widgets[key].value = widget_data.get(key) == 'on'
                    else: self.widgets[key].value = widget_data.get(key, self.widgets[key].value)
                except Exception: pass
    def load_settings(self):
        if js.key_exists(SETTINGS_PATH, 'WIDGETS'): self.load_settings_data(js.read(SETTINGS_PATH, 'WIDGETS'))
        if IN_COLAB: self.gdrive_button.toggle = js.read(SETTINGS_PATH, 'mountGDrive', False)
    def save_data(self, button):
        self.save_settings()
        self.show_notification("Settings Saved!", "success")

# --- Main Execution ---
if __name__ == "__main__":
    WidgetFactory().load_css(CSS / 'enhanced-widgets.css')
    if IN_COLAB: WidgetFactory().load_js(JS / 'main-widgets.js')
    manager = WidgetManager()
    main_container = manager.build_ui()
    display(main_container)
    manager.load_settings()
    manager.setup_callbacks()

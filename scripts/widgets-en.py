# ~ widgets-en.py | by ANXETY - IMPROVED VERSION MATCHING ORIGINAL SDAIGEN ~

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
            names = list(data_dict.keys())
            return prefixes + names
        except Exception as e:
            print(f"Warning: Could not load {data_type} data: {e}")
            return prefixes

    def get_safe_default(self, options, preferred_defaults):
        """Get the first available option from preferred defaults."""
        for default in preferred_defaults:
            if default in options:
                return default
        return next((opt for opt in options if opt != 'none'), options[0] if options else 'none')

# Initialize WidgetManager
wm = WidgetManager()
factory = wm.factory
HR = widgets.HTML('<hr>')

WEBUI_SELECTION = {
    'A1111': "--xformers --no-half-vae --share --lowram",
    'ComfyUI': "--dont-print-server",
    'Forge': "--xformers --cuda-stream --pin-shared-memory",
    'Classic': "--persistent-patches --cuda-stream --pin-shared-memory",
    'ReForge': "--xformers --cuda-stream --pin-shared-memory",
    'SD-UX': "--xformers --no-half-vae"
}

# --- MODEL SECTION ---
model_header = factory.create_header('Model Selection')

# Load model data
try:
    model_options = wm.read_model_data(f"{SCRIPTS}/_models-data.py", 'model')
except Exception as e:
    print(f"Warning: Could not load model data: {e}")
    model_options = ['none']

# Model dropdown with better styling
model_widget = factory.create_select_multiple(
    model_options, 
    'Models:', 
    ('none',),
    layout={'height': '120px', 'width': '100%'}
)

model_num_widget = factory.create_text(
    'Model Numbers:', 
    '', 
    'Enter model numbers for download (comma-separated)'
)

# Checkboxes with better layout
inpainting_model_widget = factory.create_checkbox(
    'Include Inpainting Variants', 
    False, 
    class_names=['inpaint'], 
    layout={'width': '250px'}
)

XL_models_widget = factory.create_checkbox(
    'SDXL Models', 
    False, 
    class_names=['sdxl']
)

model_options_panel = factory.create_hbox([
    inpainting_model_widget, 
    XL_models_widget
], layout={'justify_content': 'space-between'})

wm.widgets.update({
    'model': model_widget,
    'model_num': model_num_widget,
    'inpainting_model': inpainting_model_widget,
    'XL_models': XL_models_widget
})

# --- VAE SECTION ---
vae_header = factory.create_header('VAE Selection')
vae_options = wm.read_model_data(f"{SCRIPTS}/_models-data.py", 'vae')

# VAE preferred defaults matching original
vae_preferred_defaults = [
    'vae-ft-mse-840000-ema-pruned | 840000 | 840k SD1.5 VAE - vae-ft-mse-840k',
    'ClearVAE(SD1.5) - v2.3',
    'none'
]
vae_default = wm.get_safe_default(vae_options, vae_preferred_defaults)
vae_widget = factory.create_dropdown(vae_options, 'Vae:', vae_default)

vae_num_widget = factory.create_text('Vae Number:', '', 'Enter vae numbers for download.')

wm.widgets.update({
    'vae': vae_widget,
    'vae_num': vae_num_widget
})

# --- LORA SECTION ---
lora_header = factory.create_header('LoRA Selection')
lora_options = wm.read_model_data(f"{SCRIPTS}/_models-data.py", 'lora')
lora_widget = factory.create_select_multiple(
    lora_options, 
    'LoRA:', 
    ('none',),
    layout={'height': '100px'}
)

wm.widgets.update({
    'lora': lora_widget
})

# --- ADDITIONAL SECTION ---
additional_header = factory.create_header('Additional')

# Update checkboxes
latest_webui_widget = factory.create_checkbox('Update WebUI', True)
latest_extensions_widget = factory.create_checkbox('Update Extensions', True)
check_custom_nodes_deps_widget = factory.create_checkbox('Check Custom-Nodes Dependencies', True)

# WebUI and download options
change_webui_widget = factory.create_dropdown(
    list(WEBUI_SELECTION.keys()), 
    'WebUI:', 
    'A1111', 
    layout={'width': 'auto'}
)
detailed_download_widget = factory.create_dropdown(
    ['off', 'on'], 
    'Detailed Download:', 
    'off', 
    layout={'width': 'auto'}
)

# Top options row
choose_changes_box = factory.create_hbox([
    latest_webui_widget,
    latest_extensions_widget,
    check_custom_nodes_deps_widget,
    change_webui_widget,
    detailed_download_widget
], layout={'justify_content': 'space-between'})

# ControlNet section
controlnet_options = wm.read_model_data(f"{SCRIPTS}/_models-data.py", 'cnet')
controlnet_widget = factory.create_select_multiple(
    controlnet_options, 
    'ControlNet:', 
    ('none',),
    layout={'height': '80px'}
)

controlnet_num_widget = factory.create_text(
    'ControlNet Number:', 
    '', 
    'Enter ControlNet model numbers for download.'
)

commit_hash_widget = factory.create_text(
    'Commit Hash:', 
    '', 
    'Switch between branches or commits.'
)

# Token section with expandable buttons like original
civitai_token_from_env = os.getenv('CIVITAI_API_TOKEN')
civitai_token_widget = factory.create_text('CivitAI Token:', '', 'Enter your CivitAi API token.')
if civitai_token_from_env:
    civitai_token_widget.value = "Set in setup.py"
    civitai_token_widget.disabled = True

civitai_button = wm.create_expandable_button('Get CivitAI Token', 'https://civitai.com/user/account')
civitai_box = factory.create_hbox([civitai_token_widget, civitai_button])

huggingface_token_widget = factory.create_text('HuggingFace Token:')
huggingface_button = wm.create_expandable_button('Get HuggingFace Token', 'https://huggingface.co/settings/tokens')
huggingface_box = factory.create_hbox([huggingface_token_widget, huggingface_button])

ngrok_token_widget = factory.create_text('Ngrok Token:')
ngrok_button = wm.create_expandable_button('Get Ngrok Token', 'https://dashboard.ngrok.com/get-started/your-authtoken')
ngrok_box = factory.create_hbox([ngrok_token_widget, ngrok_button])

zrok_token_widget = factory.create_text('Zrok Token:')
zrok_button = wm.create_expandable_button('Get Zrok Token', 'https://docs.zrok.io/docs/getting-started/')
zrok_box = factory.create_hbox([zrok_token_widget, zrok_button])

# Arguments and theme
commandline_arguments_widget = factory.create_text('Arguments:', WEBUI_SELECTION['A1111'])

accent_colors_options = ['anxety', 'blue', 'green', 'peach', 'pink', 'red', 'yellow']
theme_accent_widget = factory.create_dropdown(
    accent_colors_options, 
    'Theme Accent:', 
    'anxety',
    layout={'width': 'auto', 'margin': '0 0 0 8px'}
)

additional_footer_box = factory.create_hbox([commandline_arguments_widget, theme_accent_widget])

# Store additional widgets
wm.widgets.update({
    'latest_webui': latest_webui_widget,
    'latest_extensions': latest_extensions_widget,
    'check_custom_nodes_deps': check_custom_nodes_deps_widget,
    'change_webui': change_webui_widget,
    'detailed_download': detailed_download_widget,
    'controlnet': controlnet_widget,
    'controlnet_num': controlnet_num_widget,
    'commit_hash': commit_hash_widget,
    'civitai_token': civitai_token_widget,
    'huggingface_token': huggingface_token_widget,
    'ngrok_token': ngrok_token_widget,
    'zrok_token': zrok_token_widget,
    'commandline_arguments': commandline_arguments_widget,
    'theme_accent': theme_accent_widget
})

# --- CUSTOM DOWNLOAD SECTION ---
custom_download_header_popup = factory.create_html('''
<div class="header custom-download-header" style="cursor: pointer;" onclick="toggleContainer()">
    <span class="header-icon">🌐</span>
    <span class="header-text">Custom Download</span>
    <span class="header-info">INFO</span>
</div>
<div class="popup">
    <div class="popup-content">
        <strong>Custom Download Instructions:</strong><br>
        • Separate multiple URLs with comma/space<br>
        • For <span class="file_name">custom filename</span> specify it through <span class="braces">[ ]</span> after URL<br>
        • <span class="required">File extension is required</span> for files<br><br>
        <div class="sample">
            <span class="sample_label">File Example:</span><br>
            <code>https://civitai.com/api/download/models/229782<span class="braces">[</span><span class="file_name">Detailer</span><span class="extension">.safetensors</span><span class="braces">]</span></code><br><br>
            <span class="sample_label">Extension Example:</span><br>
            <code>https://github.com/hako-mikan/sd-webui-regional-prompter<span class="braces">[</span><span class="file_name">Regional-Prompter</span><span class="braces">]</span></code>
        </div>
    </div>
</div>
''')

empowerment_widget = factory.create_checkbox('Empowerment Mode', False, class_names=['empowerment'])

empowerment_output_widget = factory.create_textarea(
    '', 
    '', 
    """Use special tags. Portable analogue of "File (txt)"
Tags: model (ckpt), vae, lora, embed (emb), extension (ext), adetailer (ad), control (cnet), upscale (ups), clip, unet, vision (vis), encoder (enc), diffusion (diff), config (cfg)
Short-tags: start with '$' without space -> $ckpt

------ Example ------

# LoRA
https://civitai.com/api/download/models/229782

$ext  
https://github.com/hako-mikan/sd-webui-cd-tuner[CD-Tuner]
""",
    layout={'height': '120px'}
)

# Individual URL fields
Model_url_widget = factory.create_text('Model:')
Vae_url_widget = factory.create_text('Vae:')
LoRA_url_widget = factory.create_text('LoRA:')
Embedding_url_widget = factory.create_text('Embedding:')
Extensions_url_widget = factory.create_text('Extensions:')
ADetailer_url_widget = factory.create_text('ADetailer:')
custom_file_urls_widget = factory.create_text('File (txt):')

wm.widgets.update({
    'empowerment': empowerment_widget,
    'empowerment_output': empowerment_output_widget,
    'Model_url': Model_url_widget,
    'Vae_url': Vae_url_widget,
    'LoRA_url': LoRA_url_widget,
    'Embedding_url': Embedding_url_widget,
    'Extensions_url': Extensions_url_widget,
    'ADetailer_url': ADetailer_url_widget,
    'custom_file_urls': custom_file_urls_widget
})

# --- SAVE BUTTON ---
save_button = factory.create_button('💾 Save Settings', class_names=['button', 'button_save'])

# --- GOOGLE DRIVE TOGGLE (Colab only) ---
BTN_STYLE = {'width': '48px', 'height': '48px'}
TOOLTIPS = ("Disconnect Google Drive", "Connect Google Drive")

GD_status = js.read(SETTINGS_PATH, 'mountGDrive', False)
GDrive_button = factory.create_button('📁', layout=BTN_STYLE, class_names=['sideContainer-btn', 'gdrive-btn'])
GDrive_button.tooltip = TOOLTIPS[not GD_status]
GDrive_button.toggle = GD_status

if not IN_COLAB:
    GDrive_button.layout.display = 'none'
else:
    if GD_status:
        GDrive_button.add_class('active')

    def handle_toggle(btn):
        btn.toggle = not btn.toggle
        btn.tooltip = TOOLTIPS[not btn.toggle]
        btn.toggle and btn.add_class('active') or btn.remove_class('active')

    GDrive_button.on_click(handle_toggle)

# --- EXPORT/IMPORT BUTTONS (Colab only) ---
export_button = factory.create_button('📤', layout=BTN_STYLE, class_names=['sideContainer-btn', 'export-btn'])
export_button.tooltip = "Export settings to JSON"

import_button = factory.create_button('📥', layout=BTN_STYLE, class_names=['sideContainer-btn', 'import-btn'])
import_button.tooltip = "Import settings from JSON"

if not IN_COLAB:
    export_button.layout.display = 'none'
    import_button.layout.display = 'none'

# Export/Import functions
def export_settings(button=None, filter_empty=False):
    if not IN_COLAB:
        return
        
    try:
        widgets_data = {}
        for key in wm.settings_keys:
            if key in wm.widgets:
                value = wm.widgets[key].value
                if not filter_empty or (value not in [None, '', False]):
                    widgets_data[key] = value

        settings_data = {
            'widgets': widgets_data,
            'mountGDrive': GDrive_button.toggle
        }

        display(Javascript(f'downloadJson({json.dumps(settings_data)});'))
        show_notification("Settings exported successfully!", "success")
    except Exception as e:
        show_notification(f"Export failed: {str(e)}", "error")

def import_settings(button=None):
    if not IN_COLAB:
        return
    display(Javascript('openFilePicker();'))

def apply_imported_settings(data):
    try:
        if 'widgets' in data:
            for key, value in data['widgets'].items():
                if key in wm.settings_keys and key in wm.widgets:
                    try:
                        wm.widgets[key].value = value
                    except Exception as e:
                        print(f"Warning: Could not set {key}: {e}")

        if 'mountGDrive' in data and IN_COLAB:
            GDrive_button.toggle = data['mountGDrive']
            if GDrive_button.toggle:
                GDrive_button.add_class('active')
            else:
                GDrive_button.remove_class('active')

        show_notification("Settings imported successfully!", "success")
    except Exception as e:
        show_notification(f"Import failed: {str(e)}", "error")

# --- NOTIFICATION SYSTEM ---
notification_popup = factory.create_html('', class_names=['notification-popup', 'hidden'])

def show_notification(message, message_type='info'):
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

export_button.on_click(export_settings)
import_button.on_click(import_settings)

# --- LOAD CSS/JS ---
try:
    factory.load_css(widgets_css)
    print("✅ CSS loaded successfully")
except Exception as e:
    print(f"⚠️  Warning: Could not load CSS: {e}")

if IN_COLAB:
    try:
        factory.load_js(widgets_js)
        print("✅ JavaScript loaded successfully")
    except Exception as e:
        print(f"⚠️  Warning: Could not load JavaScript: {e}")

# --- CALLBACKS ---
def update_XL_options(change, widget):
    """Update options when XL toggle changes."""
    try:
        is_xl = change['new']
        data_file = '_xl-models-data.py' if is_xl else '_models-data.py'
        
        print(f"🔄 Switching to {'SDXL' if is_xl else 'SD 1.5'} models...")
        
        # Update all selectors
        model_widget.options = wm.read_model_data(f"{SCRIPTS}/{data_file}", 'model')
        vae_widget.options = wm.read_model_data(f"{SCRIPTS}/{data_file}", 'vae')
        lora_widget.options = wm.read_model_data(f"{SCRIPTS}/{data_file}", 'lora')
        controlnet_widget.options = wm.read_model_data(f"{SCRIPTS}/{data_file}", 'cnet')
        
        # Set appropriate defaults
        if is_xl:
            # SDXL defaults
            model_widget.value = ('none',)
            vae_widget.value = 'none'
            lora_widget.value = ('none',)
            controlnet_widget.value = ('none',)
        else:
            # SD 1.5 defaults
            model_widget.value = ('none',)
            vae_preferred = [
                'vae-ft-mse-840000-ema-pruned | 840000 | 840k SD1.5 VAE - vae-ft-mse-840k',
                'ClearVAE(SD1.5) - v2.3',
                'none'
            ]
            vae_widget.value = wm.get_safe_default(vae_widget.options, vae_preferred)
            lora_widget.value = ('none',)
            controlnet_widget.value = ('none',)
        
        print(f"✅ Updated to {'SDXL' if is_xl else 'SD 1.5'} model lists")
        
    except Exception as e:
        print(f"❌ Error in update_XL_options: {e}")

def update_change_webui(change, widget):
    """Update WebUI change handling."""
    try:
        webui = change['new']
        commandline_arguments_widget.value = WEBUI_SELECTION.get(webui, '')
        
        is_comfy = webui == 'ComfyUI'
        
        # Show/hide ComfyUI specific options
        latest_extensions_widget.layout.display = 'none' if is_comfy else ''
        latest_extensions_widget.value = not is_comfy
        check_custom_nodes_deps_widget.layout.display = '' if is_comfy else 'none'
        theme_accent_widget.layout.display = 'none' if is_comfy else ''
        
        # Change label for extensions
        Extensions_url_widget.description = 'Custom Nodes:' if is_comfy else 'Extensions:'
        
        print(f"🔄 Switched to {webui} configuration")
        
    except Exception as e:
        print(f"❌ Error in update_change_webui: {e}")

def update_empowerment(change, widget):
    """Toggle empowerment mode."""
    try:
        selected_emp = change['new']
        
        customDL_widgets = [
            Model_url_widget, Vae_url_widget, LoRA_url_widget,
            Embedding_url_widget, Extensions_url_widget, ADetailer_url_widget
        ]
        
        for wg in customDL_widgets:
            wg.add_class('empowerment-text-field')

        if selected_emp:
            for wg in customDL_widgets:
                wg.layout.display = 'none'
            empowerment_output_widget.layout.display = ''
            print("⚡ Empowerment mode enabled")
        else:
            for wg in customDL_widgets:
                wg.layout.display = ''
            empowerment_output_widget.layout.display = 'none'
            print("📝 Individual URL fields enabled")
            
    except Exception as e:
        print(f"❌ Error in update_empowerment: {e}")

# Connect callbacks
factory.connect_widgets([(XL_models_widget, 'value')], update_XL_options)
factory.connect_widgets([(change_webui_widget, 'value')], update_change_webui)
factory.connect_widgets([(empowerment_widget, 'value')], update_empowerment)

# Initial setup
check_custom_nodes_deps_widget.layout.display = 'none'
empowerment_output_widget.layout.display = 'none'

# --- CREATE LAYOUT ---
model_widgets = [model_header, model_widget, model_num_widget, model_options_panel]
vae_widgets = [vae_header, vae_widget, vae_num_widget]
lora_widgets = [lora_header, lora_widget]

additional_widgets = [
    additional_header,
    choose_changes_box,
    HR,
    controlnet_widget,
    controlnet_num_widget,
    commit_hash_widget,
    civitai_box,
    huggingface_box,
    zrok_box,
    ngrok_box,
    HR,
    additional_footer_box
]

custom_download_widgets = [
    custom_download_header_popup,
    empowerment_widget,
    empowerment_output_widget,
    Model_url_widget,
    Vae_url_widget,
    LoRA_url_widget,
    Embedding_url_widget,
    Extensions_url_widget,
    ADetailer_url_widget,
    custom_file_urls_widget
]

# Create containers
model_box = factory.create_vbox(model_widgets, class_names=['container'])
vae_box = factory.create_vbox(vae_widgets, class_names=['container'])
lora_box = factory.create_vbox(lora_widgets, class_names=['container'])
additional_box = factory.create_vbox(additional_widgets, class_names=['container'])
custom_download_box = factory.create_vbox(custom_download_widgets, class_names=['container', 'container_cdl'])

# Main layout
CONTAINERS_WIDTH = '1080px'
model_vae_lora_box = factory.create_hbox(
    [model_box, vae_box, lora_box],
    class_names=['widgetContainer', 'model-vae'],
)

widgetContainer = factory.create_vbox(
    [model_vae_lora_box, additional_box, custom_download_box, save_button],
    class_names=['widgetContainer'],
    layout={'min_width': CONTAINERS_WIDTH, 'max_width': CONTAINERS_WIDTH}
)

sideContainer = factory.create_vbox(
    [GDrive_button, export_button, import_button, notification_popup],
    class_names=['sideContainer']
)

mainContainer = factory.create_hbox(
    [widgetContainer, sideContainer],
    class_names=['mainContainer'],
    layout={'align_items': 'flex-start'}
)

# Display
factory.display(mainContainer)

# --- SETTINGS MANAGEMENT ---
def save_settings():
    """Save widget values to settings."""
    widgets_values = {key: wm.widgets[key].value for key in wm.settings_keys if key in wm.widgets}
    js.save(SETTINGS_PATH, 'WIDGETS', widgets_values)
    
    if IN_COLAB:
        js.save(SETTINGS_PATH, 'mountGDrive', True if GDrive_button.toggle else False)

    update_current_webui(change_webui_widget.value)
    print("💾 Settings saved successfully!")

def load_settings():
    """Load widget values from settings."""
    if js.key_exists(SETTINGS_PATH, 'WIDGETS'):
        widget_data = js.read(SETTINGS_PATH, 'WIDGETS')
        for key in wm.settings_keys:
            if key in widget_data and key in wm.widgets:
                try:
                    wm.widgets[key].value = widget_data.get(key, '')
                except Exception as e:
                    print(f"Warning: could not load setting for {key}: {e}")

    # Load GDrive status
    if IN_COLAB:
        GD_status = js.read(SETTINGS_PATH, 'mountGDrive', False)
        GDrive_button.toggle = (GD_status == True)
        if GDrive_button.toggle:
            GDrive_button.add_class('active')
        else:
            GDrive_button.remove_class('active')

def save_data(button):
    """Handle save button click."""
    save_settings()
    show_notification("Settings saved successfully!", "success")

# Load settings and connect save button
load_settings()
save_button.on_click(save_data)

print("🎨 Widget interface loaded successfully!")
print("📝 Configure your selections and click 'Save Settings' when ready")

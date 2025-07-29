""" WebUI Utilities Module | by ANXETY """

import json_utils as js
from pathlib import Path
import json
import os

osENV = os.environ

# ======================== CONSTANTS =======================

# Constants (auto-convert env vars to Path)
PATHS = {k: Path(v) for k, v in osENV.items() if k.endswith('_path')}
HOME = PATHS.get('home_path', Path('/content'))
SETTINGS_PATH = PATHS.get('settings_path', HOME / 'LSDAI' / 'settings.json')

DEFAULT_UI = 'A1111'

# FIXED: Correct and comprehensive paths for all supported WebUIs
WEBUI_PATHS = {
    'A1111': {
        'name': 'A1111',
        'path_keys': ('models/Stable-diffusion', 'models/VAE', 'models/Lora', 'embeddings', 'extensions', 'models/ESRGAN', 'outputs')
    },
    'ComfyUI': {
        'name': 'ComfyUI',
        'path_keys': ('models/checkpoints', 'models/vae', 'models/loras', 'models/embeddings', 'custom_nodes', 'models/upscale_models', 'output')
    },
    'Forge': {
        'name': 'Forge',
        'path_keys': ('models/Stable-diffusion', 'models/VAE', 'models/Lora', 'embeddings', 'extensions', 'models/ESRGAN', 'output')
    },
    'ReForge': {
        'name': 'ReForge',
        'path_keys': ('models/Stable-diffusion', 'models/VAE', 'models/Lora', 'embeddings', 'extensions', 'models/ESRGAN', 'output')
    },
    'SD-UX': {
        'name': 'SD-UX',
        'path_keys': ('models/Stable-diffusion', 'models/VAE', 'models/Lora', 'embeddings', 'extensions', 'models/ESRGAN', 'outputs')
    },
    'Classic': {
        'name': 'Classic',
        'path_keys': ('models/Stable-diffusion', 'models/VAE', 'models/Lora', 'embeddings', 'extensions', 'models/ESRGAN', 'output')
    },
    'FaceFusion': {
        'name': 'FaceFusion',
        'path_keys': ('', '', '', '', '', '', 'output')
    },
    'DreamO': {
        'name': 'DreamO',
        'path_keys': ('', '', '', '', '', '', 'output')
    }
}

# ===================== WEBUI HANDLERS =====================

def update_current_webui(current_value: str) -> None:
    """Update the current WebUI value and save settings."""
    if not js.key_exists(SETTINGS_PATH, 'WEBUI'):
        js.save(SETTINGS_PATH, 'WEBUI', {})

    current_stored = js.read(SETTINGS_PATH, 'WEBUI.current')
    latest_value = js.read(SETTINGS_PATH, 'WEBUI.latest', None)

    if latest_value is None or current_stored != current_value:
        js.save(SETTINGS_PATH, 'WEBUI.latest', current_stored)
        js.save(SETTINGS_PATH, 'WEBUI.current', current_value)

    webui_name = WEBUI_PATHS.get(current_value, WEBUI_PATHS[DEFAULT_UI])['name']
    js.save(SETTINGS_PATH, 'WEBUI.webui_path', str(HOME / webui_name))
    _set_webui_paths(current_value)


def _set_webui_paths(ui: str) -> None:
    """Configure paths for specified UI, fallback to A1111 for unknown UIs."""
    config = WEBUI_PATHS.get(ui, WEBUI_PATHS[DEFAULT_UI])
    webui_root = HOME / config['name']
    models_root = webui_root / 'models'

    path_keys = config['path_keys']
    checkpoint, vae, lora, embed, extension, upscale, output = path_keys

    is_comfy = ui == 'ComfyUI'
    control_dir_name = 'controlnet' if is_comfy else 'ControlNet'
    adetailer_dir_name = 'ultralytics' if is_comfy else 'adetailer'
    
    path_config = {
        'model_dir': str(webui_root / checkpoint) if checkpoint else str(webui_root),
        'vae_dir': str(webui_root / vae) if vae else str(webui_root),
        'lora_dir': str(webui_root / lora) if lora else str(webui_root),
        'embed_dir': str(webui_root / embed) if embed else str(webui_root),
        'extension_dir': str(webui_root / extension) if extension else str(webui_root),
        'control_dir': str(models_root / control_dir_name),
        'upscale_dir': str(webui_root / upscale) if upscale else str(webui_root),
        'output_dir': str(webui_root / output) if output else str(webui_root),
        'config_dir': str(webui_root / 'user' / 'default') if is_comfy else str(webui_root),
        'adetailer_dir': str(models_root / adetailer_dir_name),
        'clip_dir': str(models_root / 'clip'),
        'unet_dir': str(models_root / 'unet'),
        'vision_dir': str(models_root / 'clip_vision'),
        'encoder_dir': str(models_root / 'text_encoders'),
        'diffusion_dir': str(models_root / 'diffusion_models')
    }
    
    js.update(SETTINGS_PATH, 'WEBUI', path_config)

def get_webui_main_script(ui_type: str) -> str:
    """Returns the main launch script for a given WebUI type."""
    if ui_type == 'ComfyUI':
        return 'main.py'
    return 'launch.py'

def handle_setup_timer(webui_path: str, timer_webui: float) -> float:
    """Manage timer persistence for WebUI instances."""
    timer_file = Path(webui_path) / 'static' / 'timer.txt'
    timer_file.parent.mkdir(parents=True, exist_ok=True)

    try:
        with timer_file.open('r') as f:
            timer_webui = float(f.read())
    except (FileNotFoundError, ValueError):
        pass

    with timer_file.open('w') as f:
        f.write(str(timer_webui))

    return timer_webui

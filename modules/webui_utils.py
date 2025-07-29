"""
WebUI Utilities Module for LSDAI
Provides utilities for managing different WebUI types and configurations
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Optional, Union

# Try to import json_utils for settings management
try:
    import json_utils as js
    JSON_UTILS_AVAILABLE = True
except ImportError:
    JSON_UTILS_AVAILABLE = False
    print("Warning: json_utils not available. Some features may be limited.")

# Get environment paths
HOME = Path(os.environ.get('home_path', '/content'))
SCR_PATH = Path(os.environ.get('scr_path', HOME / 'LSDAI'))
SETTINGS_PATH = Path(os.environ.get('settings_path', SCR_PATH / 'settings.json'))

# WebUI configurations
WEBUI_CONFIGS = {
    'automatic1111': {
        'name': 'AUTOMATIC1111 Stable Diffusion WebUI',
        'short_name': 'A1111',
        'repo_url': 'https://github.com/AUTOMATIC1111/stable-diffusion-webui.git',
        'install_path': HOME / 'stable-diffusion-webui',
        'main_script': 'webui.py',
        'models_dir': 'models/Stable-diffusion',
        'vae_dir': 'models/VAE',
        'lora_dir': 'models/Lora',
        'embeddings_dir': 'embeddings',
        'extensions_dir': 'extensions',
        'controlnet_dir': 'models/ControlNet',
        'default_args': [
            '--enable-insecure-extension-access',
            '--theme=dark',
            '--disable-console-progressbars'
        ],
        'colab_args': ['--share'],
        'api_enabled': True
    },
    'ComfyUI': {
        'name': 'ComfyUI',
        'short_name': 'ComfyUI',
        'repo_url': 'https://github.com/comfyanonymous/ComfyUI.git',
        'install_path': HOME / 'ComfyUI',
        'main_script': 'main.py',
        'models_dir': 'models/checkpoints',
        'vae_dir': 'models/vae',
        'lora_dir': 'models/loras',
        'embeddings_dir': 'models/embeddings',
        'extensions_dir': 'custom_nodes',
        'controlnet_dir': 'models/controlnet',
        'default_args': ['--listen'],
        'colab_args': ['--share'],
        'api_enabled': True
    },
    'InvokeAI': {
        'name': 'InvokeAI',
        'short_name': 'InvokeAI',
        'repo_url': 'https://github.com/invoke-ai/InvokeAI.git',
        'install_path': HOME / 'InvokeAI',
        'main_script': 'invokeai-web.py',
        'models_dir': 'models',
        'vae_dir': 'models',
        'lora_dir': 'models',
        'embeddings_dir': 'models',
        'extensions_dir': 'nodes',
        'controlnet_dir': 'models',
        'default_args': ['--web'],
        'colab_args': ['--host=0.0.0.0'],
        'api_enabled': True
    }
}

def get_webui_config(webui_type: str) -> Dict:
    """Get configuration for a specific WebUI type"""
    return WEBUI_CONFIGS.get(webui_type, WEBUI_CONFIGS['automatic1111'])

def get_available_webuis() -> List[str]:
    """Get list of available WebUI types"""
    return list(WEBUI_CONFIGS.keys())

def get_webui_names() -> Dict[str, str]:
    """Get mapping of WebUI types to display names"""
    return {key: config['name'] for key, config in WEBUI_CONFIGS.items()}

def get_current_webui() -> str:
    """Get the currently selected WebUI type"""
    if JSON_UTILS_AVAILABLE:
        # Assumes WIDGETS.change_webui is the source of truth
        return js.read(SETTINGS_PATH, 'WIDGETS.change_webui', 'automatic1111')
    else:
        # Fallback: read from settings file directly
        try:
            if SETTINGS_PATH.exists():
                with open(SETTINGS_PATH, 'r') as f:
                    settings = json.load(f)
                    return settings.get('WIDGETS', {}).get('change_webui', 'automatic1111')
        except:
            pass
        return 'automatic1111'

def update_current_webui(webui_type: str) -> bool:
    """Update the current WebUI type in settings"""
    if webui_type not in WEBUI_CONFIGS:
        print(f"Warning: Unknown WebUI type '{webui_type}'. Using 'automatic1111'.")
        webui_type = 'automatic1111'
    
    if JSON_UTILS_AVAILABLE:
        # This function should only be called from the widget save action
        # It assumes WIDGETS.change_webui is already being set
        config = get_webui_config(webui_type)
        js.save(SETTINGS_PATH, 'WEBUI.current', webui_type)
        js.save(SETTINGS_PATH, 'WEBUI.webui_path', str(config['install_path']))
        return True
    else:
        # Fallback for environments without json_utils
        try:
            settings = {}
            if SETTINGS_PATH.exists():
                with open(SETTINGS_PATH, 'r') as f:
                    settings = json.load(f)
            
            if 'WIDGETS' not in settings: settings['WIDGETS'] = {}
            if 'WEBUI' not in settings: settings['WEBUI'] = {}
            
            settings['WIDGETS']['change_webui'] = webui_type
            settings['WEBUI']['current'] = webui_type
            settings['WEBUI']['webui_path'] = str(get_webui_config(webui_type)['install_path'])
            
            SETTINGS_PATH.parent.mkdir(parents=True, exist_ok=True)
            with open(SETTINGS_PATH, 'w') as f:
                json.dump(settings, f, indent=2)
            
            return True
        except Exception as e:
            print(f"Error updating WebUI type: {e}")
            return False

def get_webui_path(webui_type: Optional[str] = None) -> Path:
    """Get installation path for a WebUI type"""
    if webui_type is None:
        webui_type = get_current_webui()
    
    config = get_webui_config(webui_type)
    return config['install_path']

def get_extensions_directory(webui_type: Optional[str] = None) -> Path:
    """Get extensions directory for a WebUI type"""
    if webui_type is None:
        webui_type = get_current_webui()
    
    config = get_webui_config(webui_type)
    return config['install_path'] / config['extensions_dir']

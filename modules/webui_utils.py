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
        return js.read_key('change_webui', 'automatic1111')
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
        success = js.write_key('change_webui', webui_type)
        if success:
            # Also update the WEBUI section
            config = get_webui_config(webui_type)
            js.write(SETTINGS_PATH, 'WEBUI.current', webui_type)
            js.write(SETTINGS_PATH, 'WEBUI.webui_path', str(config['install_path']))
        return success
    else:
        # Fallback: update settings file directly
        try:
            settings = {}
            if SETTINGS_PATH.exists():
                with open(SETTINGS_PATH, 'r') as f:
                    settings = json.load(f)
            
            if 'WIDGETS' not in settings:
                settings['WIDGETS'] = {}
            if 'WEBUI' not in settings:
                settings['WEBUI'] = {}
            
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

def get_webui_main_script(webui_type: Optional[str] = None) -> str:
    """Get main script name for a WebUI type"""
    if webui_type is None:
        webui_type = get_current_webui()
    
    config = get_webui_config(webui_type)
    return config['main_script']

def get_models_directory(webui_type: Optional[str] = None, model_type: str = 'models') -> Path:
    """Get models directory for a specific WebUI and model type"""
    if webui_type is None:
        webui_type = get_current_webui()
    
    config = get_webui_config(webui_type)
    webui_path = config['install_path']
    
    dir_key = f'{model_type}_dir'
    if dir_key in config:
        return webui_path / config[dir_key]
    else:
        # Fallback to general models directory
        return webui_path / config['models_dir']

def get_extensions_directory(webui_type: Optional[str] = None) -> Path:
    """Get extensions directory for a WebUI type"""
    if webui_type is None:
        webui_type = get_current_webui()
    
    config = get_webui_config(webui_type)
    return config['install_path'] / config['extensions_dir']

def is_webui_installed(webui_type: Optional[str] = None) -> bool:
    """Check if a WebUI is installed"""
    if webui_type is None:
        webui_type = get_current_webui()
    
    config = get_webui_config(webui_type)
    webui_path = config['install_path']
    main_script = webui_path / config['main_script']
    
    return webui_path.exists() and main_script.exists()

def get_webui_status() -> Dict[str, bool]:
    """Get installation status for all WebUI types"""
    return {webui_type: is_webui_installed(webui_type) for webui_type in WEBUI_CONFIGS.keys()}

def get_default_args(webui_type: Optional[str] = None, include_colab_args: bool = None) -> List[str]:
    """Get default command-line arguments for a WebUI type"""
    if webui_type is None:
        webui_type = get_current_webui()
    
    config = get_webui_config(webui_type)
    args = config['default_args'].copy()
    
    # Auto-detect if we're in Colab/cloud environment
    if include_colab_args is None:
        include_colab_args = any(env_var in os.environ for env_var in ['COLAB_GPU', 'KAGGLE_URL_BASE'])
    
    if include_colab_args:
        args.extend(config['colab_args'])
    
    return args

def build_launch_command(webui_type: Optional[str] = None, custom_args: Optional[List[str]] = None, 
                        python_exe: Optional[str] = None) -> List[str]:
    """Build complete launch command for a WebUI"""
    if webui_type is None:
        webui_type = get_current_webui()
    
    config = get_webui_config(webui_type)
    webui_path = config['install_path']
    main_script = webui_path / config['main_script']
    
    # Determine Python executable
    if python_exe is None:
        # Try to find venv python first
        venv_path = Path(os.environ.get('venv_path', HOME / 'venv'))
        venv_python = venv_path / 'bin' / 'python'
        
        if venv_python.exists():
            python_exe = str(venv_python)
        else:
            python_exe = 'python'
    
    # Build command
    cmd = [python_exe, str(main_script)]
    
    # Add default arguments
    cmd.extend(get_default_args(webui_type))
    
    # Add custom arguments
    if custom_args:
        cmd.extend(custom_args)
    
    return cmd

def parse_launch_args(args_string: str) -> List[str]:
    """Parse command-line arguments string into list"""
    import shlex
    
    if not args_string.strip():
        return []
    
    try:
        return shlex.split(args_string)
    except ValueError as e:
        print(f"Warning: Could not parse arguments '{args_string}': {e}")
        # Fallback to simple space splitting
        return args_string.split()

def validate_webui_installation(webui_type: Optional[str] = None) -> Dict[str, bool]:
    """Validate WebUI installation and return status of components"""
    if webui_type is None:
        webui_type = get_current_webui()
    
    config = get_webui_config(webui_type)
    webui_path = config['install_path']
    
    checks = {
        'webui_directory': webui_path.exists(),
        'main_script': (webui_path / config['main_script']).exists(),
        'models_directory': (webui_path / config['models_dir']).exists(),
        'extensions_directory': (webui_path / config['extensions_dir']).exists()
    }
    
    return checks

def create_webui_directories(webui_type: Optional[str] = None) -> bool:
    """Create necessary directories for a WebUI installation"""
    if webui_type is None:
        webui_type = get_current_webui()
    
    config = get_webui_config(webui_type)
    webui_path = config['install_path']
    
    try:
        # Create main directories
        directories_to_create = [
            webui_path / config['models_dir'],
            webui_path / config['vae_dir'],
            webui_path / config['lora_dir'],
            webui_path / config['embeddings_dir'],
            webui_path / config['extensions_dir'],
            webui_path / config['controlnet_dir']
        ]
        
        for directory in directories_to_create:
            directory.mkdir(parents=True, exist_ok=True)
        
        print(f"✅ Created directories for {config['name']}")
        return True
        
    except Exception as e:
        print(f"❌ Error creating directories for {webui_type}: {e}")
        return False

def get_webui_info(webui_type: Optional[str] = None) -> Dict:
    """Get comprehensive information about a WebUI installation"""
    if webui_type is None:
        webui_type = get_current_webui()
    
    config = get_webui_config(webui_type)
    validation = validate_webui_installation(webui_type)
    
    info = {
        'type': webui_type,
        'name': config['name'],
        'short_name': config['short_name'],
        'install_path': config['install_path'],
        'main_script': config['main_script'],
        'repo_url': config['repo_url'],
        'installed': validation['webui_directory'] and validation['main_script'],
        'validation': validation,
        'directories': {
            'models': config['install_path'] / config['models_dir'],
            'vae': config['install_path'] / config['vae_dir'],
            'lora': config['install_path'] / config['lora_dir'],
            'embeddings': config['install_path'] / config['embeddings_dir'],
            'extensions': config['install_path'] / config['extensions_dir'],
            'controlnet': config['install_path'] / config['controlnet_dir']
        },
        'default_args': get_default_args(webui_type),
        'api_enabled': config['api_enabled']
    }
    
    return info

def print_webui_status(webui_type: Optional[str] = None):
    """Print formatted status information for a WebUI"""
    if webui_type is None:
        webui_type = get_current_webui()
    
    info = get_webui_info(webui_type)
    
    print(f"📋 WebUI Status: {info['name']}")
    print("=" * 50)
    print(f"Type: {info['type']}")
    print(f"Install Path: {info['install_path']}")
    print(f"Installed: {'✅ Yes' if info['installed'] else '❌ No'}")
    print(f"Main Script: {info['main_script']}")
    print(f"API Enabled: {'✅ Yes' if info['api_enabled'] else '❌ No'}")
    
    print("\n📁 Directories:")
    for dir_type, dir_path in info['directories'].items():
        exists = "✅" if dir_path.exists() else "❌"
        print(f"  {dir_type.title()}: {exists} {dir_path}")
    
    print(f"\n⚙️ Default Arguments: {' '.join(info['default_args'])}")

def print_all_webui_status():
    """Print status for all available WebUIs"""
    print("📋 All WebUI Status")
    print("=" * 60)
    
    for webui_type in get_available_webuis():
        config = get_webui_config(webui_type)
        installed = is_webui_installed(webui_type)
        status = "✅ Installed" if installed else "❌ Not Installed"
        print(f"{config['name']}: {status}")
    
    print(f"\n🎯 Current WebUI: {get_webui_config(get_current_webui())['name']}")

def switch_webui(new_webui_type: str) -> bool:
    """Switch to a different WebUI type"""
    if new_webui_type not in WEBUI_CONFIGS:
        print(f"❌ Unknown WebUI type: {new_webui_type}")
        print(f"Available types: {', '.join(get_available_webuis())}")
        return False
    
    old_webui = get_current_webui()
    
    if update_current_webui(new_webui_type):
        old_config = get_webui_config(old_webui)
        new_config = get_webui_config(new_webui_type)
        
        print(f"✅ Switched WebUI:")
        print(f"  From: {old_config['name']}")
        print(f"  To: {new_config['name']}")
        
        # Check if new WebUI is installed
        if not is_webui_installed(new_webui_type):
            print(f"⚠️ Warning: {new_config['name']} is not installed yet.")
            print(f"  Run the downloading script to install it.")
        
        return True
    else:
        print(f"❌ Failed to switch to {new_webui_type}")
        return False

# Export main functions
__all__ = [
    'get_webui_config', 'get_available_webuis', 'get_webui_names',
    'get_current_webui', 'update_current_webui', 'get_webui_path',
    'get_webui_main_script', 'get_models_directory', 'get_extensions_directory',
    'is_webui_installed', 'get_webui_status', 'get_default_args',
    'build_launch_command', 'parse_launch_args', 'validate_webui_installation',
    'create_webui_directories', 'get_webui_info', 'print_webui_status',
    'print_all_webui_status', 'switch_webui'
]

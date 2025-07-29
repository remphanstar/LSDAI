"""
JSON Utilities Module for LSDAI
Provides robust JSON reading/writing with path navigation and error handling
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional, Union
import time

def get_settings_path():
    """Get the settings file path from environment or default"""
    return Path(os.environ.get('settings_path', '/content/LSDAI/settings.json'))

def ensure_file_exists(filepath: Union[str, Path]) -> Path:
    """Ensure the file and its parent directories exist"""
    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)
    
    if not filepath.exists():
        # Create empty JSON file
        filepath.write_text('{}')
    
    return filepath

def read_json_file(filepath: Union[str, Path]) -> Dict[str, Any]:
    """Read JSON file with error handling"""
    filepath = Path(filepath)
    
    if not filepath.exists():
        return {}
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            if not content:
                return {}
            return json.loads(content)
    except (json.JSONDecodeError, FileNotFoundError, PermissionError) as e:
        print(f"Warning: Could not read {filepath}: {e}")
        return {}

def write_json_file(filepath: Union[str, Path], data: Dict[str, Any]) -> bool:
    """Write JSON file with error handling"""
    try:
        filepath = ensure_file_exists(filepath)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error writing to {filepath}: {e}")
        return False

def navigate_dict(data: Dict[str, Any], path: str, default: Any = None) -> Any:
    """Navigate nested dictionary using dot notation"""
    if not path:
        return data
    
    keys = path.split('.')
    current = data
    
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return default
    
    return current

def set_nested_dict(data: Dict[str, Any], path: str, value: Any) -> Dict[str, Any]:
    """Set value in nested dictionary using dot notation"""
    if not path:
        return data
    
    keys = path.split('.')
    current = data
    
    # Navigate to the parent of the target key
    for key in keys[:-1]:
        if key not in current:
            current[key] = {}
        current = current[key]
    
    # Set the final value
    current[keys[-1]] = value
    return data

def read(filepath: Union[str, Path, None] = None, path: str = '', default: Any = None) -> Any:
    """
    Read value from JSON file using dot notation path
    
    Args:
        filepath: Path to JSON file (uses default settings path if None)
        path: Dot notation path to the value (e.g., 'WIDGETS.model')
        default: Default value if path not found
    
    Returns:
        The value at the specified path or default
    """
    if filepath is None:
        filepath = get_settings_path()
    
    data = read_json_file(filepath)
    return navigate_dict(data, path, default)

def write(filepath: Union[str, Path, None] = None, path: str = '', value: Any = None) -> bool:
    """
    Write value to JSON file using dot notation path
    
    Args:
        filepath: Path to JSON file (uses default settings path if None)
        path: Dot notation path to set (e.g., 'WIDGETS.model')
        value: Value to set
    
    Returns:
        True if successful, False otherwise
    """
    if filepath is None:
        filepath = get_settings_path()
    
    # Read existing data
    data = read_json_file(filepath)
    
    # Set the new value
    if path:
        data = set_nested_dict(data, path, value)
    else:
        # If no path, replace entire file content
        data = value if isinstance(value, dict) else {'data': value}
    
    # Write back to file
    return write_json_file(filepath, data)

def read_key(key: str, default: Any = None, filepath: Union[str, Path, None] = None) -> Any:
    """
    Read a simple key from the WIDGETS section
    
    Args:
        key: Key name in WIDGETS section
        default: Default value if key not found
        filepath: Path to JSON file (uses default if None)
    
    Returns:
        The value of the key or default
    """
    return read(filepath, f'WIDGETS.{key}', default)

def write_key(key: str, value: Any, filepath: Union[str, Path, None] = None) -> bool:
    """
    Write a simple key to the WIDGETS section
    
    Args:
        key: Key name in WIDGETS section
        value: Value to set
        filepath: Path to JSON file (uses default if None)
    
    Returns:
        True if successful, False otherwise
    """
    return write(filepath, f'WIDGETS.{key}', value)

def update_section(section: str, data: Dict[str, Any], filepath: Union[str, Path, None] = None) -> bool:
    """
    Update an entire section in the JSON file
    
    Args:
        section: Section name (e.g., 'WIDGETS', 'ENVIRONMENT')
        data: Dictionary with new data for the section
        filepath: Path to JSON file (uses default if None)
    
    Returns:
        True if successful, False otherwise
    """
    if filepath is None:
        filepath = get_settings_path()
    
    # Read existing data
    existing_data = read_json_file(filepath)
    
    # Update the section
    if section in existing_data and isinstance(existing_data[section], dict):
        existing_data[section].update(data)
    else:
        existing_data[section] = data
    
    # Write back to file
    return write_json_file(filepath, existing_data)

def get_current_timestamp() -> str:
    """Get current timestamp as ISO string"""
    return time.strftime('%Y-%m-%d %H:%M:%S')

def add_timestamp(filepath: Union[str, Path, None] = None) -> bool:
    """Add timestamp to the JSON file"""
    return write(filepath, 'last_updated', get_current_timestamp())

def backup_file(filepath: Union[str, Path, None] = None) -> Optional[Path]:
    """Create a backup of the JSON file"""
    if filepath is None:
        filepath = get_settings_path()
    
    filepath = Path(filepath)
    
    if not filepath.exists():
        return None
    
    try:
        timestamp = time.strftime('%Y%m%d_%H%M%S')
        backup_path = filepath.parent / f"{filepath.stem}_backup_{timestamp}.json"
        
        data = read_json_file(filepath)
        write_json_file(backup_path, data)
        
        return backup_path
    except Exception as e:
        print(f"Error creating backup: {e}")
        return None

def restore_from_backup(backup_path: Union[str, Path], target_path: Union[str, Path, None] = None) -> bool:
    """Restore JSON file from backup"""
    if target_path is None:
        target_path = get_settings_path()
    
    try:
        data = read_json_file(backup_path)
        return write_json_file(target_path, data)
    except Exception as e:
        print(f"Error restoring from backup: {e}")
        return False

def validate_json_structure(filepath: Union[str, Path, None] = None) -> bool:
    """Validate that the JSON file has the expected structure"""
    if filepath is None:
        filepath = get_settings_path()
    
    data = read_json_file(filepath)
    
    # Check for required top-level sections
    required_sections = ['ENVIRONMENT', 'WIDGETS']
    
    for section in required_sections:
        if section not in data:
            print(f"Warning: Missing required section '{section}' in {filepath}")
            return False
        if not isinstance(data[section], dict):
            print(f"Warning: Section '{section}' is not a dictionary in {filepath}")
            return False
    
    return True

def initialize_default_structure(filepath: Union[str, Path, None] = None) -> bool:
    """Initialize JSON file with default structure"""
    if filepath is None:
        filepath = get_settings_path()
    
    default_structure = {
        "ENVIRONMENT": {
            "env_name": "Google Colab",
            "install_deps": False,
            "fork": "remphanstar/LSDAI",
            "branch": "main",
            "lang": "en",
            "home_path": "/content",
            "scr_path": "/content/LSDAI",
            "venv_path": "/content/venv",
            "settings_path": "/content/LSDAI/settings.json",
            "start_timer": int(time.time()),
            "public_ip": "",
            "civitai_api_token": ""
        },
        "WIDGETS": {
            "change_webui": "automatic1111",
            "XL_models": False,
            "model": ["none"],
            "vae": ["none"],
            "lora": ["none"],
            "controlnet": ["none"],
            "latest_webui": True,
            "latest_extensions": False,
            "detailed_download": False,
            "commandline_arguments": "",
            "theme_accent": "anxety",
            "civitai_token": "",
            "huggingface_token": "",
            "Model_url": "",
            "Vae_url": "",
            "LoRA_url": "",
            "Embedding_url": "",
            "Extensions_url": ""
        },
        "WEBUI": {
            "current": "automatic1111",
            "webui_path": "/content/stable-diffusion-webui"
        }
    }
    
    return write_json_file(filepath, default_structure)

def get_all_settings(filepath: Union[str, Path, None] = None) -> Dict[str, Any]:
    """Get all settings from the JSON file"""
    if filepath is None:
        filepath = get_settings_path()
    
    return read_json_file(filepath)

def reset_settings(filepath: Union[str, Path, None] = None) -> bool:
    """Reset settings to default values"""
    if filepath is None:
        filepath = get_settings_path()
    
    # Create backup first
    backup_path = backup_file(filepath)
    if backup_path:
        print(f"Backup created: {backup_path}")
    
    # Initialize with defaults
    return initialize_default_structure(filepath)

# Convenience functions for common operations
def get_webui_type() -> str:
    """Get the current WebUI type"""
    return read_key('change_webui', 'automatic1111')

def set_webui_type(webui_type: str) -> bool:
    """Set the WebUI type"""
    return write_key('change_webui', webui_type)

def get_launch_args() -> str:
    """Get launch arguments"""
    return read_key('commandline_arguments', '')

def set_launch_args(args: str) -> bool:
    """Set launch arguments"""
    return write_key('commandline_arguments', args)

def get_theme() -> str:
    """Get theme setting"""
    return read_key('theme_accent', 'anxety')

def set_theme(theme: str) -> bool:
    """Set theme"""
    return write_key('theme_accent', theme)

# Debug and utility functions
def print_structure(filepath: Union[str, Path, None] = None, max_depth: int = 3):
    """Print the structure of the JSON file for debugging"""
    if filepath is None:
        filepath = get_settings_path()
    
    data = read_json_file(filepath)
    
    def print_dict(d, depth=0, max_depth=max_depth):
        if depth > max_depth:
            return
        
        indent = "  " * depth
        for key, value in d.items():
            if isinstance(value, dict):
                print(f"{indent}{key}:")
                print_dict(value, depth + 1, max_depth)
            else:
                value_str = str(value)
                if len(value_str) > 50:
                    value_str = value_str[:47] + "..."
                print(f"{indent}{key}: {value_str}")
    
    print(f"Structure of {filepath}:")
    print_dict(data)

def get_file_info(filepath: Union[str, Path, None] = None):
    """Get information about the JSON file"""
    if filepath is None:
        filepath = get_settings_path()
    
    filepath = Path(filepath)
    
    if not filepath.exists():
        print(f"File does not exist: {filepath}")
        return
    
    try:
        stat = filepath.stat()
        data = read_json_file(filepath)
        
        print(f"File: {filepath}")
        print(f"Size: {stat.st_size} bytes")
        print(f"Modified: {time.ctime(stat.st_mtime)}")
        print(f"Top-level keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dictionary'}")
        print(f"Valid JSON: {validate_json_structure(filepath)}")
        
    except Exception as e:
        print(f"Error getting file info: {e}")

# Export main functions
__all__ = [
    'read', 'write', 'read_key', 'write_key', 'update_section',
    'get_settings_path', 'validate_json_structure', 'initialize_default_structure',
    'backup_file', 'restore_from_backup', 'reset_settings',
    'get_webui_type', 'set_webui_type', 'get_launch_args', 'set_launch_args',
    'get_theme', 'set_theme', 'get_all_settings', 'print_structure', 'get_file_info'
]

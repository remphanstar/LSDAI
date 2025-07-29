# ~ json_utils.py | by ANXETY - Robust version with dot notation support ~

import json
from pathlib import Path
from typing import Any, Dict, Optional, Union
import os

# --- Internal Helper Functions ---

def _get_nested(data: Dict, key: str, default: Any = None) -> Any:
    """
    Retrieves a value from a nested dictionary using a dot-separated key.
    Example: _get_nested(data, 'WEBUI.current')
    """
    keys = key.split('.')
    for k in keys:
        if isinstance(data, dict) and k in data:
            data = data[k]
        else:
            return default
    return data

def _set_nested(data: Dict, key: str, value: Any):
    """
    Sets a value in a nested dictionary using a dot-separated key.
    Creates nested dictionaries if they don't exist.
    Example: _set_nested(data, 'WIDGETS.change_webui', 'ComfyUI')
    """
    keys = key.split('.')
    d = data
    for k in keys[:-1]:
        d = d.setdefault(k, {})
    d[keys[-1]] = value

# --- Main Public Functions ---

def read(file_path: Union[str, Path], key: Optional[str] = None, default: Any = None) -> Any:
    """
    Reads a JSON file. If a key is provided, it returns the value for that key.
    Supports dot notation for nested keys.
    If the file doesn't exist, returns the default value (or an empty dict).
    """
    file_path = Path(file_path)
    if not file_path.exists():
        return default if default is not None else {}
    
    try:
        with file_path.open('r', encoding='utf-8') as f:
            data = json.load(f)
        
        if key:
            return _get_nested(data, key, default)
        return data
    except (json.JSONDecodeError, IOError) as e:
        print(f"Warning: Could not read JSON file at {file_path}: {e}")
        return default if default is not None else {}

def write(file_path: Union[str, Path], data: Dict):
    """
    Writes an entire dictionary to a JSON file, overwriting its contents.
    Ensures the parent directory exists.
    """
    file_path = Path(file_path)
    try:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with file_path.open('w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
        return True
    except IOError as e:
        print(f"Error: Could not write to JSON file at {file_path}: {e}")
        return False

def save(file_path: Union[str, Path], key: str, value: Any):
    """
    Saves a single value to a specific key in a JSON file.
    Supports dot notation for nested keys.
    This is a read-modify-write operation.
    """
    data = read(file_path)
    _set_nested(data, key, value)
    return write(file_path, data)

def update(file_path: Union[str, Path], key: str, update_dict: Dict):
    """
    Updates a nested dictionary within a JSON file.
    This is a destructive update for the specified key.
    """
    data = read(file_path)
    _set_nested(data, key, update_dict)
    return write(file_path, data)

def key_exists(file_path: Union[str, Path], key: str) -> bool:
    """
    Checks if a dot-separated key exists within the JSON file.
    """
    data = read(file_path)
    keys = key.split('.')
    for k in keys:
        if isinstance(data, dict) and k in data:
            data = data[k]
        else:
            return False
    return True

def read_key(key: str, default: Any = None) -> Any:
    """
    Convenience function to read a key from the default settings file.
    Requires 'settings_path' to be in the environment variables.
    """
    settings_path = os.environ.get('settings_path')
    if not settings_path:
        print("Error: 'settings_path' environment variable not set.")
        return default
    return read(settings_path, f'WIDGETS.{key}', default)

def write_key(key: str, value: Any) -> bool:
    """
    Convenience function to write a key to the default settings file.
    Requires 'settings_path' to be in the environment variables.
    """
    settings_path = os.environ.get('settings_path')
    if not settings_path:
        print("Error: 'settings_path' environment variable not set.")
        return False
    return save(settings_path, f'WIDGETS.{key}', value)

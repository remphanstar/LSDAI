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

# --- Extended Functions for Widget Compatibility ---

def save_settings(data: Dict, section: str = 'WIDGETS', file_path: Union[str, Path] = None) -> bool:
    """
    Save settings data to a specific section in the JSON file.
    This function provides compatibility with the enhanced widgets system.
    
    Args:
        data: Dictionary containing the settings data to save
        section: The top-level section to save the data under (default: 'WIDGETS')
        file_path: Path to the settings file (uses environment settings_path if None)
    
    Returns:
        bool: True if successful, False otherwise
    """
    if file_path is None:
        file_path = os.environ.get('settings_path')
        if not file_path:
            print("Error: 'settings_path' environment variable not set and no file_path provided.")
            return False
    
    try:
        return save(file_path, section, data)
    except Exception as e:
        print(f"Error saving settings: {e}")
        return False

def load_settings(section: str = None, file_path: Union[str, Path] = None) -> Dict:
    """
    Load settings data from the JSON file.
    This function provides compatibility with the enhanced widgets system.
    
    Args:
        section: The specific section to load (if None, loads entire file)
        file_path: Path to the settings file (uses environment settings_path if None)
    
    Returns:
        Dict: The loaded settings data, or empty dict if error
    """
    if file_path is None:
        file_path = os.environ.get('settings_path')
        if not file_path:
            print("Error: 'settings_path' environment variable not set and no file_path provided.")
            return {}
    
    try:
        if section:
            return read(file_path, section, {})
        else:
            return read(file_path, default={})
    except Exception as e:
        print(f"Error loading settings: {e}")
        return {}

def get_settings_path() -> Optional[Path]:
    """
    Get the settings file path from environment variables.
    
    Returns:
        Path: The settings file path, or None if not set
    """
    settings_path = os.environ.get('settings_path')
    return Path(settings_path) if settings_path else None

def ensure_settings_structure(file_path: Union[str, Path] = None) -> bool:
    """
    Ensure the settings file has the required structure.
    Creates default sections if they don't exist.
    
    Args:
        file_path: Path to the settings file (uses environment settings_path if None)
    
    Returns:
        bool: True if successful, False otherwise
    """
    if file_path is None:
        file_path = get_settings_path()
        if not file_path:
            return False
    
    try:
        # Load existing data or create empty structure
        data = read(file_path, default={})
        
        # Ensure required sections exist
        required_sections = ['ENVIRONMENT', 'WIDGETS', 'WEBUI']
        modified = False
        
        for section in required_sections:
            if section not in data:
                data[section] = {}
                modified = True
        
        # Write back if modified
        if modified:
            return write(file_path, data)
        
        return True
    except Exception as e:
        print(f"Error ensuring settings structure: {e}")
        return False

def merge_settings(new_data: Dict, section: str = 'WIDGETS', file_path: Union[str, Path] = None) -> bool:
    """
    Merge new settings data with existing data in a specific section.
    
    Args:
        new_data: Dictionary containing new settings to merge
        section: The section to merge data into
        file_path: Path to the settings file (uses environment settings_path if None)
    
    Returns:
        bool: True if successful, False otherwise
    """
    if file_path is None:
        file_path = get_settings_path()
        if not file_path:
            return False
    
    try:
        # Load existing section data
        existing_data = read(file_path, section, {})
        
        # Merge with new data
        merged_data = {**existing_data, **new_data}
        
        # Save back
        return save(file_path, section, merged_data)
    except Exception as e:
        print(f"Error merging settings: {e}")
        return False

def backup_settings(backup_suffix: str = None, file_path: Union[str, Path] = None) -> bool:
    """
    Create a backup of the settings file.
    
    Args:
        backup_suffix: Suffix to add to backup filename (default: timestamp)
        file_path: Path to the settings file (uses environment settings_path if None)
    
    Returns:
        bool: True if successful, False otherwise
    """
    if file_path is None:
        file_path = get_settings_path()
        if not file_path:
            return False
    
    try:
        import time
        
        if backup_suffix is None:
            backup_suffix = str(int(time.time()))
        
        file_path = Path(file_path)
        backup_path = file_path.parent / f"{file_path.stem}_{backup_suffix}{file_path.suffix}"
        
        if file_path.exists():
            data = read(file_path)
            return write(backup_path, data)
        
        return True
    except Exception as e:
        print(f"Error creating settings backup: {e}")
        return False

def reset_section(section: str, file_path: Union[str, Path] = None) -> bool:
    """
    Reset a specific section to empty state.
    
    Args:
        section: The section to reset
        file_path: Path to the settings file (uses environment settings_path if None)
    
    Returns:
        bool: True if successful, False otherwise
    """
    if file_path is None:
        file_path = get_settings_path()
        if not file_path:
            return False
    
    try:
        return save(file_path, section, {})
    except Exception as e:
        print(f"Error resetting section {section}: {e}")
        return False

# --- Legacy Compatibility Functions ---

def get_widget_value(key: str, default: Any = None) -> Any:
    """
    Get a widget value from the WIDGETS section.
    Legacy compatibility function.
    """
    return read_key(key, default)

def set_widget_value(key: str, value: Any) -> bool:
    """
    Set a widget value in the WIDGETS section.
    Legacy compatibility function.
    """
    return write_key(key, value)

# --- Initialize settings structure on import ---
try:
    ensure_settings_structure()
except:
    pass  # Silently ignore initialization errors

# launch.py | by ANXETY - FINAL CORRECTED VERSION
# Original LSDAI launch script for WebUI startup

import os
import sys
from pathlib import Path
import shlex
from IPython import get_ipython

# --- MATPLOTLIB FIXES ---
os.environ['MPLBACKEND'] = 'Agg'
os.environ['MPLCONFIGDIR'] = '/tmp/matplotlib'
os.environ['PYTHONWARNINGS'] = 'ignore::UserWarning:matplotlib'

# --- SETUP PATHS AND MODULES ---
# This assumes that setup.py has already run and set the scr_path environment variable
sys.path.insert(0, str(Path(os.environ.get('scr_path', '')) / 'modules'))
try:
    import json_utils as js
    from webui_utils import get_webui_config # Import the necessary function
except ImportError:
    print("FATAL: Could not import json_utils or webui_utils. Please ensure the setup script ran correctly.")
    sys.exit(1)

# --- ENVIRONMENT & SETTINGS ---
osENV = os.environ
CD = os.chdir
ipySys = get_ipython().system

PATHS = {k: Path(v) for k, v in osENV.items() if k.endswith('_path')}
HOME, VENV, SETTINGS_PATH = PATHS['home_path'], PATHS['venv_path'], PATHS['settings_path']

settings = js.read(SETTINGS_PATH)
UI = js.read(SETTINGS_PATH, 'WEBUI.current', 'automatic1111')
WEBUI_CONFIG = get_webui_config(UI)
WEBUI_PATH = WEBUI_CONFIG['install_path']
commandline_arguments = js.read(SETTINGS_PATH, 'WIDGETS.commandline_arguments', '')
theme_accent = js.read(SETTINGS_PATH, 'WIDGETS.theme_accent', 'anxety')
ENV_NAME = js.read(SETTINGS_PATH, 'ENVIRONMENT.env_name')

class COLORS:
    B, X = "\033[34m", "\033[0m"
COL = COLORS

def get_python_executable():
    """Get the correct Python executable (venv or system)"""
    venv_python_paths = [
        VENV / 'bin' / 'python',
        VENV / 'Scripts' / 'python.exe'  # Windows
    ]
    
    for python_path in venv_python_paths:
        if python_path.exists():
            return str(python_path)
    
    return sys.executable

def get_launch_script_path(webui_path):
    """Find the main launch script for the WebUI using webui_utils."""
    main_script_name = WEBUI_CONFIG.get('main_script', 'launch.py')
    script_path = Path(webui_path) / main_script_name
    if script_path.exists():
        return script_path
    
    # Fallback for older configurations or variations
    possible_scripts = ['webui.py', 'launch.py', 'main.py', 'webui-user.py']
    for script_name in possible_scripts:
        script_path = Path(webui_path) / script_name
        if script_path.exists():
            return script_path
            
    return None

def parse_arguments(args_string):
    """Parse command line arguments safely"""
    if not args_string or not args_string.strip():
        return []
    
    try:
        return shlex.split(args_string)
    except ValueError as e:
        print(f"⚠️ Warning: Could not parse arguments '{args_string}': {e}")
        return args_string.split()

def get_launch_command_str():
    """Construct the final launch command as a shell-executable string."""
    python_exe = get_python_executable()
    launch_script = get_launch_script_path(WEBUI_PATH)
    
    if not Path(WEBUI_PATH).exists():
        print(f"❌ WebUI not found at: {WEBUI_PATH}")
        return None
    
    if not launch_script:
        print(f"❌ No launch script found in: {WEBUI_PATH}")
        return None
    
    print(f"🚀 WebUI Path: {WEBUI_PATH}")
    print(f"🐍 Python: {python_exe}")
    print(f"📋 Script: {launch_script}")
    
    args_list = []
    
    # Start with default arguments from config
    args_list.extend(WEBUI_CONFIG.get('default_args', []))

    # Add environment-specific arguments
    if ENV_NAME in ['Google Colab', 'Kaggle']:
        args_list.extend(WEBUI_CONFIG.get('colab_args', []))
        
    # Add user-provided arguments, allowing overrides
    user_args = parse_arguments(commandline_arguments)
    
    # Create a dict to handle args and avoid duplicates
    final_args = {arg.split('=')[0]: arg for arg in args_list}
    for arg in user_args:
        key = arg.split('=')[0]
        final_args[key] = arg
        
    # Reconstruct the command string
    command_parts = [python_exe, str(launch_script)] + list(final_args.values())
            
    return ' '.join(shlex.quote(part) for part in command_parts)

def launch_webui_process():
    """Launch the WebUI as a subprocess"""
    import subprocess
    
    launch_command = get_launch_command_str()
    
    if not launch_command:
        print("❌ Could not construct launch command")
        return False
    
    print(f"📋 Launch Command: {launch_command}")
    print("🚀 Starting WebUI...")
    
    try:
        original_cwd = os.getcwd()
        os.chdir(WEBUI_PATH)
        
        process = subprocess.Popen(
            launch_command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        
        print("✅ WebUI process started!")
        print("📝 Monitoring output for WebUI URL...")
        print("-" * 50)
        
        for line in iter(process.stdout.readline, ''):
            line = line.strip()
            if line:
                print(line)
                if any(keyword in line.lower() for keyword in ['running on', 'local url', 'public url']):
                    print(f"🎉 {line}")
        
        os.chdir(original_cwd)
        return True
        
    except Exception as e:
        print(f"❌ Error launching WebUI: {e}")
        return False

def main():
    """Main launcher function"""
    try:
        return launch_webui_process()
    except Exception as e:
        print(f"❌ Launch failed: {e}")
        return False

if __name__ == '__main__':
    # This block is for direct execution, e.g. from a terminal
    print(f"{COL.B}Executing LSDAI Launch Script...{COL.X}")
    main()

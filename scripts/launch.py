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
sys.path.insert(0, str(Path(os.environ.get('scr_path', '')) / 'modules'))
try:
    import json_utils as js
except ImportError:
    print("FATAL: Could not import json_utils. Please ensure the setup script ran correctly.")
    sys.exit(1)

# --- ENVIRONMENT & SETTINGS ---
osENV = os.environ
CD = os.chdir
ipySys = get_ipython().system

PATHS = {k: Path(v) for k, v in osENV.items() if k.endswith('_path')}
HOME, VENV, SETTINGS_PATH = PATHS['home_path'], PATHS['venv_path'], PATHS['settings_path']

settings = js.read(SETTINGS_PATH)
UI = settings.get('WEBUI', {}).get('current', 'A1111')
WEBUI = settings.get('WEBUI', {}).get('webui_path', str(HOME / UI))
commandline_arguments = settings.get('WIDGETS', {}).get('commandline_arguments', '')
theme_accent = settings.get('WIDGETS', {}).get('theme_accent', 'anxety')
ENV_NAME = settings.get('ENVIRONMENT', {}).get('env_name')

class COLORS:
    B, X = "\033[34m", "\033[0m"
COL = COLORS

def get_webui_path():
    """Get the WebUI installation path based on settings"""
    
    webui_type = js.read(SETTINGS_PATH, 'WIDGETS.change_webui', 'automatic1111')
    
    webui_paths = {
        'automatic1111': HOME / 'stable-diffusion-webui',
        'ComfyUI': HOME / 'ComfyUI',
        'InvokeAI': HOME / 'InvokeAI'
    }
    
    return webui_paths.get(webui_type, webui_paths['automatic1111'])

def get_python_executable():
    """Get the correct Python executable (venv or system)"""
    
    # Try venv first
    venv_python_paths = [
        VENV / 'bin' / 'python',
        VENV / 'Scripts' / 'python.exe'  # Windows
    ]
    
    for python_path in venv_python_paths:
        if python_path.exists():
            return str(python_path)
    
    # Fall back to system Python
    return sys.executable

def get_launch_script_path(webui_path):
    """Find the main launch script for the WebUI"""
    
    possible_scripts = [
        'webui.py',
        'launch.py', 
        'main.py',
        'webui-user.py'
    ]
    
    for script_name in possible_scripts:
        script_path = webui_path / script_name
        if script_path.exists():
            return script_path
    
    return None

def parse_arguments(args_string):
    """Parse command line arguments safely"""
    
    if not args_string.strip():
        return []
    
    try:
        return shlex.split(args_string)
    except ValueError as e:
        print(f"⚠️ Warning: Could not parse arguments '{args_string}': {e}")
        # Fall back to simple space splitting
        return args_string.split()

def get_launch_command_str():
    """Construct the final launch command as a shell-executable string."""
    
    webui_path = get_webui_path()
    python_exe = get_python_executable()
    launch_script = get_launch_script_path(webui_path)
    
    if not webui_path.exists():
        print(f"❌ WebUI not found at: {webui_path}")
        return None
    
    if not launch_script:
        print(f"❌ No launch script found in: {webui_path}")
        return None
    
    print(f"🚀 WebUI Path: {webui_path}")
    print(f"🐍 Python: {python_exe}")
    print(f"📋 Script: {launch_script}")
    
    args_dict = {}

    # 1. Set default/essential arguments
    args_dict['--enable-insecure-extension-access'] = None
    args_dict['--disable-console-progressbars'] = None
    args_dict['--theme'] = 'dark'
    
    # 2. Parse user-provided arguments, allowing overrides
    user_args = parse_arguments(commandline_arguments)
    i = 0
    while i < len(user_args):
        arg = user_args[i]
        if arg.startswith('--'):
            if i + 1 < len(user_args) and not user_args[i+1].startswith('--'):
                args_dict[arg] = user_args[i+1]
                i += 2
            else:
                args_dict[arg] = None
                i += 1
        else:
            i += 1
            
    # 3. Add environment-specific arguments
    if ENV_NAME == 'Kaggle':
        args_dict['--encrypt-pass'] = 'emoy4cnkm6imbysp84zmfiz1opahooblh7j34sgh'
        
    if ENV_NAME in ['Google Colab', 'Kaggle']:
        args_dict['--share'] = None
        
    if theme_accent != 'anxety':
        args_dict['--anxety'] = theme_accent
        
    # 4. Construct the final command string
    command_parts = [python_exe, str(launch_script)]
    for arg, value in args_dict.items():
        command_parts.append(arg)
        if value is not None:
            command_parts.append(shlex.quote(value)) # Use shlex.quote for safety
            
    return ' '.join(command_parts)

def launch_webui_process():
    """Launch the WebUI as a subprocess"""
    
    import subprocess
    
    webui_path = get_webui_path()
    launch_command = get_launch_command_str()
    
    if not launch_command:
        print("❌ Could not construct launch command")
        return False
    
    print(f"📋 Launch Command: {launch_command}")
    print("🚀 Starting WebUI...")
    
    try:
        # Change to WebUI directory
        original_cwd = os.getcwd()
        os.chdir(webui_path)
        
        # Start the process
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
        
        # Monitor output for important information
        for line in process.stdout:
            line = line.strip()
            if line:
                print(line)
                
                # Look for important status messages
                if any(keyword in line.lower() for keyword in ['running on', 'local url', 'public url']):
                    print(f"🎉 {line}")
                elif 'error' in line.lower():
                    print(f"⚠️ {line}")
        
        # Restore original directory
        os.chdir(original_cwd)
        
        return True
        
    except Exception as e:
        print(f"❌ Error launching WebUI: {e}")
        return False

def quick_launch():
    """Quick launch without extensive checks"""
    
    print("⚡ LSDAI Quick Launch")
    print("=" * 30)
    
    return launch_webui_process()

def launch_with_health_check():
    """Launch with system health checks"""
    
    print("🚀 LSDAI WebUI Launcher")
    print("=" * 30)
    
    # Health checks
    print("🔍 Performing pre-launch checks...")
    
    webui_path = get_webui_path()
    if not webui_path.exists():
        print(f"❌ WebUI not installed at: {webui_path}")
        print("🔧 Please run Cell 3 (Downloading) first")
        return False
    
    launch_script = get_launch_script_path(webui_path)
    if not launch_script:
        print(f"❌ No launch script found in: {webui_path}")
        return False
    
    python_exe = get_python_executable()
    print(f"✅ Python executable: {python_exe}")
    print(f"✅ WebUI path: {webui_path}")
    print(f"✅ Launch script: {launch_script}")
    
    # Check for required Python packages
    try:
        import torch
        print(f"✅ PyTorch {torch.__version__}")
    except ImportError:
        print("⚠️ PyTorch not found - WebUI may not work properly")
    
    print("✅ Environment is ready.")
    print("-" * 30)
    
    return launch_webui_process()

def show_launch_info():
    """Show information about the launch configuration"""
    
    print("📋 LSDAI Launch Configuration")
    print("=" * 40)
    
    webui_type = js.read(SETTINGS_PATH, 'WIDGETS.change_webui', 'automatic1111')
    print(f"🚀 WebUI Type: {webui_type}")
    
    webui_path = get_webui_path()
    print(f"📁 WebUI Path: {webui_path}")
    
    python_exe = get_python_executable()
    print(f"🐍 Python: {python_exe}")
    
    print(f"⚙️ Arguments: {commandline_arguments}")
    print(f"🎨 Theme: {theme_accent}")
    print(f"🌍 Environment: {ENV_NAME}")
    
    if webui_path.exists():
        launch_script = get_launch_script_path(webui_path)
        print(f"📋 Launch Script: {launch_script}")
        print("✅ Ready to launch")
    else:
        print("❌ WebUI not installed")
        print("🔧 Run Cell 3 (Downloading) first")

# --- MAIN EXECUTION ---
def main():
    """Main launcher function"""
    
    try:
        return launch_with_health_check()
    except Exception as e:
        print(f"❌ Launch failed: {e}")
        return False

if __name__ == '__main__':
    print("✅ Environment is ready.")
    print(f"{COL.B}Please use the launch functions in your notebook cell.{COL.X}")
    
    # Show current configuration
    show_launch_info()

# For direct execution in notebook cells
if "run_path" in globals():
    main()

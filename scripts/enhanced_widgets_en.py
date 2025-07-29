#@title **1. Enhanced Widgets** 🔽 { display-mode: "form" }

import os
import json
from pathlib import Path

# --- Robust Environment Setup for Widgets ---
# This patch ensures that even if environment variables are not perfectly set,
# the widget script can fall back to the settings.json file.

print("🔧 Verifying environment for widgets...")

settings_path = Path('/content/LSDAI/settings.json')
widget_script_path = Path('/content/LSDAI/scripts/enhanced_widgets_integration.py')

if settings_path.exists():
    with open(settings_path, 'r') as f:
        settings = json.load(f)
    
    # Get paths from the "ENVIRONMENT" section of settings.json
    env_paths = settings.get("ENVIRONMENT", {})
    
    # Check for required paths and set them in the environment if they are missing
    required_paths = ['home_path', 'scr_path', 'venv_path', 'settings_path']
    paths_updated = False
    for path_key in required_paths:
        if path_key not in os.environ and path_key in env_paths:
            os.environ[path_key] = str(env_paths[path_key])
            paths_updated = True
            
    if paths_updated:
        print("✅ Environment variables loaded from settings.json as a fallback.")
    else:
        print("✅ Environment variables appear to be correctly set.")
else:
    print("⚠️ Warning: settings.json not found. The widget script may fail if environment variables are not set.")

# --- Run the main widget integration script ---
if widget_script_path.exists():
    %run {widget_script_path}
else:
    print(f"❌ Error: The widget script could not be found at {widget_script_path}")

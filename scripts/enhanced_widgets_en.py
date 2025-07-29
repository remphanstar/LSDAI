# ~ enhanced_widgets_integration.py | by ANXETY - Robust Fallback Version ~

import os
import sys
from pathlib import Path
from IPython.display import display, HTML

# --- Setup Paths ---
try:
    SCR_PATH = Path(os.environ.get('scr_path', '/content/LSDAI'))
    sys.path.insert(0, str(SCR_PATH / 'modules'))
    
    ENHANCED_WIDGETS_PATH = SCR_PATH / 'scripts' / 'enhanced_widgets_en.py'
    ORIGINAL_WIDGETS_PATH = SCR_PATH / 'scripts' / 'widgets_en.py'
    
    print("🎯 LSDAI Widget Interface Loader")
    print("="*40)
    print(f"📁 Working directory: {os.getcwd()}")
except Exception as e:
    print(f"❌ FATAL: Could not set up initial paths: {e}")
    sys.exit(1)

def display_error(title, message, details):
    """Displays a formatted error message in the notebook."""
    error_html = f"""
    <div style="border: 2px solid #ef4444; background-color: #fee2e2; padding: 1rem; border-radius: 0.5rem; color: #b91c1c; margin: 10px 0;">
        <h3 style="margin-top: 0;">⚠️ {title}</h3>
        <p>{message}</p>
        <details style="margin-top: 10px;">
            <summary><b>Error Details (click to expand)</b></summary>
            <pre style="white-space: pre-wrap; word-wrap: break-word; background: #fecaca; padding: 0.5rem; border-radius: 0.25rem; margin-top: 5px; font-size: 12px;">{details}</pre>
        </details>
    </div>
    """
    display(HTML(error_html))

# --- Main Execution ---
try:
    print("✅ Attempting to load Enhanced Widget UI...")
    if not ENHANCED_WIDGETS_PATH.exists():
        raise FileNotFoundError("enhanced_widgets_en.py not found.")
    
    # Use IPython's run_line_magic to execute the script
    get_ipython().run_line_magic('run', str(ENHANCED_WIDGETS_PATH))
    print("✅ Enhanced Widget UI loaded successfully.")

except Exception as e:
    display_error(
        "Enhanced Widgets Loading Error",
        "The enhanced UI script failed to load. Falling back to the original, stable widget interface.",
        e
    )
    
    try:
        print("\n" + "─"*40)
        print("📦 Loading Original Widget UI as fallback...")
        if not ORIGINAL_WIDGETS_PATH.exists():
            raise FileNotFoundError("widgets_en.py not found. Cannot load any UI.")
            
        get_ipython().run_line_magic('run', str(ORIGINAL_WIDGETS_PATH))
        print("✅ Original Widget UI loaded successfully.")

    except Exception as fallback_e:
        display_error(
            "Fallback UI Loading Error",
            "The original widget UI also failed to load. Please check the repository files.",
            fallback_e
        )

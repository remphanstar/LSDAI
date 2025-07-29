# ~ enhanced_widgets_integration.py | by ANXETY - Clean Loader (Corrected) ~

# This script provides a seamless user experience by attempting to load the new,
# feature-rich enhanced widget interface, while providing a fallback to the
# original, stable widget interface if any issues arise.

from IPython.display import display, HTML
from pathlib import Path

def run_script(script_path):
    """Executes a script file using standard Python."""
    try:
        with open(script_path, 'r', encoding='utf-8') as f:
            script_content = f.read()
        # The 'globals()' argument is important to ensure the script
        # runs in the main notebook scope, just like %run would.
        exec(script_content, globals())
    except FileNotFoundError:
        print(f"❌ Error: Script not found at {script_path}")
    except Exception as e:
        # Re-raise the exception so the main try...except block can catch it.
        raise e

try:
    # Attempt to run the new enhanced widgets script. This script contains the
    # modern, refactored UI with all the requested functionality.
    print("✅ Attempting to load Enhanced Widget UI...")
    run_script('scripts/enhanced_widgets_en.py')
    print("✅ Enhanced Widget UI loaded successfully.")

except Exception as e:
    # If any error occurs during the execution of the enhanced script,
    # catch the exception, print a detailed error message, and then
    # fall back to the original script.
    
    error_message = f"""
    <div style="border: 2px solid #ef4444; background-color: #fee2e2; padding: 1rem; border-radius: 0.5rem; color: #b91c1c;">
        <h3 style="margin-top: 0;">⚠️ Error Loading Enhanced Widgets</h3>
        <p>The new UI script (`enhanced_widgets_en.py`) failed to load. This is usually due to a syntax error or a problem with the widget layout.</p>
        <p><b>Falling back to the original, stable widget interface.</b></p>
        <hr style="border-color: #fca5a5;">
        <p><b>Error Details:</b></p>
        <pre style="white-space: pre-wrap; word-wrap: break-word; background: #fecaca; padding: 0.5rem; border-radius: 0.25rem;">{e}</pre>
    </div>
    """
    display(HTML(error_message))
    
    # Run the original, stable widgets script as a fallback
    print("📦 Falling back to Original Widget UI...")
    run_script('scripts/widgets_en.py')


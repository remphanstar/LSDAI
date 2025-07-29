# Enhanced widgets integration - FIXED AND SIMPLIFIED
# This script provides a seamless user experience by attempting to load the new,
# feature-rich enhanced widget interface, while providing a fallback to the
# original, stable widget interface if any issues arise.

from IPython.display import display, HTML
from pathlib import Path
import sys
import os

def run_script(script_path):
    """Executes a script file using standard Python."""
    try:
        script_path = Path(script_path)
        if not script_path.exists():
            print(f"❌ Error: Script not found at {script_path}")
            return False
            
        with open(script_path, 'r', encoding='utf-8') as f:
            script_content = f.read()
        
        # Execute in the global namespace to maintain compatibility
        exec(script_content, globals())
        return True
        
    except FileNotFoundError:
        print(f"❌ Error: Script not found at {script_path}")
        return False
    except Exception as e:
        # Re-raise the exception so the main try...except block can catch it.
        raise e

def show_error_message(error_details):
    """Display a styled error message in the notebook"""
    error_html = f"""
    <div style="border: 2px solid #ef4444; background-color: #fee2e2; padding: 1rem; border-radius: 0.5rem; color: #b91c1c; margin: 10px 0;">
        <h3 style="margin-top: 0;">⚠️ Enhanced Widgets Loading Error</h3>
        <p>The enhanced UI script failed to load. Falling back to the original, stable widget interface.</p>
        <details style="margin-top: 10px;">
            <summary><b>Error Details (click to expand)</b></summary>
            <pre style="white-space: pre-wrap; word-wrap: break-word; background: #fecaca; padding: 0.5rem; border-radius: 0.25rem; margin-top: 5px; font-size: 12px;">{error_details}</pre>
        </details>
    </div>
    """
    display(HTML(error_html))

def load_enhanced_widgets():
    """Attempt to load enhanced widgets with comprehensive error handling"""
    
    # Try multiple possible locations for enhanced widgets
    enhanced_script_paths = [
        'scripts/enhanced_widgets_en.py',
        'enhanced_widgets_en.py',
        Path(os.environ.get('scr_path', '/content/LSDAI')) / 'scripts' / 'enhanced_widgets_en.py'
    ]
    
    for script_path in enhanced_script_paths:
        if Path(script_path).exists():
            try:
                print("✅ Attempting to load Enhanced Widget UI...")
                success = run_script(script_path)
                if success:
                    print("✅ Enhanced Widget UI loaded successfully.")
                    return True
                    
            except Exception as e:
                print(f"⚠️ Enhanced widgets failed from {script_path}: {e}")
                show_error_message(str(e))
                continue
    
    print("⚠️ Enhanced widgets not found or failed to load")
    return False

def load_original_widgets():
    """Load the original, stable widgets interface"""
    
    # Try multiple possible locations for original widgets
    original_script_paths = [
        'scripts/widgets_en.py',
        'widgets_en.py',
        Path(os.environ.get('scr_path', '/content/LSDAI')) / 'scripts' / 'widgets_en.py'
    ]
    
    for script_path in original_script_paths:
        if Path(script_path).exists():
            try:
                print("📦 Loading Original Widget UI...")
                success = run_script(script_path)
                if success:
                    print("✅ Original Widget UI loaded successfully.")
                    return True
                    
            except Exception as e:
                print(f"❌ Original widgets also failed from {script_path}: {e}")
                continue
    
    print("❌ No widget interface found!")
    return False

def main():
    """Main widget loading function"""
    
    print("🎯 LSDAI Widget Interface Loader")
    print("=" * 40)
    
    # Ensure we're in the right directory
    scr_path = os.environ.get('scr_path', '/content/LSDAI')
    if os.path.exists(scr_path):
        os.chdir(scr_path)
        print(f"📁 Working directory: {scr_path}")
    
    # Add modules to Python path if not already there
    modules_path = os.path.join(scr_path, 'modules')
    if os.path.exists(modules_path) and modules_path not in sys.path:
        sys.path.insert(0, modules_path)
        print(f"🐍 Added {modules_path} to Python path")
    
    # Try enhanced widgets first
    if load_enhanced_widgets():
        return
    
    # Fall back to original widgets
    if load_original_widgets():
        return
    
    # If both fail, show instructions
    show_fallback_instructions()

def show_fallback_instructions():
    """Show instructions when all widget interfaces fail"""
    
    instructions_html = """
    <div style="border: 2px solid #f59e0b; background-color: #fef3c7; padding: 1rem; border-radius: 0.5rem; color: #92400e; margin: 10px 0;">
        <h3 style="margin-top: 0;">⚠️ Widget Interface Not Available</h3>
        <p>Both enhanced and original widget interfaces failed to load. This might be due to:</p>
        <ul>
            <li>Missing or corrupted script files</li>
            <li>Incomplete LSDAI setup</li>
            <li>Python path or module import issues</li>
        </ul>
        <p><b>Troubleshooting Steps:</b></p>
        <ol>
            <li>Re-run Cell 1 (Setup) to ensure all files are downloaded</li>
            <li>Check that the LSDAI repository was cloned successfully</li>
            <li>Verify that scripts/widgets_en.py exists</li>
            <li>Try restarting the runtime and running from Cell 1</li>
        </ol>
    </div>
    """
    display(HTML(instructions_html))

# Execute the main function when this script is run
if __name__ == "__main__" or "run_path" in globals():
    main()

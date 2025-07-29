#@title **3. Enhanced Launch** 🔽 { display-mode: "form" }
#@markdown ### Launch WebUI with system optimizations and monitoring

import os
from pathlib import Path

# Path to the script that needs fixing
script_path = Path('/content/LSDAI/scripts/enhanced_launch_integration.py')

if not script_path.exists():
    print(f"❌ Error: Launch script not found at {script_path}")
else:
    print("🔧 Applying runtime patch to fix widget creation error...")
    try:
        # Read the original, broken script code
        original_code = script_path.read_text()

        # Define the incorrect line of code causing the crash
        broken_line = "self.widgets['check_custom_nodes_deps'] = self.factory.create_checkbox('Check ComfyUI Dependencies', True, layout={'display': 'none'})"
        
        # Define the corrected line using keyword arguments to ensure proper assignment
        fixed_line = "self.widgets['check_custom_nodes_deps'] = self.factory.create_checkbox(description='Check ComfyUI Dependencies', value=True, layout={'display': 'none'})"

        # Check if the patch is needed
        if broken_line in original_code:
            # Replace the broken line with the corrected one
            patched_code = original_code.replace(broken_line, fixed_line)
            print("✅ Patch successfully applied in memory.")
            
            # Change to the script's directory and execute the patched code
            %cd /content/LSDAI
            exec(patched_code, {'__name__': '__main__', '__file__': str(script_path)})

        else:
            # If the broken line isn't found, the script may already be fixed
            print("⚠️  Warning: Broken code not found. The script may already be fixed. Running as is.")
            %run {script_path}

    except Exception as e:
        # Fallback in case of any unexpected errors during the patching process
        print(f"❌ An error occurred during the patching or execution process: {e}")
        print("   Running the original script as a fallback...")
        %run {script_path}

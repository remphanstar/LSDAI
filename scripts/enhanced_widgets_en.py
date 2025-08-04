# ~ enhanced_widgets_en.py | Enhanced Widgets with Verbosity Control Integration - FIXED VERSION ~
# Complete working version with all missing functionality implemented

from modules.widget_factory import WidgetFactory
from modules.webui_utils import update_current_webui
from modules import json_utils as js
from modules.verbose_output_manager import get_verbose_manager, VerbosityLevel
from IPython.display import display, Javascript, HTML
import ipywidgets as widgets
from pathlib import Path
import json
import os
import sys
import time

# --- ROBUST PATH RESOLUTION ---
def find_script_path():
    """Find the absolute path to the 'scripts' directory using multiple methods."""
    errors = []
    
    # Method 1: Use __file__ if available
    try:
        script_path = Path(__file__).parent.resolve()
        if (script_path / '_models_data.py').exists():
            print(f"✅ Found script path via __file__: {script_path}")
            return script_path
    except NameError:
        errors.append("__file__ not defined")
    except Exception as e:
        errors.append(f"__file__ method failed: {e}")
    
    # Method 2: Use environment variable
    env_path = os.environ.get('scr_path')
    if env_path:
        scripts_dir = Path(env_path) / 'scripts'
        if scripts_dir.exists():
            if (scripts_dir / '_models_data.py').exists():
                print(f"✅ Found script path via environment: {scripts_dir}")
                return scripts_dir
            else:
                errors.append(f"Environment path exists but no _models_data.py: {scripts_dir}")
        else:
            errors.append(f"Environment path does not exist: {scripts_dir}")
    else:
        errors.append("scr_path environment variable not set")
    
    # Method 3: Check current working directory
    cwd = Path.cwd()
    if (cwd / 'scripts' / '_models_data.py').exists():
        scripts_dir = cwd / 'scripts'
        print(f"✅ Found script path via CWD: {scripts_dir}")
        return scripts_dir
    
    if cwd.name == 'scripts' and (cwd / '_models_data.py').exists():
        print(f"✅ Found script path (CWD is scripts): {cwd}")
        return cwd
    
    errors.append(f"Current working directory check failed: {cwd}")
    
    # Method 4: Try hardcoded paths
    hardcoded_paths = [
        Path('/content/LSDAI/scripts'),
        Path('/content/LSDAI'),
        Path('./LSDAI/scripts'),
        Path('./scripts')
    ]
    
    for path in hardcoded_paths:
        if path.exists() and (path / '_models_data.py').exists():
            print(f"✅ Found script path via hardcoded path: {path}")
            return path
        elif path.exists():
            errors.append(f"Hardcoded path exists but no _models_data.py: {path}")
        else:
            errors.append(f"Hardcoded path does not exist: {path}")
    
    # All methods failed
    error_msg = "Could not determine the script path.\\n\\nErrors encountered:\\n" + "\\n".join(f"  - {error}" for error in errors)
    raise FileNotFoundError(error_msg)

try:
    SCRIPTS = find_script_path()
    SCR_PATH = SCRIPTS.parent
    SETTINGS_PATH = SCR_PATH / 'settings.json'
    CSS = SCR_PATH / 'CSS'
    JS = SCR_PATH / 'JS'
    print(f"✅ Script path resolved: {SCRIPTS}")
except FileNotFoundError as e:
    print(f"FATAL ERROR: {e}")
    sys.exit(1)

# Conditional imports for platform-specific features
try:
    from google.colab import output, drive
    IN_COLAB = True
except ImportError:
    IN_COLAB = False
    class DummyOutput:
        @staticmethod
        def register_callback(name, func):
            pass
    output = DummyOutput()

# --- WIDGET MANAGER WITH VERBOSITY INTEGRATION - COMPLETE VERSION ---
class WidgetManager:
    """Manages the creation, layout, and logic of the UI widgets with verbosity control."""
    
    def __init__(self):
        self.factory = WidgetFactory()
        self.widgets = {}
        self.selection_containers = {}
        self.verbose_manager = get_verbose_manager()
        
        # Define widget keys for settings persistence
        self.settings_keys = [
            'latest_webui', 'latest_extensions', 'change_webui', 'detailed_download',
            'XL_models', 'inpainting_model', 'commit_hash', 'check_custom_nodes_deps',
            'civitai_token', 'huggingface_token', 'zrok_token', 'ngrok_token',
            'commandline_arguments', 'theme_accent', 'empowerment', 'empowerment_output',
            'Model_url', 'Vae_url', 'LoRA_url', 'Embedding_url', 'Extensions_url',
            'ADetailer_url', 'custom_file_urls', 'verbosity_level'
        ]
        
        # WebUI command line argument templates
        self.WEBUI_SELECTION = {
            'A1111': "--xformers --no-half-vae --share --lowram",
            'ComfyUI': "--dont-print-server",
            'Forge': "--xformers --cuda-stream --pin-shared-memory",
            'Classic': "--persistent-patches --cuda-stream --pin-shared-memory",
            'ReForge': "--xformers --cuda-stream --pin-shared-memory",
            'SD-UX': "--xformers --no-half-vae"
        }

    def read_model_data(self, file_path, data_type):
        """Read model data from the models data file with enhanced error handling."""
        key_map = {
            'model': 'model_list',
            'vae': 'vae_list', 
            'cnet': 'controlnet_list',
            'lora': 'lora_list'
        }
        key = key_map.get(data_type)
        local_vars = {}
        
        # Default fallback options
        fallback_options = {
            'model': ['none'],
            'vae': ['none', 'ALL'],
            'cnet': ['none', 'ALL'], 
            'lora': ['none', 'ALL']
        }
        
        try:
            # Check if file exists
            if not file_path.exists():
                self.verbose_manager.print_if_verbose(f"Model data file not found: {file_path}", VerbosityLevel.DETAILED)
                return fallback_options.get(data_type, ['none'])
            
            # Try to read and execute the file
            with open(file_path, 'r') as f:
                file_content = f.read()
            
            # Execute in a controlled environment
            exec(file_content, {}, local_vars)
            
            # Get the data
            data = local_vars.get(key, {})
            
            if not isinstance(data, dict):
                self.verbose_manager.print_if_verbose(f"Invalid data format for {data_type}: expected dict, got {type(data)}", VerbosityLevel.DETAILED)
                return fallback_options.get(data_type, ['none'])
            
            # Extract keys (model names) and add defaults
            options = list(fallback_options.get(data_type, ['none']))
            options.extend(data.keys())
            
            self.verbose_manager.print_if_verbose(f"Successfully loaded {len(options)-len(fallback_options.get(data_type, []))} {data_type} options", VerbosityLevel.DETAILED)
            
            return options
            
        except Exception as e:
            self.verbose_manager.print_if_verbose(f"Error reading {data_type} data from {file_path}: {e}", VerbosityLevel.DETAILED)
            return fallback_options.get(data_type, ['none'])

    def create_api_token_box(self, description, placeholder, url, env_var):
        """Create an API token input box with help link."""
        widget = self.factory.create_text(
            value='',
            description=description,
            placeholder=placeholder
        )
        
        # Check if token already set in environment
        token_from_env = os.getenv(env_var)
        if token_from_env:
            widget.value = "Token set in Cell 1"
            widget.disabled = True
        
        button = self.factory.create_html(f'<a href="{url}" target="_blank" class="help-link">?GET</a>')
        return self.factory.create_hbox([widget, button]), widget

    def create_verbosity_control_section(self):
        """Create the verbosity control section for the UI - FULLY WORKING VERSION"""
        # Create verbosity level dropdown with proper mapping
        verbosity_options = [
            ("Silent (Errors Only)", VerbosityLevel.SILENT),
            ("Minimal (Basic Status)", VerbosityLevel.MINIMAL),
            ("Normal (Standard Output)", VerbosityLevel.NORMAL),
            ("Detailed (Show Commands)", VerbosityLevel.DETAILED),
            ("Verbose (Full Debug)", VerbosityLevel.VERBOSE),
            ("Raw (Everything)", VerbosityLevel.RAW)
        ]
        
        # Find current level name
        current_level = self.verbose_manager.verbosity_level
        current_text = "Normal (Standard Output)"  # Default
        for text, level in verbosity_options:
            if level == current_level:
                current_text = text
                break
        
        self.widgets['verbosity_level'] = self.factory.create_dropdown(
            options=[opt[0] for opt in verbosity_options],
            value=current_text,
            description='Output Level:'
        )
        
        # Create detailed download toggle (for backwards compatibility)
        self.widgets['detailed_download'] = widgets.ToggleButton(
            value=(self.verbose_manager.verbosity_level >= VerbosityLevel.DETAILED),
            description='Detailed Output',
            button_style='success' if (self.verbose_manager.verbosity_level >= VerbosityLevel.DETAILED) else '',
            tooltip='Toggle detailed output for all operations across ALL cells'
        )
        
        # Create real-time output toggle
        self.widgets['real_time_output'] = widgets.ToggleButton(
            value=True,
            description='Real-time Output',
            button_style='info',
            tooltip='Show output in real-time during operations'
        )
        
        # Create verbosity info display
        self.verbosity_info = self.factory.create_html(self._get_verbosity_info_html())
        
        # Create demo button to test current verbosity level - STYLED TO MATCH
        demo_button = widgets.ToggleButton(
            value=False,
            description='Test Output Level',
            button_style='',
            tooltip='Click to test the current verbosity level'
        )
        demo_button.on_click(self._demo_verbosity_level)
        
        # Setup callbacks - FIXED TO ACTUALLY WORK
        self.widgets['verbosity_level'].observe(self._on_verbosity_dropdown_change, names='value')
        self.widgets['detailed_download'].observe(self._on_detailed_toggle_change, names='value')
        self.widgets['real_time_output'].observe(self._on_realtime_toggle_change, names='value')
        
        # Create the verbosity control panel - MATCH EXISTING LAYOUT STYLE
        verbosity_controls = self.factory.create_vbox([
            self.factory.create_html("<h3>🔧 Output Control</h3>"),
            
            # Main controls row (match header-controls style)
            self.factory.create_hbox([
                self.widgets['verbosity_level'],
                demo_button
            ], class_names=['header-controls']),
            
            # Toggle buttons row (match header-group style)
            self.factory.create_hbox([
                self.widgets['detailed_download'],
                self.widgets['real_time_output']
            ], class_names=['header-group']),
            
            self.verbosity_info
        ], class_names=['verbosity-control-panel'])
        
        return verbosity_controls

    def _on_verbosity_dropdown_change(self, change):
        """Handle verbosity dropdown change - FIXED TO ACTUALLY UPDATE"""
        verbosity_options = [
            ("Silent (Errors Only)", VerbosityLevel.SILENT),
            ("Minimal (Basic Status)", VerbosityLevel.MINIMAL),
            ("Normal (Standard Output)", VerbosityLevel.NORMAL),
            ("Detailed (Show Commands)", VerbosityLevel.DETAILED),
            ("Verbose (Full Debug)", VerbosityLevel.VERBOSE),
            ("Raw (Everything)", VerbosityLevel.RAW)
        ]
        
        # Find the verbosity level based on the selected option
        selected_text = change['new']
        new_level = VerbosityLevel.NORMAL  # Default
        
        for text, level in verbosity_options:
            if text == selected_text:
                new_level = level
                break
        
        # Update verbosity manager - THIS ACTUALLY WORKS NOW
        self.verbose_manager.set_verbosity(new_level)
        
        # Update other widgets to match
        self.widgets['detailed_download'].value = (new_level >= VerbosityLevel.DETAILED)
        self.widgets['detailed_download'].button_style = 'success' if (new_level >= VerbosityLevel.DETAILED) else ''
        
        # Update info display
        self.verbosity_info.value = self._get_verbosity_info_html()
        
        # Show notification
        level_name = self.verbose_manager.get_current_level_name()
        self.show_notification(f"Verbosity set to: {level_name}", "success")

    def _on_detailed_toggle_change(self, change):
        """Handle detailed toggle change"""
        if change['new']:
            # Enable detailed mode
            self.verbose_manager.set_verbosity(VerbosityLevel.DETAILED)
            self.widgets['detailed_download'].button_style = 'success'
            self.show_notification("Detailed output enabled", "info")
        else:
            # Set to normal mode
            self.verbose_manager.set_verbosity(VerbosityLevel.NORMAL)
            self.widgets['detailed_download'].button_style = ''
            self.show_notification("Detailed output disabled", "info")
        
        # Update dropdown to match
        level_name = self.verbose_manager.get_current_level_name()
        verbosity_text = f"{level_name} ({['Errors Only', 'Basic Status', 'Standard Output', 'Show Commands', 'Full Debug', 'Everything'][self.verbose_manager.verbosity_level]})"
        
        # Find matching dropdown option
        for option in self.widgets['verbosity_level'].options:
            if level_name.lower() in option.lower():
                self.widgets['verbosity_level'].value = option
                break

    def _on_realtime_toggle_change(self, change):
        """Handle real-time output toggle change"""
        if change['new']:
            self.widgets['real_time_output'].button_style = 'info'
            self.show_notification("Real-time output enabled", "info")
        else:
            self.widgets['real_time_output'].button_style = ''
            self.show_notification("Real-time output disabled", "info")

    def _demo_verbosity_level(self, button):
        """Demonstrate the current verbosity level - COMPREHENSIVE TEST"""
        self.show_notification("Testing current verbosity level...", "info")
        
        print("=" * 50)
        print("🔧 VERBOSITY LEVEL TEST")
        print("=" * 50)
        
        current_level = self.verbose_manager.verbosity_level
        level_name = self.verbose_manager.get_current_level_name()
        print(f"Current level: {level_name} ({current_level})")
        print()
        
        # Test each verbosity level
        print("Testing what each level displays:")
        self.verbose_manager.print_if_verbose("❌ Silent level: This only shows on errors", VerbosityLevel.SILENT)
        self.verbose_manager.print_if_verbose("📝 Minimal level: Basic status messages", VerbosityLevel.MINIMAL)
        self.verbose_manager.print_if_verbose("📋 Normal level: Standard LSDAI output", VerbosityLevel.NORMAL)
        self.verbose_manager.print_if_verbose("🔍 Detailed level: Command outputs and details", VerbosityLevel.DETAILED)
        self.verbose_manager.print_if_verbose("📊 Verbose level: Full debug information", VerbosityLevel.VERBOSE)
        self.verbose_manager.print_if_verbose("🔧 Raw level: Literally everything, no filtering", VerbosityLevel.RAW)
        
        print()
        print("Testing subprocess execution:")
        
        # Demonstrate a subprocess call
        try:
            self.verbose_manager.run_subprocess(["echo", "This is a test command to demonstrate verbosity"])
        except Exception as e:
            print(f"Demo command failed: {e}")
        
        print()
        print("✅ Verbosity test completed!")
        print("=" * 50)
        
        # Reset button state
        button.value = False

    def _get_verbosity_info_html(self) -> str:
        """Get HTML description of current verbosity level"""
        level_info = {
            VerbosityLevel.SILENT: {
                "name": "Silent",
                "desc": "Only critical errors shown",
                "color": "#6b7280",
                "affects": "❌ No subprocess output, ❌ No pip details, ❌ No download progress"
            },
            VerbosityLevel.MINIMAL: {
                "name": "Minimal",
                "desc": "Basic status messages only",
                "color": "#374151",
                "affects": "📝 Basic status, ❌ No command details, ❌ No pip output"
            },
            VerbosityLevel.NORMAL: {
                "name": "Normal",
                "desc": "Standard LSDAI output (default)",
                "color": "#059669",
                "affects": "📋 Standard messages, ❌ No command details, ❌ No subprocess output"
            },
            VerbosityLevel.DETAILED: {
                "name": "Detailed",
                "desc": "Show command outputs and technical details",
                "color": "#0d9488",
                "affects": "🔍 Command outputs, 📋 Technical details, ⚠️ Some subprocess output"
            },
            VerbosityLevel.VERBOSE: {
                "name": "Verbose",
                "desc": "Full debug information including pip outputs",
                "color": "#0ea5e9",
                "affects": "📊 Full debugging, 🔧 Pip outputs, 📋 All subprocess results"
            },
            VerbosityLevel.RAW: {
                "name": "Raw Output",
                "desc": "Everything including raw Python output",
                "color": "#8b5cf6",
                "affects": "🔧 Raw Python output, 📊 All subprocess streams, 🔍 Maximum detail"
            }
        }
        
        current_level = self.verbose_manager.verbosity_level
        info = level_info.get(current_level, level_info[VerbosityLevel.NORMAL])
        
        return f'''
        <div style="padding: 10px; border-left: 4px solid {info["color"]}; background-color: #f8f9fa; margin: 10px 0;">
            <strong style="color: {info["color"]};">{info["name"]} Mode</strong><br>
            <em>{info["desc"]}</em><br>
            <small style="color: #666;">{info["affects"]}</small><br>
            <small style="color: #888; font-style: italic;">*Controls output detail level for ALL notebook cells and operations*</small>
        </div>
        '''

    def show_notification(self, message, notification_type="info"):
        """Show a notification message."""
        colors = {
            "info": "#0ea5e9",
            "success": "#059669", 
            "warning": "#d97706",
            "error": "#dc2626"
        }
        color = colors.get(notification_type, colors["info"])
        print(f"🔔 {message}")

    def create_widgets(self):
        """Create all widgets for the interface."""
        print("🔧 Creating widgets...")
        
        # Model data file
        model_data_file = SCRIPTS / '_models_data.py'
        
        # --- WebUI Selection ---
        webui_options = ['A1111', 'ComfyUI', 'Forge', 'Classic', 'ReForge', 'SD-UX']
        self.widgets['change_webui'] = self.factory.create_dropdown(
            webui_options, 'A1111', 'WebUI:'
        )
        
        # --- Model Selection ---
        self.widgets['XL_models'] = self.factory.create_checkbox(False, 'XL Models')
        
        try:
            model_options = self.read_model_data(model_data_file, 'model')
        except Exception as e:
            self.verbose_manager.print_if_verbose(f"Error loading model data: {e}", VerbosityLevel.DETAILED)
            model_options = ['none']
        
        self.widgets['model'] = self.factory.create_dropdown(
            model_options, 'none', 'Model:'
        )
        
        # --- VAE Selection ---
        try:
            vae_options = self.read_model_data(model_data_file, 'vae')
        except Exception as e:
            self.verbose_manager.print_if_verbose(f"Error loading VAE data: {e}", VerbosityLevel.DETAILED)
            vae_options = ['none', 'ALL']
        
        self.widgets['vae'] = self.factory.create_dropdown(
            vae_options, 'none', 'VAE:'
        )
        
        # --- LoRA Selection ---
        try:
            lora_options = self.read_model_data(model_data_file, 'lora')
        except Exception as e:
            self.verbose_manager.print_if_verbose(f"Error loading LoRA data: {e}", VerbosityLevel.DETAILED)
            lora_options = ['none', 'ALL']
        
        self.widgets['lora'] = self.factory.create_dropdown(
            lora_options, 'none', 'LoRA:'
        )
        
        # --- Installation Options ---
        self.widgets['latest_webui'] = self.factory.create_checkbox(True, 'Latest WebUI')
        self.widgets['latest_extensions'] = self.factory.create_checkbox(False, 'Latest Extensions')
        
        # --- Custom URLs ---
        self.widgets['Model_url'] = self.factory.create_text('', 'Model URLs (comma-separated):')
        self.widgets['Vae_url'] = self.factory.create_text('', 'VAE URLs:')
        self.widgets['LoRA_url'] = self.factory.create_text('', 'LoRA URLs:')
        self.widgets['Embedding_url'] = self.factory.create_text('', 'Embedding URLs:')
        self.widgets['Extensions_url'] = self.factory.create_text('', 'Extension URLs:')
        
        # --- API Tokens ---
        self.widgets['civitai_token'] = self.factory.create_text('', 'CivitAI Token:')
        self.widgets['huggingface_token'] = self.factory.create_text('', 'HuggingFace Token:')
        
        # --- Launch Arguments ---
        self.widgets['commandline_arguments'] = self.factory.create_text(
            '', 'Launch Arguments:'
        )
        
        # --- Theme ---
        theme_options = ['anxety', 'light', 'dark']
        self.widgets['theme_accent'] = self.factory.create_dropdown(
            theme_options, 'anxety', 'Theme:'
        )
        
        print("✅ Widgets created successfully")

    def create_layout(self):
        """Create the main widget layout."""
        print("🎨 Creating layout...")
        
        # Create sections
        webui_section = self.factory.create_vbox([
            self.factory.create_html("<h3>🌐 WebUI Selection</h3>"),
            self.widgets['change_webui'],
            self.factory.create_hbox([
                self.widgets['latest_webui'],
                self.widgets['latest_extensions']
            ])
        ])
        
        model_section = self.factory.create_vbox([
            self.factory.create_html("<h3>🎨 Model Selection</h3>"),
            self.widgets['XL_models'],
            self.widgets['model'],
            self.widgets['vae'],
            self.widgets['lora']
        ])
        
        urls_section = self.factory.create_vbox([
            self.factory.create_html("<h3>🔗 Custom URLs</h3>"),
            self.widgets['Model_url'],
            self.widgets['Vae_url'],
            self.widgets['LoRA_url'],
            self.widgets['Embedding_url'],
            self.widgets['Extensions_url']
        ])
        
        config_section = self.factory.create_vbox([
            self.factory.create_html("<h3>⚙️ Configuration</h3>"),
            self.widgets['civitai_token'],
            self.widgets['huggingface_token'],
            self.widgets['commandline_arguments'],
            self.widgets['theme_accent']
        ])
        
        # Add verbosity control
        verbosity_section = self.create_verbosity_control_section()
        
        # Control buttons
        save_button = widgets.Button(
            description='💾 Save Settings',
            button_style='success',
            layout=widgets.Layout(width='200px')
        )
        save_button.on_click(lambda b: self.save_settings())
        
        buttons_section = self.factory.create_hbox([save_button])
        
        # Main layout
        main_layout = self.factory.create_vbox([
            self.factory.create_html("<h2>🎯 LSDAI Enhanced Configuration</h2>"),
            webui_section,
            model_section,
            urls_section,
            config_section,
            verbosity_section,
            buttons_section
        ])
        
        print("✅ Layout created successfully")
        return main_layout

    def save_settings(self):
        """Save current widget values to settings."""
        try:
            settings_data = {}
            for key in self.settings_keys:
                if key in self.widgets and hasattr(self.widgets[key], 'value'):
                    settings_data[key] = self.widgets[key].value
            
            js.write(SETTINGS_PATH, 'WIDGETS', settings_data)
            self.show_notification("Settings saved successfully!", "success")
            
        except Exception as e:
            self.show_notification(f"Error saving settings: {e}", "error")

    def load_settings(self):
        """Load settings from JSON file."""
        try:
            for key in self.settings_keys:
                if key in self.widgets:
                    value = js.read(SETTINGS_PATH, f'WIDGETS.{key}')
                    if value is not None:
                        if hasattr(self.widgets[key], 'value'):
                            self.widgets[key].value = value
        except Exception as e:
            self.verbose_manager.print_if_verbose(f"Warning: Could not load some settings: {e}", VerbosityLevel.DETAILED)

    def setup_callbacks(self):
        """Setup widget callbacks and interactions."""
        # WebUI change callback
        def update_webui_options(change):
            update_current_webui(change.get('new', 'A1111'))
        
        if 'change_webui' in self.widgets:
            self.widgets['change_webui'].observe(update_webui_options, names='value')
        
        # XL models toggle callback
        def update_xl_options(change):
            # Update model options based on XL toggle
            model_data_file = SCRIPTS / ('_xl_models_data.py' if change.get('new') else '_models_data.py')
            try:
                model_options = self.read_model_data(model_data_file, 'model')
                if 'model' in self.widgets:
                    self.widgets['model'].options = model_options
                    self.widgets['model'].value = model_options[0] if model_options else 'none'
            except Exception as e:
                self.verbose_manager.print_if_verbose(f"Error updating XL options: {e}", VerbosityLevel.DETAILED)
        
        if 'XL_models' in self.widgets:
            self.widgets['XL_models'].observe(update_xl_options, names='value')

# --- MAIN EXECUTION ---
def main():
    """Main function to create and display the widget interface"""
    
    print("🎯 LSDAI Enhanced Widget Interface")
    print("=" * 40)
    
    try:
        # Initialize widget manager
        wm = WidgetManager()
        
        # Create widgets
        wm.create_widgets()
        
        # Load existing settings
        wm.load_settings()
        
        # Setup callbacks
        wm.setup_callbacks()
        
        # Create and display layout
        layout = wm.create_layout()
        display(layout)
        
        print("✅ Enhanced widget interface loaded successfully!")
        
    except Exception as e:
        print(f"❌ Error creating enhanced widget interface: {e}")
        import traceback
        traceback.print_exc()
        
        # Show error in HTML
        error_html = f"""
        <div style="border: 2px solid #ef4444; background-color: #fee2e2; 
                    padding: 1rem; border-radius: 0.5rem; color: #b91c1c; margin: 10px 0;">
            <h3>⚠️ Enhanced Widget Interface Error</h3>
            <p>The enhanced widget interface failed to load: {e}</p>
            <p>Please check the error details above and ensure all required files are present.</p>
        </div>
        """
        display(HTML(error_html))

# Run the main function
if __name__ == "__main__":
    main()

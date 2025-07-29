# Enhanced widgets integration with full model selection
import json_utils as js
from pathlib import Path
import ipywidgets as widgets
from IPython.display import display, HTML, Javascript, clear_output
import importlib.util
import os

# Get settings path from environment or default
SETTINGS_PATH = Path(os.environ.get('settings_path', '/content/LSDAI/settings.json'))
SCRIPTS_PATH = Path(os.environ.get('scr_path', '/content/LSDAI')) / 'scripts'

# Import original widget factory
try:
    from modules.widget_factory import WidgetFactory
    ORIGINAL_WIDGETS_AVAILABLE = True
except ImportError:
    ORIGINAL_WIDGETS_AVAILABLE = False
    print("⚠️ Original widget_factory not found")

# Import enhancements
try:
    from scripts.enhanced_widgets_en import EnhancedWidgetManager
    ENHANCEMENTS_AVAILABLE = True
except ImportError:
    ENHANCEMENTS_AVAILABLE = False
    print("⚠️ Enhanced widgets not available")

class ModelDataManager:
    """Handles loading and managing model data from files"""
    
    def __init__(self):
        self.sd15_data = self._load_model_data('_models_data.py')
        self.sdxl_data = self._load_model_data('_xl_models_data.py')
        
    def _load_model_data(self, filename):
        """Load model data from Python file"""
        try:
            file_path = SCRIPTS_PATH / filename
            if not file_path.exists():
                print(f"⚠️ Model data file not found: {filename}")
                return {}
                
            spec = importlib.util.spec_from_file_location("model_data", file_path)
            model_data_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(model_data_module)
            
            return {
                'model_list': getattr(model_data_module, 'model_list', {}),
                'vae_list': getattr(model_data_module, 'vae_list', {}),
                'lora_list': getattr(model_data_module, 'lora_list', {}),
                'controlnet_list': getattr(model_data_module, 'controlnet_list', {})
            }
        except Exception as e:
            print(f"⚠️ Error loading {filename}: {e}")
            return {}
    
    def get_options(self, category, is_xl=False):
        """Get options for a specific category"""
        data = self.sdxl_data if is_xl else self.sd15_data
        category_data = data.get(category, {})
        
        if not category_data:
            return ['none']
            
        options = ['none'] + list(category_data.keys())
        return options
    
    def get_model_info(self, category, model_name, is_xl=False):
        """Get detailed info about a specific model"""
        data = self.sdxl_data if is_xl else self.sd15_data
        return data.get(category, {}).get(model_name, {})

class IntegratedWidgetSystem:
    def __init__(self):
        self.original_factory = WidgetFactory() if ORIGINAL_WIDGETS_AVAILABLE else None
        self.enhanced_manager = EnhancedWidgetManager() if ENHANCEMENTS_AVAILABLE else None
        self.model_manager = ModelDataManager()
        self.widgets = {}
        
    def create_integrated_interface(self):
        """Create comprehensive model selection interface"""
        
        # Clear any existing output first
        clear_output(wait=True)
        
        print("🚀 Loading LSDAI Model Selection Interface")
        
        # Load styling
        self._load_styles()
        
        # Create the complete interface
        self._create_comprehensive_model_interface()
        
    def _load_styles(self):
        """Load CSS styling"""
        css_content = """
        <style>
        .lsdai-container {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        .lsdai-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px 10px 0 0;
            text-align: center;
            margin-bottom: 0;
        }
        .lsdai-section {
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            padding: 15px;
            margin: 10px 0;
        }
        .lsdai-section h3 {
            color: #495057;
            border-bottom: 2px solid #007bff;
            padding-bottom: 8px;
            margin-top: 0;
        }
        .model-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
            margin: 15px 0;
        }
        .model-selector {
            background: white;
            border: 1px solid #ced4da;
            border-radius: 6px;
            padding: 10px;
        }
        .model-selector label {
            font-weight: 600;
            color: #495057;
            margin-bottom: 5px;
        }
        .xl-toggle {
            background: linear-gradient(45deg, #ff6b6b, #4ecdc4);
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 25px;
            font-weight: bold;
            margin: 10px 0;
        }
        .save-button {
            background: linear-gradient(45deg, #28a745, #20c997);
            color: white;
            border: none;
            padding: 15px 30px;
            border-radius: 25px;
            font-size: 16px;
            font-weight: bold;
            margin: 20px auto;
            display: block;
        }
        .status-display {
            background: #d4edda;
            border: 1px solid #c3e6cb;
            color: #155724;
            padding: 10px;
            border-radius: 6px;
            margin: 10px 0;
        }
        </style>
        """
        display(HTML(css_content))
        
    def _create_comprehensive_model_interface(self):
        """Create the complete model selection interface"""
        
        # Main container
        container_widgets = []
        
        # Header
        header = widgets.HTML('''
        <div class="lsdai-header">
            <h2>🎨 LSDAI Enhanced Model Selection</h2>
            <p>Select your models, VAEs, LoRAs, and ControlNets with advanced multi-selection</p>
        </div>
        ''')
        container_widgets.append(header)
        
        # XL Models Toggle Section
        xl_section = self._create_xl_toggle_section()
        container_widgets.append(xl_section)
        
        # Model Selection Grid
        model_grid = self._create_model_selection_grid()
        container_widgets.append(model_grid)
        
        # WebUI and Advanced Settings
        webui_section = self._create_webui_section()
        container_widgets.append(webui_section)
        
        # API Tokens Section
        tokens_section = self._create_tokens_section()
        container_widgets.append(tokens_section)
        
        # Save and Status
        save_section = self._create_save_section()
        container_widgets.append(save_section)
        
        # Main container
        main_interface = widgets.VBox(
            container_widgets,
            layout=widgets.Layout(
                width='100%',
                max_width='1200px',
                margin='0 auto',
                padding='20px'
            )
        )
        
        display(main_interface)
        print("✅ Enhanced model selection interface loaded!")
        
    def _create_xl_toggle_section(self):
        """Create XL models toggle section"""
        
        # XL Models toggle
        xl_toggle = widgets.ToggleButton(
            value=js.read(SETTINGS_PATH, 'XL_models', False),
            description='🚀 SDXL Models',
            button_style='info',
            layout=widgets.Layout(width='200px', height='50px')
        )
        self.widgets['XL_models'] = xl_toggle
        
        # Inpainting toggle
        inpainting_toggle = widgets.ToggleButton(
            value=js.read(SETTINGS_PATH, 'inpainting_model', False),
            description='🖼️ Include Inpainting',
            button_style='warning',
            layout=widgets.Layout(width='200px', height='50px')
        )
        self.widgets['inpainting_model'] = inpainting_toggle
        
        # Toggle row
        toggle_row = widgets.HBox([
            xl_toggle,
            inpainting_toggle,
            widgets.HTML('<div style="flex: 1;"></div>'),  # Spacer
            widgets.HTML('<p style="margin: 15px 0; color: #6c757d;">Toggle between SD 1.5 and SDXL model sets</p>')
        ])
        
        # Set up XL toggle handler
        def on_xl_change(change):
            is_xl = change['new']
            js.save(SETTINGS_PATH, 'XL_models', is_xl)
            self._update_model_options(is_xl)
            
        xl_toggle.observe(on_xl_change, names='value')
        
        def on_inpainting_change(change):
            js.save(SETTINGS_PATH, 'inpainting_model', change['new'])
            
        inpainting_toggle.observe(on_inpainting_change, names='value')
        
        return widgets.HTML(f'''
        <div class="lsdai-section">
            <h3>📋 Model Configuration</h3>
        </div>
        ''') 
        
    def _create_model_selection_grid(self):
        """Create the main model selection grid"""
        
        is_xl = js.read(SETTINGS_PATH, 'XL_models', False)
        
        # Create model selectors
        model_selector = self._create_model_selector('Models', 'model_list', is_xl, height='150px')
        vae_selector = self._create_model_selector('VAE', 'vae_list', is_xl, height='100px')
        lora_selector = self._create_model_selector('LoRA', 'lora_list', is_xl, height='120px')
        controlnet_selector = self._create_model_selector('ControlNet', 'controlnet_list', is_xl, height='120px')
        
        # Grid layout
        grid_html = widgets.HTML('''
        <div class="lsdai-section">
            <h3>🎨 Model Selection</h3>
            <p>Select multiple models using Ctrl+Click (Windows) or Cmd+Click (Mac)</p>
        </div>
        ''')
        
        # Create 2x2 grid
        top_row = widgets.HBox([model_selector, vae_selector])
        bottom_row = widgets.HBox([lora_selector, controlnet_selector])
        
        grid_container = widgets.VBox([
            grid_html,
            top_row,
            bottom_row
        ])
        
        return grid_container
        
    def _create_model_selector(self, title, category, is_xl, height='120px'):
        """Create a model selector widget"""
        
        options = self.model_manager.get_options(category, is_xl)
        
        # Get saved values
        saved_values = js.read(SETTINGS_PATH, category.replace('_list', ''), ['none'])
        if isinstance(saved_values, str):
            saved_values = [saved_values]
        
        # Validate saved values exist in options
        valid_values = [v for v in saved_values if v in options]
        if not valid_values:
            valid_values = ['none']
            
        selector = widgets.SelectMultiple(
            options=options,
            value=valid_values,
            description=f'{title}:',
            layout=widgets.Layout(
                width='100%',
                height=height,
                margin='5px'
            ),
            style={'description_width': 'initial'}
        )
        
        # Store reference
        widget_key = category.replace('_list', '')
        self.widgets[widget_key] = selector
        
        # Set up change handler
        def on_change(change):
            js.save(SETTINGS_PATH, widget_key, list(change['new']))
            
        selector.observe(on_change, names='value')
        
        # Wrap in styled container
        container = widgets.VBox([
            selector
        ], layout=widgets.Layout(
            border='1px solid #ced4da',
            border_radius='6px',
            padding='10px',
            margin='5px',
            background_color='white'
        ))
        
        return container
        
    def _update_model_options(self, is_xl):
        """Update all model selectors when XL toggle changes"""
        
        categories = ['model', 'vae', 'lora', 'controlnet']
        
        for category in categories:
            if category in self.widgets:
                widget = self.widgets[category]
                category_key = f"{category}_list"
                
                # Get new options
                new_options = self.model_manager.get_options(category_key, is_xl)
                widget.options = new_options
                
                # Reset to 'none' when switching
                widget.value = ['none']
                js.save(SETTINGS_PATH, category, ['none'])
                
        print(f"✅ Updated to {'SDXL' if is_xl else 'SD 1.5'} model collections")
        
    def _create_webui_section(self):
        """Create WebUI configuration section"""
        
        webui_options = ['automatic1111', 'ComfyUI', 'InvokeAI', 'StableSwarmUI', 'Forge', 'ReForge']
        webui_dropdown = widgets.Dropdown(
            options=webui_options,
            value=js.read(SETTINGS_PATH, 'change_webui', 'automatic1111'),
            description='WebUI:',
            layout=widgets.Layout(width='300px')
        )
        self.widgets['change_webui'] = webui_dropdown
        
        # Extensions toggle
        extensions_toggle = widgets.ToggleButton(
            value=js.read(SETTINGS_PATH, 'latest_extensions', True),
            description='📦 Latest Extensions',
            button_style='success',
            layout=widgets.Layout(width='200px')
        )
        self.widgets['latest_extensions'] = extensions_toggle
        
        # Command line arguments
        args_text = widgets.Textarea(
            value=js.read(SETTINGS_PATH, 'commandline_arguments', ''),
            description='Launch Args:',
            placeholder='--xformers --api --listen --port 7860',
            layout=widgets.Layout(width='100%', height='80px')
        )
        self.widgets['commandline_arguments'] = args_text
        
        # Set up change handlers
        def on_webui_change(change):
            js.save(SETTINGS_PATH, 'change_webui', change['new'])
        webui_dropdown.observe(on_webui_change, names='value')
        
        def on_extensions_change(change):
            js.save(SETTINGS_PATH, 'latest_extensions', change['new'])
        extensions_toggle.observe(on_extensions_change, names='value')
        
        def on_args_change(change):
            js.save(SETTINGS_PATH, 'commandline_arguments', change['new'])
        args_text.observe(on_args_change, names='value')
        
        # Layout
        webui_row = widgets.HBox([webui_dropdown, extensions_toggle])
        
        section = widgets.VBox([
            widgets.HTML('''
            <div class="lsdai-section">
                <h3>🚀 WebUI Configuration</h3>
            </div>
            '''),
            webui_row,
            args_text
        ])
        
        return section
        
    def _create_tokens_section(self):
        """Create API tokens section"""
        
        civitai_token = widgets.Password(
            value=js.read(SETTINGS_PATH, 'civitai_token', ''),
            description='Civitai Token:',
            placeholder='Your Civitai API token for premium models',
            layout=widgets.Layout(width='100%')
        )
        self.widgets['civitai_token'] = civitai_token
        
        hf_token = widgets.Password(
            value=js.read(SETTINGS_PATH, 'huggingface_token', ''),
            description='HuggingFace Token:',
            placeholder='Your HuggingFace token for gated models',
            layout=widgets.Layout(width='100%')
        )
        self.widgets['huggingface_token'] = hf_token
        
        # Set up change handlers
        def on_civitai_change(change):
            js.save(SETTINGS_PATH, 'civitai_token', change['new'])
        civitai_token.observe(on_civitai_change, names='value')
        
        def on_hf_change(change):
            js.save(SETTINGS_PATH, 'huggingface_token', change['new'])
        hf_token.observe(on_hf_change, names='value')
        
        section = widgets.VBox([
            widgets.HTML('''
            <div class="lsdai-section">
                <h3>🔑 API Tokens (Optional)</h3>
                <p>Add your API tokens to access premium and gated models</p>
            </div>
            '''),
            civitai_token,
            hf_token
        ])
        
        return section
        
    def _create_save_section(self):
        """Create save button and status section"""
        
        save_button = widgets.Button(
            description='💾 Save All Settings',
            button_style='success',
            layout=widgets.Layout(width='250px', height='50px')
        )
        
        status_output = widgets.Output(
            layout=widgets.Layout(height='60px', width='100%')
        )
        
        def save_all_settings(b):
            try:
                # Auto-save happens on each change, but this gives user feedback
                with status_output:
                    status_output.clear_output()
                    print("✅ All settings saved successfully!")
                    print(f"📊 Models: {len(self.widgets.get('model', {}).get('value', ['none'])) - 1} selected")
                    print(f"🎨 VAE: {len(self.widgets.get('vae', {}).get('value', ['none'])) - 1} selected")
                    print(f"🔧 LoRA: {len(self.widgets.get('lora', {}).get('value', ['none'])) - 1} selected")
                    print(f"🎮 ControlNet: {len(self.widgets.get('controlnet', {}).get('value', ['none'])) - 1} selected")
                    
            except Exception as e:
                with status_output:
                    status_output.clear_output()
                    print(f"❌ Error saving settings: {e}")
                    
        save_button.on_click(save_all_settings)
        
        # Auto-save initial state
        save_all_settings(None)
        
        section = widgets.VBox([
            widgets.HTML('<div style="text-align: center; margin: 20px 0;">'),
            save_button,
            widgets.HTML('</div>'),
            status_output
        ])
        
        return section

# Main integration function
def create_integrated_widgets():
    """Main function to create integrated widget interface"""
    integrated_system = IntegratedWidgetSystem()
    integrated_system.create_integrated_interface()

# For backward compatibility and direct execution
if __name__ == "__main__":
    create_integrated_widgets()

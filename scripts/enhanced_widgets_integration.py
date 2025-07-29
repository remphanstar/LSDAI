# Enhanced widgets integration - Backward compatible with original
import json_utils as js
from pathlib import Path
import ipywidgets as widgets
from IPython.display import display, HTML, Javascript, clear_output
import os

# Get settings path from environment or default
SETTINGS_PATH = Path(os.environ.get('settings_path', '/content/LSDAI/settings.json'))

# Import original widget factory
try:
    from modules.widget_factory import WidgetFactory
    ORIGINAL_WIDGETS_AVAILABLE = True
except ImportError:
    ORIGINAL_WIDGETS_AVAILABLE = False
    print("⚠️ Original widget_factory not found")

# Import enhancements - FIXED IMPORT
try:
    from scripts.enhanced_widgets_en import EnhancedWidgetManager  # Fixed: was enhanced_widgets
    ENHANCEMENTS_AVAILABLE = True
except ImportError:
    ENHANCEMENTS_AVAILABLE = False
    print("⚠️ Enhanced widgets not available")

class IntegratedWidgetSystem:
    def __init__(self):
        self.original_factory = WidgetFactory() if ORIGINAL_WIDGETS_AVAILABLE else None
        self.enhanced_manager = EnhancedWidgetManager() if ENHANCEMENTS_AVAILABLE else None
        self.settings_keys = [
            # Original LSDAI settings
            'XL_models', 'model', 'model_num', 'inpainting_model', 'vae', 'vae_num', 'lora',
            'latest_webui', 'latest_extensions', 'check_custom_nodes_deps', 'change_webui', 
            'detailed_download', 'controlnet', 'controlnet_num', 'commit_hash',
            'civitai_token', 'huggingface_token', 'zrok_token', 'ngrok_token', 
            'commandline_arguments', 'theme_accent', 'empowerment', 'empowerment_output',
            'Model_url', 'Vae_url', 'LoRA_url', 'Embedding_url', 'Extensions_url', 'ADetailer_url',
            'custom_file_urls',
            # Enhanced settings
            'model_favorites', 'download_queue', 'auto_preview', 'batch_mode', 'advanced_filters',
            'cloud_sync_enabled', 'notification_channels', 'performance_mode'
        ]
        
    def create_integrated_interface(self):
        """Create interface that combines original + enhanced features"""
        
        # Clear any existing output first
        clear_output(wait=True)
        
        if ENHANCEMENTS_AVAILABLE:
            print("🚀 Loading Enhanced LSDAI Interface")
            
            try:
                # Load enhanced CSS/JS
                self._load_enhanced_styles()
                
                # Try to create enhanced interface
                if hasattr(self.enhanced_manager, 'create_enhanced_interface'):
                    enhanced_interface = self.enhanced_manager.create_enhanced_interface()
                    
                    # Add original LSDAI compatibility layer
                    compatibility_layer = self._create_compatibility_layer()
                    
                    # Combine interfaces
                    combined_interface = widgets.VBox([
                        enhanced_interface,
                        compatibility_layer
                    ])
                    
                    display(combined_interface)
                    print("✅ Enhanced interface loaded successfully!")
                    return
                    
                else:
                    print("⚠️ Enhanced interface method not found")
                    raise AttributeError("create_enhanced_interface method missing")
                
            except Exception as e:
                print(f"⚠️ Enhanced interface failed: {e}")
                # Clear the failed output before showing fallback
                clear_output(wait=True)
                print("🔄 Loading clean LSDAI interface...")
                self._create_comprehensive_interface()
        else:
            print("📦 Loading LSDAI Interface")
            self._create_comprehensive_interface()
            
    def _load_enhanced_styles(self):
        """Load enhanced CSS and JavaScript"""
        
        # Load enhanced CSS
        css_files = [
            'CSS/enhanced_widgets.css',
            'CSS/main_widgets.css'  # Your original CSS
        ]
        
        for css_file in css_files:
            if Path(css_file).exists():
                with open(css_file, 'r') as f:
                    css_content = f.read()
                    display(HTML(f'<style>{css_content}</style>'))
                    
        # Load enhanced JavaScript
        js_files = [
            'JS/enhanced_widgets.js',
            'JS/main_widgets.js'  # Your original JS
        ]
        
        for js_file in js_files:
            if Path(js_file).exists():
                with open(js_file, 'r') as f:
                    js_content = f.read()
                    display(Javascript(js_content))
                    
    def _create_compatibility_layer(self):
        """Create compatibility layer for original LSDAI settings"""
        
        # Create original-style widgets for backward compatibility
        compatibility_widgets = []
        
        # XL Models toggle (original functionality)
        xl_toggle = widgets.ToggleButton(
            value=js.read(SETTINGS_PATH, 'XL_models', False),
            description='SDXL Models',
            button_style='info'
        )
        
        def on_xl_toggle_change(change):
            js.save(SETTINGS_PATH, 'XL_models', change['new'])
            # Trigger enhanced model manager update
            if hasattr(self.enhanced_manager, 'update_model_filter'):
                self.enhanced_manager.update_model_filter('xl_models', change['new'])
                
        xl_toggle.observe(on_xl_toggle_change, names='value')
        compatibility_widgets.append(xl_toggle)
        
        # WebUI Selection (enhanced with original options)
        webui_options = ['automatic1111', 'ComfyUI', 'InvokeAI', 'StableSwarmUI']
        webui_dropdown = widgets.Dropdown(
            options=webui_options,
            value=js.read(SETTINGS_PATH, 'change_webui', 'automatic1111'),
            description='WebUI:'
        )
        
        def on_webui_change(change):
            js.save(SETTINGS_PATH, 'change_webui', change['new'])
            # Update enhanced launcher
            if hasattr(self.enhanced_manager, 'update_webui_selection'):
                self.enhanced_manager.update_webui_selection(change['new'])
                
        webui_dropdown.observe(on_webui_change, names='value')
        compatibility_widgets.append(webui_dropdown)
        
        # Command line arguments (enhanced with suggestions)
        args_text = widgets.Textarea(
            value=js.read(SETTINGS_PATH, 'commandline_arguments', ''),
            description='Arguments:',
            placeholder='--xformers --opt-channelslast'
        )
        
        def on_args_change(change):
            js.save(SETTINGS_PATH, 'commandline_arguments', change['new'])
            
        args_text.observe(on_args_change, names='value')
        compatibility_widgets.append(args_text)
        
        return widgets.VBox(compatibility_widgets, 
                          layout=widgets.Layout(border='1px solid #ddd', padding='10px'))
        
    def _create_comprehensive_interface(self):
        """Create comprehensive LSDAI interface - SINGLE CLEAN VERSION"""
        
        # Load CSS styling
        try:
            css_files = ['CSS/main_widgets.css']
            for css_file in css_files:
                if Path(css_file).exists():
                    with open(css_file, 'r') as f:
                        css_content = f.read()
                        display(HTML(f'<style>{css_content}</style>'))
        except:
            pass
        
        # Create comprehensive widget interface
        all_widgets = []
        
        # Header
        header = widgets.HTML('<h2 style="color: #4CAF50; text-align: center; margin-bottom: 20px;">🎨 LSDAI Configuration Interface</h2>')
        all_widgets.append(header)
        
        # Model Selection Section
        model_section = widgets.HTML('<h3 style="color: #2196F3; border-bottom: 2px solid #2196F3; padding-bottom: 5px;">📁 Model Selection</h3>')
        all_widgets.append(model_section)
        
        # Create model selection in a nice layout
        model_row1 = widgets.HBox([
            widgets.ToggleButton(
                value=js.read(SETTINGS_PATH, 'XL_models', False),
                description='SDXL Models',
                button_style='info',
                layout=widgets.Layout(width='200px')
            ),
            widgets.ToggleButton(
                value=js.read(SETTINGS_PATH, 'latest_extensions', True),
                description='Latest Extensions',
                button_style='success',
                layout=widgets.Layout(width='200px')
            )
        ], layout=widgets.Layout(margin='10px 0'))
        all_widgets.append(model_row1)
        
        # Model and VAE URLs
        model_text = widgets.Text(
            value=js.read(SETTINGS_PATH, 'model', ''),
            description='Model URL:',
            placeholder='https://civitai.com/api/download/models/...',
            layout=widgets.Layout(width='100%', margin='5px 0')
        )
        all_widgets.append(model_text)
        
        vae_text = widgets.Text(
            value=js.read(SETTINGS_PATH, 'vae', ''),
            description='VAE URL:',
            placeholder='https://huggingface.co/...',
            layout=widgets.Layout(width='100%', margin='5px 0')
        )
        all_widgets.append(vae_text)
        
        # WebUI Section
        webui_section = widgets.HTML('<h3 style="color: #2196F3; border-bottom: 2px solid #2196F3; padding-bottom: 5px; margin-top: 30px;">🚀 WebUI Configuration</h3>')
        all_widgets.append(webui_section)
        
        # WebUI selection
        webui_dropdown = widgets.Dropdown(
            options=['automatic1111', 'ComfyUI', 'InvokeAI', 'StableSwarmUI'],
            value=js.read(SETTINGS_PATH, 'change_webui', 'automatic1111'),
            description='WebUI:',
            layout=widgets.Layout(width='300px', margin='10px 0')
        )
        all_widgets.append(webui_dropdown)
        
        # Advanced Section
        advanced_section = widgets.HTML('<h3 style="color: #2196F3; border-bottom: 2px solid #2196F3; padding-bottom: 5px; margin-top: 30px;">⚙️ Advanced Settings</h3>')
        all_widgets.append(advanced_section)
        
        # Command line arguments
        args_text = widgets.Textarea(
            value=js.read(SETTINGS_PATH, 'commandline_arguments', ''),
            description='Launch Args:',
            placeholder='--xformers --api --listen --port 7860',
            layout=widgets.Layout(width='100%', height='100px', margin='10px 0')
        )
        all_widgets.append(args_text)
        
        # API Tokens Section
        tokens_section = widgets.HTML('<h3 style="color: #2196F3; border-bottom: 2px solid #2196F3; padding-bottom: 5px; margin-top: 30px;">🔑 API Tokens (Optional)</h3>')
        all_widgets.append(tokens_section)
        
        # Token inputs in a nice layout
        token_row = widgets.HBox([
            widgets.Password(
                value=js.read(SETTINGS_PATH, 'civitai_token', ''),
                description='Civitai Token:',
                placeholder='Your Civitai API token',
                layout=widgets.Layout(width='50%')
            ),
            widgets.Password(
                value=js.read(SETTINGS_PATH, 'huggingface_token', ''),
                description='HF Token:',
                placeholder='Your HuggingFace token', 
                layout=widgets.Layout(width='50%')
            )
        ], layout=widgets.Layout(margin='10px 0'))
        all_widgets.append(token_row)
        
        # Save button
        save_button = widgets.Button(
            description='💾 Save All Settings',
            button_style='success',
            layout=widgets.Layout(width='300px', height='50px', margin='20px auto')
        )
        all_widgets.append(save_button)
        
        # Status output
        status_output = widgets.Output(layout=widgets.Layout(height='60px'))
        all_widgets.append(status_output)
        
        # Set up save functionality for all widgets
        xl_toggle = model_row1.children[0]
        extensions_toggle = model_row1.children[1]
        civitai_token = token_row.children[0]
        hf_token = token_row.children[1]
        
        def save_all_settings(b=None):
            try:
                js.save(SETTINGS_PATH, 'XL_models', xl_toggle.value)
                js.save(SETTINGS_PATH, 'model', model_text.value)
                js.save(SETTINGS_PATH, 'vae', vae_text.value)
                js.save(SETTINGS_PATH, 'change_webui', webui_dropdown.value)
                js.save(SETTINGS_PATH, 'latest_extensions', extensions_toggle.value)
                js.save(SETTINGS_PATH, 'commandline_arguments', args_text.value)
                js.save(SETTINGS_PATH, 'civitai_token', civitai_token.value)
                js.save(SETTINGS_PATH, 'huggingface_token', hf_token.value)
                
                with status_output:
                    status_output.clear_output()
                    print("✅ All settings saved successfully!")
                    
            except Exception as e:
                with status_output:
                    status_output.clear_output()
                    print(f"❌ Error saving settings: {e}")
        
        # Auto-save on changes
        def on_change(change):
            save_all_settings()
            
        xl_toggle.observe(on_change, names='value')
        extensions_toggle.observe(on_change, names='value')
        webui_dropdown.observe(on_change, names='value')
        
        # Manual save button
        save_button.on_click(save_all_settings)
        
        # Load initial settings display
        save_all_settings()
        
        # Create and display the interface
        interface = widgets.VBox(
            all_widgets,
            layout=widgets.Layout(
                width='100%',
                max_width='1000px',
                padding='30px',
                margin='0 auto',
                border='2px solid #ddd',
                border_radius='15px',
                background_color='#fafafa'
            )
        )
        
        display(interface)
        print("✅ LSDAI interface loaded with full functionality!")

# Main integration function
def create_integrated_widgets():
    """Main function to create integrated widget interface"""
    integrated_system = IntegratedWidgetSystem()
    integrated_system.create_integrated_interface()

# For backward compatibility and direct execution
if __name__ == "__main__":
    create_integrated_widgets()

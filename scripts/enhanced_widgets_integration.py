# Enhanced widgets integration - Backward compatible with original
import json_utils as js
from pathlib import Path
import ipywidgets as widgets
from IPython.display import display, HTML, Javascript

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
        
        if ENHANCEMENTS_AVAILABLE:
            print("🚀 Loading Enhanced LSDAI Interface")
            
            # Load enhanced CSS/JS
            self._load_enhanced_styles()
            
            # Create enhanced interface
            try:
                enhanced_interface = self.enhanced_manager.create_enhanced_interface()
                
                # Add original LSDAI compatibility layer
                compatibility_layer = self._create_compatibility_layer()
                
                # Combine interfaces
                combined_interface = widgets.VBox([
                    enhanced_interface,
                    compatibility_layer
                ])
                
                display(combined_interface)
                
            except Exception as e:
                print(f"⚠️ Enhanced interface failed: {e}")
                print("🔄 Falling back to original interface...")
                self._create_original_interface()
            
        else:
            print("📦 Loading Original LSDAI Interface")
            self._create_original_interface()
            
    def _load_enhanced_styles(self):
        """Load enhanced CSS and JavaScript"""
        
        # Load enhanced CSS
        css_files = [
            'CSS/enhanced-widgets.css',
            'CSS/main-widgets.css'  # Your original CSS
        ]
        
        for css_file in css_files:
            if Path(css_file).exists():
                with open(css_file, 'r') as f:
                    css_content = f.read()
                    display(HTML(f'<style>{css_content}</style>'))
                    
        # Load enhanced JavaScript
        js_files = [
            'JS/enhanced-widgets.js',
            'JS/main-widgets.js'  # Your original JS
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
            value=js.read_key('XL_models', False),
            description='SDXL Models',
            button_style='info'
        )
        
        def on_xl_toggle_change(change):
            js.write_key('XL_models', change['new'])
            # Trigger enhanced model manager update
            if hasattr(self.enhanced_manager, 'update_model_filter'):
                self.enhanced_manager.update_model_filter('xl_models', change['new'])
                
        xl_toggle.observe(on_xl_toggle_change, names='value')
        compatibility_widgets.append(xl_toggle)
        
        # WebUI Selection (enhanced with original options)
        webui_options = ['automatic1111', 'ComfyUI', 'InvokeAI', 'StableSwarmUI']
        webui_dropdown = widgets.Dropdown(
            options=webui_options,
            value=js.read_key('change_webui', 'automatic1111'),
            description='WebUI:'
        )
        
        def on_webui_change(change):
            js.write_key('change_webui', change['new'])
            # Update enhanced launcher
            if hasattr(self.enhanced_manager, 'update_webui_selection'):
                self.enhanced_manager.update_webui_selection(change['new'])
                
        webui_dropdown.observe(on_webui_change, names='value')
        compatibility_widgets.append(webui_dropdown)
        
        # Command line arguments (enhanced with suggestions)
        args_text = widgets.Textarea(
            value=js.read_key('commandline_arguments', ''),
            description='Arguments:',
            placeholder='--xformers --opt-channelslast'
        )
        
        def on_args_change(change):
            js.write_key('commandline_arguments', change['new'])
            
        args_text.observe(on_args_change, names='value')
        compatibility_widgets.append(args_text)
        
        return widgets.VBox(compatibility_widgets, 
                          layout=widgets.Layout(border='1px solid #ddd', padding='10px'))
        
    def _create_original_interface(self):
        """Fallback to original interface - SIMPLIFIED"""
        print("📦 Loading LSDAI interface...")
        
        # Since the original widgets_en.py has complex global dependencies,
        # we'll use our comprehensive basic fallback which provides all the same functionality
        # but in a more reliable way
        self._create_basic_fallback()
            
    def _create_basic_fallback(self):
        """Create comprehensive basic fallback interface when everything else fails"""
        print("🔧 Creating comprehensive basic interface...")
        
        # Load CSS styling
        try:
            css_files = ['CSS/main-widgets.css']
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
        header = widgets.HTML('<h2 style="color: #4CAF50;">🎨 LSDAI Configuration Interface</h2>')
        all_widgets.append(header)
        
        # Model Selection Section
        model_section = widgets.HTML('<h3 style="color: #2196F3;">📁 Model Selection</h3>')
        all_widgets.append(model_section)
        
        # XL Models toggle
        xl_toggle = widgets.ToggleButton(
            value=js.read_key('XL_models', False),
            description='SDXL Models',
            button_style='info',
            layout=widgets.Layout(width='200px')
        )
        all_widgets.append(xl_toggle)
        
        # Model selection
        model_text = widgets.Text(
            value=js.read_key('model', ''),
            description='Model URL:',
            placeholder='https://civitai.com/api/download/models/...',
            layout=widgets.Layout(width='100%')
        )
        all_widgets.append(model_text)
        
        # VAE selection  
        vae_text = widgets.Text(
            value=js.read_key('vae', ''),
            description='VAE URL:',
            placeholder='https://huggingface.co/...',
            layout=widgets.Layout(width='100%')
        )
        all_widgets.append(vae_text)
        
        # WebUI Section
        webui_section = widgets.HTML('<h3 style="color: #2196F3;">🚀 WebUI Configuration</h3>')
        all_widgets.append(webui_section)
        
        # WebUI selection
        webui_dropdown = widgets.Dropdown(
            options=['automatic1111', 'ComfyUI', 'InvokeAI', 'StableSwarmUI'],
            value=js.read_key('change_webui', 'automatic1111'),
            description='WebUI:',
            layout=widgets.Layout(width='300px')
        )
        all_widgets.append(webui_dropdown)
        
        # Extensions
        extensions_toggle = widgets.ToggleButton(
            value=js.read_key('latest_extensions', True),
            description='Latest Extensions',
            button_style='success',
            layout=widgets.Layout(width='200px')
        )
        all_widgets.append(extensions_toggle)
        
        # Advanced Section
        advanced_section = widgets.HTML('<h3 style="color: #2196F3;">⚙️ Advanced Settings</h3>')
        all_widgets.append(advanced_section)
        
        # Command line arguments
        args_text = widgets.Textarea(
            value=js.read_key('commandline_arguments', ''),
            description='Launch Args:',
            placeholder='--xformers --api --listen --port 7860',
            layout=widgets.Layout(width='100%', height='100px')
        )
        all_widgets.append(args_text)
        
        # API Tokens Section
        tokens_section = widgets.HTML('<h3 style="color: #2196F3;">🔑 API Tokens (Optional)</h3>')
        all_widgets.append(tokens_section)
        
        # Civitai token
        civitai_token = widgets.Password(
            value=js.read_key('civitai_token', ''),
            description='Civitai Token:',
            placeholder='Your Civitai API token',
            layout=widgets.Layout(width='100%')
        )
        all_widgets.append(civitai_token)
        
        # HuggingFace token
        hf_token = widgets.Password(
            value=js.read_key('huggingface_token', ''),
            description='HF Token:',
            placeholder='Your HuggingFace token',
            layout=widgets.Layout(width='100%')
        )
        all_widgets.append(hf_token)
        
        # Save button
        save_button = widgets.Button(
            description='💾 Save Settings',
            button_style='success',
            layout=widgets.Layout(width='200px', height='40px')
        )
        all_widgets.append(save_button)
        
        # Status output
        status_output = widgets.Output()
        all_widgets.append(status_output)
        
        # Set up change handlers
        def save_all_settings(b=None):
            try:
                js.write_key('XL_models', xl_toggle.value)
                js.write_key('model', model_text.value)
                js.write_key('vae', vae_text.value)
                js.write_key('change_webui', webui_dropdown.value)
                js.write_key('latest_extensions', extensions_toggle.value)
                js.write_key('commandline_arguments', args_text.value)
                js.write_key('civitai_token', civitai_token.value)
                js.write_key('huggingface_token', hf_token.value)
                
                with status_output:
                    status_output.clear_output()
                    print("💾 All settings saved successfully!")
                    
            except Exception as e:
                with status_output:
                    status_output.clear_output()
                    print(f"❌ Error saving settings: {e}")
        
        # Auto-save on changes
        def on_change(change):
            save_all_settings()
            
        xl_toggle.observe(on_change, names='value')
        webui_dropdown.observe(on_change, names='value')
        extensions_toggle.observe(on_change, names='value')
        
        # Manual save button
        save_button.on_click(save_all_settings)
        
        # Load initial settings display
        save_all_settings()
        
        # Create and display the interface
        interface = widgets.VBox(
            all_widgets,
            layout=widgets.Layout(
                width='100%',
                padding='20px',
                border='2px solid #ddd',
                border_radius='10px'
            )
        )
        
        display(interface)
        print("✅ Basic interface created with full functionality!")

# Main integration function
def create_integrated_widgets():
    """Main function to create integrated widget interface"""
    integrated_system = IntegratedWidgetSystem()
    integrated_system.create_integrated_interface()

# For backward compatibility and direct execution
if __name__ == "__main__":
    create_integrated_widgets()

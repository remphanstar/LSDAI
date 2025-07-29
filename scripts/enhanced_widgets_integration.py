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
        """Fallback to original interface - FIXED"""
        try:
            # FIXED: Import and run the original widgets script
            print("✅ Loading original LSDAI widgets...")
            
            # Execute the original widgets_en.py script
            # This will display the original interface directly
            exec(open('scripts/widgets_en.py').read())
            
        except Exception as e:
            print(f"⚠️ Could not load original interface: {e}")
            self._create_basic_fallback()
            
    def _create_basic_fallback(self):
        """Create basic fallback interface when everything else fails"""
        print("🔧 Creating basic fallback interface...")
        
        # Create minimal working interface
        basic_widgets = []
        
        # XL Models toggle
        xl_toggle = widgets.ToggleButton(
            value=js.read_key('XL_models', False),
            description='SDXL Models',
            button_style='info'
        )
        basic_widgets.append(xl_toggle)
        
        # WebUI selection
        webui_dropdown = widgets.Dropdown(
            options=['automatic1111', 'ComfyUI', 'InvokeAI'],
            value=js.read_key('change_webui', 'automatic1111'),
            description='WebUI:'
        )
        basic_widgets.append(webui_dropdown)
        
        # Command line arguments
        args_text = widgets.Textarea(
            value=js.read_key('commandline_arguments', ''),
            description='Arguments:',
            placeholder='--xformers --api --listen'
        )
        basic_widgets.append(args_text)
        
        # Save button
        save_button = widgets.Button(
            description='Save Settings',
            button_style='success'
        )
        
        def save_settings(b):
            js.write_key('XL_models', xl_toggle.value)
            js.write_key('change_webui', webui_dropdown.value)
            js.write_key('commandline_arguments', args_text.value)
            print("💾 Settings saved!")
            
        save_button.on_click(save_settings)
        basic_widgets.append(save_button)
        
        # Set up change handlers
        def on_xl_change(change):
            js.write_key('XL_models', change['new'])
        xl_toggle.observe(on_xl_change, names='value')
        
        def on_webui_change(change):
            js.write_key('change_webui', change['new'])
        webui_dropdown.observe(on_webui_change, names='value')
        
        def on_args_change(change):
            js.write_key('commandline_arguments', change['new'])
        args_text.observe(on_args_change, names='value')
        
        # Display basic interface
        fallback_interface = widgets.VBox([
            widgets.HTML('<h2>🎨 LSDAI Basic Interface</h2>'),
            widgets.HTML('<p>Enhanced widgets not available. Using basic interface.</p>'),
            *basic_widgets
        ])
        
        display(fallback_interface)

# Main integration function
def create_integrated_widgets():
    """Main function to create integrated widget interface"""
    integrated_system = IntegratedWidgetSystem()
    integrated_system.create_integrated_interface()

# For backward compatibility and direct execution
if __name__ == "__main__":
    create_integrated_widgets()

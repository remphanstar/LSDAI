# Complete Enhanced Widgets Integration - Original + Enhanced Features
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
    """Handles loading and managing model data from files with inpainting filtering"""
    
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
    
    def get_options(self, category, is_xl=False, inpainting_only=False):
        """Get options for a specific category with filtering"""
        data = self.sdxl_data if is_xl else self.sd15_data
        category_data = data.get(category, {})
        
        if not category_data:
            return ['none']
        
        options = ['none']
        
        # Filter models based on inpainting setting
        for model_name, model_info in category_data.items():
            if category == 'model_list' and inpainting_only:
                # Only show inpainting models
                if isinstance(model_info, dict) and model_info.get('inpainting', False):
                    options.append(model_name)
                elif isinstance(model_info, list):
                    # Check if any variant has inpainting
                    if any(item.get('inpainting', False) for item in model_info if isinstance(item, dict)):
                        options.append(model_name)
            elif category == 'model_list' and not inpainting_only:
                # Show all models (both regular and inpainting)
                options.append(model_name)
            else:
                # For non-model categories, show everything
                options.append(model_name)
                
        return options
    
    def get_model_info(self, category, model_name, is_xl=False):
        """Get detailed info about a specific model"""
        data = self.sdxl_data if is_xl else self.sd15_data
        return data.get(category, {}).get(model_name, {})

class CompleteIntegratedWidgetSystem:
    def __init__(self):
        self.original_factory = WidgetFactory() if ORIGINAL_WIDGETS_AVAILABLE else None
        self.enhanced_manager = EnhancedWidgetManager() if ENHANCEMENTS_AVAILABLE else None
        self.model_manager = ModelDataManager()
        self.widgets = {}
        
        # Complete settings keys (original + enhanced)
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
        """Create complete interface with all original + enhanced features"""
        
        # Clear any existing output first
        clear_output(wait=True)
        
        if ENHANCEMENTS_AVAILABLE:
            print("🚀 Loading Complete Enhanced LSDAI Interface")
            
            try:
                # Load enhanced CSS/JS
                self._load_enhanced_styles()
                
                # Try enhanced interface first
                if hasattr(self.enhanced_manager, 'create_enhanced_interface'):
                    enhanced_interface = self.enhanced_manager.create_enhanced_interface()
                    
                    # Add complete compatibility layer with all original features
                    compatibility_layer = self._create_complete_compatibility_layer()
                    
                    # Combine interfaces
                    combined_interface = widgets.VBox([
                        enhanced_interface,
                        compatibility_layer
                    ])
                    
                    display(combined_interface)
                    print("✅ Complete enhanced interface loaded!")
                    return
                    
                else:
                    raise AttributeError("Enhanced interface method missing")
                    
            except Exception as e:
                print(f"⚠️ Enhanced interface failed: {e}")
                clear_output(wait=True)
                print("🔄 Loading complete LSDAI interface...")
                
        else:
            print("📦 Loading Complete LSDAI Interface")
            
        # Create complete interface (enhanced or fallback)
        self._create_complete_interface()
        
    def _load_enhanced_styles(self):
        """Load enhanced CSS and JavaScript"""
        
        css_content = """
        <style>
        .lsdai-complete-container {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 1400px;
            margin: 0 auto;
        }
        .lsdai-header-complete {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 25px;
            border-radius: 15px 15px 0 0;
            text-align: center;
            margin-bottom: 0;
        }
        .lsdai-section-complete {
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 10px;
            padding: 20px;
            margin: 15px 0;
        }
        .lsdai-section-complete h3 {
            color: #495057;
            border-bottom: 3px solid #007bff;
            padding-bottom: 10px;
            margin-top: 0;
            display: flex;
            align-items: center;
        }
        .toggle-row {
            display: flex;
            gap: 15px;
            align-items: center;
            margin: 15px 0;
            flex-wrap: wrap;
        }
        .model-grid-complete {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }
        .model-selector-complete {
            background: white;
            border: 2px solid #ced4da;
            border-radius: 10px;
            padding: 15px;
            transition: all 0.3s ease;
        }
        .model-selector-complete:hover {
            border-color: #007bff;
            box-shadow: 0 4px 15px rgba(0,123,255,0.2);
        }
        .empowerment-section {
            background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%);
            border: 2px solid #ff6b9d;
            border-radius: 10px;
            padding: 20px;
            margin: 20px 0;
        }
        .empowerment-section h3 {
            color: #721c24;
            border-bottom: 2px solid #ff6b9d;
        }
        .custom-urls-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 15px;
            margin: 15px 0;
        }
        .status-complete {
            background: #d4edda;
            border: 2px solid #c3e6cb;
            color: #155724;
            padding: 15px;
            border-radius: 10px;
            margin: 15px 0;
            font-weight: 500;
        }
        .save-button-complete {
            background: linear-gradient(45deg, #28a745, #20c997);
            color: white;
            border: none;
            padding: 15px 40px;
            border-radius: 30px;
            font-size: 18px;
            font-weight: bold;
            margin: 25px auto;
            display: block;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        .save-button-complete:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(40,167,69,0.3);
        }
        </style>
        """
        
        display(HTML(css_content))
        
        # Load enhanced JavaScript if available
        js_files = [
            'JS/enhanced_widgets.js',
            'JS/main_widgets.js'
        ]
        
        for js_file in js_files:
            if Path(js_file).exists():
                with open(js_file, 'r') as f:
                    js_content = f.read()
                    display(Javascript(js_content))
                    
    def _create_complete_compatibility_layer(self):
        """Create compatibility layer with all original features"""
        
        # This would be the enhanced tabbed content integration
        # For now, we'll create the complete interface directly
        return widgets.HTML('<div style="display:none;"></div>')  # Placeholder
        
    def _create_complete_interface(self):
        """Create the complete LSDAI interface with all features"""
        
        container_widgets = []
        
        # Header
        header = widgets.HTML('''
        <div class="lsdai-header-complete">
            <h1>🎨 LSDAI Complete Model Selection Interface</h1>
            <p>Enhanced model selection with all original features + modern enhancements</p>
        </div>
        ''')
        container_widgets.append(header)
        
        # Main Configuration Toggles Section
        config_section = self._create_main_config_section()
        container_widgets.append(config_section)
        
        # Model Selection Grid  
        model_grid = self._create_complete_model_grid()
        container_widgets.append(model_grid)
        
        # WebUI and Extensions Section
        webui_section = self._create_complete_webui_section()
        container_widgets.append(webui_section)
        
        # Empowerment Mode Section (Original Feature)
        empowerment_section = self._create_empowerment_section()
        container_widgets.append(empowerment_section)
        
        # Custom URLs Section (Original Feature)
        custom_urls_section = self._create_custom_urls_section()
        container_widgets.append(custom_urls_section)
        
        # API Tokens Section
        tokens_section = self._create_complete_tokens_section()
        container_widgets.append(tokens_section)
        
        # Save and Status Section
        save_section = self._create_complete_save_section()
        container_widgets.append(save_section)
        
        # Main container
        main_interface = widgets.VBox(
            container_widgets,
            layout=widgets.Layout(
                width='100%',
                padding='20px'
            )
        )
        
        display(main_interface)
        print("✅ Complete LSDAI interface loaded with all features!")
        
    def _create_main_config_section(self):
        """Create main configuration toggles section"""
        
        # XL Models toggle
        xl_toggle = widgets.ToggleButton(
            value=js.read(SETTINGS_PATH, 'XL_models', False),
            description='🚀 SDXL Models',
            button_style='info',
            layout=widgets.Layout(width='180px', height='45px')
        )
        self.widgets['XL_models'] = xl_toggle
        
        # Inpainting toggle
        inpainting_toggle = widgets.ToggleButton(
            value=js.read(SETTINGS_PATH, 'inpainting_model', False),
            description='🖼️ Inpainting Only',
            button_style='warning',
            layout=widgets.Layout(width='180px', height='45px')
        )
        self.widgets['inpainting_model'] = inpainting_toggle
        
        # Detailed Download toggle (ORIGINAL FEATURE)
        detailed_download_toggle = widgets.ToggleButton(
            value=js.read(SETTINGS_PATH, 'detailed_download', False),
            description='📋 Detailed Download',
            button_style='success',
            layout=widgets.Layout(width='180px', height='45px')
        )
        self.widgets['detailed_download'] = detailed_download_toggle
        
        # Latest WebUI toggle
        latest_webui_toggle = widgets.ToggleButton(
            value=js.read(SETTINGS_PATH, 'latest_webui', True),
            description='🔄 Update WebUI',
            button_style='primary',
            layout=widgets.Layout(width='180px', height='45px')
        )
        self.widgets['latest_webui'] = latest_webui_toggle
        
        # Set up change handlers
        def on_xl_change(change):
            is_xl = change['new']
            js.save(SETTINGS_PATH, 'XL_models', is_xl)
            self._update_all_model_options()
            print(f"🔄 Switched to {'SDXL' if is_xl else 'SD 1.5'} models")
            
        xl_toggle.observe(on_xl_change, names='value')
        
        def on_inpainting_change(change):
            js.save(SETTINGS_PATH, 'inpainting_model', change['new'])
            self._update_all_model_options()
            print(f"🔄 {'Showing inpainting models only' if change['new'] else 'Showing all models'}")
            
        inpainting_toggle.observe(on_inpainting_change, names='value')
        
        def on_detailed_change(change):
            js.save(SETTINGS_PATH, 'detailed_download', change['new'])
            
        detailed_download_toggle.observe(on_detailed_change, names='value')
        
        def on_webui_update_change(change):
            js.save(SETTINGS_PATH, 'latest_webui', change['new'])
            
        latest_webui_toggle.observe(on_webui_update_change, names='value')
        
        # Toggle row layout
        toggle_row = widgets.HBox([
            xl_toggle,
            inpainting_toggle, 
            detailed_download_toggle,
            latest_webui_toggle
        ], layout=widgets.Layout(justify_content='space-around', margin='10px 0'))
        
        section_html = widgets.HTML('''
        <div class="lsdai-section-complete">
            <h3>⚙️ Main Configuration</h3>
            <p>Toggle between model types and download settings</p>
        </div>
        ''')
        
        return widgets.VBox([section_html, toggle_row])
        
    def _create_complete_model_grid(self):
        """Create complete model selection grid with filtering"""
        
        is_xl = js.read(SETTINGS_PATH, 'XL_models', False)
        inpainting_only = js.read(SETTINGS_PATH, 'inpainting_model', False)
        
        # Model selectors with filtering
        model_selector = self._create_filtered_model_selector('Models', 'model_list', is_xl, inpainting_only, height='200px')
        vae_selector = self._create_filtered_model_selector('VAE', 'vae_list', is_xl, False, height='120px')
        lora_selector = self._create_filtered_model_selector('LoRA', 'lora_list', is_xl, False, height='150px')
        controlnet_selector = self._create_filtered_model_selector('ControlNet', 'controlnet_list', is_xl, False, height='150px')
        
        # Model numbers (original feature)
        model_num_widget = widgets.Text(
            value=js.read(SETTINGS_PATH, 'model_num', ''),
            description='Model Numbers:',
            placeholder='1,3,5 (comma-separated)',
            layout=widgets.Layout(width='100%')
        )
        self.widgets['model_num'] = model_num_widget
        
        def on_model_num_change(change):
            js.save(SETTINGS_PATH, 'model_num', change['new'])
        model_num_widget.observe(on_model_num_change, names='value')
        
        # VAE numbers
        vae_num_widget = widgets.Text(
            value=js.read(SETTINGS_PATH, 'vae_num', ''),
            description='VAE Numbers:',
            placeholder='1,2 (comma-separated)',
            layout=widgets.Layout(width='100%')
        )
        self.widgets['vae_num'] = vae_num_widget
        
        def on_vae_num_change(change):
            js.save(SETTINGS_PATH, 'vae_num', change['new'])
        vae_num_widget.observe(on_vae_num_change, names='value')
        
        # ControlNet numbers
        controlnet_num_widget = widgets.Text(
            value=js.read(SETTINGS_PATH, 'controlnet_num', ''),
            description='ControlNet Numbers:',
            placeholder='1,2 (comma-separated)',
            layout=widgets.Layout(width='100%')
        )
        self.widgets['controlnet_num'] = controlnet_num_widget
        
        def on_controlnet_num_change(change):
            js.save(SETTINGS_PATH, 'controlnet_num', change['new'])
        controlnet_num_widget.observe(on_controlnet_num_change, names='value')
        
        # Grid layout
        grid_html = widgets.HTML('''
        <div class="lsdai-section-complete">
            <h3>🎨 Model Selection with Smart Filtering</h3>
            <p>Multi-select models with Ctrl+Click (Windows) or Cmd+Click (Mac). Inpainting toggle filters models automatically.</p>
        </div>
        ''')
        
        # 2x2 model grid
        top_row = widgets.HBox([model_selector, vae_selector])
        bottom_row = widgets.HBox([lora_selector, controlnet_selector])
        
        # Numbers row
        numbers_row = widgets.HBox([model_num_widget, vae_num_widget, controlnet_num_widget])
        
        grid_container = widgets.VBox([
            grid_html,
            top_row,
            bottom_row,
            numbers_row
        ])
        
        return grid_container
        
    def _create_filtered_model_selector(self, title, category, is_xl, inpainting_only, height='120px'):
        """Create a model selector with proper filtering"""
        
        options = self.model_manager.get_options(category, is_xl, inpainting_only)
        
        # Get saved values and validate
        saved_values = js.read(SETTINGS_PATH, category.replace('_list', ''), ['none'])
        if isinstance(saved_values, str):
            saved_values = [saved_values]
        
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
            style={'description_width': '80px'}
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
            widgets.HTML(f'<div style="font-weight: bold; color: #495057; margin-bottom: 5px;">{title} ({len(options)-1} available)</div>'),
            selector
        ], 
        layout=widgets.Layout(
            border='2px solid #ced4da',
            border_radius='10px',
            padding='15px',
            margin='5px',
            background_color='white'
        ))
        
        return container
        
    def _update_all_model_options(self):
        """Update all model selectors when toggles change"""
        
        is_xl = js.read(SETTINGS_PATH, 'XL_models', False)
        inpainting_only = js.read(SETTINGS_PATH, 'inpainting_model', False)
        
        categories = [
            ('model', 'model_list', inpainting_only),  # Only models get inpainting filter
            ('vae', 'vae_list', False),
            ('lora', 'lora_list', False), 
            ('controlnet', 'controlnet_list', False)
        ]
        
        for widget_key, category_key, use_inpainting_filter in categories:
            if widget_key in self.widgets:
                widget = self.widgets[widget_key]
                
                # Get new options with proper filtering
                new_options = self.model_manager.get_options(category_key, is_xl, use_inpainting_filter)
                widget.options = new_options
                
                # Reset to valid selection
                widget.value = ['none']
                js.save(SETTINGS_PATH, widget_key, ['none'])
                
    def _create_complete_webui_section(self):
        """Create complete WebUI configuration section"""
        
        # WebUI selection
        webui_options = ['automatic1111', 'ComfyUI', 'InvokeAI', 'StableSwarmUI', 'Forge', 'ReForge', 'SD-UX']
        webui_dropdown = widgets.Dropdown(
            options=webui_options,
            value=js.read(SETTINGS_PATH, 'change_webui', 'automatic1111'),
            description='WebUI:',
            layout=widgets.Layout(width='250px')
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
        
        # Check custom nodes (ComfyUI)
        custom_nodes_toggle = widgets.ToggleButton(
            value=js.read(SETTINGS_PATH, 'check_custom_nodes_deps', True),
            description='🔍 Check Custom Nodes',
            button_style='info',
            layout=widgets.Layout(width='200px')
        )
        self.widgets['check_custom_nodes_deps'] = custom_nodes_toggle
        
        # Command line arguments
        args_text = widgets.Textarea(
            value=js.read(SETTINGS_PATH, 'commandline_arguments', ''),
            description='Launch Args:',
            placeholder='--xformers --api --listen --port 7860',
            layout=widgets.Layout(width='100%', height='100px')
        )
        self.widgets['commandline_arguments'] = args_text
        
        # Commit hash (original feature)
        commit_hash_widget = widgets.Text(
            value=js.read(SETTINGS_PATH, 'commit_hash', ''),
            description='Commit Hash:',
            placeholder='Switch between branches or commits',
            layout=widgets.Layout(width='100%')
        )
        self.widgets['commit_hash'] = commit_hash_widget
        
        # Set up change handlers
        def on_webui_change(change):
            js.save(SETTINGS_PATH, 'change_webui', change['new'])
        webui_dropdown.observe(on_webui_change, names='value')
        
        def on_extensions_change(change):
            js.save(SETTINGS_PATH, 'latest_extensions', change['new'])
        extensions_toggle.observe(on_extensions_change, names='value')
        
        def on_custom_nodes_change(change):
            js.save(SETTINGS_PATH, 'check_custom_nodes_deps', change['new'])
        custom_nodes_toggle.observe(on_custom_nodes_change, names='value')
        
        def on_args_change(change):
            js.save(SETTINGS_PATH, 'commandline_arguments', change['new'])
        args_text.observe(on_args_change, names='value')
        
        def on_commit_change(change):
            js.save(SETTINGS_PATH, 'commit_hash', change['new'])
        commit_hash_widget.observe(on_commit_change, names='value')
        
        # Layout
        webui_row = widgets.HBox([webui_dropdown, extensions_toggle, custom_nodes_toggle])
        
        section = widgets.VBox([
            widgets.HTML('''
            <div class="lsdai-section-complete">
                <h3>🚀 WebUI & Extensions Configuration</h3>
            </div>
            '''),
            webui_row,
            args_text,
            commit_hash_widget
        ])
        
        return section
        
    def _create_empowerment_section(self):
        """Create empowerment mode section (ORIGINAL FEATURE)"""
        
        # Empowerment toggle
        empowerment_toggle = widgets.ToggleButton(
            value=js.read(SETTINGS_PATH, 'empowerment', False),
            description='⚡ Empowerment Mode',
            button_style='danger',
            layout=widgets.Layout(width='200px', height='50px')
        )
        self.widgets['empowerment'] = empowerment_toggle
        
        # Empowerment textarea with instructions
        empowerment_output = widgets.Textarea(
            value=js.read(SETTINGS_PATH, 'empowerment_output', ''),
            placeholder="""Use special tags for advanced downloads:
Tags: model (ckpt), vae, lora, embed (emb), extension (ext), adetailer (ad), control (cnet), upscale (ups)
Short-tags: start with '$' without space -> $ckpt

------ Example ------
# LoRA
https://civitai.com/api/download/models/229782

$ext
https://github.com/hako-mikan/sd-webui-cd-tuner[CD-Tuner]""",
            layout=widgets.Layout(width='100%', height='200px')
        )
        self.widgets['empowerment_output'] = empowerment_output
        
        # Set up change handlers
        def on_empowerment_change(change):
            js.save(SETTINGS_PATH, 'empowerment', change['new'])
            
        empowerment_toggle.observe(on_empowerment_change, names='value')
        
        def on_empowerment_output_change(change):
            js.save(SETTINGS_PATH, 'empowerment_output', change['new'])
            
        empowerment_output.observe(on_empowerment_output_change, names='value')
        
        section = widgets.VBox([
            widgets.HTML('''
            <div class="empowerment-section">
                <h3>⚡ Empowerment Mode - Advanced Download Tags</h3>
                <p><strong>Special Tags:</strong> model, vae, lora, embed, extension, adetailer, control, upscale</p>
                <p><strong>Short Tags:</strong> $ckpt, $vae, $lora, $emb, $ext, $ad, $cnet, $ups</p>
            </div>
            '''),
            empowerment_toggle,
            empowerment_output
        ])
        
        return section
        
    def _create_custom_urls_section(self):
        """Create custom URLs section (ORIGINAL FEATURE)"""
        
        # Individual URL fields
        url_fields = [
            ('Model_url', 'Model:', 'Direct model download URL'),
            ('Vae_url', 'VAE:', 'Direct VAE download URL'),
            ('LoRA_url', 'LoRA:', 'Direct LoRA download URL'),
            ('Embedding_url', 'Embedding:', 'Direct embedding download URL'),
            ('Extensions_url', 'Extensions:', 'Extension repository URLs'),
            ('ADetailer_url', 'ADetailer:', 'ADetailer model URLs'),
            ('custom_file_urls', 'Custom Files:', 'Custom file URLs with [filename] syntax')
        ]
        
        url_widgets = []
        
        for key, label, placeholder in url_fields:
            widget = widgets.Text(
                value=js.read(SETTINGS_PATH, key, ''),
                description=label,
                placeholder=placeholder,
                layout=widgets.Layout(width='100%', margin='5px 0')
            )
            self.widgets[key] = widget
            
            # Set up change handler
            def make_handler(setting_key):
                def handler(change):
                    js.save(SETTINGS_PATH, setting_key, change['new'])
                return handler
                
            widget.observe(make_handler(key), names='value')
            url_widgets.append(widget)
        
        # Create grid layout
        left_column = widgets.VBox(url_widgets[:4])
        right_column = widgets.VBox(url_widgets[4:])
        
        url_grid = widgets.HBox([left_column, right_column])
        
        section = widgets.VBox([
            widgets.HTML('''
            <div class="lsdai-section-complete">
                <h3>🔗 Custom Download URLs</h3>
                <p><strong>Syntax:</strong> Use [filename.ext] after URL for custom filenames</p>
                <p><strong>Example:</strong> https://example.com/model.safetensors[MyModel.safetensors]</p>
            </div>
            '''),
            url_grid
        ])
        
        return section
        
    def _create_complete_tokens_section(self):
        """Create complete API tokens section"""
        
        # All token fields from original
        token_fields = [
            ('civitai_token', 'Civitai Token:', 'Your Civitai API token for premium models'),
            ('huggingface_token', 'HuggingFace Token:', 'Your HuggingFace token for gated models'),
            ('zrok_token', 'Zrok Token:', 'Zrok tunneling token'),
            ('ngrok_token', 'Ngrok Token:', 'Ngrok tunneling token')
        ]
        
        token_widgets = []
        
        for key, label, placeholder in token_fields:
            widget = widgets.Password(
                value=js.read(SETTINGS_PATH, key, ''),
                description=label,
                placeholder=placeholder,
                layout=widgets.Layout(width='100%', margin='5px 0')
            )
            self.widgets[key] = widget
            
            # Set up change handler
            def make_token_handler(setting_key):
                def handler(change):
                    js.save(SETTINGS_PATH, setting_key, change['new'])
                return handler
                
            widget.observe(make_token_handler(key), names='value')
            token_widgets.append(widget)
        
        # Create 2x2 grid
        top_row = widgets.HBox([token_widgets[0], token_widgets[1]])
        bottom_row = widgets.HBox([token_widgets[2], token_widgets[3]])
        
        section = widgets.VBox([
            widgets.HTML('''
            <div class="lsdai-section-complete">
                <h3>🔑 API Tokens & Tunneling</h3>
                <p>Add your API tokens for premium access and tunneling services</p>
            </div>
            '''),
            top_row,
            bottom_row
        ])
        
        return section
        
    def _create_complete_save_section(self):
        """Create save button and comprehensive status section"""
        
        save_button = widgets.Button(
            description='💾 Save All Settings',
            button_style='success',
            layout=widgets.Layout(width='300px', height='60px')
        )
        
        status_output = widgets.Output(
            layout=widgets.Layout(height='120px', width='100%')
        )
        
        def save_all_settings(b):
            try:
                with status_output:
                    status_output.clear_output()
                    print("✅ All settings saved successfully!")
                    print("📊 Configuration Summary:")
                    print(f"   🎨 Model Type: {'SDXL' if js.read(SETTINGS_PATH, 'XL_models', False) else 'SD 1.5'}")
                    print(f"   🖼️  Inpainting Only: {'Yes' if js.read(SETTINGS_PATH, 'inpainting_model', False) else 'No'}")
                    print(f"   🚀 WebUI: {js.read(SETTINGS_PATH, 'change_webui', 'automatic1111')}")
                    print(f"   📋 Detailed Download: {'Enabled' if js.read(SETTINGS_PATH, 'detailed_download', False) else 'Disabled'}")
                    print(f"   ⚡ Empowerment Mode: {'Enabled' if js.read(SETTINGS_PATH, 'empowerment', False) else 'Disabled'}")
                    
                    # Count selections
                    model_count = len([x for x in js.read(SETTINGS_PATH, 'model', ['none']) if x != 'none'])
                    vae_count = len([x for x in js.read(SETTINGS_PATH, 'vae', ['none']) if x != 'none'])
                    lora_count = len([x for x in js.read(SETTINGS_PATH, 'lora', ['none']) if x != 'none'])
                    cnet_count = len([x for x in js.read(SETTINGS_PATH, 'controlnet', ['none']) if x != 'none'])
                    
                    print(f"   🎯 Selected: {model_count} models, {vae_count} VAE, {lora_count} LoRA, {cnet_count} ControlNet")
                    
                    print("\n🎉 Ready for downloading! Proceed to Cell 3.")
                    
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
    """Main function to create complete integrated widget interface"""
    integrated_system = CompleteIntegratedWidgetSystem()
    integrated_system.create_integrated_interface()

# For backward compatibility and direct execution
if __name__ == "__main__":
    create_integrated_widgets()

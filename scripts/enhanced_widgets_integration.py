# Working Enhanced Widgets Integration - Visual Cards + All Features
import json_utils as js
from pathlib import Path
import ipywidgets as widgets
from IPython.display import display, HTML, Javascript, clear_output
import importlib.util
import json
import os

# Get settings path from environment or default
SETTINGS_PATH = Path(os.environ.get('settings_path', '/content/LSDAI/settings.json'))
SCRIPTS_PATH = Path(os.environ.get('scr_path', '/content/LSDAI')) / 'scripts'

class ModelDataManager:
    """Load and manage model data from files"""
    
    def __init__(self):
        self.sd15_data = self._load_model_data('_models_data.py')
        self.sdxl_data = self._load_model_data('_xl_models_data.py')
        
    def _load_model_data(self, filename):
        """Load model data from Python file"""
        try:
            file_path = SCRIPTS_PATH / filename
            if not file_path.exists():
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
    
    def get_models_list(self, category, is_xl=False, inpainting_only=False):
        """Get models list with filtering"""
        data = self.sdxl_data if is_xl else self.sd15_data
        category_data = data.get(category, {})
        
        models = []
        for name, info in category_data.items():
            # Handle both dict and list formats
            if isinstance(info, dict):
                model_info = info
            elif isinstance(info, list) and len(info) > 0:
                model_info = info[0] if isinstance(info[0], dict) else {}
            else:
                model_info = {}
            
            # Filter for inpainting if needed
            if category == 'model_list' and inpainting_only:
                if not model_info.get('inpainting', False):
                    continue
            
            models.append({
                'name': name,
                'info': model_info,
                'inpainting': model_info.get('inpainting', False)
            })
        
        return models

class WorkingEnhancedInterface:
    def __init__(self):
        self.model_manager = ModelDataManager()
        self.widgets = {}
        
    def create_integrated_interface(self):
        """Create working enhanced interface"""
        
        clear_output(wait=True)
        print("🚀 Loading Working Enhanced LSDAI Interface")
        
        # Load enhanced styles
        self._load_enhanced_styles()
        
        # Create the interface
        self._create_working_interface()
        
        print("✅ Working enhanced interface loaded!")
        
    def _load_enhanced_styles(self):
        """Load enhanced CSS"""
        
        css_content = """
        <style>
        .lsdai-enhanced-container {
            max-width: 1200px;
            margin: 0 auto;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        
        .lsdai-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 12px 12px 0 0;
            text-align: center;
        }
        
        .tab-navigation {
            display: flex;
            background: #f8f9fa;
            margin: 0;
            padding: 0;
        }
        
        .tab-btn {
            flex: 1;
            padding: 15px 10px;
            background: #f8f9fa;
            border: none;
            border-bottom: 3px solid transparent;
            cursor: pointer;
            font-weight: 600;
            transition: all 0.3s ease;
        }
        
        .tab-btn:hover {
            background: #e9ecef;
        }
        
        .tab-btn.active {
            background: white;
            border-bottom-color: #007bff;
            color: #007bff;
        }
        
        .tab-content {
            background: white;
            min-height: 400px;
            padding: 20px;
            border-radius: 0 0 12px 12px;
        }
        
        .tab-panel {
            display: none;
        }
        
        .tab-panel.active {
            display: block;
        }
        
        .control-section {
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            padding: 15px;
            margin: 15px 0;
        }
        
        .toggle-row {
            display: flex;
            gap: 15px;
            margin: 10px 0;
            flex-wrap: wrap;
        }
        
        .enhanced-toggle {
            padding: 8px 16px;
            border: 2px solid #007bff;
            border-radius: 20px;
            background: white;
            color: #007bff;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .enhanced-toggle.active {
            background: #007bff;
            color: white;
        }
        
        .enhanced-toggle:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,123,255,0.3);
        }
        
        .models-section {
            margin: 20px 0;
        }
        
        .models-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 15px;
            margin: 15px 0;
        }
        
        .model-card {
            background: white;
            border: 2px solid #e9ecef;
            border-radius: 10px;
            padding: 15px;
            transition: all 0.3s ease;
            cursor: pointer;
        }
        
        .model-card:hover {
            border-color: #007bff;
            transform: translateY(-2px);
            box-shadow: 0 4px 15px rgba(0,123,255,0.1);
        }
        
        .model-card.selected {
            border-color: #28a745;
            background: linear-gradient(145deg, #d4edda 0%, #c3e6cb 100%);
        }
        
        .model-checkbox-container {
            display: flex;
            align-items: flex-start;
            gap: 10px;
            margin-bottom: 10px;
        }
        
        .model-checkbox {
            width: 18px;
            height: 18px;
            margin-top: 2px;
        }
        
        .model-name {
            font-weight: 600;
            font-size: 14px;
            line-height: 1.4;
            color: #495057;
            flex: 1;
        }
        
        .model-tags {
            display: flex;
            gap: 5px;
            flex-wrap: wrap;
            margin-top: 8px;
        }
        
        .model-tag {
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 10px;
            font-weight: 600;
            text-transform: uppercase;
        }
        
        .model-tag.inpainting {
            background: #fff3cd;
            color: #856404;
        }
        
        .model-tag.sdxl {
            background: #d1ecf1;
            color: #0c5460;
        }
        
        .selection-counter {
            background: linear-gradient(45deg, #007bff, #0056b3);
            color: white;
            padding: 10px 20px;
            border-radius: 20px;
            margin: 15px 0;
            text-align: center;
            font-weight: 600;
        }
        
        .config-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 15px;
            margin: 15px 0;
        }
        
        .config-input {
            width: 100%;
            padding: 8px 12px;
            border: 1px solid #ced4da;
            border-radius: 6px;
            font-size: 14px;
        }
        
        .config-textarea {
            width: 100%;
            padding: 10px;
            border: 1px solid #ced4da;
            border-radius: 6px;
            font-size: 14px;
            resize: vertical;
        }
        
        .save-button {
            background: linear-gradient(45deg, #28a745, #20c997);
            color: white;
            border: none;
            padding: 12px 30px;
            border-radius: 25px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            margin: 20px auto;
            display: block;
        }
        
        .save-button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(40,167,69,0.3);
        }
        </style>
        """
        
        display(HTML(css_content))
        
    def _create_working_interface(self):
        """Create the working interface with tabs"""
        
        # Create main interface
        interface_widgets = []
        
        # Header
        header = widgets.HTML('''
        <div class="lsdai-enhanced-container">
            <div class="lsdai-header">
                <h2>🎨 LSDAI Enhanced Model Selection</h2>
                <p>Visual model selection with enhanced features</p>
            </div>
        </div>
        ''')
        interface_widgets.append(header)
        
        # Tab navigation
        tabs_html = '''
        <div class="lsdai-enhanced-container">
            <div class="tab-navigation" id="tab-nav">
                <button class="tab-btn active" onclick="showTab('models')">🎨 Models</button>
                <button class="tab-btn" onclick="showTab('config')">⚙️ Config</button>
                <button class="tab-btn" onclick="showTab('queue')">📥 Queue</button>
                <button class="tab-btn" onclick="showTab('batch')">⚡ Batch</button>
                <button class="tab-btn" onclick="showTab('settings')">💾 Settings</button>
            </div>
        </div>
        '''
        interface_widgets.append(widgets.HTML(tabs_html))
        
        # Tab content container
        tab_container = widgets.VBox(layout=widgets.Layout(
            background_color='white',
            border_radius='0 0 12px 12px',
            padding='20px',
            margin='0 auto',
            max_width='1200px'
        ))
        
        # Models tab (default)
        models_tab = self._create_models_tab()
        tab_container.children = [models_tab]
        self.widgets['tab_container'] = tab_container
        
        interface_widgets.append(tab_container)
        
        # Add JavaScript for tab switching
        self._add_tab_javascript()
        
        # Display everything
        main_interface = widgets.VBox(interface_widgets)
        display(main_interface)
        
    def _create_models_tab(self):
        """Create the models tab with visual cards"""
        
        # Get current settings
        is_xl = js.read(SETTINGS_PATH, 'XL_models', False)
        inpainting_only = js.read(SETTINGS_PATH, 'inpainting_model', False)
        detailed_download = js.read(SETTINGS_PATH, 'detailed_download', False)
        
        # Main toggles
        xl_toggle = widgets.ToggleButton(
            value=is_xl,
            description='🚀 SDXL Models',
            button_style='info',
            layout=widgets.Layout(width='150px')
        )
        
        inpainting_toggle = widgets.ToggleButton(
            value=inpainting_only,
            description='🖼️ Inpainting Only',
            button_style='warning',
            layout=widgets.Layout(width='150px')
        )
        
        detailed_toggle = widgets.ToggleButton(
            value=detailed_download,
            description='📋 Detailed Download',
            button_style='success',
            layout=widgets.Layout(width='150px')
        )
        
        # Store widgets
        self.widgets.update({
            'XL_models': xl_toggle,
            'inpainting_model': inpainting_toggle,
            'detailed_download': detailed_toggle
        })
        
        # Toggle change handlers
        def on_xl_change(change):
            js.save(SETTINGS_PATH, 'XL_models', change['new'])
            self._refresh_models_tab()
            
        def on_inpainting_change(change):
            js.save(SETTINGS_PATH, 'inpainting_model', change['new'])
            self._refresh_models_tab()
            
        def on_detailed_change(change):
            js.save(SETTINGS_PATH, 'detailed_download', change['new'])
            
        xl_toggle.observe(on_xl_change, names='value')
        inpainting_toggle.observe(on_inpainting_change, names='value')
        detailed_toggle.observe(on_detailed_change, names='value')
        
        # Toggles row
        toggles_row = widgets.HBox([xl_toggle, inpainting_toggle, detailed_toggle])
        
        # Selection counter
        counter = widgets.HTML('<div class="selection-counter">Loading models...</div>')
        self.widgets['selection_counter'] = counter
        
        # Model sections
        model_sections = self._create_model_sections(is_xl, inpainting_only)
        
        # Combine everything
        tab_content = widgets.VBox([
            widgets.HTML('<div class="control-section"><h3>🎛️ Configuration</h3></div>'),
            toggles_row,
            counter,
            *model_sections
        ])
        
        self._update_selection_counter()
        
        return tab_content
        
    def _create_model_sections(self, is_xl, inpainting_only):
        """Create model selection sections with visual cards"""
        
        sections = []
        categories = [
            ('model_list', 'Models', '🎨'),
            ('vae_list', 'VAE', '🎭'),
            ('lora_list', 'LoRA', '🔧'),
            ('controlnet_list', 'ControlNet', '🎮')
        ]
        
        for category, title, icon in categories:
            # Get models for this category
            use_inpainting_filter = (category == 'model_list' and inpainting_only)
            models = self.model_manager.get_models_list(category, is_xl, use_inpainting_filter)
            
            if not models:
                continue
                
            # Section header
            section_header = widgets.HTML(f'''
            <div class="models-section">
                <h3>{icon} {title} ({len(models)} available)</h3>
            </div>
            ''')
            
            # Create model cards
            model_cards = []
            saved_selections = js.read(SETTINGS_PATH, category.replace('_list', ''), [])
            if isinstance(saved_selections, str):
                saved_selections = [saved_selections]
            
            for i, model in enumerate(models):
                # Create checkbox
                checkbox = widgets.Checkbox(
                    value=model['name'] in saved_selections,
                    description=model['name'],
                    layout=widgets.Layout(width='100%'),
                    style={'description_width': '0px'}  # Hide default description
                )
                
                # Tags
                tags = []
                if model['inpainting']:
                    tags.append('inpainting')
                if is_xl:
                    tags.append('sdxl')
                    
                tags_html = ''.join([f'<span class="model-tag {tag}">{tag}</span>' for tag in tags])
                
                # Model card with custom styling
                card_html = widgets.HTML(f'''
                <div class="model-card {'selected' if model['name'] in saved_selections else ''}" id="card-{category}-{i}">
                    <div class="model-checkbox-container">
                        <div class="model-name">{model['name']}</div>
                    </div>
                    <div class="model-tags">
                        {tags_html}
                    </div>
                </div>
                ''')
                
                # Store reference for updates
                checkbox._model_name = model['name']
                checkbox._category = category
                checkbox._card_id = f"card-{category}-{i}"
                
                # Change handler
                def make_handler(cat, name, card_id):
                    def handler(change):
                        # Update saved selections
                        current = js.read(SETTINGS_PATH, cat.replace('_list', ''), [])
                        if isinstance(current, str):
                            current = [current]
                        
                        if change['new']:
                            if name not in current:
                                current.append(name)
                        else:
                            if name in current:
                                current.remove(name)
                        
                        # Filter out 'none' values
                        current = [x for x in current if x != 'none']
                        
                        js.save(SETTINGS_PATH, cat.replace('_list', ''), current)
                        self._update_selection_counter()
                        
                        # Update card styling
                        display(Javascript(f'''
                        const card = document.getElementById("{card_id}");
                        if (card) {{
                            if ({str(change['new']).lower()}) {{
                                card.classList.add("selected");
                            }} else {{
                                card.classList.remove("selected");
                            }}
                        }}
                        '''))
                        
                    return handler
                
                checkbox.observe(make_handler(category, model['name'], f"card-{category}-{i}"), names='value')
                
                # Combine checkbox and card
                model_widget = widgets.VBox([
                    checkbox,
                    card_html
                ], layout=widgets.Layout(margin='5px'))
                
                model_cards.append(model_widget)
            
            # Create grid layout
            if model_cards:
                # Split into rows of 3
                rows = []
                for i in range(0, len(model_cards), 3):
                    row_cards = model_cards[i:i+3]
                    # Pad row if needed
                    while len(row_cards) < 3:
                        row_cards.append(widgets.HTML(''))
                    rows.append(widgets.HBox(row_cards, layout=widgets.Layout(width='100%')))
                
                sections.extend([section_header] + rows)
        
        return sections
        
    def _refresh_models_tab(self):
        """Refresh the models tab when toggles change"""
        print("🔄 Refreshing models...")
        
        # Get new settings
        is_xl = js.read(SETTINGS_PATH, 'XL_models', False)
        inpainting_only = js.read(SETTINGS_PATH, 'inpainting_model', False)
        
        # Recreate models tab
        new_models_tab = self._create_models_tab()
        
        # Update tab container
        if 'tab_container' in self.widgets:
            self.widgets['tab_container'].children = [new_models_tab]
            
        print(f"✅ Updated to {'SDXL' if is_xl else 'SD 1.5'} models")
        
    def _update_selection_counter(self):
        """Update the selection counter"""
        
        categories = ['model', 'vae', 'lora', 'controlnet']
        total = 0
        breakdown = []
        
        for category in categories:
            selections = js.read(SETTINGS_PATH, category, [])
            if isinstance(selections, str):
                selections = [selections]
            count = len([x for x in selections if x != 'none'])
            total += count
            if count > 0:
                breakdown.append(f"{category}: {count}")
        
        if 'selection_counter' in self.widgets:
            if total > 0:
                counter_html = f'<div class="selection-counter">✅ {total} models selected ({", ".join(breakdown)})</div>'
            else:
                counter_html = '<div class="selection-counter">No models selected</div>'
                
            self.widgets['selection_counter'].value = counter_html
        
    def _add_tab_javascript(self):
        """Add JavaScript for tab functionality"""
        
        js_content = """
        <script>
        function showTab(tabName) {
            // This would switch tabs - simplified for now
            console.log('Switching to tab:', tabName);
            
            // Update tab buttons
            const tabBtns = document.querySelectorAll('.tab-btn');
            tabBtns.forEach(btn => btn.classList.remove('active'));
            
            // Find and activate clicked tab
            const clickedBtn = event ? event.target : document.querySelector(`[onclick="showTab('${tabName}')"]`);
            if (clickedBtn) {
                clickedBtn.classList.add('active');
            }
            
            // For now, keep showing models tab
            // In a full implementation, this would switch the Python widget content
        }
        </script>
        """
        
        display(Javascript(js_content))

# Main integration function
def create_integrated_widgets():
    """Create the working enhanced interface"""
    interface = WorkingEnhancedInterface()
    interface.create_integrated_interface()

# For backward compatibility and direct execution
if __name__ == "__main__":
    create_integrated_widgets()

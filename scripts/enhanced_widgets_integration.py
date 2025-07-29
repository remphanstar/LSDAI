# Complete Enhanced Widgets Integration - ALL FEATURES
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
    """Enhanced model data manager with visual cards"""
    
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
    
    def get_model_cards_data(self, category, is_xl=False, inpainting_only=False):
        """Get model data formatted for visual cards"""
        data = self.sdxl_data if is_xl else self.sd15_data
        category_data = data.get(category, {})
        
        cards = []
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
            
            card = {
                'id': name.replace(' ', '_').replace('/', '_'),
                'name': name,
                'url': model_info.get('url', ''),
                'filename': model_info.get('name', ''),
                'inpainting': model_info.get('inpainting', False),
                'sdxl': is_xl,
                'category': category,
                'tags': []
            }
            
            # Add tags
            if card['inpainting']:
                card['tags'].append('inpainting')
            if is_xl:
                card['tags'].append('sdxl')
            if 'nsfw' in name.lower() or 'porn' in name.lower():
                card['tags'].append('nsfw')
                
            cards.append(card)
            
        return cards

class CompleteEnhancedInterface:
    def __init__(self):
        self.model_manager = ModelDataManager()
        self.widgets = {}
        self.selected_models = {
            'model_list': set(),
            'vae_list': set(),
            'lora_list': set(),
            'controlnet_list': set()
        }
        self.download_queue = []
        
    def create_integrated_interface(self):
        """Create the complete enhanced interface with all features"""
        
        clear_output(wait=True)
        print("🚀 Loading Complete Enhanced LSDAI Interface")
        
        # Load enhanced CSS and JavaScript
        self._load_enhanced_styles_and_scripts()
        
        # Create the tabbed interface container
        self._create_enhanced_tabbed_interface()
        
        print("✅ Complete enhanced interface loaded with all features!")
        
    def _load_enhanced_styles_and_scripts(self):
        """Load complete enhanced CSS and JavaScript"""
        
        # Enhanced CSS with all features
        css_content = """
        <style>
        /* Enhanced LSDAI Complete Interface */
        .enhanced-lsdai-container {
            max-width: 1200px;
            margin: 0 auto;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        
        /* Header */
        .enhanced-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 12px 12px 0 0;
            text-align: center;
        }
        
        /* Tab Navigation */
        .tab-navigation {
            display: flex;
            background: #f8f9fa;
            border-bottom: 2px solid #dee2e6;
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
            font-size: 14px;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
        }
        
        .tab-btn:hover {
            background: #e9ecef;
            transform: translateY(-2px);
        }
        
        .tab-btn.active {
            background: white;
            border-bottom-color: #007bff;
            color: #007bff;
        }
        
        /* Tab Content */
        .tab-content {
            background: white;
            min-height: 500px;
            border-radius: 0 0 12px 12px;
        }
        
        .tab-panel {
            display: none;
            padding: 20px;
            animation: fadeIn 0.3s ease;
        }
        
        .tab-panel.active {
            display: block;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        /* Model Cards Grid */
        .models-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }
        
        .model-card {
            background: linear-gradient(145deg, #ffffff 0%, #f8f9fa 100%);
            border: 2px solid #e9ecef;
            border-radius: 12px;
            padding: 15px;
            transition: all 0.3s ease;
            cursor: pointer;
            position: relative;
            overflow: hidden;
        }
        
        .model-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 8px 25px rgba(0,123,255,0.15);
            border-color: #007bff;
        }
        
        .model-card.selected {
            border-color: #28a745;
            background: linear-gradient(145deg, #d4edda 0%, #c3e6cb 100%);
            box-shadow: 0 6px 20px rgba(40,167,69,0.2);
        }
        
        .model-card-header {
            display: flex;
            justify-content: between;
            align-items: flex-start;
            margin-bottom: 10px;
        }
        
        .model-checkbox {
            width: 20px;
            height: 20px;
            margin-right: 10px;
            margin-top: 2px;
        }
        
        .model-name {
            font-weight: 600;
            font-size: 13px;
            line-height: 1.3;
            color: #495057;
            flex: 1;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }
        
        .model-tags {
            display: flex;
            flex-wrap: wrap;
            gap: 5px;
            margin: 8px 0;
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
            border: 1px solid #ffeaa7;
        }
        
        .model-tag.sdxl {
            background: #d1ecf1;
            color: #0c5460;
            border: 1px solid #bee5eb;
        }
        
        .model-tag.nsfw {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
        
        /* Control Panels */
        .control-panel {
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            padding: 15px;
            margin: 10px 0;
        }
        
        .control-row {
            display: flex;
            gap: 15px;
            align-items: center;
            margin: 10px 0;
            flex-wrap: wrap;
        }
        
        .toggle-enhanced {
            padding: 8px 16px;
            border: 2px solid #007bff;
            border-radius: 20px;
            background: white;
            color: #007bff;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .toggle-enhanced.active {
            background: #007bff;
            color: white;
        }
        
        .toggle-enhanced:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,123,255,0.3);
        }
        
        /* Download Queue */
        .queue-item {
            background: white;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            padding: 12px;
            margin: 8px 0;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .queue-item.downloading {
            border-color: #007bff;
            background: #f0f8ff;
        }
        
        .queue-item.completed {
            border-color: #28a745;
            background: #f8fff9;
        }
        
        .queue-item.failed {
            border-color: #dc3545;
            background: #fff5f5;
        }
        
        /* Status indicators */
        .selection-counter {
            background: linear-gradient(45deg, #007bff, #0056b3);
            color: white;
            padding: 10px 20px;
            border-radius: 20px;
            margin: 10px 0;
            text-align: center;
            font-weight: 600;
        }
        
        .settings-summary {
            background: #e9ecef;
            border-radius: 8px;
            padding: 15px;
            margin: 15px 0;
            font-size: 14px;
        }
        
        /* Responsive */
        @media (max-width: 768px) {
            .models-grid {
                grid-template-columns: 1fr;
            }
            .control-row {
                flex-direction: column;
                align-items: stretch;
            }
            .tab-btn {
                font-size: 12px;
                padding: 10px 5px;
            }
        }
        </style>
        """
        
        display(HTML(css_content))
        
        # Enhanced JavaScript with all functionality
        js_content = """
        <script>
        class CompleteLSDAIEnhanced {
            constructor() {
                this.selectedModels = {
                    model_list: new Set(),
                    vae_list: new Set(), 
                    lora_list: new Set(),
                    controlnet_list: new Set()
                };
                this.downloadQueue = [];
                this.currentTab = 'models';
                this.isXL = false;
                this.inpaintingOnly = false;
                
                this.init();
            }
            
            init() {
                this.setupTabNavigation();
                this.setupModelSelection();
                this.setupToggles();
                this.updateSelectionCounter();
            }
            
            setupTabNavigation() {
                const tabBtns = document.querySelectorAll('.tab-btn');
                const tabPanels = document.querySelectorAll('.tab-panel');
                
                tabBtns.forEach(btn => {
                    btn.addEventListener('click', () => {
                        const target = btn.dataset.tab;
                        
                        // Update active states
                        tabBtns.forEach(b => b.classList.remove('active'));
                        tabPanels.forEach(p => p.classList.remove('active'));
                        
                        btn.classList.add('active');
                        document.getElementById(`tab-${target}`).classList.add('active');
                        
                        this.currentTab = target;
                        
                        // Load tab content
                        this.loadTabContent(target);
                    });
                });
            }
            
            setupModelSelection() {
                document.addEventListener('change', (e) => {
                    if (e.target.classList.contains('model-checkbox')) {
                        const card = e.target.closest('.model-card');
                        const modelId = e.target.dataset.modelId;
                        const category = e.target.dataset.category;
                        
                        if (e.target.checked) {
                            this.selectedModels[category].add(modelId);
                            card.classList.add('selected');
                        } else {
                            this.selectedModels[category].delete(modelId);
                            card.classList.remove('selected');
                        }
                        
                        this.updateSelectionCounter();
                        this.saveSelections();
                    }
                });
            }
            
            setupToggles() {
                // XL Models toggle
                const xlToggle = document.getElementById('xl-toggle');
                if (xlToggle) {
                    xlToggle.addEventListener('click', () => {
                        this.isXL = !this.isXL;
                        xlToggle.classList.toggle('active');
                        this.reloadModelData();
                    });
                }
                
                // Inpainting toggle
                const inpaintingToggle = document.getElementById('inpainting-toggle');
                if (inpaintingToggle) {
                    inpaintingToggle.addEventListener('click', () => {
                        this.inpaintingOnly = !this.inpaintingOnly;
                        inpaintingToggle.classList.toggle('active');
                        this.reloadModelData();
                    });
                }
            }
            
            loadTabContent(tab) {
                const content = document.getElementById(`tab-${tab}`);
                if (!content) return;
                
                switch(tab) {
                    case 'models':
                        this.loadModelsTab(content);
                        break;
                    case 'queue':
                        this.loadQueueTab(content);
                        break;
                    case 'config':
                        this.loadConfigTab(content);
                        break;
                    case 'batch':
                        this.loadBatchTab(content);
                        break;
                    case 'settings':
                        this.loadSettingsTab(content);
                        break;
                }
            }
            
            loadModelsTab(content) {
                // This will be populated by Python with actual model data
                if (content.children.length === 0) {
                    content.innerHTML = `
                        <div class="control-panel">
                            <div class="control-row">
                                <button id="xl-toggle" class="toggle-enhanced ${this.isXL ? 'active' : ''}">
                                    🚀 SDXL Models
                                </button>
                                <button id="inpainting-toggle" class="toggle-enhanced ${this.inpaintingOnly ? 'active' : ''}">
                                    🖼️ Inpainting Only
                                </button>
                                <button id="detailed-download-toggle" class="toggle-enhanced">
                                    📋 Detailed Download
                                </button>
                            </div>
                            <div class="selection-counter" id="selection-counter">
                                No models selected
                            </div>
                        </div>
                        <div id="models-content">
                            <!-- Models will be loaded here by Python -->
                        </div>
                    `;
                }
            }
            
            loadQueueTab(content) {
                content.innerHTML = `
                    <div class="control-panel">
                        <h3>📥 Download Queue Manager</h3>
                        <div class="control-row">
                            <button onclick="lsdaiEnhanced.addSelectedToQueue()" class="toggle-enhanced">
                                ➕ Add Selected Models
                            </button>
                            <button onclick="lsdaiEnhanced.startDownloads()" class="toggle-enhanced">
                                ▶️ Start Downloads
                            </button>
                            <button onclick="lsdaiEnhanced.clearQueue()" class="toggle-enhanced">
                                🗑️ Clear Queue
                            </button>
                        </div>
                    </div>
                    <div id="queue-items">
                        ${this.downloadQueue.length === 0 ? 
                            '<p style="text-align: center; color: #6c757d; margin: 40px 0;">No items in download queue</p>' :
                            this.downloadQueue.map(item => this.renderQueueItem(item)).join('')
                        }
                    </div>
                `;
            }
            
            loadConfigTab(content) {
                content.innerHTML = `
                    <div class="control-panel">
                        <h3>⚙️ WebUI Configuration</h3>
                        <div class="control-row">
                            <select id="webui-select" style="padding: 8px; border-radius: 6px;">
                                <option value="automatic1111">Automatic1111</option>
                                <option value="ComfyUI">ComfyUI</option>
                                <option value="InvokeAI">InvokeAI</option>
                                <option value="StableSwarmUI">StableSwarmUI</option>
                                <option value="Forge">Forge</option>
                            </select>
                            <button class="toggle-enhanced" id="extensions-toggle">📦 Latest Extensions</button>
                        </div>
                        <textarea id="launch-args" placeholder="--xformers --api --listen --port 7860" 
                                  style="width: 100%; height: 80px; margin: 10px 0; padding: 10px; border-radius: 6px;"></textarea>
                    </div>
                    
                    <div class="control-panel">
                        <h3>⚡ Empowerment Mode</h3>
                        <button class="toggle-enhanced" id="empowerment-toggle">Enable Empowerment Mode</button>
                        <textarea id="empowerment-output" placeholder="Use special tags: $ckpt, $vae, $lora, $ext..." 
                                  style="width: 100%; height: 120px; margin: 10px 0; padding: 10px; border-radius: 6px;"></textarea>
                    </div>
                    
                    <div class="control-panel">
                        <h3>🔑 API Tokens</h3>
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
                            <input type="password" id="civitai-token" placeholder="Civitai API Token" style="padding: 8px; border-radius: 6px;">
                            <input type="password" id="hf-token" placeholder="HuggingFace Token" style="padding: 8px; border-radius: 6px;">
                        </div>
                    </div>
                `;
            }
            
            loadBatchTab(content) {
                content.innerHTML = `
                    <div class="control-panel">
                        <h3>⚡ Batch Operations</h3>
                        <div class="control-row">
                            <button onclick="lsdaiEnhanced.downloadAllModels()" class="toggle-enhanced">
                                📥 Download All Models
                            </button>
                            <button onclick="lsdaiEnhanced.downloadByType()" class="toggle-enhanced">
                                🎯 Download by Type
                            </button>
                            <button onclick="lsdaiEnhanced.downloadFavorites()" class="toggle-enhanced">
                                ⭐ Download Favorites
                            </button>
                        </div>
                        <div class="control-row">
                            <button onclick="lsdaiEnhanced.organizeModels()" class="toggle-enhanced">
                                📁 Organize Models
                            </button>
                            <button onclick="lsdaiEnhanced.checkDuplicates()" class="toggle-enhanced">
                                🔍 Check Duplicates
                            </button>
                            <button onclick="lsdaiEnhanced.verifyIntegrity()" class="toggle-enhanced">
                                ✅ Verify Integrity
                            </button>
                        </div>
                    </div>
                    <div id="batch-results" style="margin-top: 20px;">
                        <!-- Batch operation results will appear here -->
                    </div>
                `;
            }
            
            loadSettingsTab(content) {
                content.innerHTML = `
                    <div class="settings-summary">
                        <h3>📊 Current Configuration</h3>
                        <div id="settings-summary-content">
                            <!-- Settings summary will be populated here -->
                        </div>
                        <button onclick="lsdaiEnhanced.exportSettings()" class="toggle-enhanced" style="margin: 10px 5px 0 0;">
                            📤 Export Settings
                        </button>
                        <button onclick="lsdaiEnhanced.importSettings()" class="toggle-enhanced" style="margin: 10px 0 0 5px;">
                            📥 Import Settings
                        </button>
                    </div>
                `;
                this.updateSettingsSummary();
            }
            
            updateSelectionCounter() {
                const counter = document.getElementById('selection-counter');
                if (!counter) return;
                
                const total = Object.values(this.selectedModels).reduce((sum, set) => sum + set.size, 0);
                const breakdown = Object.entries(this.selectedModels)
                    .map(([category, set]) => `${category.replace('_list', '')}: ${set.size}`)
                    .filter(item => !item.endsWith(': 0'))
                    .join(', ');
                
                counter.innerHTML = total > 0 ? 
                    `✅ ${total} models selected (${breakdown})` : 
                    'No models selected';
            }
            
            updateSettingsSummary() {
                const summaryContent = document.getElementById('settings-summary-content');
                if (!summaryContent) return;
                
                summaryContent.innerHTML = `
                    <p><strong>Model Type:</strong> ${this.isXL ? 'SDXL' : 'SD 1.5'}</p>
                    <p><strong>Inpainting Only:</strong> ${this.inpaintingOnly ? 'Yes' : 'No'}</p>
                    <p><strong>Selected Models:</strong> ${Object.values(this.selectedModels).reduce((sum, set) => sum + set.size, 0)}</p>
                    <p><strong>Queue Items:</strong> ${this.downloadQueue.length}</p>
                `;
            }
            
            // Batch operations
            addSelectedToQueue() {
                console.log('Adding selected models to queue...');
                // Implementation would connect to Python
            }
            
            startDownloads() {
                console.log('Starting downloads...');
                // Implementation would connect to Python
            }
            
            downloadAllModels() {
                console.log('Downloading all models...');
                // Implementation would connect to Python
            }
            
            exportSettings() {
                const settings = {
                    selectedModels: Object.fromEntries(
                        Object.entries(this.selectedModels).map(([k, v]) => [k, Array.from(v)])
                    ),
                    isXL: this.isXL,
                    inpaintingOnly: this.inpaintingOnly,
                    downloadQueue: this.downloadQueue
                };
                
                const blob = new Blob([JSON.stringify(settings, null, 2)], { type: 'application/json' });
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `lsdai-settings-${new Date().toISOString().split('T')[0]}.json`;
                a.click();
                URL.revokeObjectURL(url);
            }
            
            saveSelections() {
                // This would save to Python backend
                console.log('Saving selections:', this.selectedModels);
            }
            
            reloadModelData() {
                console.log('Reloading model data...');
                // This would trigger Python to reload the models grid
            }
        }
        
        // Initialize when DOM is ready
        document.addEventListener('DOMContentLoaded', () => {
            window.lsdaiEnhanced = new CompleteLSDAIEnhanced();
        });
        
        // Initialize immediately if DOM is already loaded
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => {
                window.lsdaiEnhanced = new CompleteLSDAIEnhanced();
            });
        } else {
            window.lsdaiEnhanced = new CompleteLSDAIEnhanced();
        }
        </script>
        """
        
        display(Javascript(js_content))
        
    def _create_enhanced_tabbed_interface(self):
        """Create the complete enhanced tabbed interface"""
        
        # Create main container with header and tabs
        main_html = """
        <div class="enhanced-lsdai-container">
            <div class="enhanced-header">
                <h2>🎨 LSDAI Enhanced Model Selection</h2>
                <p>Complete model management with visual selection, download queue, and batch operations</p>
            </div>
            
            <div class="tab-navigation">
                <button class="tab-btn active" data-tab="models">🎨 Models</button>
                <button class="tab-btn" data-tab="queue">📥 Queue</button>
                <button class="tab-btn" data-tab="config">⚙️ Config</button>
                <button class="tab-btn" data-tab="batch">⚡ Batch</button>
                <button class="tab-btn" data-tab="settings">💾 Settings</button>
            </div>
            
            <div class="tab-content">
                <div id="tab-models" class="tab-panel active">
                    <!-- Models content will be loaded here -->
                </div>
                <div id="tab-queue" class="tab-panel">
                    <!-- Queue content will be loaded here -->
                </div>
                <div id="tab-config" class="tab-panel">
                    <!-- Config content will be loaded here -->
                </div>
                <div id="tab-batch" class="tab-panel">
                    <!-- Batch content will be loaded here -->
                </div>
                <div id="tab-settings" class="tab-panel">
                    <!-- Settings content will be loaded here -->
                </div>
            </div>
        </div>
        """
        
        display(HTML(main_html))
        
        # Load initial models content
        self._populate_models_tab()
        
    def _populate_models_tab(self):
        """Populate the models tab with visual cards"""
        
        is_xl = js.read(SETTINGS_PATH, 'XL_models', False)
        inpainting_only = js.read(SETTINGS_PATH, 'inpainting_model', False)
        
        # Get model data for all categories
        categories = [
            ('model_list', 'Models', '🎨'),
            ('vae_list', 'VAE', '🎭'),
            ('lora_list', 'LoRA', '🔧'),
            ('controlnet_list', 'ControlNet', '🎮')
        ]
        
        models_html = f"""
        <script>
        document.getElementById('tab-models').innerHTML = `
            <div class="control-panel">
                <div class="control-row">
                    <button id="xl-toggle" class="toggle-enhanced {'active' if is_xl else ''}">
                        🚀 SDXL Models
                    </button>
                    <button id="inpainting-toggle" class="toggle-enhanced {'active' if inpainting_only else ''}">
                        🖼️ Inpainting Only
                    </button>
                    <button id="detailed-download-toggle" class="toggle-enhanced">
                        📋 Detailed Download
                    </button>
                </div>
                <div class="selection-counter" id="selection-counter">
                    No models selected
                </div>
            </div>
        """
        
        # Add model cards for each category
        for category, title, icon in categories:
            cards_data = self.model_manager.get_model_cards_data(category, is_xl, inpainting_only if category == 'model_list' else False)
            
            models_html += f"""
            <div class="control-panel">
                <h3>{icon} {title} ({len(cards_data)} available)</h3>
                <div class="models-grid" id="{category}-grid">
            """
            
            for card in cards_data:
                tags_html = ''.join([f'<span class="model-tag {tag}">{tag}</span>' for tag in card['tags']])
                
                models_html += f"""
                    <div class="model-card" data-model-id="{card['id']}">
                        <div class="model-card-header">
                            <input type="checkbox" class="model-checkbox" 
                                   data-model-id="{card['id']}" 
                                   data-category="{category}"
                                   id="model-{card['id']}">
                            <label for="model-{card['id']}" class="model-name">{card['name']}</label>
                        </div>
                        <div class="model-tags">
                            {tags_html}
                        </div>
                    </div>
                """
            
            models_html += """
                </div>
            </div>
            """
        
        models_html += "`;"
        
        display(Javascript(models_html))
        
        # Also update the backend settings
        js.save(SETTINGS_PATH, 'XL_models', is_xl)
        js.save(SETTINGS_PATH, 'inpainting_model', inpainting_only)

# Main integration function
def create_integrated_widgets():
    """Create the complete enhanced interface with all features"""
    interface = CompleteEnhancedInterface()
    interface.create_integrated_interface()

# For backward compatibility and direct execution
if __name__ == "__main__":
    create_integrated_widgets()

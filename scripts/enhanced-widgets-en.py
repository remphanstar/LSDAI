# Enhanced widgets-en.py with advanced features
# Save as: scripts/enhanced-widgets-en.py

from widget_factory import WidgetFactory
from webui_utils import update_current_webui
import json_utils as js

from IPython.display import display, Javascript, HTML
import ipywidgets as widgets
from pathlib import Path
import importlib.util
import json
import os

# Enhanced Widget Manager with new features
class EnhancedWidgetManager:
    def __init__(self):
        self.factory = WidgetFactory()
        self.widgets = {}
        self.settings_keys = [
            'XL_models', 'model', 'model_num', 'inpainting_model', 'vae', 'vae_num', 'lora',
            'latest_webui', 'latest_extensions', 'check_custom_nodes_deps', 'change_webui', 'detailed_download',
            'controlnet', 'controlnet_num', 'commit_hash',
            'civitai_token', 'huggingface_token', 'zrok_token', 'ngrok_token', 'commandline_arguments', 'theme_accent',
            'empowerment', 'empowerment_output',
            'Model_url', 'Vae_url', 'LoRA_url', 'Embedding_url', 'Extensions_url', 'ADetailer_url',
            'custom_file_urls',
            # New enhanced features
            'model_favorites', 'download_queue', 'auto_preview', 'batch_mode', 'advanced_filters'
        ]
        self.model_cache = {}
        self.download_queue = []

    def create_enhanced_model_selector(self):
        """Create enhanced model selector with visual previews and filtering."""
        
        # Model preview and info container
        model_preview_html = self.factory.create_html('''
        <div id="model-preview-container" class="model-preview-container">
            <div class="model-preview-header">
                <h3>🎨 Enhanced Model Selection</h3>
                <div class="model-stats">
                    <span id="total-models">0 models</span> | 
                    <span id="selected-count">0 selected</span> |
                    <span id="download-size">0 GB</span>
                </div>
            </div>
            
            <div class="model-filters">
                <input type="text" id="model-search" placeholder="Search models..." class="search-input">
                <select id="model-type-filter" class="filter-select">
                    <option value="all">All Types</option>
                    <option value="checkpoint">Checkpoints</option>
                    <option value="lora">LoRA</option>
                    <option value="vae">VAE</option>
                    <option value="controlnet">ControlNet</option>
                </select>
                <select id="model-style-filter" class="filter-select">
                    <option value="all">All Styles</option>
                    <option value="realistic">Realistic</option>
                    <option value="anime">Anime</option>
                    <option value="artistic">Artistic</option>
                </select>
                <button id="clear-filters" class="filter-btn">Clear</button>
            </div>
            
            <div id="model-grid" class="model-grid">
                <!-- Models will be populated here by JavaScript -->
            </div>
            
            <div class="model-actions">
                <button id="select-all" class="action-btn">Select All Visible</button>
                <button id="clear-selection" class="action-btn">Clear Selection</button>
                <button id="add-to-queue" class="action-btn primary">Add to Download Queue</button>
                <button id="toggle-favorites" class="action-btn">⭐ Show Favorites</button>
            </div>
        </div>
        ''')

        return model_preview_html

    def create_download_queue_manager(self):
        """Create download queue management interface."""
        
        queue_html = self.factory.create_html('''
        <div id="download-queue-container" class="queue-container">
            <div class="queue-header">
                <h3>📥 Download Queue Manager</h3>
                <div class="queue-controls">
                    <button id="start-queue" class="queue-btn primary">Start Downloads</button>
                    <button id="pause-queue" class="queue-btn">Pause</button>
                    <button id="clear-queue" class="queue-btn danger">Clear Queue</button>
                </div>
            </div>
            
            <div class="queue-stats">
                <div class="stat">
                    <span class="stat-label">Items:</span>
                    <span id="queue-count">0</span>
                </div>
                <div class="stat">
                    <span class="stat-label">Total Size:</span>
                    <span id="queue-size">0 GB</span>
                </div>
                <div class="stat">
                    <span class="stat-label">ETA:</span>
                    <span id="queue-eta">--:--</span>
                </div>
            </div>
            
            <div id="queue-list" class="queue-list">
                <!-- Queue items will appear here -->
            </div>
            
            <div class="progress-container">
                <div class="progress-label">Overall Progress</div>
                <div class="progress-bar">
                    <div id="overall-progress" class="progress-fill"></div>
                </div>
                <div class="progress-text">
                    <span id="progress-percent">0%</span>
                    <span id="progress-speed">0 MB/s</span>
                </div>
            </div>
        </div>
        ''')

        return queue_html

    def create_advanced_configuration(self):
        """Create advanced configuration panel."""
        
        config_html = self.factory.create_html('''
        <div id="advanced-config-container" class="config-container">
            <div class="config-header">
                <h3>⚙️ Advanced Configuration</h3>
                <button id="toggle-config" class="toggle-btn">Show/Hide</button>
            </div>
            
            <div id="config-content" class="config-content" style="display: none;">
                <div class="config-section">
                    <h4>Download Settings</h4>
                    <div class="config-row">
                        <label>Concurrent Downloads:</label>
                        <input type="range" id="concurrent-downloads" min="1" max="8" value="3">
                        <span id="concurrent-value">3</span>
                    </div>
                    <div class="config-row">
                        <label>Download Speed Limit (MB/s):</label>
                        <input type="number" id="speed-limit" min="0" max="1000" value="0" placeholder="0 = unlimited">
                    </div>
                    <div class="config-row">
                        <label>Auto-retry Failed Downloads:</label>
                        <input type="checkbox" id="auto-retry" checked>
                    </div>
                </div>
                
                <div class="config-section">
                    <h4>Model Management</h4>
                    <div class="config-row">
                        <label>Auto-download Previews:</label>
                        <input type="checkbox" id="auto-preview" checked>
                    </div>
                    <div class="config-row">
                        <label>Organize by Model Type:</label>
                        <input type="checkbox" id="organize-by-type" checked>
                    </div>
                    <div class="config-row">
                        <label>Check for Model Updates:</label>
                        <input type="checkbox" id="check-updates">
                    </div>
                </div>
                
                <div class="config-section">
                    <h4>Storage Management</h4>
                    <div class="config-row">
                        <label>Auto-cleanup Old Versions:</label>
                        <input type="checkbox" id="auto-cleanup">
                    </div>
                    <div class="config-row">
                        <label>Compress Unused Models:</label>
                        <input type="checkbox" id="compress-models">
                    </div>
                    <div class="config-row">
                        <label>Storage Location:</label>
                        <select id="storage-location">
                            <option value="default">Default</option>
                            <option value="gdrive">Google Drive</option>
                            <option value="custom">Custom Path</option>
                        </select>
                    </div>
                </div>
            </div>
        </div>
        ''')

        return config_html

    def create_model_comparison_tool(self):
        """Create model comparison interface."""
        
        comparison_html = self.factory.create_html('''
        <div id="comparison-container" class="comparison-container">
            <div class="comparison-header">
                <h3>🔍 Model Comparison Tool</h3>
                <button id="start-comparison" class="comparison-btn">Compare Selected</button>
            </div>
            
            <div id="comparison-content" class="comparison-content">
                <div class="comparison-grid">
                    <div class="comparison-item" id="model-a">
                        <h4>Model A</h4>
                        <div class="model-preview-img"></div>
                        <div class="model-details">
                            <div class="detail-row">
                                <span class="label">Type:</span>
                                <span class="value">--</span>
                            </div>
                            <div class="detail-row">
                                <span class="label">Size:</span>
                                <span class="value">--</span>
                            </div>
                            <div class="detail-row">
                                <span class="label">Base:</span>
                                <span class="value">--</span>
                            </div>
                            <div class="detail-row">
                                <span class="label">Tags:</span>
                                <span class="value">--</span>
                            </div>
                        </div>
                    </div>
                    
                    <div class="comparison-vs">VS</div>
                    
                    <div class="comparison-item" id="model-b">
                        <h4>Model B</h4>
                        <div class="model-preview-img"></div>
                        <div class="model-details">
                            <div class="detail-row">
                                <span class="label">Type:</span>
                                <span class="value">--</span>
                            </div>
                            <div class="detail-row">
                                <span class="label">Size:</span>
                                <span class="value">--</span>
                            </div>
                            <div class="detail-row">
                                <span class="label">Base:</span>
                                <span class="value">--</span>
                            </div>
                            <div class="detail-row">
                                <span class="label">Tags:</span>
                                <span class="value">--</span>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="comparison-summary">
                    <h4>Compatibility Analysis</h4>
                    <div id="compatibility-result" class="compatibility-result">
                        Select two models to compare compatibility
                    </div>
                </div>
            </div>
        </div>
        ''')

        return comparison_html

    def create_batch_operations_panel(self):
        """Create batch operations interface."""
        
        batch_html = self.factory.create_html('''
        <div id="batch-container" class="batch-container">
            <div class="batch-header">
                <h3>⚡ Batch Operations</h3>
                <div class="batch-mode-toggle">
                    <label class="toggle-switch">
                        <input type="checkbox" id="batch-mode-enabled">
                        <span class="toggle-slider"></span>
                        <span class="toggle-label">Batch Mode</span>
                    </label>
                </div>
            </div>
            
            <div id="batch-content" class="batch-content" style="display: none;">
                <div class="batch-section">
                    <h4>Bulk Download</h4>
                    <div class="batch-row">
                        <button id="download-all-models" class="batch-btn">Download All Models</button>
                        <button id="download-by-type" class="batch-btn">Download by Type</button>
                        <button id="download-favorites" class="batch-btn">Download Favorites</button>
                    </div>
                </div>
                
                <div class="batch-section">
                    <h4>Model Management</h4>
                    <div class="batch-row">
                        <button id="organize-models" class="batch-btn">Organize Models</button>
                        <button id="check-duplicates" class="batch-btn">Find Duplicates</button>
                        <button id="verify-integrity" class="batch-btn">Verify Integrity</button>
                    </div>
                </div>
                
                <div class="batch-section">
                    <h4>Cleanup Operations</h4>
                    <div class="batch-row">
                        <button id="clean-temp" class="batch-btn">Clean Temp Files</button>
                        <button id="remove-broken" class="batch-btn">Remove Broken</button>
                        <button id="compress-old" class="batch-btn">Compress Old</button>
                    </div>
                </div>
                
                <div class="batch-progress">
                    <div class="progress-label">Batch Operation Progress</div>
                    <div class="progress-bar">
                        <div id="batch-progress" class="progress-fill"></div>
                    </div>
                    <div id="batch-status" class="batch-status">Ready</div>
                </div>
            </div>
        </div>
        ''')

        return batch_html

    def create_settings_manager(self):
        """Create enhanced settings management."""
        
        settings_html = self.factory.create_html('''
        <div id="settings-manager" class="settings-manager">
            <div class="settings-header">
                <h3>💾 Settings Manager</h3>
                <div class="settings-actions">
                    <button id="export-settings" class="settings-btn">📤 Export</button>
                    <button id="import-settings" class="settings-btn">📥 Import</button>
                    <button id="reset-settings" class="settings-btn danger">🔄 Reset</button>
                </div>
            </div>
            
            <div class="settings-presets">
                <h4>Quick Presets</h4>
                <div class="preset-buttons">
                    <button class="preset-btn" data-preset="beginner">👶 Beginner</button>
                    <button class="preset-btn" data-preset="intermediate">🧑‍🎨 Intermediate</button>
                    <button class="preset-btn" data-preset="advanced">🔬 Advanced</button>
                    <button class="preset-btn" data-preset="professional">💼 Professional</button>
                </div>
            </div>
            
            <div class="settings-backup">
                <h4>Backup & Restore</h4>
                <div class="backup-row">
                    <button id="create-backup" class="backup-btn">Create Backup</button>
                    <select id="backup-list" class="backup-select">
                        <option value="">Select backup...</option>
                    </select>
                    <button id="restore-backup" class="backup-btn">Restore</button>
                </div>
            </div>
            
            <div class="settings-sync">
                <h4>Cloud Sync</h4>
                <div class="sync-row">
                    <label>Sync to Google Drive:</label>
                    <input type="checkbox" id="sync-gdrive">
                    <button id="sync-now" class="sync-btn">Sync Now</button>
                </div>
            </div>
        </div>
        ''')

        return settings_html

# Initialize Enhanced Widget Manager
ewm = EnhancedWidgetManager()
factory = ewm.factory

# Create all enhanced components
enhanced_model_selector = ewm.create_enhanced_model_selector()
download_queue_manager = ewm.create_download_queue_manager()
advanced_configuration = ewm.create_advanced_configuration()
model_comparison_tool = ewm.create_model_comparison_tool()
batch_operations_panel = ewm.create_batch_operations_panel()
settings_manager = ewm.create_settings_manager()

# Create tabbed interface for organization
tabbed_interface = factory.create_html('''
<div class="enhanced-ui-container">
    <div class="tab-navigation">
        <button class="tab-btn active" data-tab="models">🎨 Models</button>
        <button class="tab-btn" data-tab="queue">📥 Queue</button>
        <button class="tab-btn" data-tab="config">⚙️ Config</button>
        <button class="tab-btn" data-tab="compare">🔍 Compare</button>
        <button class="tab-btn" data-tab="batch">⚡ Batch</button>
        <button class="tab-btn" data-tab="settings">💾 Settings</button>
    </div>
    
    <div class="tab-content">
        <div id="tab-models" class="tab-panel active"></div>
        <div id="tab-queue" class="tab-panel"></div>
        <div id="tab-config" class="tab-panel"></div>
        <div id="tab-compare" class="tab-panel"></div>
        <div id="tab-batch" class="tab-panel"></div>
        <div id="tab-settings" class="tab-panel"></div>
    </div>
</div>
''')

# Enhanced notification system
notification_system = factory.create_html('''
<div id="notification-container" class="notification-container">
    <!-- Notifications will appear here -->
</div>
''')

# Main layout with enhanced features
main_enhanced_layout = factory.create_vbox([
    tabbed_interface,
    notification_system
], class_names=['enhanced-main-container'])

# Display the enhanced interface
factory.display(main_enhanced_layout)

print("🚀 Enhanced Widget System Loaded!")
print("✨ Features: Visual Model Selector, Download Queue, Batch Operations, Model Comparison")

// Enhanced JavaScript for Advanced Widget System
// Save as: JS/enhanced-widgets.js

class EnhancedWidgetManager {
    constructor() {
        this.selectedModels = new Set();
        this.downloadQueue = [];
        this.modelCache = new Map();
        this.favorites = new Set();
        this.currentFilter = {
            search: '',
            type: 'all',
            style: 'all'
        };
        this.downloadProgress = new Map();
        this.settings = this.loadSettings();
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.setupTabNavigation();
        this.loadModelData();
        this.setupKeyboardShortcuts();
        this.setupNotificationSystem();
        this.initializeWebSockets();
    }

    // Tab Navigation System
    setupTabNavigation() {
        const tabButtons = document.querySelectorAll('.tab-btn');
        const tabPanels = document.querySelectorAll('.tab-panel');
        
        tabButtons.forEach(button => {
            button.addEventListener('click', () => {
                const targetTab = button.dataset.tab;
                
                // Remove active class from all tabs
                tabButtons.forEach(btn => btn.classList.remove('active'));
                tabPanels.forEach(panel => panel.classList.remove('active'));
                
                // Add active class to clicked tab
                button.classList.add('active');
                document.getElementById(`tab-${targetTab}`).classList.add('active');
                
                // Load tab content
                this.loadTabContent(targetTab);
            });
        });
    }

    loadTabContent(tabName) {
        const panel = document.getElementById(`tab-${tabName}`);
        
        switch(tabName) {
            case 'models':
                this.renderModelSelector(panel);
                break;
            case 'queue':
                this.renderDownloadQueue(panel);
                break;
            case 'config':
                this.renderAdvancedConfig(panel);
                break;
            case 'compare':
                this.renderModelComparison(panel);
                break;
            case 'batch':
                this.renderBatchOperations(panel);
                break;
            case 'settings':
                this.renderSettingsManager(panel);
                break;
        }
    }

    // Enhanced Model Selector
    renderModelSelector(container) {
        const modelSelector = document.getElementById('model-preview-container');
        if (modelSelector) {
            container.appendChild(modelSelector);
            this.setupModelFilters();
            this.setupModelGrid();
            this.setupModelActions();
        }
    }

    setupModelFilters() {
        const searchInput = document.getElementById('model-search');
        const typeFilter = document.getElementById('model-type-filter');
        const styleFilter = document.getElementById('model-style-filter');
        const clearFilters = document.getElementById('clear-filters');

        // Debounced search
        let searchTimeout;
        searchInput?.addEventListener('input', (e) => {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                this.currentFilter.search = e.target.value.toLowerCase();
                this.filterModels();
            }, 300);
        });

        typeFilter?.addEventListener('change', (e) => {
            this.currentFilter.type = e.target.value;
            this.filterModels();
        });

        styleFilter?.addEventListener('change', (e) => {
            this.currentFilter.style = e.target.value;
            this.filterModels();
        });

        clearFilters?.addEventListener('click', () => {
            searchInput.value = '';
            typeFilter.value = 'all';
            styleFilter.value = 'all';
            this.currentFilter = { search: '', type: 'all', style: 'all' };
            this.filterModels();
        });
    }

    setupModelGrid() {
        const modelGrid = document.getElementById('model-grid');
        if (!modelGrid) return;

        // Load and render models
        this.loadModelData().then(models => {
            this.renderModelCards(models, modelGrid);
        });
    }

    async loadModelData() {
        // Simulate loading model data (in real implementation, this would fetch from API)
        if (this.modelCache.size > 0) return Array.from(this.modelCache.values());

        const sampleModels = [
            {
                id: 'model_1',
                name: 'Realistic Vision V6.0',
                type: 'checkpoint',
                style: 'realistic',
                size: '2.1 GB',
                base: 'SD 1.5',
                preview: 'https://via.placeholder.com/280x150/4f46e5/ffffff?text=Realistic+Vision',
                tags: ['realistic', 'photography', 'portraits'],
                rating: 4.8,
                downloads: 125000,
                civitaiUrl: 'https://civitai.com/models/4201'
            },
            {
                id: 'model_2',
                name: 'Anime Pastel Dream',
                type: 'checkpoint',
                style: 'anime',
                size: '2.1 GB',
                base: 'SD 1.5',
                preview: 'https://via.placeholder.com/280x150/8b5cf6/ffffff?text=Anime+Pastel',
                tags: ['anime', 'pastel', 'cute'],
                rating: 4.6,
                downloads: 98000,
                civitaiUrl: 'https://civitai.com/models/1234'
            },
            {
                id: 'model_3',
                name: 'DreamShaper XL',
                type: 'checkpoint',
                style: 'artistic',
                size: '6.4 GB',
                base: 'SDXL',
                preview: 'https://via.placeholder.com/280x150/06b6d4/ffffff?text=DreamShaper+XL',
                tags: ['artistic', 'versatile', 'xl'],
                rating: 4.9,
                downloads: 200000,
                civitaiUrl: 'https://civitai.com/models/112902'
            },
            {
                id: 'model_4',
                name: 'Detail Tweaker LoRA',
                type: 'lora',
                style: 'enhancement',
                size: '144 MB',
                base: 'SD 1.5',
                preview: 'https://via.placeholder.com/280x150/10b981/ffffff?text=Detail+Tweaker',
                tags: ['lora', 'detail', 'enhancement'],
                rating: 4.7,
                downloads: 75000,
                civitaiUrl: 'https://civitai.com/models/5678'
            }
        ];

        // Cache the models
        sampleModels.forEach(model => this.modelCache.set(model.id, model));
        return sampleModels;
    }

    renderModelCards(models, container) {
        container.innerHTML = '';
        
        models.forEach(model => {
            const card = this.createModelCard(model);
            container.appendChild(card);
        });

        this.updateModelStats(models);
    }

    createModelCard(model) {
        const card = document.createElement('div');
        card.className = 'model-card';
        card.dataset.modelId = model.id;
        card.dataset.type = model.type;
        card.dataset.style = model.style;

        card.innerHTML = `
            <div class="model-preview-img">
                <img src="${model.preview}" alt="${model.name}" loading="lazy">
                <div class="model-favorite" data-model-id="${model.id}">
                    ${this.favorites.has(model.id) ? '⭐' : '☆'}
                </div>
            </div>
            <div class="model-info">
                <div class="model-title">${model.name}</div>
                <div class="model-tags">
                    <span class="model-tag type-${model.type}">${model.type}</span>
                    ${model.tags.map(tag => `<span class="model-tag style-${tag}">${tag}</span>`).join('')}
                </div>
                <div class="model-stats-row">
                    <span>⭐ ${model.rating}</span>
                    <span>📥 ${this.formatNumber(model.downloads)}</span>
                    <span>💾 ${model.size}</span>
                </div>
            </div>
        `;

        // Add event listeners
        card.addEventListener('click', (e) => {
            if (!e.target.classList.contains('model-favorite')) {
                this.toggleModelSelection(model.id);
            }
        });

        const favoriteBtn = card.querySelector('.model-favorite');
        favoriteBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            this.toggleFavorite(model.id);
        });

        return card;
    }

    toggleModelSelection(modelId) {
        if (this.selectedModels.has(modelId)) {
            this.selectedModels.delete(modelId);
        } else {
            this.selectedModels.add(modelId);
        }
        
        this.updateModelCardSelection(modelId);
        this.updateModelStats();
    }

    updateModelCardSelection(modelId) {
        const card = document.querySelector(`[data-model-id="${modelId}"]`);
        if (card) {
            card.classList.toggle('selected', this.selectedModels.has(modelId));
        }
    }

    toggleFavorite(modelId) {
        if (this.favorites.has(modelId)) {
            this.favorites.delete(modelId);
        } else {
            this.favorites.add(modelId);
        }
        
        const favoriteBtn = document.querySelector(`[data-model-id="${modelId}"] .model-favorite`);
        if (favoriteBtn) {
            favoriteBtn.textContent = this.favorites.has(modelId) ? '⭐' : '☆';
        }
        
        this.saveFavorites();
    }

    filterModels() {
        const cards = document.querySelectorAll('.model-card');
        let visibleCount = 0;
        
        cards.forEach(card => {
            const modelName = card.querySelector('.model-title').textContent.toLowerCase();
            const modelType = card.dataset.type;
            const modelStyle = card.dataset.style;
            
            const matchesSearch = !this.currentFilter.search || modelName.includes(this.currentFilter.search);
            const matchesType = this.currentFilter.type === 'all' || modelType === this.currentFilter.type;
            const matchesStyle = this.currentFilter.style === 'all' || modelStyle === this.currentFilter.style;
            
            const isVisible = matchesSearch && matchesType && matchesStyle;
            card.style.display = isVisible ? 'block' : 'none';
            
            if (isVisible) visibleCount++;
        });
        
        this.updateVisibleModelCount(visibleCount);
    }

    updateModelStats(models = null) {
        const totalCount = models ? models.length : this.modelCache.size;
        const selectedCount = this.selectedModels.size;
        const selectedSize = this.calculateSelectedSize();
        
        const totalElement = document.getElementById('total-models');
        const selectedElement = document.getElementById('selected-count');
        const sizeElement = document.getElementById('download-size');
        
        if (totalElement) totalElement.textContent = `${totalCount} models`;
        if (selectedElement) selectedElement.textContent = `${selectedCount} selected`;
        if (sizeElement) sizeElement.textContent = `${selectedSize.toFixed(1)} GB`;
    }

    updateVisibleModelCount(count) {
        const totalElement = document.getElementById('total-models');
        if (totalElement) {
            totalElement.textContent = `${count} models visible`;
        }
    }

    calculateSelectedSize() {
        let totalSize = 0;
        this.selectedModels.forEach(modelId => {
            const model = this.modelCache.get(modelId);
            if (model) {
                const sizeStr = model.size.replace(/[^\d.]/g, '');
                const size = parseFloat(sizeStr);
                if (model.size.includes('MB')) {
                    totalSize += size / 1024;
                } else {
                    totalSize += size;
                }
            }
        });
        return totalSize;
    }

    setupModelActions() {
        const selectAllBtn = document.getElementById('select-all');
        const clearSelectionBtn = document.getElementById('clear-selection');
        const addToQueueBtn = document.getElementById('add-to-queue');
        const toggleFavoritesBtn = document.getElementById('toggle-favorites');

        selectAllBtn?.addEventListener('click', () => {
            const visibleCards = document.querySelectorAll('.model-card:not([style*="display: none"])');
            visibleCards.forEach(card => {
                const modelId = card.dataset.modelId;
                this.selectedModels.add(modelId);
                this.updateModelCardSelection(modelId);
            });
            this.updateModelStats();
        });

        clearSelectionBtn?.addEventListener('click', () => {
            this.selectedModels.clear();
            document.querySelectorAll('.model-card').forEach(card => {
                card.classList.remove('selected');
            });
            this.updateModelStats();
        });

        addToQueueBtn?.addEventListener('click', () => {
            this.addSelectedToQueue();
        });

        toggleFavoritesBtn?.addEventListener('click', () => {
            this.toggleFavoritesView();
        });
    }

    // Download Queue Management
    renderDownloadQueue(container) {
        const queueManager = document.getElementById('download-queue-container');
        if (queueManager) {
            container.appendChild(queueManager);
            this.setupQueueControls();
            this.updateQueueDisplay();
        }
    }

    setupQueueControls() {
        const startBtn = document.getElementById('start-queue');
        const pauseBtn = document.getElementById('pause-queue');
        const clearBtn = document.getElementById('clear-queue');

        startBtn?.addEventListener('click', () => this.startDownloadQueue());
        pauseBtn?.addEventListener('click', () => this.pauseDownloadQueue());
        clearBtn?.addEventListener('click', () => this.clearDownloadQueue());
    }

    addSelectedToQueue() {
        this.selectedModels.forEach(modelId => {
            const model = this.modelCache.get(modelId);
            if (model && !this.downloadQueue.find(item => item.id === modelId)) {
                this.downloadQueue.push({
                    id: modelId,
                    name: model.name,
                    url: model.civitaiUrl,
                    size: model.size,
                    status: 'queued',
                    progress: 0
                });
            }
        });
        
        this.updateQueueDisplay();
        this.showNotification('Added selected models to download queue', 'success');
    }

    updateQueueDisplay() {
        const queueList = document.getElementById('queue-list');
        const queueCount = document.getElementById('queue-count');
        const queueSize = document.getElementById('queue-size');
        
        if (!queueList) return;
        
        queueList.innerHTML = '';
        
        this.downloadQueue.forEach(item => {
            const queueItem = document.createElement('div');
            queueItem.className = 'queue-item';
            queueItem.innerHTML = `
                <div class="queue-item-status">
                    ${this.getStatusIcon(item.status)}
                </div>
                <div class="queue-item-info">
                    <div class="queue-item-title">${item.name}</div>
                    <div class="queue-item-details">${item.size} • ${item.status}</div>
                </div>
                <div class="queue-item-progress">${item.progress}%</div>
            `;
            queueList.appendChild(queueItem);
        });
        
        if (queueCount) queueCount.textContent = this.downloadQueue.length;
        if (queueSize) {
            const totalSize = this.downloadQueue.reduce((total, item) => {
                const size = parseFloat(item.size.replace(/[^\d.]/g, ''));
                return total + (item.size.includes('MB') ? size / 1024 : size);
            }, 0);
            queueSize.textContent = `${totalSize.toFixed(1)} GB`;
        }
    }

    getStatusIcon(status) {
        const icons = {
            'queued': '⏳',
            'downloading': '⬇️',
            'completed': '✅',
            'error': '❌',
            'paused': '⏸️'
        };
        return icons[status] || '❓';
    }

    startDownloadQueue() {
        this.showNotification('Starting download queue...', 'info');
        // Implement download logic
        this.processDownloadQueue();
    }

    async processDownloadQueue() {
        const queuedItems = this.downloadQueue.filter(item => item.status === 'queued');
        
        for (const item of queuedItems) {
            item.status = 'downloading';
            this.updateQueueDisplay();
            
            try {
                await this.downloadModel(item);
                item.status = 'completed';
                item.progress = 100;
            } catch (error) {
                item.status = 'error';
                this.showNotification(`Download failed: ${item.name}`, 'error');
            }
            
            this.updateQueueDisplay();
        }
    }

    async downloadModel(item) {
        // Simulate download progress
        return new Promise((resolve) => {
            let progress = 0;
            const interval = setInterval(() => {
                progress += Math.random() * 10;
                item.progress = Math.min(progress, 100);
                this.updateQueueDisplay();
                
                if (progress >= 100) {
                    clearInterval(interval);
                    resolve();
                }
            }, 500);
        });
    }

    // Advanced Configuration
    renderAdvancedConfig(container) {
        const configContainer = document.getElementById('advanced-config-container');
        if (configContainer) {
            container.appendChild(configContainer);
            this.setupAdvancedConfig();
        }
    }

    setupAdvancedConfig() {
        const toggleBtn = document.getElementById('toggle-config');
        const configContent = document.getElementById('config-content');
        
        toggleBtn?.addEventListener('click', () => {
            const isHidden = configContent.style.display === 'none';
            configContent.style.display = isHidden ? 'block' : 'none';
            toggleBtn.textContent = isHidden ? 'Hide' : 'Show';
        });

        // Setup config controls
        this.setupConfigControls();
    }

    setupConfigControls() {
        const concurrentSlider = document.getElementById('concurrent-downloads');
        const concurrentValue = document.getElementById('concurrent-value');
        
        concurrentSlider?.addEventListener('input', (e) => {
            concurrentValue.textContent = e.target.value;
            this.settings.concurrentDownloads = parseInt(e.target.value);
            this.saveSettings();
        });
        
        // Setup other config controls...
    }

    // Model Comparison
    renderModelComparison(container) {
        const comparisonContainer = document.getElementById('comparison-container');
        if (comparisonContainer) {
            container.appendChild(comparisonContainer);
            this.setupModelComparison();
        }
    }

    setupModelComparison() {
        const startComparisonBtn = document.getElementById('start-comparison');
        
        startComparisonBtn?.addEventListener('click', () => {
            const selected = Array.from(this.selectedModels);
            if (selected.length < 2) {
                this.showNotification('Please select at least 2 models to compare', 'warning');
                return;
            }
            
            this.compareModels(selected.slice(0, 2));
        });
    }

    compareModels(modelIds) {
        const [modelA, modelB] = modelIds.map(id => this.modelCache.get(id));
        
        if (!modelA || !modelB) return;
        
        // Update comparison display
        this.updateComparisonDisplay('model-a', modelA);
        this.updateComparisonDisplay('model-b', modelB);
        
        // Analyze compatibility
        this.analyzeCompatibility(modelA, modelB);
    }

    updateComparisonDisplay(containerId, model) {
        const container = document.getElementById(containerId);
        if (!container) return;
        
        const details = container.querySelectorAll('.detail-row .value');
        details[0].textContent = model.type;
        details[1].textContent = model.size;
        details[2].textContent = model.base;
        details[3].textContent = model.tags.join(', ');
        
        const previewImg = container.querySelector('.model-preview-img');
        previewImg.style.backgroundImage = `url(${model.preview})`;
    }

    analyzeCompatibility(modelA, modelB) {
        const result = document.getElementById('compatibility-result');
        if (!result) return;
        
        let compatibility = 'Unknown';
        let details = '';
        
        if (modelA.base === modelB.base) {
            compatibility = 'Compatible';
            details = `Both models use ${modelA.base} architecture and can be used together.`;
        } else {
            compatibility = 'Incompatible';
            details = `Models use different architectures (${modelA.base} vs ${modelB.base}).`;
        }
        
        result.innerHTML = `
            <div class="compatibility-status ${compatibility.toLowerCase()}">${compatibility}</div>
            <div class="compatibility-details">${details}</div>
        `;
    }

    // Batch Operations
    renderBatchOperations(container) {
        const batchContainer = document.getElementById('batch-container');
        if (batchContainer) {
            container.appendChild(batchContainer);
            this.setupBatchOperations();
        }
    }

    setupBatchOperations() {
        const batchModeToggle = document.getElementById('batch-mode-enabled');
        const batchContent = document.getElementById('batch-content');
        
        batchModeToggle?.addEventListener('change', (e) => {
            batchContent.style.display = e.target.checked ? 'block' : 'none';
        });
        
        // Setup batch operation buttons
        this.setupBatchButtons();
    }

    setupBatchButtons() {
        const buttons = {
            'download-all-models': () => this.batchDownloadAll(),
            'download-by-type': () => this.batchDownloadByType(),
            'download-favorites': () => this.batchDownloadFavorites(),
            'organize-models': () => this.organizeModels(),
            'check-duplicates': () => this.checkDuplicates(),
            'verify-integrity': () => this.verifyIntegrity()
        };
        
        Object.entries(buttons).forEach(([id, handler]) => {
            const button = document.getElementById(id);
            button?.addEventListener('click', handler);
        });
    }

    // Settings Manager
    renderSettingsManager(container) {
        const settingsManager = document.getElementById('settings-manager');
        if (settingsManager) {
            container.appendChild(settingsManager);
            this.setupSettingsManager();
        }
    }

    setupSettingsManager() {
        const exportBtn = document.getElementById('export-settings');
        const importBtn = document.getElementById('import-settings');
        const resetBtn = document.getElementById('reset-settings');
        
        exportBtn?.addEventListener('click', () => this.exportSettings());
        importBtn?.addEventListener('click', () => this.importSettings());
        resetBtn?.addEventListener('click', () => this.resetSettings());
        
        // Setup preset buttons
        const presetBtns = document.querySelectorAll('.preset-btn');
        presetBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                const preset = btn.dataset.preset;
                this.applyPreset(preset);
            });
        });
    }

    // Utility Functions
    formatNumber(num) {
        if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
        if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
        return num.toString();
    }

    showNotification(message, type = 'info') {
        const container = document.querySelector('.notification-container');
        if (!container) return;
        
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.innerHTML = `
            <div class="notification-content">${message}</div>
            <button class="notification-close">×</button>
        `;
        
        container.appendChild(notification);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            notification.style.transform = 'translateX(450px)';
            setTimeout(() => notification.remove(), 300);
        }, 5000);
        
        // Manual close
        notification.querySelector('.notification-close').addEventListener('click', () => {
            notification.style.transform = 'translateX(450px)';
            setTimeout(() => notification.remove(), 300);
        });
    }

    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Ctrl+A - Select all visible models
            if (e.ctrlKey && e.key === 'a' && e.target.tagName !== 'INPUT') {
                e.preventDefault();
                document.getElementById('select-all')?.click();
            }
            
            // Escape - Clear selection
            if (e.key === 'Escape') {
                document.getElementById('clear-selection')?.click();
            }
            
            // Ctrl+D - Add to download queue
            if (e.ctrlKey && e.key === 'd') {
                e.preventDefault();
                document.getElementById('add-to-queue')?.click();
            }
        });
    }

    setupNotificationSystem() {
        // Create notification container if it doesn't exist
        if (!document.querySelector('.notification-container')) {
            const container = document.createElement('div');
            container.className = 'notification-container';
            document.body.appendChild(container);
        }
    }

    initializeWebSockets() {
        // Initialize WebSocket connection for real-time updates
        // This would connect to a backend service in a real implementation
        console.log('WebSocket connection initialized for real-time updates');
    }

    // Settings Management
    loadSettings() {
        const defaults = {
            concurrentDownloads: 3,
            autoPreview: true,
            organizeByType: true,
            autoCleanup: false,
            storageLocation: 'default'
        };
        
        try {
            const saved = localStorage.getItem('enhancedWidgetSettings');
            return saved ? { ...defaults, ...JSON.parse(saved) } : defaults;
        } catch {
            return defaults;
        }
    }

    saveSettings() {
        try {
            localStorage.setItem('enhancedWidgetSettings', JSON.stringify(this.settings));
        } catch (error) {
            console.warn('Could not save settings:', error);
        }
    }

    saveFavorites() {
        try {
            localStorage.setItem('modelFavorites', JSON.stringify(Array.from(this.favorites)));
        } catch (error) {
            console.warn('Could not save favorites:', error);
        }
    }

    loadFavorites() {
        try {
            const saved = localStorage.getItem('modelFavorites');
            if (saved) {
                this.favorites = new Set(JSON.parse(saved));
            }
        } catch (error) {
            console.warn('Could not load favorites:', error);
        }
    }

    exportSettings() {
        const data = {
            settings: this.settings,
            favorites: Array.from(this.favorites),
            selectedModels: Array.from(this.selectedModels),
            downloadQueue: this.downloadQueue
        };
        
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `enhanced-widget-settings-${new Date().toISOString().split('T')[0]}.json`;
        a.click();
        URL.revokeObjectURL(url);
        
        this.showNotification('Settings exported successfully!', 'success');
    }

    // Event Listeners Setup
    setupEventListeners() {
        // Initialize tab content
        this.loadTabContent('models');
        
        // Load favorites
        this.loadFavorites();
        
        // Setup global error handling
        window.addEventListener('error', (e) => {
            console.error('Global error:', e.error);
            this.showNotification('An error occurred. Please check the console.', 'error');
        });
    }
}

// Initialize the Enhanced Widget Manager when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.enhancedWidgetManager = new EnhancedWidgetManager();
    console.log('Enhanced Widget Manager initialized');
});

// Export for global access
window.EnhancedWidgetManager = EnhancedWidgetManager;

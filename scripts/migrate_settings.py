# Migration script for existing LSDAI settings
import json_utils as js
import json
from pathlib import Path

def migrate_existing_settings():
    """Migrate existing LSDAI settings to enhanced format"""
    
    print("🔄 Migrating LSDAI settings to enhanced format...")
    
    # Read existing settings
    try:
        existing_settings = js.read(js.SETTINGS_PATH)
        widgets_settings = existing_settings.get('WIDGETS', {})
    except:
        print("⚠️  No existing settings found")
        return
        
    # Create enhanced configuration
    enhanced_config = {
        "version": "2.0.0",
        "migrated_from": "original_lsdai",
        "migration_date": time.time(),
        
        # Preserve original settings
        "original_settings": widgets_settings,
        
        # Enhanced module configuration
        "modules": {
            "enhanced_download_manager": {
                "enabled": True,
                "concurrent_downloads": 3,
                "auto_retry": True
            },
            "enhanced_model_manager": {
                "enabled": True,
                "auto_discovery": True,
                "cache_duration": 3600
            },
            "notification_system": {
                "enabled": True,
                "channels": ["browser"]
            },
            "advanced_logging": {
                "enabled": True,
                "log_level": "INFO"
            }
        },
        
        # UI preferences
        "ui_enhancements": {
            "enhanced_widgets": True,
            "visual_model_selector": True,
            "download_queue_ui": True,
            "dark_theme": True
        },
        
        # Performance settings based on existing WebUI selection
        "performance": {
            "auto_optimization": True,
            "resource_monitoring": True,
            "webui_type": widgets_settings.get('change_webui', 'automatic1111')
        }
    }
    
    # Save enhanced configuration
    config_file = Path('data/enhancement_config.json')
    config_file.parent.mkdir(exist_ok=True)
    
    with open(config_file, 'w') as f:
        json.dump(enhanced_config, f, indent=2)
        
    print(f"✅ Settings migrated to {config_file}")
    print("🔧 Run the configuration wizard to customize: python -m scripts.master_integration --wizard")

if __name__ == "__main__":
    migrate_existing_settings()

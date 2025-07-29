# Automated Setup and Installation Script for LSDAI Enhancement Suite
# Save as: setup_enhancements.py

import subprocess
import urllib.request
import zipfile
import shutil
import json
import sys
import os
from pathlib import Path
from typing import List, Dict, Any

class LSDAIEnhancementInstaller:
    """Automated installer for LSDAI Enhancement Suite"""
    
    def __init__(self):
        self.base_path = Path(os.getcwd())
        self.enhancement_version = "2.0.0"
        self.required_packages = [
            'requests>=2.28.0',
            'psutil>=5.9.0',
            'gitpython>=3.1.0',
            'pillow>=9.0.0',
            'numpy>=1.21.0',
            'opencv-python>=4.5.0',
            'google-auth>=2.0.0',
            'google-auth-oauthlib>=0.5.0',
            'google-api-python-client>=2.0.0'
        ]
        self.optional_packages = [
            'GPUtil>=1.4.0',  # For GPU monitoring
            'matplotlib>=3.5.0',  # For visualization
            'pandas>=1.4.0',  # For data analysis
            'scikit-learn>=1.1.0'  # For ML metrics
        ]
        
    def check_environment(self) -> Dict[str, Any]:
        """Check if environment is suitable for installation"""
        print("🔍 Checking environment compatibility...")
        
        status = {
            'python_version': sys.version_info,
            'python_compatible': sys.version_info >= (3, 8),
            'current_directory': str(self.base_path),
            'is_colab': 'google.colab' in sys.modules,
            'is_kaggle': 'kaggle' in os.environ.get('KAGGLE_KERNEL_RUN_TYPE', ''),
            'has_git': False,
            'has_existing_lsdai': False,
            'has_webui': False,
            'platform': sys.platform
        }
        
        # Check for git
        try:
            subprocess.run(['git', '--version'], capture_output=True, check=True)
            status['has_git'] = True
        except (subprocess.CalledProcessError, FileNotFoundError):
            status['has_git'] = False
            
        # Check for existing LSDAI
        lsdai_indicators = [
            'scripts/setup.py',
            'scripts/widgets-en.py',
            'scripts/downloading-en.py',
            'scripts/launch.py'
        ]
        
        status['has_existing_lsdai'] = any(
            (self.base_path / indicator).exists() 
            for indicator in lsdai_indicators
        )
        
        # Check for WebUI
        webui_paths = [
            'stable-diffusion-webui',
            'ComfyUI',
            'webui.py',
            'launch.py'
        ]
        
        status['has_webui'] = any(
            (self.base_path / path).exists() 
            for path in webui_paths
        )
        
        return status
        
    def install_dependencies(self, include_optional: bool = True) -> bool:
        """Install required Python packages"""
        print("📦 Installing Python dependencies...")
        
        packages_to_install = self.required_packages.copy()
        if include_optional:
            packages_to_install.extend(self.optional_packages)
            
        failed_packages = []
        
        for package in packages_to_install:
            try:
                print(f"  Installing {package}...")
                subprocess.run([
                    sys.executable, '-m', 'pip', 'install', package
                ], check=True, capture_output=True)
                print(f"  ✅ {package}")
            except subprocess.CalledProcessError as e:
                print(f"  ❌ Failed to install {package}: {e}")
                failed_packages.append(package)
                
        if failed_packages:
            print(f"⚠️  Failed to install some packages: {failed_packages}")
            print("   These features may not work properly.")
            
        return len(failed_packages) == 0
        
    def create_directory_structure(self) -> bool:
        """Create necessary directory structure"""
        print("📁 Creating directory structure...")
        
        directories = [
            'modules',
            'scripts',
            'CSS',
            'JS',
            'data',
            'logs',
            'benchmark_results',
            'backups'
        ]
        
        try:
            for directory in directories:
                dir_path = self.base_path / directory
                dir_path.mkdir(exist_ok=True)
                print(f"  ✅ {directory}/")
                
            return True
            
        except Exception as e:
            print(f"❌ Error creating directories: {e}")
            return False
            
    def install_enhancement_files(self) -> bool:
        """Install all enhancement module files"""
        print("📥 Installing enhancement files...")
        
        # This would typically download files from a repository
        # For this example, we'll create the file structure
        
        files_to_create = {
            'modules/__init__.py': '',
            'scripts/__init__.py': '',
            'data/README.md': '# LSDAI Enhancement Suite Data Directory\n\nThis directory contains:\n- Configuration files\n- Cached data\n- User preferences\n- Model metadata\n',
            'logs/README.md': '# LSDAI Enhancement Suite Logs\n\nThis directory contains system logs and monitoring data.\n',
            'CSS/README.md': '# Enhanced CSS Styles\n\nCustom CSS files for the enhanced UI.\n',
            'JS/README.md': '# Enhanced JavaScript\n\nJavaScript files for enhanced functionality.\n'
        }
        
        try:
            for file_path, content in files_to_create.items():
                full_path = self.base_path / file_path
                full_path.parent.mkdir(parents=True, exist_ok=True)
                
                if not full_path.exists():
                    with open(full_path, 'w') as f:
                        f.write(content)
                    print(f"  ✅ {file_path}")
                    
            return True
            
        except Exception as e:
            print(f"❌ Error installing files: {e}")
            return False
            
    def integrate_with_existing_lsdai(self) -> bool:
        """Integrate enhancements with existing LSDAI"""
        print("🔗 Integrating with existing LSDAI...")
        
        try:
            # Backup existing widgets-en.py
            original_widgets = self.base_path / 'scripts' / 'widgets-en.py'
            if original_widgets.exists():
                backup_path = self.base_path / 'scripts' / 'widgets-en.py.backup'
                shutil.copy2(original_widgets, backup_path)
                print(f"  ✅ Backed up original widgets to {backup_path}")
                
            # Create integration wrapper
            integration_code = '''
# LSDAI Enhancement Suite Integration
# This file integrates the enhanced features with existing LSDAI

import sys
from pathlib import Path

# Add enhancement modules to path
enhancement_path = Path(__file__).parent.parent / "modules"
if str(enhancement_path) not in sys.path:
    sys.path.insert(0, str(enhancement_path))

# Try to load enhanced widgets, fall back to original if not available
try:
    from scripts.enhanced_widgets import *
    print("🚀 Enhanced widgets loaded successfully!")
except ImportError as e:
    print(f"⚠️  Enhanced widgets not available: {e}")
    print("📦 Using original LSDAI widgets")
    
    # Load original widgets
    try:
        exec(open(Path(__file__).parent / "widgets-en.py.backup").read())
    except FileNotFoundError:
        print("❌ Original widgets backup not found")
        raise
'''
            
            # Write integration file
            integration_file = self.base_path / 'scripts' / 'widgets-enhanced.py'
            with open(integration_file, 'w') as f:
                f.write(integration_code)
                
            print(f"  ✅ Created integration file: {integration_file}")
            
            # Create enhanced launch script
            enhanced_launch_code = '''
# Enhanced LSDAI Launch Script
import sys
from pathlib import Path

# Add enhancement modules to path
enhancement_path = Path(__file__).parent.parent / "modules"
if str(enhancement_path) not in sys.path:
    sys.path.insert(0, str(enhancement_path))

# Initialize enhancement suite
try:
    from master_integration import LSDAIEnhancementSuite
    
    suite = LSDAIEnhancementSuite()
    suite.initialize()
    
    # Launch enhanced WebUI
    suite.launch_enhanced_webui()
    
except ImportError:
    print("⚠️  Enhancement suite not available, using standard launch")
    from scripts import launch
    launch.main()
'''
            
            enhanced_launch_file = self.base_path / 'launch_enhanced.py'
            with open(enhanced_launch_file, 'w') as f:
                f.write(enhanced_launch_code)
                
            print(f"  ✅ Created enhanced launch script: {enhanced_launch_file}")
            
            return True
            
        except Exception as e:
            print(f"❌ Integration error: {e}")
            return False
            
    def create_configuration(self) -> bool:
        """Create default configuration"""
        print("⚙️  Creating default configuration...")
        
        default_config = {
            "version": self.enhancement_version,
            "installation_date": sys.version,
            "modules": {
                "enhanced_download_manager": {
                    "enabled": True,
                    "concurrent_downloads": 3,
                    "auto_retry": True,
                    "download_timeout": 300
                },
                "enhanced_model_manager": {
                    "enabled": True,
                    "auto_discovery": True,
                    "cache_duration": 3600,
                    "auto_organize": True
                },
                "extension_manager": {
                    "enabled": True,
                    "auto_update": False,
                    "check_interval": 86400
                },
                "cloud_sync": {
                    "enabled": False,
                    "auto_sync_interval": 3600,
                    "backup_retention_days": 30
                },
                "notification_system": {
                    "enabled": True,
                    "channels": ["browser"],
                    "rate_limit": 5
                },
                "advanced_logging": {
                    "enabled": True,
                    "log_level": "INFO",
                    "retention_days": 7
                },
                "benchmark_suite": {
                    "enabled": True,
                    "auto_benchmark": False,
                    "save_images": True
                }
            },
            "ui_enhancements": {
                "enhanced_widgets": True,
                "visual_model_selector": True,
                "download_queue_ui": True,
                "advanced_configuration": True,
                "model_comparison": True,
                "batch_operations": True,
                "dark_theme": True
            },
            "performance": {
                "auto_optimization": True,
                "resource_monitoring": True,
                "performance_alerts": True,
                "memory_limit_gb": 8
            }
        }
        
        try:
            config_file = self.base_path / 'data' / 'enhancement_config.json'
            config_file.parent.mkdir(exist_ok=True)
            
            with open(config_file, 'w') as f:
                json.dump(default_config, f, indent=2)
                
            print(f"  ✅ Configuration saved to {config_file}")
            return True
            
        except Exception as e:
            print(f"❌ Configuration creation error: {e}")
            return False
            
    def run_post_install_tests(self) -> Dict[str, bool]:
        """Run post-installation tests"""
        print("🧪 Running post-installation tests...")
        
        test_results = {}
        
        # Test module imports
        modules_to_test = [
            'json_utils',
            'modules.EnhancedManager',
            'modules.EnhancedModelManager',
            'modules.ExtensionManager',
            'modules.CloudSync',
            'modules.NotificationSystem',
            'modules.AdvancedLogging',
            'modules.ModelBenchmarking'
        ]
        
        for module_name in modules_to_test:
            try:
                __import__(module_name)
                test_results[f'import_{module_name}'] = True
                print(f"  ✅ {module_name}")
            except ImportError as e:
                test_results[f'import_{module_name}'] = False
                print(f"  ❌ {module_name}: {e}")
                
        # Test file structure
        required_files = [
            'data/enhancement_config.json',
            'modules/__init__.py',
            'scripts/__init__.py'
        ]
        
        for file_path in required_files:
            file_exists = (self.base_path / file_path).exists()
            test_results[f'file_{file_path}'] = file_exists
            print(f"  {'✅' if file_exists else '❌'} {file_path}")
            
        return test_results
        
    def create_quick_start_guide(self) -> bool:
        """Create quick start guide"""
        print("📖 Creating quick start guide...")
        
        guide_content = f"""# LSDAI Enhancement Suite v{self.enhancement_version} - Quick Start Guide

## 🚀 Getting Started

### 1. Basic Usage
To start with enhancements:
```bash
python launch_enhanced.py
```

### 2. Configuration Wizard
Run the configuration wizard to set up advanced features:
```bash
python -m scripts.master_integration --wizard
```

### 3. Check System Status
```bash
python -m scripts.master_integration --status
```

## 🎯 Key Features

### Enhanced Download Manager
- Real-time progress tracking
- Batch downloads
- Auto-retry failed downloads
- Queue management

### Smart Model Management
- Automatic model discovery
- Visual model browser
- Model comparison tools
- Favorites and collections

### Advanced UI
- Modern, responsive design
- Tabbed interface
- Visual progress indicators
- Interactive model cards

### Cloud Sync & Backup
- Google Drive integration
- GitHub backup
- Automatic settings sync
- Version history

### Notification System
- Browser notifications
- Email alerts
- Discord/Slack webhooks
- Custom notification rules

### Performance Monitoring
- Resource usage tracking
- Performance alerts
- System optimization
- Benchmark suite

## 🔧 Configuration

### Manual Configuration
Edit the configuration file:
```
data/enhancement_config.json
```

### Environment Variables
Set these for additional features:
- `CIVITAI_API_TOKEN`: For CivitAI integration
- `GITHUB_TOKEN`: For GitHub backup
- `GDRIVE_CREDENTIALS`: For Google Drive sync

## 📚 Advanced Usage

### Cloud Sync Setup
```python
from modules.CloudSync import setup_cloud_sync

# Setup Google Drive and GitHub
setup_cloud_sync(
    gdrive_credentials="your_credentials.json",
    github_token="your_github_token"
)
```

### Model Benchmarking
```python
from modules.ModelBenchmarking import quick_model_comparison

# Compare models
results = quick_model_comparison([
    "model1.safetensors",
    "model2.safetensors"
])
```

### Custom Notifications
```python
from modules.NotificationSystem import send_notification

send_notification(
    "Custom Alert",
    "Your custom message here",
    severity="info",
    category="custom"
)
```

## 🆘 Troubleshooting

### Common Issues

1. **Import Errors**
   - Ensure all dependencies are installed
   - Check Python version (3.8+ required)

2. **WebUI Won't Start**
   - Check if original LSDAI is properly installed
   - Verify file permissions

3. **Cloud Sync Issues**
   - Verify credentials are correctly configured
   - Check internet connectivity

### Getting Help
- Check logs in `logs/` directory
- Run health check: `python -m scripts.master_integration --health-check`
- Report issues with detailed error messages

## 📝 File Structure
```
LSDAI/
├── modules/              # Enhancement modules
├── scripts/              # Enhanced scripts
├── CSS/                  # Custom styles
├── JS/                   # Enhanced JavaScript
├── data/                 # Configuration and cache
├── logs/                 # System logs
├── benchmark_results/    # Benchmark data
└── launch_enhanced.py    # Enhanced launcher
```

## 🔄 Updates

To update the enhancement suite:
1. Backup your configuration
2. Download latest version
3. Run installer again
4. Restore configuration

Enjoy your enhanced LSDAI experience! 🎉
"""
        
        try:
            guide_file = self.base_path / 'ENHANCEMENT_GUIDE.md'
            with open(guide_file, 'w') as f:
                f.write(guide_content)
                
            print(f"  ✅ Quick start guide created: {guide_file}")
            return True
            
        except Exception as e:
            print(f"❌ Error creating guide: {e}")
            return False
            
    def run_installation(self, skip_dependencies: bool = False, 
                        include_optional: bool = True) -> bool:
        """Run complete installation process"""
        print(f"🔥 LSDAI Enhancement Suite v{self.enhancement_version} Installer")
        print("=" * 60)
        
        # Check environment
        env_status = self.check_environment()
        
        if not env_status['python_compatible']:
            print("❌ Python 3.8+ required")
            return False
            
        if not env_status['has_existing_lsdai']:
            print("⚠️  Warning: Existing LSDAI installation not detected")
            response = input("Continue anyway? (y/N): ").strip().lower()
            if response != 'y':
                return False
                
        print(f"✅ Environment check passed")
        print(f"   Platform: {env_status['platform']}")
        print(f"   Python: {env_status['python_version']}")
        print(f"   Directory: {env_status['current_directory']}")
        
        # Install dependencies
        if not skip_dependencies:
            deps_success = self.install_dependencies(include_optional)
            if not deps_success:
                print("⚠️  Some dependencies failed to install")
                response = input("Continue with installation? (y/N): ").strip().lower()
                if response != 'y':
                    return False
                    
        # Create directory structure
        if not self.create_directory_structure():
            print("❌ Failed to create directory structure")
            return False
            
        # Install enhancement files
        if not self.install_enhancement_files():
            print("❌ Failed to install enhancement files")
            return False
            
        # Integrate with existing LSDAI
        if env_status['has_existing_lsdai']:
            if not self.integrate_with_existing_lsdai():
                print("❌ Failed to integrate with existing LSDAI")
                return False
        else:
            print("⚠️  Skipping LSDAI integration (not detected)")
            
        # Create configuration
        if not self.create_configuration():
            print("❌ Failed to create configuration")
            return False
            
        # Run tests
        test_results = self.run_post_install_tests()
        failed_tests = [test for test, result in test_results.items() if not result]
        
        if failed_tests:
            print(f"⚠️  Some tests failed: {failed_tests}")
            print("   Installation may be incomplete")
        else:
            print("✅ All post-installation tests passed")
            
        # Create documentation
        self.create_quick_start_guide()
        
        # Final message
        print("\n" + "=" * 60)
        print("🎉 LSDAI Enhancement Suite installation completed!")
        print("\n📋 Next steps:")
        print("   1. Read ENHANCEMENT_GUIDE.md for usage instructions")
        print("   2. Run configuration wizard: python -m scripts.master_integration --wizard")
        print("   3. Launch enhanced WebUI: python launch_enhanced.py")
        print("\n✨ Enjoy your enhanced LSDAI experience!")
        
        return len(failed_tests) == 0

def main():
    """Main installer entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="LSDAI Enhancement Suite Installer")
    parser.add_argument('--skip-deps', action='store_true', 
                       help='Skip dependency installation')
    parser.add_argument('--no-optional', action='store_true',
                       help='Skip optional dependencies')
    parser.add_argument('--check-only', action='store_true',
                       help='Only check environment compatibility')
    
    args = parser.parse_args()
    
    installer = LSDAIEnhancementInstaller()
    
    if args.check_only:
        # Just check environment
        status = installer.check_environment()
        print("Environment Status:")
        for key, value in status.items():
            print(f"  {key}: {value}")
        return
        
    # Run full installation
    success = installer.run_installation(
        skip_dependencies=args.skip_deps,
        include_optional=not args.no_optional
    )
    
    if not success:
        print("❌ Installation failed")
        sys.exit(1)
    else:
        print("✅ Installation successful")

if __name__ == "__main__":
    main()

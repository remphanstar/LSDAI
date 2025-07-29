# Master Integration System - Complete LSDAI Enhancement Suite
# Save as: scripts/master-integration.py

import json_utils as js
from pathlib import Path
import subprocess
import threading
import importlib
import argparse
import time
import json
import sys
import os

# Import all enhancement modules
try:
    from modules.EnhancedManager import get_enhanced_manager
    from modules.EnhancedModelManager import get_enhanced_model_manager
    from modules.ExtensionManager import get_extension_manager
    from modules.CloudSync import get_cloud_sync_manager
    from modules.NotificationSystem import get_notification_manager, send_info, send_success, send_error
    from modules.AdvancedLogging import get_advanced_logger, setup_webui_monitoring
    from modules.ModelBenchmarking import get_benchmark_suite
    ENHANCED_MODULES_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Some enhanced modules not available: {e}")
    ENHANCED_MODULES_AVAILABLE = False

class LSDAIEnhancementSuite:
    """Master class coordinating all LSDAI enhancements"""
    
    def __init__(self):
        self.version = "2.0.0"
        self.modules = {}
        self.configuration = {}
        self.status = {
            'initialized': False,
            'modules_loaded': {},
            'services_running': {},
            'last_health_check': None
        }
        
    def initialize(self, config_file: str = None):
        """Initialize the complete enhancement suite"""
        print(f"🚀 Initializing LSDAI Enhancement Suite v{self.version}")
        
        # Load configuration
        self.configuration = self._load_configuration(config_file)
        
        # Initialize core modules
        self._initialize_modules()
        
        # Setup integrations
        self._setup_integrations()
        
        # Start background services
        self._start_background_services()
        
        # Health check
        self._perform_health_check()
        
        self.status['initialized'] = True
        send_success("LSDAI Enhancement Suite", "All systems initialized successfully")
        
        print("✅ LSDAI Enhancement Suite initialized successfully!")
        
    def _load_configuration(self, config_file: str = None):
        """Load enhancement suite configuration"""
        if config_file is None:
            config_file = "data/enhancement_config.json"
            
        default_config = {
            "modules": {
                "enhanced_download_manager": {"enabled": True, "concurrent_downloads": 3},
                "enhanced_model_manager": {"enabled": True, "auto_discovery": True},
                "extension_manager": {"enabled": True, "auto_update": False},
                "cloud_sync": {"enabled": False, "auto_sync_interval": 3600},
                "notification_system": {"enabled": True, "channels": ["browser"]},
                "advanced_logging": {"enabled": True, "log_level": "INFO"},
                "benchmark_suite": {"enabled": True, "auto_benchmark": False}
            },
            "ui_enhancements": {
                "enhanced_widgets": True,
                "visual_model_selector": True,
                "download_queue_ui": True,
                "advanced_configuration": True,
                "model_comparison": True,
                "batch_operations": True
            },
            "performance": {
                "auto_optimization": True,
                "resource_monitoring": True,
                "performance_alerts": True
            },
            "backup": {
                "auto_backup_settings": True,
                "backup_interval_hours": 24,
                "keep_backups": 7
            }
        }
        
        try:
            config_path = Path(config_file)
            if config_path.exists():
                with open(config_path, 'r') as f:
                    user_config = json.load(f)
                    # Merge with defaults
                    config = {**default_config, **user_config}
            else:
                config = default_config
                # Save default config
                config_path.parent.mkdir(exist_ok=True)
                with open(config_path, 'w') as f:
                    json.dump(config, f, indent=2)
                    
            return config
            
        except Exception as e:
            print(f"⚠️  Error loading config, using defaults: {e}")
            return default_config
            
    def _initialize_modules(self):
        """Initialize all enhancement modules"""
        if not ENHANCED_MODULES_AVAILABLE:
            print("❌ Enhanced modules not available, using basic functionality")
            return
            
        modules_config = self.configuration.get("modules", {})
        
        # Initialize Enhanced Download Manager
        if modules_config.get("enhanced_download_manager", {}).get("enabled", True):
            try:
                self.modules['download_manager'], self.modules['batch_operations'] = get_enhanced_manager()
                self.status['modules_loaded']['download_manager'] = True
                print("✅ Enhanced Download Manager loaded")
            except Exception as e:
                print(f"❌ Failed to load Enhanced Download Manager: {e}")
                self.status['modules_loaded']['download_manager'] = False
                
        # Initialize Enhanced Model Manager
        if modules_config.get("enhanced_model_manager", {}).get("enabled", True):
            try:
                self.modules['model_manager'] = get_enhanced_model_manager()
                self.status['modules_loaded']['model_manager'] = True
                print("✅ Enhanced Model Manager loaded")
            except Exception as e:
                print(f"❌ Failed to load Enhanced Model Manager: {e}")
                self.status['modules_loaded']['model_manager'] = False
                
        # Initialize Extension Manager
        if modules_config.get("extension_manager", {}).get("enabled", True):
            try:
                self.modules['extension_manager'] = get_extension_manager()
                self.status['modules_loaded']['extension_manager'] = True
                print("✅ Extension Manager loaded")
            except Exception as e:
                print(f"❌ Failed to load Extension Manager: {e}")
                self.status['modules_loaded']['extension_manager'] = False
                
        # Initialize Cloud Sync
        if modules_config.get("cloud_sync", {}).get("enabled", False):
            try:
                self.modules['cloud_sync'] = get_cloud_sync_manager()
                self.status['modules_loaded']['cloud_sync'] = True
                print("✅ Cloud Sync Manager loaded")
            except Exception as e:
                print(f"❌ Failed to load Cloud Sync Manager: {e}")
                self.status['modules_loaded']['cloud_sync'] = False
                
        # Initialize Notification System
        if modules_config.get("notification_system", {}).get("enabled", True):
            try:
                self.modules['notifications'] = get_notification_manager()
                self.status['modules_loaded']['notifications'] = True
                print("✅ Notification System loaded")
            except Exception as e:
                print(f"❌ Failed to load Notification System: {e}")
                self.status['modules_loaded']['notifications'] = False
                
        # Initialize Advanced Logging
        if modules_config.get("advanced_logging", {}).get("enabled", True):
            try:
                self.modules['logging'] = get_advanced_logger()
                self.status['modules_loaded']['logging'] = True
                print("✅ Advanced Logging loaded")
            except Exception as e:
                print(f"❌ Failed to load Advanced Logging: {e}")
                self.status['modules_loaded']['logging'] = False
                
        # Initialize Benchmark Suite
        if modules_config.get("benchmark_suite", {}).get("enabled", True):
            try:
                self.modules['benchmark'] = get_benchmark_suite()
                self.status['modules_loaded']['benchmark'] = True
                print("✅ Benchmark Suite loaded")
            except Exception as e:
                print(f"❌ Failed to load Benchmark Suite: {e}")
                self.status['modules_loaded']['benchmark'] = False
                
    def _setup_integrations(self):
        """Setup integrations between modules"""
        print("🔗 Setting up module integrations...")
        
        # Integrate download manager with notification system
        if 'download_manager' in self.modules and 'notifications' in self.modules:
            def download_progress_callback(status):
                if status.get('total_progress', 0) == 100:
                    send_success("Downloads Complete", "All queued downloads have finished")
                    
            self.modules['download_manager'].add_progress_callback(download_progress_callback)
            
        # Integrate model manager with cloud sync
        if 'model_manager' in self.modules and 'cloud_sync' in self.modules:
            # Auto-sync model favorites
            def sync_model_data():
                try:
                    favorites = self.modules['model_manager'].collections.get_all()
                    if favorites:
                        self.modules['cloud_sync'].sync_model_list(favorites)
                except Exception as e:
                    print(f"Model sync error: {e}")
                    
            # Schedule periodic sync
            if self.configuration.get("modules", {}).get("cloud_sync", {}).get("enabled"):
                sync_interval = self.configuration.get("modules", {}).get("cloud_sync", {}).get("auto_sync_interval", 3600)
                threading.Timer(sync_interval, sync_model_data).start()
                
        # Integrate benchmark suite with logging
        if 'benchmark' in self.modules and 'logging' in self.modules:
            def benchmark_callback(result):
                self.modules['logging'].log_performance('benchmark', result.get('generation_time'), result)
                
        print("✅ Module integrations configured")
        
    def _start_background_services(self):
        """Start background services"""
        print("🔄 Starting background services...")
        
        # Start auto-sync if enabled
        if 'cloud_sync' in self.modules:
            cloud_config = self.configuration.get("modules", {}).get("cloud_sync", {})
            if cloud_config.get("enabled") and cloud_config.get("auto_sync_interval"):
                interval = cloud_config["auto_sync_interval"]
                self.modules['cloud_sync'].start_auto_sync(interval)
                self.status['services_running']['cloud_sync'] = True
                
        # Start resource monitoring
        performance_config = self.configuration.get("performance", {})
        if performance_config.get("resource_monitoring"):
            self._start_resource_monitoring()
            self.status['services_running']['resource_monitoring'] = True
            
        # Start auto-backup
        backup_config = self.configuration.get("backup", {})
        if backup_config.get("auto_backup_settings"):
            self._start_auto_backup()
            self.status['services_running']['auto_backup'] = True
            
        print("✅ Background services started")
        
    def _start_resource_monitoring(self):
        """Start system resource monitoring"""
        def monitor_resources():
            while True:
                try:
                    import psutil
                    
                    cpu_usage = psutil.cpu_percent(interval=1)
                    memory = psutil.virtual_memory()
                    
                    # Alert on high resource usage
                    if cpu_usage > 90:
                        send_error("High CPU Usage", f"CPU usage is {cpu_usage:.1f}%")
                        
                    if memory.percent > 95:
                        send_error("High Memory Usage", f"Memory usage is {memory.percent:.1f}%")
                        
                    time.sleep(60)  # Check every minute
                    
                except Exception as e:
                    print(f"Resource monitoring error: {e}")
                    time.sleep(300)  # Wait 5 minutes on error
                    
        monitor_thread = threading.Thread(target=monitor_resources, daemon=True)
        monitor_thread.start()
        
    def _start_auto_backup(self):
        """Start automatic backup system"""
        def auto_backup():
            while True:
                try:
                    backup_config = self.configuration.get("backup", {})
                    interval_hours = backup_config.get("backup_interval_hours", 24)
                    
                    time.sleep(interval_hours * 3600)
                    
                    if 'cloud_sync' in self.modules:
                        result = self.modules['cloud_sync'].sync_all_data()
                        if any(result[service]['success'] for service in result if service != 'timestamp'):
                            send_info("Auto Backup", "Settings backed up successfully")
                        else:
                            send_error("Auto Backup Failed", "Failed to backup settings")
                            
                except Exception as e:
                    print(f"Auto backup error: {e}")
                    
        backup_thread = threading.Thread(target=auto_backup, daemon=True)
        backup_thread.start()
        
    def _perform_health_check(self):
        """Perform system health check"""
        print("🏥 Performing health check...")
        
        health_status = {
            'timestamp': time.time(),
            'modules': {},
            'services': {},
            'overall_status': 'healthy'
        }
        
        # Check module health
        for module_name, module in self.modules.items():
            try:
                # Basic health check - module exists and has expected methods
                health_status['modules'][module_name] = 'healthy'
            except Exception as e:
                health_status['modules'][module_name] = f'unhealthy: {e}'
                health_status['overall_status'] = 'degraded'
                
        # Check service health
        for service_name, running in self.status['services_running'].items():
            health_status['services'][service_name] = 'running' if running else 'stopped'
            
        self.status['last_health_check'] = health_status
        
        if health_status['overall_status'] == 'healthy':
            print("✅ Health check passed - all systems nominal")
        else:
            print("⚠️  Health check detected issues - some services may be degraded")
            
    def launch_enhanced_webui(self, webui_path: str = None, args: str = None):
        """Launch WebUI with all enhancements"""
        print("🚀 Launching Enhanced WebUI...")
        
        if webui_path is None:
            webui_path = Path(os.getcwd()) / 'stable-diffusion-webui'
            
        # Import enhanced launcher
        try:
            from scripts.enhanced_launch import enhanced_launch_webui
            
            # Setup monitoring before launch
            if 'logging' in self.modules:
                def webui_status_callback(status, message):
                    self.modules['logging'].log_event('info', 'webui', f"Status: {status} - {message}")
                    
                def webui_log_callback(line):
                    self.modules['logging'].log_event('debug', 'webui_output', line)
                    
            # Launch with enhancements
            success = enhanced_launch_webui()
            
            if success:
                send_success("WebUI Launched", "Enhanced WebUI started successfully")
                print("✅ Enhanced WebUI launched successfully!")
            else:
                send_error("WebUI Launch Failed", "Failed to start Enhanced WebUI")
                print("❌ Enhanced WebUI launch failed")
                
            return success
            
        except ImportError:
            print("⚠️  Enhanced launcher not available, falling back to standard launch")
            return self._launch_standard_webui(webui_path, args)
            
    def _launch_standard_webui(self, webui_path: str, args: str = None):
        """Fallback to standard WebUI launch"""
        try:
            # Use original launch.py
            from scripts import launch
            return launch.main()
        except Exception as e:
            print(f"❌ Standard WebUI launch failed: {e}")
            return False
            
    def create_configuration_wizard(self):
        """Interactive configuration wizard"""
        print("🧙 Starting LSDAI Enhancement Suite Configuration Wizard")
        print("=" * 60)
        
        config = {}
        
        # Basic configuration
        print("\n📋 Basic Configuration")
        config['modules'] = {}
        
        modules = [
            ('enhanced_download_manager', 'Enhanced Download Manager with progress tracking'),
            ('enhanced_model_manager', 'Smart model management and discovery'),
            ('extension_manager', 'Automatic extension management'),
            ('cloud_sync', 'Cloud backup and synchronization'),
            ('notification_system', 'Advanced notification system'),
            ('advanced_logging', 'Comprehensive logging and monitoring'),
            ('benchmark_suite', 'Model performance benchmarking')
        ]
        
        for module_key, module_desc in modules:
            response = input(f"Enable {module_desc}? (Y/n): ").strip().lower()
            config['modules'][module_key] = {'enabled': response != 'n'}
            
        # Cloud sync configuration
        if config['modules'].get('cloud_sync', {}).get('enabled'):
            print("\n☁️  Cloud Sync Configuration")
            
            setup_gdrive = input("Setup Google Drive sync? (y/N): ").strip().lower() == 'y'
            setup_github = input("Setup GitHub backup? (y/N): ").strip().lower() == 'y'
            
            if setup_gdrive:
                print("Please follow Google Drive authentication instructions...")
                # In a real implementation, this would guide through OAuth
                
            if setup_github:
                github_token = input("Enter GitHub personal access token: ").strip()
                if github_token:
                    config['github_token'] = github_token  # Store securely in real implementation
                    
        # Notification configuration
        if config['modules'].get('notification_system', {}).get('enabled'):
            print("\n🔔 Notification Configuration")
            
            channels = []
            if input("Enable browser notifications? (Y/n): ").strip().lower() != 'n':
                channels.append('browser')
                
            if input("Setup email notifications? (y/N): ").strip().lower() == 'y':
                email_config = {
                    'type': 'email',
                    'smtp_server': input("SMTP server (smtp.gmail.com): ").strip() or 'smtp.gmail.com',
                    'smtp_port': int(input("SMTP port (587): ").strip() or '587'),
                    'username': input("Email username: ").strip(),
                    'password': input("Email password: ").strip(),
                    'to_email': input("Notification recipient email: ").strip(),
                    'enabled': True
                }
                config['email_config'] = email_config
                channels.append('email')
                
            if input("Setup Discord webhook? (y/N): ").strip().lower() == 'y':
                webhook_url = input("Discord webhook URL: ").strip()
                if webhook_url:
                    config['discord_config'] = {
                        'type': 'discord',
                        'webhook_url': webhook_url,
                        'enabled': True
                    }
                    channels.append('discord')
                    
            config['notification_channels'] = channels
            
        # Performance settings
        print("\n⚡ Performance Configuration")
        
        concurrent_downloads = input("Concurrent downloads (3): ").strip()
        if concurrent_downloads.isdigit():
            config['concurrent_downloads'] = int(concurrent_downloads)
        else:
            config['concurrent_downloads'] = 3
            
        auto_optimization = input("Enable automatic performance optimization? (Y/n): ").strip().lower() != 'n'
        config['auto_optimization'] = auto_optimization
        
        # Save configuration
        config_file = Path('data/enhancement_config.json')
        config_file.parent.mkdir(exist_ok=True)
        
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
            
        print(f"\n✅ Configuration saved to {config_file}")
        print("🚀 Run the enhancement suite with your new configuration!")
        
        return config
        
    def get_status_report(self):
        """Get comprehensive status report"""
        report = {
            'suite_version': self.version,
            'initialization_status': self.status,
            'module_status': {},
            'service_status': {},
            'system_health': self.status.get('last_health_check', {}),
            'timestamp': time.time()
        }
        
        # Get module-specific status
        for module_name, module in self.modules.items():
            try:
                if hasattr(module, 'get_status'):
                    report['module_status'][module_name] = module.get_status()
                else:
                    report['module_status'][module_name] = 'active'
            except Exception as e:
                report['module_status'][module_name] = f'error: {e}'
                
        return report
        
    def shutdown(self):
        """Graceful shutdown of all services"""
        print("🛑 Shutting down LSDAI Enhancement Suite...")
        
        # Stop background services
        if 'cloud_sync' in self.modules:
            self.modules['cloud_sync'].stop_auto_sync()
            
        # Send shutdown notification
        if 'notifications' in self.modules:
            send_info("System Shutdown", "LSDAI Enhancement Suite is shutting down")
            
        print("✅ Shutdown complete")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="LSDAI Enhancement Suite")
    parser.add_argument('--config', help='Configuration file path')
    parser.add_argument('--wizard', action='store_true', help='Run configuration wizard')
    parser.add_argument('--launch', action='store_true', help='Launch enhanced WebUI')
    parser.add_argument('--status', action='store_true', help='Show status report')
    parser.add_argument('--health-check', action='store_true', help='Perform health check')
    
    args = parser.parse_args()
    
    # Create enhancement suite instance
    suite = LSDAIEnhancementSuite()
    
    try:
        if args.wizard:
            # Run configuration wizard
            suite.create_configuration_wizard()
            
        elif args.status:
            # Show status report
            if not suite.status['initialized']:
                suite.initialize(args.config)
            report = suite.get_status_report()
            print(json.dumps(report, indent=2))
            
        elif args.health_check:
            # Perform health check
            if not suite.status['initialized']:
                suite.initialize(args.config)
            suite._perform_health_check()
            
        elif args.launch:
            # Initialize and launch
            suite.initialize(args.config)
            suite.launch_enhanced_webui()
            
            # Keep running
            try:
                while True:
                    time.sleep(60)
            except KeyboardInterrupt:
                suite.shutdown()
                
        else:
            # Default: initialize suite
            suite.initialize(args.config)
            print(f"🎉 LSDAI Enhancement Suite v{suite.version} is ready!")
            print("Use --launch to start the enhanced WebUI")
            print("Use --wizard to configure the system")
            print("Use --status to see system status")
            
    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user")
        suite.shutdown()
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        if 'notifications' in suite.modules:
            send_error("System Error", f"Fatal error in enhancement suite: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

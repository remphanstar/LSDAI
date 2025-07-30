# Enhanced downloading integration - FIXED VERSION
# Properly integrates with restored downloading_en.py functionality
# Full verbosity system integration and actual function calls

import json_utils as js
from pathlib import Path
import subprocess
import time
import os

# Get settings path from environment or default
SETTINGS_PATH = Path(os.environ.get('settings_path', '/content/LSDAI/settings.json'))

# Import verbosity system for consistent output control
try:
    from modules.verbose_output_manager import get_verbose_manager, VerbosityLevel, vprint
    verbose_manager = get_verbose_manager()
    
    def log_msg(message, level=VerbosityLevel.NORMAL):
        """Unified logging with verbosity control"""
        vprint(message, level)
        
    VERBOSITY_AVAILABLE = True
    log_msg("✨ Enhanced downloading integration with verbosity system", VerbosityLevel.DETAILED)
except ImportError:
    def log_msg(message, level=None):
        print(message)
    VERBOSITY_AVAILABLE = False
    print("📦 Enhanced downloading integration - standard output")

# Import original downloading functions from restored downloading_en.py
try:
    from scripts.downloading_en import (
        main as downloading_main,
        setup_comprehensive_safe_venv,
        install_webui,
        download_models_and_assets,
        setup_performance_monitoring
    )
    ORIGINAL_DOWNLOADING_AVAILABLE = True
    log_msg("✅ Original downloading functions imported successfully", VerbosityLevel.DETAILED)
except ImportError as e:
    ORIGINAL_DOWNLOADING_AVAILABLE = False
    log_msg(f"❌ Original downloading functions not found: {e}", VerbosityLevel.MINIMAL)
    log_msg("   Make sure downloading_en.py has been restored from downloading_en(1).py", VerbosityLevel.MINIMAL)

# Import enhancements if available
try:
    from modules.EnhancedManager import get_enhanced_manager
    from modules.NotificationSystem import send_info, send_success, send_error
    from modules.AdvancedLogging import get_advanced_logger
    ENHANCEMENTS_AVAILABLE = True
    log_msg("✨ Enhanced modules loaded", VerbosityLevel.DETAILED)
except ImportError:
    ENHANCEMENTS_AVAILABLE = False
    log_msg("📦 Using standard LSDAI functionality", VerbosityLevel.DETAILED)

class EnhancedDownloadingSystem:
    """Enhanced downloading system that properly integrates with restored functionality"""
    
    def __init__(self):
        self.enhanced_mode = ENHANCEMENTS_AVAILABLE
        self.original_mode = ORIGINAL_DOWNLOADING_AVAILABLE
        self.enhanced_manager = None
        self.batch_ops = None
        
        if ENHANCEMENTS_AVAILABLE:
            try:
                self.enhanced_manager, self.batch_ops = get_enhanced_manager()
                log_msg("✅ Enhanced manager initialized", VerbosityLevel.DETAILED)
            except Exception as e:
                log_msg(f"⚠️ Could not initialize enhanced manager: {e}", VerbosityLevel.DETAILED)
                self.enhanced_mode = False
    
    def run_enhanced_downloading(self):
        """Main enhanced downloading execution with full integration"""
        
        log_msg("📥 LSDAI Enhanced Downloading System", VerbosityLevel.NORMAL)
        log_msg("="*40, VerbosityLevel.NORMAL)
        
        if not self.original_mode:
            log_msg("❌ CRITICAL: Original downloading functions not available", VerbosityLevel.MINIMAL)
            log_msg("   Please restore downloading_en.py from downloading_en(1).py", VerbosityLevel.MINIMAL)
            return False
        
        # Enhanced mode with progress tracking
        if self.enhanced_mode:
            return self._run_enhanced_mode()
        else:
            return self._run_standard_mode()
    
    def _run_enhanced_mode(self):
        """Run with enhanced features and progress tracking"""
        
        log_msg("✨ Running in enhanced mode with progress tracking", VerbosityLevel.NORMAL)
        
        try:
            # Step 1: Enhanced venv setup with progress tracking
            log_msg("🐍 Setting up enhanced virtual environment...", VerbosityLevel.NORMAL)
            
            # Use enhanced manager for progress tracking if available
            if self.enhanced_manager:
                log_msg("📊 Initializing enhanced progress tracking...", VerbosityLevel.DETAILED)
                self.enhanced_manager.start_progress_tracking("Environment Setup")
            
            venv_result = self._setup_enhanced_venv()
            
            if self.enhanced_manager:
                self.enhanced_manager.update_progress("Environment Setup", 25)
            
            # Step 2: Enhanced WebUI installation
            log_msg("🚀 Installing WebUI with enhanced monitoring...", VerbosityLevel.NORMAL)
            webui_result = self._install_webui_enhanced()
            
            if self.enhanced_manager:
                self.enhanced_manager.update_progress("Environment Setup", 50)
            
            # Step 3: Enhanced model downloading with batch operations
            log_msg("🎨 Downloading models with enhanced batch operations...", VerbosityLevel.NORMAL)
            models_result = self._download_models_enhanced()
            
            if self.enhanced_manager:
                self.enhanced_manager.update_progress("Environment Setup", 75)
            
            # Step 4: Enhanced monitoring setup
            log_msg("📊 Setting up enhanced monitoring...", VerbosityLevel.NORMAL)
            monitoring_result = self._setup_enhanced_monitoring()
            
            if self.enhanced_manager:
                self.enhanced_manager.complete_progress("Environment Setup")
            
            # Send completion notification
            overall_success = all([venv_result, webui_result, models_result])
            
            if overall_success:
                send_success("LSDAI Enhanced Setup Complete", 
                           f"All components installed successfully with enhanced features!")
                log_msg("🎉 Enhanced setup completed successfully!", VerbosityLevel.NORMAL)
            else:
                send_error("LSDAI Enhanced Setup Issues", 
                         "Some components failed - check logs for details")
                log_msg("⚠️ Enhanced setup completed with some issues", VerbosityLevel.MINIMAL)
                
            return overall_success
            
        except Exception as e:
            log_msg(f"❌ Enhanced mode execution failed: {e}", VerbosityLevel.MINIMAL)
            if ENHANCEMENTS_AVAILABLE:
                send_error("Enhanced Mode Failed", f"Falling back to standard mode: {e}")
            
            # Fallback to standard mode
            return self._run_standard_mode()
    
    def _run_standard_mode(self):
        """Run with standard functionality using restored downloading_en.py"""
        
        log_msg("📦 Running in standard mode using restored functionality", VerbosityLevel.NORMAL)
        
        try:
            # Direct execution of restored main function
            log_msg("🔄 Executing restored downloading system...", VerbosityLevel.NORMAL)
            
            # Call the main function from restored downloading_en.py
            downloading_main()
            
            log_msg("✅ Standard downloading completed successfully", VerbosityLevel.NORMAL)
            return True
            
        except Exception as e:
            log_msg(f"❌ Standard mode execution failed: {e}", VerbosityLevel.MINIMAL)
            return False
    
    def _setup_enhanced_venv(self):
        """Setup enhanced virtual environment"""
        try:
            if self.enhanced_mode:
                log_msg("🔧 Using enhanced venv setup with monitoring...", VerbosityLevel.DETAILED)
                
                # Enhanced setup with monitoring
                result = setup_comprehensive_safe_venv()
                
                if self.enhanced_manager:
                    # Log venv setup details
                    self.enhanced_manager.log_operation("venv_setup", 
                                                      {"success": result, "enhanced": True})
                
                return result
            else:
                # Standard restored functionality
                log_msg("🔧 Using standard venv setup...", VerbosityLevel.DETAILED)
                return setup_comprehensive_safe_venv()
                
        except Exception as e:
            log_msg(f"❌ Venv setup error: {e}", VerbosityLevel.MINIMAL)
            return False
    
    def _install_webui_enhanced(self):
        """Install WebUI with enhanced features"""
        try:
            if self.enhanced_mode:
                log_msg("🚀 Enhanced WebUI installation with monitoring...", VerbosityLevel.DETAILED)
                
                # Enhanced installation with logging
                result = install_webui()
                
                if self.enhanced_manager:
                    # Log WebUI installation details
                    self.enhanced_manager.log_operation("webui_install", 
                                                      {"success": result, "enhanced": True})
                
                return result
            else:
                # Standard restored functionality
                log_msg("🚀 Standard WebUI installation...", VerbosityLevel.DETAILED)
                return install_webui()
                
        except Exception as e:
            log_msg(f"❌ WebUI installation error: {e}", VerbosityLevel.MINIMAL)
            return False
    
    def _download_models_enhanced(self):
        """Download models with enhanced progress tracking"""
        try:
            if self.enhanced_mode and self.batch_ops:
                log_msg("🎨 Enhanced model downloading with batch operations...", VerbosityLevel.DETAILED)
                
                # Use enhanced batch operations for model downloading
                try:
                    # Get download URLs from settings
                    widget_settings = js.read_key('WIDGETS', {})
                    
                    # Create download queue
                    download_queue = []
                    
                    # Add model URLs
                    for key in ['Model_url', 'Vae_url', 'LoRA_url', 'Embedding_url', 'custom_file_urls']:
                        urls_string = widget_settings.get(key, '')
                        if urls_string:
                            urls = [url.strip() for url in urls_string.split(',') if url.strip()]
                            download_queue.extend(urls)
                    
                    if download_queue:
                        # Use enhanced batch operations
                        log_msg(f"📥 Processing {len(download_queue)} downloads with enhanced manager...", VerbosityLevel.DETAILED)
                        result = self.batch_ops.process_download_queue(download_queue)
                        log_msg(f"✅ Enhanced batch download completed: {result}", VerbosityLevel.DETAILED)
                        return True
                    else:
                        log_msg("⚠️ No downloads specified, using standard download process...", VerbosityLevel.DETAILED)
                        
                except Exception as enhanced_error:
                    log_msg(f"⚠️ Enhanced download failed, using standard: {enhanced_error}", VerbosityLevel.DETAILED)
                
                # Fallback to standard download
                return download_models_and_assets()
            else:
                # Standard restored functionality
                log_msg("🎨 Standard model downloading...", VerbosityLevel.DETAILED)
                return download_models_and_assets()
                
        except Exception as e:
            log_msg(f"❌ Model download error: {e}", VerbosityLevel.MINIMAL)
            return False
    
    def _setup_enhanced_monitoring(self):
        """Setup enhanced monitoring and logging"""
        try:
            if self.enhanced_mode:
                log_msg("📊 Setting up enhanced monitoring systems...", VerbosityLevel.DETAILED)
                
                # Setup performance monitoring
                setup_performance_monitoring()
                
                # Setup advanced logging if available
                if ENHANCEMENTS_AVAILABLE:
                    try:
                        logger = get_advanced_logger()
                        logger.log_system_info()
                        logger.start_monitoring()
                        log_msg("✅ Advanced logging and monitoring active", VerbosityLevel.DETAILED)
                    except Exception as e:
                        log_msg(f"⚠️ Advanced logging setup failed: {e}", VerbosityLevel.DETAILED)
                
                return True
            else:
                # Standard monitoring
                log_msg("📊 Setting up standard monitoring...", VerbosityLevel.DETAILED)
                setup_performance_monitoring()
                return True
                
        except Exception as e:
            log_msg(f"⚠️ Monitoring setup error: {e}", VerbosityLevel.DETAILED)
            return False

# Main integration function
def run_enhanced_downloading():
    """Main function to run enhanced downloading with proper integration"""
    
    log_msg("🚀 Starting LSDAI Enhanced Downloading Integration", VerbosityLevel.NORMAL)
    
    # Initialize system
    system = EnhancedDownloadingSystem()
    
    # Execute downloading
    success = system.run_enhanced_downloading()
    
    if success:
        log_msg("🎉 Enhanced downloading completed successfully!", VerbosityLevel.NORMAL)
        log_msg("🚀 Ready to proceed to Cell 4 (Launch)", VerbosityLevel.NORMAL)
    else:
        log_msg("❌ Enhanced downloading failed", VerbosityLevel.MINIMAL)
        log_msg("🔧 Check the output above for error details", VerbosityLevel.MINIMAL)
    
    return success

# Backward compatibility functions
def setup_venv():
    """Backward compatibility wrapper for venv setup"""
    if ORIGINAL_DOWNLOADING_AVAILABLE:
        return setup_comprehensive_safe_venv()
    else:
        log_msg("❌ Original downloading functions not available", VerbosityLevel.MINIMAL)
        return False

def install_webui_and_extensions():
    """Backward compatibility wrapper for WebUI installation"""
    if ORIGINAL_DOWNLOADING_AVAILABLE:
        return install_webui()
    else:
        log_msg("❌ Original downloading functions not available", VerbosityLevel.MINIMAL)
        return False

def download_assets():
    """Backward compatibility wrapper for asset downloading"""
    if ORIGINAL_DOWNLOADING_AVAILABLE:
        return download_models_and_assets()
    else:
        log_msg("❌ Original downloading functions not available", VerbosityLevel.MINIMAL)
        return False

# For direct execution
if __name__ == "__main__":
    success = run_enhanced_downloading()
    
    if not success:
        log_msg("\n" + "="*60, VerbosityLevel.MINIMAL)
        log_msg("🛠️ TROUBLESHOOTING GUIDE", VerbosityLevel.MINIMAL)
        log_msg("="*60, VerbosityLevel.MINIMAL)
        log_msg("If you see errors above:", VerbosityLevel.MINIMAL)
        log_msg("1. Ensure Cell 1 (Setup) completed successfully", VerbosityLevel.MINIMAL)
        log_msg("2. Check that downloading_en.py has been restored", VerbosityLevel.MINIMAL)
        log_msg("3. Verify all modules are properly imported", VerbosityLevel.MINIMAL)
        log_msg("4. Try running Cell 2 (Widgets) again", VerbosityLevel.MINIMAL)
        log_msg("="*60, VerbosityLevel.MINIMAL)

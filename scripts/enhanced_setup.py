# Enhanced setup.py - Maintains original functionality + enhancements
import json_utils as js
from pathlib import Path
import subprocess
import requests
import os
import sys

# Import original setup functionality
from scripts.setup import *  # This imports your existing setup functions

class EnhancedSetup:
    def __init__(self):
        self.original_setup = True
        self.enhancements_available = self._check_enhancements()
        
    def _check_enhancements(self):
        """Check if enhancement modules are available"""
        try:
            import modules.EnhancedManager
            return True
        except ImportError:
            return False
            
    def run_enhanced_setup(self, branch="main"):
        """Run setup with enhancements"""
        print("🚀 LSDAI Enhanced Setup v2.0")
        print("=" * 40)
        
        # Run original setup first
        print("📦 Running original LSDAI setup...")
        try:
            # Call your existing setup functions
            original_setup_result = run_original_setup(branch)
            print("✅ Original setup completed")
        except Exception as e:
            print(f"⚠️  Original setup issue: {e}")
            
        # Setup enhancements if available
        if self.enhancements_available:
            print("✨ Setting up enhancements...")
            self._setup_enhancements()
        else:
            print("📥 Installing enhancements...")
            self._install_enhancements()
            
    def _setup_enhancements(self):
        """Setup enhancement modules"""
        try:
            # Create enhanced directories
            enhancement_dirs = ['modules', 'data', 'logs', 'benchmark_results']
            for dir_name in enhancement_dirs:
                Path(dir_name).mkdir(exist_ok=True)
                
            # Initialize enhancement suite
            from scripts.master_integration import LSDAIEnhancementSuite
            suite = LSDAIEnhancementSuite()
            
            # Quick setup for existing LSDAI users
            suite.configuration = {
                "modules": {
                    "enhanced_download_manager": {"enabled": True},
                    "enhanced_model_manager": {"enabled": True},
                    "notification_system": {"enabled": True},
                    "advanced_logging": {"enabled": True}
                }
            }
            
            print("✅ Enhancements ready!")
            
        except Exception as e:
            print(f"❌ Enhancement setup failed: {e}")
            
    def _install_enhancements(self):
        """Install enhancement modules"""
        print("📥 Downloading enhancement suite...")
        try:
            # Download and install enhancements
            subprocess.run([
                sys.executable, '-m', 'pip', 'install', 
                'git+https://github.com/your-repo/lsdai-enhancements.git'
            ], check=True)
            print("✅ Enhancements installed")
        except Exception as e:
            print(f"❌ Enhancement installation failed: {e}")

# Enhanced entry point
def main():
    enhanced_setup = EnhancedSetup()
    enhanced_setup.run_enhanced_setup()

if __name__ == "__main__":
    main()

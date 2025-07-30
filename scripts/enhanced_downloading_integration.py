#!/usr/bin/env python3
# ~ enhanced_downloading_integration.py | With Complete Verbosity Integration ~

import os
import sys
import json
from pathlib import Path

# Import verbose output manager
from modules.verbose_output_manager import (
    get_verbose_manager, VerbosityLevel, 
    vprint, vrun, vpip_install, vdownload, vgit_clone
)

class VerboseDownloadManager:
    """Download manager with complete verbosity integration"""
    
    def __init__(self):
        self.verbose_manager = get_verbose_manager()
        self.base_path = Path(os.environ.get('home_path', '/content'))
        self.settings_path = Path(os.environ.get('settings_path', '/content/LSDAI/settings.json'))
    
    def setup_venv(self):
        """Setup virtual environment with verbose output"""
        venv_path = self.base_path / 'venv'
        
        vprint("🐍 Setting up virtual environment...", VerbosityLevel.NORMAL)
        vprint(f"   Target path: {venv_path}", VerbosityLevel.DETAILED)
        
        if venv_path.exists():
            vprint("✅ Virtual environment already exists", VerbosityLevel.NORMAL)
            return True
        
        # Create venv with verbose output
        vprint("📦 Creating new virtual environment...", VerbosityLevel.DETAILED)
        
        try:
            # Raw mode shows full python -m venv output
            vrun([sys.executable, '-m', 'venv', str(venv_path)])
            vprint("✅ Virtual environment created successfully", VerbosityLevel.NORMAL)
            return True
        except Exception as e:
            vprint(f"❌ Failed to create virtual environment: {e}", VerbosityLevel.MINIMAL)
            return False
    
    def install_webui(self, webui_type='automatic1111'):
        """Install WebUI with verbose progress tracking"""
        
        webui_configs = {
            'automatic1111': {
                'repo': 'https://github.com/AUTOMATIC1111/stable-diffusion-webui',
                'path': 'stable-diffusion-webui'
            },
            'comfyui': {
                'repo': 'https://github.com/comfyanonymous/ComfyUI',
                'path': 'ComfyUI'
            }
        }
        
        if webui_type not in webui_configs:
            vprint(f"❌ Unknown WebUI type: {webui_type}", VerbosityLevel.MINIMAL)
            return False
        
        config = webui_configs[webui_type]
        install_path = self.base_path / config['path']
        
        vprint(f"🚀 Installing {webui_type} WebUI...", VerbosityLevel.NORMAL)
        vprint(f"   Repository: {config['repo']}", VerbosityLevel.DETAILED)
        vprint(f"   Install path: {install_path}", VerbosityLevel.DETAILED)
        
        # Check if already installed
        if install_path.exists():
            vprint(f"✅ {webui_type} already installed", VerbosityLevel.NORMAL)
            
            # Try to update in verbose modes
            if self.verbose_manager.should_show(VerbosityLevel.DETAILED):
                vprint("🔄 Checking for updates...", VerbosityLevel.DETAILED)
                try:
                    vrun(['git', 'pull'], cwd=install_path)
                    vprint("✅ WebUI updated to latest version", VerbosityLevel.DETAILED)
                except:
                    vprint("⚠️ Could not update WebUI", VerbosityLevel.DETAILED)
            
            return True
        
        # Clone repository with verbose output
        success = vgit_clone(config['repo'], install_path)
        
        if success:
            vprint(f"✅ {webui_type} WebUI installed successfully", VerbosityLevel.NORMAL)
            
            # Install requirements if they exist
            requirements_file = install_path / 'requirements.txt'
            if requirements_file.exists():
                vprint("📦 Installing WebUI requirements...", VerbosityLevel.NORMAL)
                vpip_install(['-r', str(requirements_file)])
        
        return success
    
    def download_models(self):
        """Download selected models with verbose progress"""
        
        # Load selected models from settings
        try:
            with open(self.settings_path, 'r') as f:
                settings = json.load(f)
            
            selected_models = settings.get('WIDGETS', {}).get('model', [])
            selected_vaes = settings.get('WIDGETS', {}).get('vae', [])
            selected_loras = settings.get('WIDGETS', {}).get('lora', [])
            
        except Exception as e:
            vprint(f"❌ Could not load settings: {e}", VerbosityLevel.MINIMAL)
            return False
        
        total_downloads = len(selected_models) + len(selected_vaes) + len(selected_loras)
        
        if total_downloads == 0:
            vprint("⚠️ No models selected for download", VerbosityLevel.NORMAL)
            return True
        
        vprint(f"📥 Starting download of {total_downloads} items...", VerbosityLevel.NORMAL)
        
        # Download models
        success_count = 0
        
        for i, model_name in enumerate(selected_models, 1):
            vprint(f"   [{i}/{len(selected_models)}] Processing model: {model_name}", VerbosityLevel.NORMAL)
            
            # Get model URL from model data
            model_url = self.get_model_url(model_name, 'model')
            if model_url:
                model_path = self.base_path / 'models' / 'Stable-diffusion' / f"{model_name}.safetensors"
                model_path.parent.mkdir(parents=True, exist_ok=True)
                
                if vdownload(model_url, model_path, f"Model: {model_name}"):
                    success_count += 1
            else:
                vprint(f"❌ Could not find URL for model: {model_name}", VerbosityLevel.MINIMAL)
        
        # Download VAEs  
        for i, vae_name in enumerate(selected_vaes, 1):
            vprint(f"   [{i}/{len(selected_vaes)}] Processing VAE: {vae_name}", VerbosityLevel.NORMAL)
            
            vae_url = self.get_model_url(vae_name, 'vae')
            if vae_url:
                vae_path = self.base_path / 'models' / 'VAE' / f"{vae_name}.safetensors"
                vae_path.parent.mkdir(parents=True, exist_ok=True)
                
                if vdownload(vae_url, vae_path, f"VAE: {vae_name}"):
                    success_count += 1
            else:
                vprint(f"❌ Could not find URL for VAE: {vae_name}", VerbosityLevel.MINIMAL)
        
        # Download LoRAs
        for i, lora_name in enumerate(selected_loras, 1):
            vprint(f"   [{i}/{len(selected_loras)}] Processing LoRA: {lora_name}", VerbosityLevel.NORMAL)
            
            lora_url = self.get_model_url(lora_name, 'lora')
            if lora_url:
                lora_path = self.base_path / 'models' / 'Lora' / f"{lora_name}.safetensors"
                lora_path.parent.mkdir(parents=True, exist_ok=True)
                
                if vdownload(lora_url, lora_path, f"LoRA: {lora_name}"):
                    success_count += 1
            else:
                vprint(f"❌ Could not find URL for LoRA: {lora_name}", VerbosityLevel.MINIMAL)
        
        vprint(f"✅ Download completed: {success_count}/{total_downloads} successful", VerbosityLevel.NORMAL)
        return success_count > 0
    
    def get_model_url(self, model_name, model_type):
        """Get model URL from model data with verbose debugging"""
        
        vprint(f"🔍 Looking up URL for {model_type}: {model_name}", VerbosityLevel.VERBOSE)
        
        # Read model data
        scripts_path = Path(os.environ.get('scr_path', '/content/LSDAI')) / 'scripts'
        model_data_file = scripts_path / '_models_data.py'
        
        if not model_data_file.exists():
            vprint(f"❌ Model data file not found: {model_data_file}", VerbosityLevel.DETAILED)
            return None
        
        try:
            # Execute model data file to get the data
            local_vars = {}
            with open(model_data_file) as f:
                exec(f.read(), {}, local_vars)
            
            # Map data type to variable name
            data_map = {
                'model': 'model_list',
                'vae': 'vae_list',
                'lora': 'lora_list',
                'cnet': 'controlnet_list'
            }
            
            data_var = data_map.get(model_type)
            if not data_var or data_var not in local_vars:
                vprint(f"❌ No data found for type: {model_type}", VerbosityLevel.DETAILED)
                return None
            
            model_data = local_vars[data_var]
            
            if model_name in model_data:
                url = model_data[model_name]
                vprint(f"✅ Found URL for {model_name}: {url}", VerbosityLevel.VERBOSE)
                return url
            else:
                vprint(f"❌ Model {model_name} not found in {model_type} data", VerbosityLevel.DETAILED)
                return None
                
        except Exception as e:
            vprint(f"❌ Error reading model data: {e}", VerbosityLevel.DETAILED)
            return None

def main():
    """Main execution function with verbose output"""
    verbose_manager = get_verbose_manager()
    
    vprint("=" * 50, VerbosityLevel.NORMAL)
    vprint("🔥 LSDAI Enhanced Downloader with Verbosity Control", VerbosityLevel.NORMAL)
    vprint("=" * 50, VerbosityLevel.NORMAL)
    
    # Show current verbosity level
    level_names = {
        VerbosityLevel.SILENT: "Silent",
        VerbosityLevel.MINIMAL: "Minimal",
        VerbosityLevel.NORMAL: "Normal", 
        VerbosityLevel.DETAILED: "Detailed",
        VerbosityLevel.VERBOSE: "Verbose",
        VerbosityLevel.RAW: "Raw Output"
    }
    current_level = level_names.get(verbose_manager.verbosity_level, "Unknown")
    vprint(f"🔧 Current verbosity level: {current_level}", VerbosityLevel.MINIMAL)
    
    downloader = VerboseDownloadManager()
    
    # Execute download steps
    steps = [
        ("🐍 1. Setting up Virtual Environment", downloader.setup_venv),
        ("🚀 2. Installing WebUI", lambda: downloader.install_webui('automatic1111')),
        ("📥 3. Downloading Models and Assets", downloader.download_models)
    ]
    
    for step_name, step_func in steps:
        vprint(f"\n{step_name}...", VerbosityLevel.NORMAL)
        
        try:
            with verbose_manager.capture_output() as captured:
                success = step_func()
                
                if not success:
                    vprint(f"❌ {step_name} failed", VerbosityLevel.MINIMAL)
                    return False
                    
                vprint(f"✅ {step_name} completed successfully", VerbosityLevel.NORMAL)
                
        except Exception as e:
            vprint(f"❌ {step_name} failed with error: {e}", VerbosityLevel.MINIMAL)
            return False
    
    vprint("\n🎉 All download operations completed successfully!", VerbosityLevel.NORMAL)
    return True

if __name__ == "__main__":
    main()

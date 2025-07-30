# ~ verbose_output_manager.py | Complete Verbosity Control System for LSDAI - FIXED ~

import os
import sys
import subprocess
import json
from pathlib import Path
from typing import Optional, Dict, Any, List
from contextlib import contextmanager
import threading
import time

class VerbosityLevel:
    """Verbosity level constants"""
    SILENT = 0      # No output except errors
    MINIMAL = 1     # Basic status messages only
    NORMAL = 2      # Standard LSDAI output (current default)
    DETAILED = 3    # Show command outputs and details
    VERBOSE = 4     # Show everything including pip, subprocess, debug info
    RAW = 5         # Raw python output, no filtering whatsoever

class VerboseOutputManager:
    """Global verbosity management system for all LSDAI operations"""
    
    def __init__(self):
        self.verbosity_level = VerbosityLevel.NORMAL
        self.settings_path = Path(os.environ.get('settings_path', '/content/LSDAI/settings.json'))
        self.original_stdout = sys.stdout
        self.original_stderr = sys.stderr
        self.output_buffer = []
        self.real_time_display = True
        
        # Level name mapping
        self.level_names = {
            VerbosityLevel.SILENT: "Silent",
            VerbosityLevel.MINIMAL: "Minimal", 
            VerbosityLevel.NORMAL: "Normal",
            VerbosityLevel.DETAILED: "Detailed",
            VerbosityLevel.VERBOSE: "Verbose",
            VerbosityLevel.RAW: "Raw Output"
        }
        
        # Load verbosity setting from settings.json
        self.load_verbosity_setting()
    
    def get_level_name(self, level: Optional[int] = None) -> str:
        """Get the name of the current or specified verbosity level"""
        if level is None:
            level = self.verbosity_level
        return self.level_names.get(level, "Unknown")
    
    def get_current_level_name(self) -> str:
        """Get the name of the current verbosity level"""
        return self.get_level_name(self.verbosity_level)
    
    def load_verbosity_setting(self):
        """Load verbosity setting from settings.json"""
        try:
            if self.settings_path.exists():
                with open(self.settings_path, 'r') as f:
                    settings = json.load(f)
                
                # Check for explicit verbosity level first
                explicit_level = settings.get('WIDGETS', {}).get('verbosity_level')
                if explicit_level is not None:
                    self.verbosity_level = int(explicit_level)
                    return
                
                # Fall back to detailed_download boolean
                verbosity = settings.get('WIDGETS', {}).get('detailed_download', False)
                if verbosity:
                    self.verbosity_level = VerbosityLevel.RAW
                else:
                    self.verbosity_level = VerbosityLevel.NORMAL
                    
        except Exception as e:
            print(f"Warning: Could not load verbosity setting: {e}")
            self.verbosity_level = VerbosityLevel.NORMAL
    
    def save_verbosity_setting(self, level: int):
        """Save verbosity setting to settings.json"""
        try:
            # Update the settings
            settings = {}
            if self.settings_path.exists():
                with open(self.settings_path, 'r') as f:
                    settings = json.load(f)
            
            if 'WIDGETS' not in settings:
                settings['WIDGETS'] = {}
            
            # Map verbosity levels to detailed_download boolean for backwards compatibility
            settings['WIDGETS']['detailed_download'] = (level >= VerbosityLevel.DETAILED)
            
            # Also save the exact level for internal use
            settings['WIDGETS']['verbosity_level'] = level
            
            with open(self.settings_path, 'w') as f:
                json.dump(settings, f, indent=4)
                
            self.verbosity_level = level
            
            # Set environment variable for other processes
            os.environ['LSDAI_VERBOSITY'] = str(level)
            
        except Exception as e:
            print(f"Warning: Could not save verbosity setting: {e}")
    
    def set_verbosity(self, level: int):
        """Set the global verbosity level"""
        self.save_verbosity_setting(level)
        self.verbosity_level = level
        
        # Notify about the change
        level_name = self.get_level_name(level)
        print(f"🔧 Verbosity level set to: {level_name}")
    
    def should_show(self, required_level: int) -> bool:
        """Check if output should be shown based on current verbosity level"""
        return self.verbosity_level >= required_level
    
    def print_if_verbose(self, message: str, required_level: int = VerbosityLevel.NORMAL):
        """Print message only if verbosity level permits"""
        if self.should_show(required_level):
            print(message)
    
    def run_subprocess(self, cmd: List[str], cwd: Optional[Path] = None, 
                      show_output: bool = None, **kwargs) -> subprocess.CompletedProcess:
        """Run subprocess with verbosity-aware output handling"""
        
        if show_output is None:
            show_output = self.should_show(VerbosityLevel.DETAILED)
        
        # Show command if detailed level or higher
        if self.should_show(VerbosityLevel.DETAILED):
            cmd_str = ' '.join(str(c) for c in cmd)
            print(f"🔧 Running command: {cmd_str}")
            if cwd:
                print(f"   Working directory: {cwd}")
        
        # Determine output handling based on verbosity
        if self.verbosity_level >= VerbosityLevel.RAW:
            # Raw mode - show everything in real time
            stdout = None
            stderr = None
        elif self.verbosity_level >= VerbosityLevel.VERBOSE:
            # Verbose mode - capture and display
            stdout = subprocess.PIPE
            stderr = subprocess.STDOUT
        elif self.verbosity_level >= VerbosityLevel.DETAILED:
            # Detailed mode - capture key output
            stdout = subprocess.PIPE
            stderr = subprocess.STDOUT
        else:
            # Normal/Minimal/Silent - capture everything
            stdout = subprocess.PIPE
            stderr = subprocess.PIPE
        
        try:
            if cwd:
                result = subprocess.run(cmd, cwd=cwd, stdout=stdout, stderr=stderr, 
                                      text=True, check=True, **kwargs)
            else:
                result = subprocess.run(cmd, stdout=stdout, stderr=stderr, 
                                      text=True, check=True, **kwargs)
            
            # Handle captured output
            if result.stdout and self.should_show(VerbosityLevel.VERBOSE):
                print(result.stdout)
            
            return result
            
        except subprocess.CalledProcessError as e:
            # Always show errors regardless of verbosity level
            print(f"❌ Command failed with exit code {e.returncode}")
            if e.stdout and self.should_show(VerbosityLevel.MINIMAL):
                print(f"Output: {e.stdout}")
            if e.stderr and self.should_show(VerbosityLevel.MINIMAL):
                print(f"Error: {e.stderr}")
            raise
    
    def run_pip_install(self, packages: List[str], upgrade: bool = False, 
                       force_reinstall: bool = False, **kwargs) -> bool:
        """Run pip install with verbosity-aware output"""
        
        pip_cmd = [sys.executable, "-m", "pip", "install"]
        
        # Add verbosity flags based on current level
        if self.verbosity_level <= VerbosityLevel.MINIMAL:
            pip_cmd.append("-q")  # Quiet mode
        elif self.verbosity_level >= VerbosityLevel.VERBOSE:
            pip_cmd.append("-v")  # Verbose mode
        
        if upgrade:
            pip_cmd.append("--upgrade")
        if force_reinstall:
            pip_cmd.append("--force-reinstall")
        
        pip_cmd.extend(packages)
        
        if self.should_show(VerbosityLevel.NORMAL):
            package_list = ', '.join(packages)
            print(f"📦 Installing packages: {package_list}")
        
        try:
            self.run_subprocess(pip_cmd, **kwargs)
            
            if self.should_show(VerbosityLevel.NORMAL):
                print(f"✅ Packages installed successfully")
            
            return True
            
        except subprocess.CalledProcessError:
            print(f"❌ Failed to install packages: {', '.join(packages)}")
            return False
    
    def download_file(self, url: str, destination: Path, description: str = None) -> bool:
        """Download file with verbosity-aware progress display"""
        
        if description is None:
            description = f"file to {destination.name}"
        
        if self.should_show(VerbosityLevel.NORMAL):
            print(f"📥 Downloading {description}...")
            if self.should_show(VerbosityLevel.DETAILED):
                print(f"   URL: {url}")
                print(f"   Destination: {destination}")
        
        # Choose download method based on verbosity
        if self.verbosity_level >= VerbosityLevel.VERBOSE:
            # Use wget with progress bar
            wget_cmd = ["wget", "--progress=bar", "-O", str(destination), url]
        elif self.verbosity_level >= VerbosityLevel.DETAILED:
            # Use wget with minimal progress
            wget_cmd = ["wget", "--progress=dot", "-O", str(destination), url]
        else:
            # Use wget quietly
            wget_cmd = ["wget", "-q", "-O", str(destination), url]
        
        try:
            self.run_subprocess(wget_cmd)
            
            if self.should_show(VerbosityLevel.NORMAL):
                print(f"✅ Downloaded {description} successfully")
            
            return True
            
        except subprocess.CalledProcessError:
            print(f"❌ Failed to download {description}")
            return False
    
    def git_clone(self, repo_url: str, destination: Path, branch: str = None) -> bool:
        """Git clone with verbosity-aware output"""
        
        git_cmd = ["git", "clone"]
        
        if self.verbosity_level < VerbosityLevel.DETAILED:
            git_cmd.append("-q")  # Quiet mode
        elif self.verbosity_level >= VerbosityLevel.VERBOSE:
            git_cmd.append("--progress")  # Show progress
        
        if branch:
            git_cmd.extend(["-b", branch])
        
        git_cmd.extend([repo_url, str(destination)])
        
        if self.should_show(VerbosityLevel.NORMAL):
            print(f"📥 Cloning repository: {repo_url}")
            if self.should_show(VerbosityLevel.DETAILED):
                print(f"   Destination: {destination}")
                if branch:
                    print(f"   Branch: {branch}")
        
        try:
            self.run_subprocess(git_cmd)
            
            if self.should_show(VerbosityLevel.NORMAL):
                print(f"✅ Repository cloned successfully")
            
            return True
            
        except subprocess.CalledProcessError:
            print(f"❌ Failed to clone repository: {repo_url}")
            return False

    @contextmanager
    def capture_output(self):
        """Context manager to capture all output during operations"""
        if self.verbosity_level < VerbosityLevel.RAW:
            # Only capture if not in raw mode
            captured_output = []
            
            class OutputCapture:
                def write(self, text):
                    captured_output.append(text)
                    if verbose_manager.should_show(VerbosityLevel.VERBOSE):
                        verbose_manager.original_stdout.write(text)
                
                def flush(self):
                    if hasattr(verbose_manager.original_stdout, 'flush'):
                        verbose_manager.original_stdout.flush()
            
            old_stdout = sys.stdout
            old_stderr = sys.stderr
            
            capture = OutputCapture()
            sys.stdout = capture
            sys.stderr = capture
            
            try:
                yield captured_output
            finally:
                sys.stdout = old_stdout
                sys.stderr = old_stderr
        else:
            # Raw mode - no capture
            yield []

# Global instance
verbose_manager = VerboseOutputManager()

def get_verbose_manager() -> VerboseOutputManager:
    """Get the global verbose output manager"""
    return verbose_manager

def set_global_verbosity(level: int):
    """Set global verbosity level"""
    verbose_manager.set_verbosity(level)

def should_show_verbose(required_level: int = VerbosityLevel.NORMAL) -> bool:
    """Check if output should be shown"""
    return verbose_manager.should_show(required_level)

def vprint(message: str, level: int = VerbosityLevel.NORMAL):
    """Verbosity-aware print function"""
    verbose_manager.print_if_verbose(message, level)

def vrun(cmd: List[str], **kwargs) -> subprocess.CompletedProcess:
    """Verbosity-aware subprocess run"""
    return verbose_manager.run_subprocess(cmd, **kwargs)

def vpip_install(packages: List[str], **kwargs) -> bool:
    """Verbosity-aware pip install"""
    return verbose_manager.run_pip_install(packages, **kwargs)

def vdownload(url: str, destination: Path, description: str = None) -> bool:
    """Verbosity-aware file download"""
    return verbose_manager.download_file(url, destination, description)

def vgit_clone(repo_url: str, destination: Path, branch: str = None) -> bool:
    """Verbosity-aware git clone"""
    return verbose_manager.git_clone(repo_url, destination, branch)

# Auto-load verbosity setting on import
try:
    verbose_manager.load_verbosity_setting()
except:
    pass  # Silently ignore errors during import

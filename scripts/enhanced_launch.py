# Enhanced WebUI Launcher with Performance Optimization
# Save as: scripts/enhanced-launch.py

import json_utils as js
from pathlib import Path
import subprocess
import threading
import psutil
import GPUtil
import signal
import time
import json
import sys
import os
import re

class SystemOptimizer:
    """System optimization for better WebUI performance"""
    
    def __init__(self):
        self.original_settings = {}
        self.optimizations_applied = False
        
    def detect_system_specs(self):
        """Detect system specifications"""
        specs = {
            'cpu_count': psutil.cpu_count(),
            'ram_total_gb': psutil.virtual_memory().total / (1024**3),
            'ram_available_gb': psutil.virtual_memory().available / (1024**3),
            'gpu_info': self._get_gpu_info(),
            'platform': sys.platform,
            'is_colab': 'google.colab' in sys.modules,
            'is_kaggle': 'kaggle' in os.environ.get('KAGGLE_KERNEL_RUN_TYPE', ''),
            'cuda_available': self._check_cuda()
        }
        
        return specs
        
    def _get_gpu_info(self):
        """Get GPU information"""
        try:
            gpus = GPUtil.getGPUs()
            if gpus:
                gpu = gpus[0]  # Primary GPU
                return {
                    'name': gpu.name,
                    'memory_total_gb': gpu.memoryTotal / 1024,
                    'memory_free_gb': gpu.memoryFree / 1024,
                    'memory_used_gb': gpu.memoryUsed / 1024,
                    'driver_version': gpu.driver,
                    'uuid': gpu.uuid
                }
        except Exception:
            pass
            
        # Fallback: try nvidia-smi
        try:
            result = subprocess.run(['nvidia-smi', '--query-gpu=name,memory.total,memory.free,driver_version', '--format=csv,nounits,noheader'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                if lines:
                    parts = lines[0].split(', ')
                    return {
                        'name': parts[0],
                        'memory_total_gb': float(parts[1]) / 1024,
                        'memory_free_gb': float(parts[2]) / 1024,
                        'driver_version': parts[3]
                    }
        except Exception:
            pass
            
        return None
        
    def _check_cuda(self):
        """Check if CUDA is available"""
        try:
            result = subprocess.run(['nvidia-smi'], capture_output=True)
            return result.returncode == 0
        except Exception:
            return False
            
    def apply_optimizations(self, specs, webui_type='automatic1111'):
        """Apply system optimizations based on specs"""
        optimizations = []
        
        # Memory optimizations
        if specs['ram_total_gb'] < 16:
            optimizations.extend([
                '--lowvram',
                '--precision=full',
                '--no-half-vae'
            ])
        elif specs['ram_total_gb'] < 32:
            optimizations.extend([
                '--medvram',
                '--opt-split-attention'
            ])
            
        # GPU optimizations
        gpu_info = specs.get('gpu_info')
        if gpu_info:
            if gpu_info['memory_total_gb'] < 6:
                optimizations.extend([
                    '--lowvram',
                    '--always-batch-cond-uncond'
                ])
            elif gpu_info['memory_total_gb'] < 12:
                optimizations.extend([
                    '--medvram',
                    '--opt-channelslast'
                ])
            else:
                optimizations.extend([
                    '--no-half',
                    '--precision=full'
                ])
                
        # Platform-specific optimizations
        if specs['is_colab']:
            optimizations.extend([
                '--share',
                '--enable-insecure-extension-access',
                '--xformers'
            ])
            
        if specs['is_kaggle']:
            optimizations.extend([
                '--listen',
                '--port=7860'
            ])
            
        # CPU optimizations
        if specs['cpu_count'] >= 8:
            optimizations.append(f'--api-server-stop-timeout={min(specs["cpu_count"] * 2, 60)}')
            
        self.optimizations_applied = True
        return optimizations
        
    def optimize_environment(self):
        """Optimize environment variables"""
        env_optimizations = {
            'PYTORCH_CUDA_ALLOC_CONF': 'max_split_size_mb:128',
            'CUDA_LAUNCH_BLOCKING': '0',
            'TOKENIZERS_PARALLELISM': 'false',
            'TRANSFORMERS_CACHE': '/tmp/transformers_cache',
            'HF_HOME': '/tmp/huggingface_cache'
        }
        
        for key, value in env_optimizations.items():
            if key not in os.environ:
                os.environ[key] = value
                
    def monitor_resources(self, callback=None, interval=5):
        """Monitor system resources during WebUI operation"""
        def monitor_loop():
            while True:
                try:
                    cpu_usage = psutil.cpu_percent(interval=1)
                    memory = psutil.virtual_memory()
                    
                    gpu_info = None
                    try:
                        gpus = GPUtil.getGPUs()
                        if gpus:
                            gpu = gpus[0]
                            gpu_info = {
                                'usage': gpu.load * 100,
                                'memory_usage': (gpu.memoryUsed / gpu.memoryTotal) * 100,
                                'temperature': gpu.temperature
                            }
                    except Exception:
                        pass
                        
                    stats = {
                        'timestamp': time.time(),
                        'cpu_usage': cpu_usage,
                        'memory_usage': memory.percent,
                        'memory_available_gb': memory.available / (1024**3),
                        'gpu_info': gpu_info
                    }
                    
                    if callback:
                        callback(stats)
                        
                except Exception as e:
                    print(f"Resource monitoring error: {e}")
                    
                time.sleep(interval)
                
        monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        monitor_thread.start()
        return monitor_thread

class WebUIManager:
    """Advanced WebUI management with process control"""
    
    def __init__(self):
        self.process = None
        self.optimizer = SystemOptimizer()
        self.launch_config = {}
        self.status_callbacks = []
        self.log_callbacks = []
        self.auto_restart = False
        
    def add_status_callback(self, callback):
        """Add status change callback"""
        self.status_callbacks.append(callback)
        
    def add_log_callback(self, callback):
        """Add log output callback"""
        self.log_callbacks.append(callback)
        
    def _notify_status(self, status, message=""):
        """Notify status callbacks"""
        for callback in self.status_callbacks:
            try:
                callback(status, message)
            except Exception as e:
                print(f"Status callback error: {e}")
                
    def _notify_log(self, line):
        """Notify log callbacks"""
        for callback in self.log_callbacks:
            try:
                callback(line)
            except Exception as e:
                print(f"Log callback error: {e}")
                
    def prepare_launch(self, webui_type='automatic1111'):
        """Prepare WebUI launch with optimization"""
        print("🔧 Preparing WebUI launch...")
        
        # Detect system specs
        specs = self.optimizer.detect_system_specs()
        print(f"📊 System specs detected:")
        print(f"   CPU: {specs['cpu_count']} cores")
        print(f"   RAM: {specs['ram_total_gb']:.1f} GB total, {specs['ram_available_gb']:.1f} GB available")
        
        if specs['gpu_info']:
            gpu = specs['gpu_info']
            print(f"   GPU: {gpu['name']} ({gpu['memory_total_gb']:.1f} GB)")
        else:
            print("   GPU: Not detected")
            
        # Apply optimizations
        optimizations = self.optimizer.apply_optimizations(specs, webui_type)
        print(f"⚡ Applied {len(optimizations)} optimizations")
        
        # Optimize environment
        self.optimizer.optimize_environment()
        
        self.launch_config = {
            'specs': specs,
            'optimizations': optimizations,
            'webui_type': webui_type
        }
        
        return self.launch_config
        
    def launch_webui(self, webui_path, args=None, auto_restart=True):
        """Launch WebUI with enhanced configuration"""
        self.auto_restart = auto_restart
        
        if not self.launch_config:
            self.prepare_launch()
            
        # Build command
        cmd = self._build_launch_command(webui_path, args)
        
        print(f"🚀 Launching WebUI...")
        print(f"Command: {' '.join(cmd[:3])}...")  # Show first few parts
        
        try:
            # Start process
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1,
                cwd=webui_path
            )
            
            self._notify_status('starting', 'WebUI process started')
            
            # Start output monitoring
            self._start_output_monitoring()
            
            # Start resource monitoring
            self.optimizer.monitor_resources(self._resource_callback)
            
            return True
            
        except Exception as e:
            print(f"❌ Launch failed: {e}")
            self._notify_status('error', str(e))
            return False
            
    def _build_launch_command(self, webui_path, additional_args=None):
        """Build WebUI launch command"""
        webui_path = Path(webui_path)
        
        # Determine launch script
        if (webui_path / 'webui.py').exists():
            cmd = [sys.executable, 'webui.py']
        elif (webui_path / 'launch.py').exists():
            cmd = [sys.executable, 'launch.py']
        elif (webui_path / 'webui.sh').exists():
            cmd = ['bash', 'webui.sh']
        else:
            raise FileNotFoundError("No launch script found")
            
        # Add optimizations
        if 'optimizations' in self.launch_config:
            cmd.extend(self.launch_config['optimizations'])
            
        # Add user arguments
        if additional_args:
            if isinstance(additional_args, str):
                cmd.extend(additional_args.split())
            elif isinstance(additional_args, list):
                cmd.extend(additional_args)
                
        return cmd
        
    def _start_output_monitoring(self):
        """Start monitoring WebUI output"""
        def monitor_output():
            startup_patterns = [
                r'Running on local URL:\s*(http://[^\s]+)',
                r'Running on public URL:\s*(https://[^\s]+)',
                r'Model loaded',
                r'Startup time:',
                r'ERROR',
                r'CRITICAL'
            ]
            
            compiled_patterns = [(pattern, re.compile(pattern, re.IGNORECASE)) for pattern in startup_patterns]
            
            while self.process and self.process.poll() is None:
                try:
                    line = self.process.stdout.readline()
                    if not line:
                        break
                        
                    line = line.strip()
                    if line:
                        self._notify_log(line)
                        
                        # Check for important events
                        for pattern_name, pattern in compiled_patterns:
                            match = pattern.search(line)
                            if match:
                                if 'Running on' in pattern_name:
                                    url = match.group(1)
                                    self._notify_status('running', f'WebUI available at: {url}')
                                elif 'Model loaded' in pattern_name:
                                    self._notify_status('ready', 'Model loaded successfully')
                                elif 'ERROR' in pattern_name or 'CRITICAL' in pattern_name:
                                    self._notify_status('error', line)
                                    
                except Exception as e:
                    print(f"Output monitoring error: {e}")
                    break
                    
            # Process ended
            if self.process:
                exit_code = self.process.poll()
                if exit_code != 0 and self.auto_restart:
                    print("🔄 WebUI crashed, attempting restart...")
                    self._notify_status('restarting', f'Process crashed with exit code {exit_code}')
                    time.sleep(5)
                    # Auto-restart logic would go here
                else:
                    self._notify_status('stopped', f'Process ended with exit code {exit_code}')
                    
        monitor_thread = threading.Thread(target=monitor_output, daemon=True)
        monitor_thread.start()
        
    def _resource_callback(self, stats):
        """Handle resource monitoring updates"""
        # Log resource usage periodically
        if int(stats['timestamp']) % 30 == 0:  # Every 30 seconds
            print(f"📊 Resources: CPU {stats['cpu_usage']:.1f}%, RAM {stats['memory_usage']:.1f}%", end="")
            if stats['gpu_info']:
                gpu = stats['gpu_info']
                print(f", GPU {gpu['usage']:.1f}% ({gpu['memory_usage']:.1f}% VRAM)")
            else:
                print()
                
        # Check for resource issues
        if stats['memory_usage'] > 90:
            self._notify_status('warning', 'High memory usage detected')
            
        if stats['gpu_info'] and stats['gpu_info']['memory_usage'] > 95:
            self._notify_status('warning', 'High GPU memory usage detected')
            
    def stop_webui(self, timeout=30):
        """Stop WebUI gracefully"""
        if not self.process:
            return True
            
        print("🛑 Stopping WebUI...")
        self._notify_status('stopping', 'Shutdown initiated')
        
        try:
            # Try graceful shutdown first
            self.process.terminate()
            
            # Wait for graceful shutdown
            try:
                self.process.wait(timeout=timeout)
                print("✅ WebUI stopped gracefully")
                self._notify_status('stopped', 'Shutdown completed')
                return True
            except subprocess.TimeoutExpired:
                print("⚠️  Graceful shutdown timeout, forcing...")
                
            # Force kill if needed
            self.process.kill()
            self.process.wait()
            print("✅ WebUI force stopped")
            self._notify_status('stopped', 'Forced shutdown completed')
            return True
            
        except Exception as e:
            print(f"❌ Stop error: {e}")
            self._notify_status('error', f'Stop error: {e}')
            return False
        finally:
            self.process = None
            
    def restart_webui(self):
        """Restart WebUI"""
        if self.process:
            self.stop_webui()
            
        # Wait a moment before restart
        time.sleep(2)
        
        # Re-launch with same configuration
        return self.launch_webui()
        
    def get_status(self):
        """Get current WebUI status"""
        if not self.process:
            return 'stopped'
        elif self.process.poll() is None:
            return 'running'
        else:
            return 'crashed'
            
    def get_urls(self):
        """Get WebUI URLs if available"""
        # This would be populated by the output monitoring
        # For now, return common defaults
        return {
            'local': 'http://127.0.0.1:7860',
            'public': None  # Would be set when detected
        }

class LaunchProfileManager:
    """Manage different launch profiles for different use cases"""
    
    def __init__(self):
        self.profiles = self._load_default_profiles()
        self.custom_profiles = self._load_custom_profiles()
        
    def _load_default_profiles(self):
        """Load default launch profiles"""
        return {
            'fast_generation': {
                'name': 'Fast Generation',
                'description': 'Optimized for speed, lower quality',
                'args': ['--opt-channelslast', '--opt-split-attention', '--lowvram']
            },
            'high_quality': {
                'name': 'High Quality',
                'description': 'Optimized for quality, slower generation',
                'args': ['--no-half', '--precision=full', '--disable-safe-unpickle']
            },
            'low_memory': {
                'name': 'Low Memory',
                'description': 'For systems with limited RAM/VRAM',
                'args': ['--lowvram', '--always-batch-cond-uncond', '--medvram']
            },
            'development': {
                'name': 'Development',
                'description': 'For extension development and testing',
                'args': ['--enable-insecure-extension-access', '--api', '--api-log']
            },
            'colab_optimized': {
                'name': 'Colab Optimized',
                'description': 'Optimized for Google Colab environment',
                'args': ['--share', '--enable-insecure-extension-access', '--xformers', '--opt-channelslast']
            }
        }
        
    def _load_custom_profiles(self):
        """Load custom user profiles"""
        try:
            profiles_file = Path('data/launch_profiles.json')
            if profiles_file.exists():
                with open(profiles_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading custom profiles: {e}")
            
        return {}
        
    def get_profile(self, profile_name):
        """Get launch profile by name"""
        if profile_name in self.profiles:
            return self.profiles[profile_name]
        elif profile_name in self.custom_profiles:
            return self.custom_profiles[profile_name]
        else:
            return None
            
    def save_custom_profile(self, name, args, description=""):
        """Save a custom launch profile"""
        self.custom_profiles[name] = {
            'name': name,
            'description': description,
            'args': args
        }
        
        # Save to file
        try:
            profiles_file = Path('data/launch_profiles.json')
            profiles_file.parent.mkdir(exist_ok=True)
            
            with open(profiles_file, 'w') as f:
                json.dump(self.custom_profiles, f, indent=2)
                
            return True
        except Exception as e:
            print(f"Error saving profile: {e}")
            return False

# Enhanced launch function integrating all components
def enhanced_launch_webui():
    """Enhanced WebUI launcher with all optimizations"""
    
    # Load settings
    try:
        settings = js.read(js.SETTINGS_PATH)
        widgets_settings = settings.get('WIDGETS', {})
    except Exception as e:
        print(f"⚠️  Could not load settings: {e}")
        widgets_settings = {}
        
    # Initialize managers
    webui_manager = WebUIManager()
    profile_manager = LaunchProfileManager()
    
    # Setup status callback for user feedback
    def status_callback(status, message):
        print(f"🔄 Status: {status} - {message}")
        
    def log_callback(line):
        # Filter and display important log lines
        if any(keyword in line.lower() for keyword in ['error', 'warning', 'model loaded', 'running on']):
            print(f"📋 {line}")
            
    webui_manager.add_status_callback(status_callback)
    webui_manager.add_log_callback(log_callback)
    
    # Prepare launch
    webui_type = widgets_settings.get('change_webui', 'automatic1111')
    config = webui_manager.prepare_launch(webui_type)
    
    # Get WebUI path
    webui_path = Path(os.getcwd()) / 'stable-diffusion-webui'
    if not webui_path.exists():
        webui_path = Path(os.getcwd()) / 'ComfyUI'
        
    if not webui_path.exists():
        print("❌ WebUI installation not found!")
        return False
        
    # Get launch arguments
    launch_args = widgets_settings.get('commandline_arguments', '')
    
    # Apply launch profile if specified
    launch_profile = widgets_settings.get('launch_profile', 'auto')
    if launch_profile != 'auto':
        profile = profile_manager.get_profile(launch_profile)
        if profile:
            print(f"📋 Using launch profile: {profile['name']}")
            launch_args = ' '.join(profile['args']) + ' ' + launch_args
            
    # Launch WebUI
    success = webui_manager.launch_webui(
        webui_path=webui_path,
        args=launch_args,
        auto_restart=widgets_settings.get('auto_restart', True)
    )
    
    if success:
        print("🎉 WebUI launched successfully!")
        
        # Keep the script running to monitor the WebUI
        try:
            while webui_manager.get_status() == 'running':
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Shutdown requested...")
            webui_manager.stop_webui()
            
    return success

# For backward compatibility with existing launch.py
if __name__ == "__main__":
    enhanced_launch_webui()

# AdvancedLogging.py - Advanced Logging and Monitoring System for LSDAI
# Provides comprehensive logging, monitoring, and system information tracking

import os
import json
import time
import threading
import psutil
import platform
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import subprocess

# Get environment paths
HOME = Path(os.environ.get('home_path', '/content'))
SCR_PATH = Path(os.environ.get('scr_path', HOME / 'LSDAI'))
LOGS_PATH = SCR_PATH / 'logs'

class SystemMonitor:
    """Monitor system resources and performance"""
    
    def __init__(self):
        self.monitoring = False
        self.monitor_thread = None
        self.system_stats = []
        self.max_stats_history = 1000
        
    def start_monitoring(self, interval: float = 5.0):
        """Start system monitoring"""
        if self.monitoring:
            return
        
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, args=(interval,))
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        print("📊 System monitoring started")
    
    def stop_monitoring(self):
        """Stop system monitoring"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1)
        print("📊 System monitoring stopped")
    
    def _monitor_loop(self, interval: float):
        """Main monitoring loop"""
        while self.monitoring:
            try:
                stats = self.get_current_stats()
                self.system_stats.append(stats)
                
                # Keep only recent stats
                if len(self.system_stats) > self.max_stats_history:
                    self.system_stats = self.system_stats[-self.max_stats_history:]
                
                time.sleep(interval)
            except Exception as e:
                print(f"Monitoring error: {e}")
                time.sleep(interval)
    
    def get_current_stats(self) -> Dict[str, Any]:
        """Get current system statistics"""
        try:
            # CPU stats
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            
            # Memory stats
            memory = psutil.virtual_memory()
            
            # Disk stats
            disk = psutil.disk_usage('/')
            
            # GPU stats (if available)
            gpu_stats = self._get_gpu_stats()
            
            return {
                'timestamp': datetime.now().isoformat(),
                'cpu': {
                    'percent': cpu_percent,
                    'count': cpu_count,
                    'per_core': psutil.cpu_percent(percpu=True)
                },
                'memory': {
                    'total': memory.total,
                    'available': memory.available,
                    'percent': memory.percent,
                    'used': memory.used
                },
                'disk': {
                    'total': disk.total,
                    'used': disk.used,
                    'free': disk.free,
                    'percent': (disk.used / disk.total) * 100
                },
                'gpu': gpu_stats
            }
        except Exception as e:
            return {
                'timestamp': datetime.now().isoformat(),
                'error': str(e)
            }
    
    def _get_gpu_stats(self) -> Dict[str, Any]:
        """Get GPU statistics if available"""
        try:
            # Try nvidia-smi
            result = subprocess.run([
                'nvidia-smi', '--query-gpu=memory.used,memory.total,utilization.gpu,temperature.gpu',
                '--format=csv,noheader,nounits'
            ], capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                gpus = []
                
                for i, line in enumerate(lines):
                    parts = line.split(', ')
                    if len(parts) >= 4:
                        gpus.append({
                            'id': i,
                            'memory_used': int(parts[0]),
                            'memory_total': int(parts[1]),
                            'utilization': int(parts[2]),
                            'temperature': int(parts[3])
                        })
                
                return {'nvidia': gpus, 'available': True}
            else:
                return {'available': False, 'error': 'nvidia-smi not available'}
                
        except Exception as e:
            return {'available': False, 'error': str(e)}
    
    def get_stats_summary(self, minutes: int = 60) -> Dict[str, Any]:
        """Get summary of stats for the last N minutes"""
        if not self.system_stats:
            return {'error': 'No stats available'}
        
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        recent_stats = [
            stat for stat in self.system_stats 
            if datetime.fromisoformat(stat['timestamp']) > cutoff_time
        ]
        
        if not recent_stats:
            return {'error': 'No recent stats available'}
        
        # Calculate averages
        cpu_values = [stat['cpu']['percent'] for stat in recent_stats if 'cpu' in stat]
        memory_values = [stat['memory']['percent'] for stat in recent_stats if 'memory' in stat]
        
        return {
            'timeframe_minutes': minutes,
            'sample_count': len(recent_stats),
            'cpu': {
                'average': sum(cpu_values) / len(cpu_values) if cpu_values else 0,
                'max': max(cpu_values) if cpu_values else 0,
                'min': min(cpu_values) if cpu_values else 0
            },
            'memory': {
                'average': sum(memory_values) / len(memory_values) if memory_values else 0,
                'max': max(memory_values) if memory_values else 0,
                'min': min(memory_values) if memory_values else 0
            },
            'latest': recent_stats[-1] if recent_stats else {}
        }

class AdvancedLogger:
    """Advanced logging system with multiple output formats and levels"""
    
    def __init__(self, log_name: str = "lsdai"):
        self.log_name = log_name
        self.log_file = LOGS_PATH / f"{log_name}.log"
        self.json_log_file = LOGS_PATH / f"{log_name}.json"
        self.max_log_size = 10 * 1024 * 1024  # 10MB
        self.max_json_entries = 10000
        
        # Ensure logs directory exists
        LOGS_PATH.mkdir(parents=True, exist_ok=True)
        
        # Initialize log files
        self._init_log_files()
    
    def _init_log_files(self):
        """Initialize log files if they don't exist"""
        if not self.log_file.exists():
            self.log_file.touch()
        
        if not self.json_log_file.exists():
            initial_data = {
                'log_name': self.log_name,
                'created': datetime.now().isoformat(),
                'entries': []
            }
            with open(self.json_log_file, 'w') as f:
                json.dump(initial_data, f, indent=2)
    
    def _rotate_log_if_needed(self):
        """Rotate log file if it gets too large"""
        try:
            if self.log_file.exists() and self.log_file.stat().st_size > self.max_log_size:
                # Rotate log file
                backup_file = self.log_file.with_suffix('.log.old')
                if backup_file.exists():
                    backup_file.unlink()
                self.log_file.rename(backup_file)
                self.log_file.touch()
        except Exception as e:
            print(f"Log rotation error: {e}")
    
    def log(self, level: str, message: str, category: str = "general", extra_data: Dict = None):
        """Log a message with specified level"""
        timestamp = datetime.now()
        
        # Format for text log
        text_entry = f"[{timestamp.strftime('%Y-%m-%d %H:%M:%S')}] [{level.upper()}] [{category}] {message}"
        
        # Write to text log
        try:
            self._rotate_log_if_needed()
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(text_entry + '\n')
        except Exception as e:
            print(f"Text log write error: {e}")
        
        # Prepare JSON entry
        json_entry = {
            'timestamp': timestamp.isoformat(),
            'level': level.upper(),
            'category': category,
            'message': message
        }
        
        if extra_data:
            json_entry['extra'] = extra_data
        
        # Write to JSON log
        try:
            # Read existing JSON log
            with open(self.json_log_file, 'r') as f:
                log_data = json.load(f)
            
            # Add new entry
            log_data['entries'].append(json_entry)
            
            # Keep only recent entries
            if len(log_data['entries']) > self.max_json_entries:
                log_data['entries'] = log_data['entries'][-self.max_json_entries:]
            
            # Write back
            with open(self.json_log_file, 'w') as f:
                json.dump(log_data, f, indent=2)
                
        except Exception as e:
            print(f"JSON log write error: {e}")
        
        # Also print to console for immediate feedback
        print(text_entry)
    
    def info(self, message: str, category: str = "general", extra_data: Dict = None):
        """Log info message"""
        self.log("info", message, category, extra_data)
    
    def warning(self, message: str, category: str = "general", extra_data: Dict = None):
        """Log warning message"""
        self.log("warning", message, category, extra_data)
    
    def error(self, message: str, category: str = "general", extra_data: Dict = None):
        """Log error message"""
        self.log("error", message, category, extra_data)
    
    def debug(self, message: str, category: str = "general", extra_data: Dict = None):
        """Log debug message"""
        self.log("debug", message, category, extra_data)
    
    def success(self, message: str, category: str = "general", extra_data: Dict = None):
        """Log success message"""
        self.log("success", message, category, extra_data)
    
    def log_system_info(self):
        """Log comprehensive system information"""
        self.info("Logging system information", "system")
        
        # Platform info
        system_info = {
            'platform': platform.platform(),
            'system': platform.system(),
            'release': platform.release(),
            'version': platform.version(),
            'machine': platform.machine(),
            'processor': platform.processor(),
            'python_version': platform.python_version()
        }
        
        self.info("System platform information", "system", system_info)
        
        # CPU info
        try:
            cpu_info = {
                'physical_cores': psutil.cpu_count(logical=False),
                'total_cores': psutil.cpu_count(logical=True),
                'max_frequency': psutil.cpu_freq().max if psutil.cpu_freq() else None,
                'current_frequency': psutil.cpu_freq().current if psutil.cpu_freq() else None
            }
            self.info("CPU information", "system", cpu_info)
        except Exception as e:
            self.error(f"Could not get CPU info: {e}", "system")
        
        # Memory info
        try:
            memory = psutil.virtual_memory()
            memory_info = {
                'total_gb': round(memory.total / (1024**3), 2),
                'available_gb': round(memory.available / (1024**3), 2),
                'percent_used': memory.percent
            }
            self.info("Memory information", "system", memory_info)
        except Exception as e:
            self.error(f"Could not get memory info: {e}", "system")
        
        # Disk info
        try:
            disk = psutil.disk_usage('/')
            disk_info = {
                'total_gb': round(disk.total / (1024**3), 2),
                'used_gb': round(disk.used / (1024**3), 2),
                'free_gb': round(disk.free / (1024**3), 2),
                'percent_used': round((disk.used / disk.total) * 100, 2)
            }
            self.info("Disk information", "system", disk_info)
        except Exception as e:
            self.error(f"Could not get disk info: {e}", "system")
        
        # Environment info
        env_info = {
            'home_path': os.environ.get('home_path', 'Not set'),
            'scr_path': os.environ.get('scr_path', 'Not set'),
            'venv_path': os.environ.get('venv_path', 'Not set'),
            'colab_detected': 'COLAB_GPU' in os.environ,
            'kaggle_detected': 'KAGGLE_URL_BASE' in os.environ
        }
        self.info("Environment information", "system", env_info)
    
    def log_download_event(self, url: str, filename: str, success: bool, size: Optional[int] = None, error: Optional[str] = None):
        """Log download event"""
        extra_data = {
            'url': url,
            'filename': filename,
            'success': success
        }
        
        if size:
            extra_data['size_bytes'] = size
            extra_data['size_mb'] = round(size / (1024**2), 2)
        
        if error:
            extra_data['error'] = error
        
        if success:
            self.success(f"Downloaded: {filename}", "download", extra_data)
        else:
            self.error(f"Download failed: {filename}", "download", extra_data)
    
    def log_webui_event(self, event: str, webui_type: str, details: Optional[Dict] = None):
        """Log WebUI-related event"""
        extra_data = {'webui_type': webui_type}
        if details:
            extra_data.update(details)
        
        self.info(f"WebUI {event}", "webui", extra_data)
    
    def get_recent_logs(self, level: Optional[str] = None, category: Optional[str] = None, count: int = 100) -> List[Dict]:
        """Get recent log entries with optional filtering"""
        try:
            with open(self.json_log_file, 'r') as f:
                log_data = json.load(f)
            
            entries = log_data.get('entries', [])
            
            # Apply filters
            if level:
                entries = [e for e in entries if e.get('level', '').lower() == level.lower()]
            
            if category:
                entries = [e for e in entries if e.get('category', '').lower() == category.lower()]
            
            # Return most recent entries
            return entries[-count:]
            
        except Exception as e:
            print(f"Error reading log entries: {e}")
            return []
    
    def clear_logs(self):
        """Clear all log files"""
        try:
            self.log_file.unlink(missing_ok=True)
            self.json_log_file.unlink(missing_ok=True)
            self._init_log_files()
            self.info("Log files cleared", "system")
        except Exception as e:
            self.error(f"Error clearing logs: {e}", "system")

class WebUIMonitor:
    """Monitor WebUI processes and performance"""
    
    def __init__(self, logger: AdvancedLogger):
        self.logger = logger
        self.monitoring = False
        self.monitor_thread = None
        self.webui_process = None
        self.webui_stats = []
    
    def start_monitoring(self, process_name: str = "python"):
        """Start monitoring WebUI process"""
        if self.monitoring:
            return
        
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_webui, args=(process_name,))
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        
        self.logger.info(f"Started WebUI monitoring for process: {process_name}", "webui")
    
    def stop_monitoring(self):
        """Stop WebUI monitoring"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1)
        
        self.logger.info("Stopped WebUI monitoring", "webui")
    
    def _monitor_webui(self, process_name: str):
        """Monitor WebUI process"""
        while self.monitoring:
            try:
                # Find WebUI process
                webui_processes = []
                for proc in psutil.process_iter(['pid', 'name', 'memory_info', 'cpu_percent']):
                    try:
                        if process_name in proc.info['name'].lower():
                            webui_processes.append(proc)
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
                
                if webui_processes:
                    for proc in webui_processes:
                        try:
                            stats = {
                                'timestamp': datetime.now().isoformat(),
                                'pid': proc.pid,
                                'memory_mb': round(proc.memory_info().rss / (1024**2), 2),
                                'cpu_percent': proc.cpu_percent()
                            }
                            self.webui_stats.append(stats)
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            continue
                
                # Keep only recent stats
                if len(self.webui_stats) > 1000:
                    self.webui_stats = self.webui_stats[-1000:]
                
                time.sleep(10)  # Check every 10 seconds
                
            except Exception as e:
                self.logger.error(f"WebUI monitoring error: {e}", "webui")
                time.sleep(10)

# Global instances
_system_monitor = SystemMonitor()
_advanced_logger = AdvancedLogger()
_webui_monitor = WebUIMonitor(_advanced_logger)

# Convenience functions
def get_advanced_logger(name: str = "lsdai") -> AdvancedLogger:
    """Get advanced logger instance"""
    if name == "lsdai":
        return _advanced_logger
    else:
        return AdvancedLogger(name)

def get_system_monitor() -> SystemMonitor:
    """Get system monitor instance"""
    return _system_monitor

def setup_webui_monitoring(process_name: str = "python"):
    """Setup WebUI monitoring"""
    _webui_monitor.start_monitoring(process_name)

def stop_webui_monitoring():
    """Stop WebUI monitoring"""
    _webui_monitor.stop_monitoring()

def start_system_monitoring(interval: float = 5.0):
    """Start system monitoring"""
    _system_monitor.start_monitoring(interval)

def stop_system_monitoring():
    """Stop system monitoring"""
    _system_monitor.stop_monitoring()

def log_system_startup():
    """Log system startup information"""
    _advanced_logger.log_system_info()
    _advanced_logger.info("LSDAI system started", "system")

def log_system_shutdown():
    """Log system shutdown"""
    _advanced_logger.info("LSDAI system shutdown", "system")

# Export main classes and functions
__all__ = [
    'AdvancedLogger', 'SystemMonitor', 'WebUIMonitor',
    'get_advanced_logger', 'get_system_monitor',
    'setup_webui_monitoring', 'stop_webui_monitoring',
    'start_system_monitoring', 'stop_system_monitoring',
    'log_system_startup', 'log_system_shutdown'
]

# Advanced Logging and Monitoring System
# Save as: modules/AdvancedLogging.py

import json_utils as js
from pathlib import Path
import threading
import logging
import sqlite3
import psutil
import json
import time
import os
import re
from datetime import datetime, timedelta
from collections import defaultdict, deque
import gzip
import traceback

class PerformanceMetrics:
    """Performance metrics collection and analysis"""
    
    def __init__(self, window_size=1000):
        self.window_size = window_size
        self.metrics = {
            'generation_times': deque(maxlen=window_size),
            'memory_usage': deque(maxlen=window_size),
            'gpu_usage': deque(maxlen=window_size),
            'model_load_times': deque(maxlen=window_size),
            'api_response_times': deque(maxlen=window_size),
            'error_counts': defaultdict(int),
            'feature_usage': defaultdict(int)
        }
        self.session_start = time.time()
        self.total_generations = 0
        self.total_errors = 0
        
    def record_generation(self, duration, settings=None):
        """Record image generation metrics"""
        self.metrics['generation_times'].append({
            'timestamp': time.time(),
            'duration': duration,
            'settings': settings or {}
        })
        self.total_generations += 1
        
    def record_memory_usage(self, ram_percent, vram_mb=None):
        """Record memory usage"""
        self.metrics['memory_usage'].append({
            'timestamp': time.time(),
            'ram_percent': ram_percent,
            'vram_mb': vram_mb
        })
        
    def record_gpu_usage(self, gpu_percent, temperature=None):
        """Record GPU usage"""
        self.metrics['gpu_usage'].append({
            'timestamp': time.time(),
            'usage_percent': gpu_percent,
            'temperature': temperature
        })
        
    def record_model_load(self, model_name, duration):
        """Record model loading time"""
        self.metrics['model_load_times'].append({
            'timestamp': time.time(),
            'model_name': model_name,
            'duration': duration
        })
        
    def record_api_call(self, endpoint, duration, success=True):
        """Record API call metrics"""
        self.metrics['api_response_times'].append({
            'timestamp': time.time(),
            'endpoint': endpoint,
            'duration': duration,
            'success': success
        })
        
    def record_error(self, error_type, details=None):
        """Record error occurrence"""
        self.metrics['error_counts'][error_type] += 1
        self.total_errors += 1
        
    def record_feature_usage(self, feature_name):
        """Record feature usage"""
        self.metrics['feature_usage'][feature_name] += 1
        
    def get_statistics(self):
        """Get comprehensive statistics"""
        now = time.time()
        session_duration = now - self.session_start
        
        stats = {
            'session': {
                'duration_hours': session_duration / 3600,
                'total_generations': self.total_generations,
                'total_errors': self.total_errors,
                'avg_generations_per_hour': self.total_generations / (session_duration / 3600) if session_duration > 0 else 0
            },
            'performance': {},
            'usage': dict(self.metrics['feature_usage']),
            'errors': dict(self.metrics['error_counts'])
        }
        
        # Calculate generation time statistics
        if self.metrics['generation_times']:
            times = [g['duration'] for g in self.metrics['generation_times']]
            stats['performance']['generation_times'] = {
                'avg': sum(times) / len(times),
                'min': min(times),
                'max': max(times),
                'median': sorted(times)[len(times)//2],
                'count': len(times)
            }
            
        # Calculate memory statistics
        if self.metrics['memory_usage']:
            ram_usage = [m['ram_percent'] for m in self.metrics['memory_usage']]
            stats['performance']['memory'] = {
                'avg_ram_percent': sum(ram_usage) / len(ram_usage),
                'max_ram_percent': max(ram_usage),
                'current_ram_percent': ram_usage[-1] if ram_usage else 0
            }
            
            vram_usage = [m['vram_mb'] for m in self.metrics['memory_usage'] if m['vram_mb']]
            if vram_usage:
                stats['performance']['memory']['avg_vram_mb'] = sum(vram_usage) / len(vram_usage)
                stats['performance']['memory']['max_vram_mb'] = max(vram_usage)
                
        return stats
        
    def export_metrics(self, filepath):
        """Export metrics to file"""
        data = {
            'session_start': self.session_start,
            'metrics': {
                'generation_times': list(self.metrics['generation_times']),
                'memory_usage': list(self.metrics['memory_usage']),
                'gpu_usage': list(self.metrics['gpu_usage']),
                'model_load_times': list(self.metrics['model_load_times']),
                'api_response_times': list(self.metrics['api_response_times']),
                'error_counts': dict(self.metrics['error_counts']),
                'feature_usage': dict(self.metrics['feature_usage'])
            },
            'statistics': self.get_statistics()
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)

class AdvancedLogger:
    """Advanced logging system with structured logging and analysis"""
    
    def __init__(self, log_dir=None):
        if log_dir is None:
            log_dir = Path(os.getcwd()) / "logs"
            
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        self.db_path = self.log_dir / "events.db"
        self.current_log_file = None
        self.metrics = PerformanceMetrics()
        
        self._setup_database()
        self._setup_file_logging()
        self._setup_structured_logging()
        
    def _setup_database(self):
        """Setup SQLite database for structured logging"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS log_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL NOT NULL,
                    level TEXT NOT NULL,
                    category TEXT NOT NULL,
                    message TEXT NOT NULL,
                    details TEXT,
                    session_id TEXT,
                    thread_name TEXT,
                    module_name TEXT
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS performance_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL NOT NULL,
                    event_type TEXT NOT NULL,
                    duration REAL,
                    metadata TEXT,
                    session_id TEXT
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS error_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL NOT NULL,
                    error_type TEXT NOT NULL,
                    error_message TEXT NOT NULL,
                    stack_trace TEXT,
                    context TEXT,
                    session_id TEXT
                )
            ''')
            
            # Create indexes
            conn.execute('CREATE INDEX IF NOT EXISTS idx_log_timestamp ON log_events(timestamp)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_log_category ON log_events(category)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_perf_type ON performance_events(event_type)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_error_type ON error_events(error_type)')
            
    def _setup_file_logging(self):
        """Setup file-based logging with rotation"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.current_log_file = self.log_dir / f"webui_{timestamp}.log"
        
        # Setup Python logging
        self.logger = logging.getLogger('LSDAI')
        self.logger.setLevel(logging.DEBUG)
        
        # File handler with rotation
        file_handler = logging.FileHandler(self.current_log_file)
        file_handler.setLevel(logging.DEBUG)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)8s | %(name)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
    def _setup_structured_logging(self):
        """Setup structured logging to database"""
        self.session_id = f"session_{int(time.time())}"
        
    def log_event(self, level, category, message, details=None):
        """Log structured event"""
        timestamp = time.time()
        thread_name = threading.current_thread().name
        
        # Log to database
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT INTO log_events 
                (timestamp, level, category, message, details, session_id, thread_name, module_name)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                timestamp, level, category, message, 
                json.dumps(details) if details else None,
                self.session_id, thread_name, __name__
            ))
            
        # Log to file
        log_level = getattr(logging, level.upper(), logging.INFO)
        self.logger.log(log_level, f"[{category}] {message}")
        
    def log_performance(self, event_type, duration=None, metadata=None):
        """Log performance event"""
        timestamp = time.time()
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT INTO performance_events 
                (timestamp, event_type, duration, metadata, session_id)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                timestamp, event_type, duration,
                json.dumps(metadata) if metadata else None,
                self.session_id
            ))
            
        # Update metrics
        if event_type == 'generation' and duration:
            self.metrics.record_generation(duration, metadata)
        elif event_type == 'model_load' and duration:
            model_name = metadata.get('model_name', 'unknown') if metadata else 'unknown'
            self.metrics.record_model_load(model_name, duration)
            
    def log_error(self, error_type, error_message, stack_trace=None, context=None):
        """Log error event"""
        timestamp = time.time()
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT INTO error_events 
                (timestamp, error_type, error_message, stack_trace, context, session_id)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                timestamp, error_type, error_message, stack_trace,
                json.dumps(context) if context else None,
                self.session_id
            ))
            
        # Update metrics
        self.metrics.record_error(error_type, {'message': error_message, 'context': context})
        
        # Log to file
        self.logger.error(f"[{error_type}] {error_message}")
        if stack_trace:
            self.logger.error(f"Stack trace: {stack_trace}")
            
    def get_recent_events(self, hours=24, category=None, level=None):
        """Get recent log events"""
        since_timestamp = time.time() - (hours * 3600)
        
        query = "SELECT * FROM log_events WHERE timestamp >= ?"
        params = [since_timestamp]
        
        if category:
            query += " AND category = ?"
            params.append(category)
            
        if level:
            query += " AND level = ?"
            params.append(level)
            
        query += " ORDER BY timestamp DESC LIMIT 1000"
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
            
    def get_error_summary(self, hours=24):
        """Get error summary for specified time period"""
        since_timestamp = time.time() - (hours * 3600)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT error_type, COUNT(*) as count, 
                       MAX(timestamp) as last_occurrence
                FROM error_events 
                WHERE timestamp >= ?
                GROUP BY error_type
                ORDER BY count DESC
            ''', (since_timestamp,))
            
            return [
                {
                    'error_type': row[0],
                    'count': row[1],
                    'last_occurrence': datetime.fromtimestamp(row[2]).isoformat()
                }
                for row in cursor.fetchall()
            ]
            
    def get_performance_summary(self, hours=24):
        """Get performance summary"""
        since_timestamp = time.time() - (hours * 3600)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT event_type, 
                       COUNT(*) as count,
                       AVG(duration) as avg_duration,
                       MIN(duration) as min_duration,
                       MAX(duration) as max_duration
                FROM performance_events 
                WHERE timestamp >= ? AND duration IS NOT NULL
                GROUP BY event_type
            ''', (since_timestamp,))
            
            summary = {}
            for row in cursor.fetchall():
                summary[row[0]] = {
                    'count': row[1],
                    'avg_duration': row[2],
                    'min_duration': row[3],
                    'max_duration': row[4]
                }
                
            return summary
            
    def export_logs(self, output_path, hours=24, compress=True):
        """Export logs to file"""
        since_timestamp = time.time() - (hours * 3600)
        output_path = Path(output_path)
        
        export_data = {
            'export_timestamp': time.time(),
            'session_id': self.session_id,
            'time_range_hours': hours,
            'events': self.get_recent_events(hours),
            'errors': self.get_error_summary(hours),
            'performance': self.get_performance_summary(hours),
            'metrics': self.metrics.get_statistics()
        }
        
        if compress:
            with gzip.open(f"{output_path}.gz", 'wt') as f:
                json.dump(export_data, f, indent=2)
        else:
            with open(output_path, 'w') as f:
                json.dump(export_data, f, indent=2)
                
    def cleanup_old_logs(self, days=30):
        """Clean up old log files and database entries"""
        cutoff_timestamp = time.time() - (days * 24 * 3600)
        
        # Clean database
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM log_events WHERE timestamp < ?", (cutoff_timestamp,))
            conn.execute("DELETE FROM performance_events WHERE timestamp < ?", (cutoff_timestamp,))
            conn.execute("DELETE FROM error_events WHERE timestamp < ?", (cutoff_timestamp,))
            conn.execute("VACUUM")  # Reclaim space
            
        # Clean old log files
        cutoff_date = datetime.now() - timedelta(days=days)
        for log_file in self.log_dir.glob("webui_*.log*"):
            if log_file.stat().st_mtime < cutoff_date.timestamp():
                log_file.unlink()

class WebUIMonitor:
    """Monitor WebUI processes and output for insights"""
    
    def __init__(self, logger):
        self.logger = logger
        self.patterns = self._compile_patterns()
        self.monitoring = False
        self.monitor_thread = None
        
    def _compile_patterns(self):
        """Compile regex patterns for log analysis"""
        return {
            'generation_complete': re.compile(r'(\d+) images? created in ([\d.]+)s', re.IGNORECASE),
            'model_loaded': re.compile(r'Loading .*model (?:from )?(.+?)(?:\s|$)', re.IGNORECASE),
            'memory_usage': re.compile(r'torch\.cuda\.memory_allocated: ([\d.]+)([KMGT]?B)', re.IGNORECASE),
            'api_request': re.compile(r'(\w+) /(?:api/)?(\w+)', re.IGNORECASE),
            'error_occurred': re.compile(r'(error|exception|failed|traceback)', re.IGNORECASE),
            'startup_time': re.compile(r'Startup time: ([\d.]+)s', re.IGNORECASE),
            'extension_loaded': re.compile(r'Loading extension: (.+)', re.IGNORECASE)
        }
        
    def start_monitoring(self, process):
        """Start monitoring WebUI process output"""
        self.monitoring = True
        self.monitor_thread = threading.Thread(
            target=self._monitor_process,
            args=(process,),
            daemon=True
        )
        self.monitor_thread.start()
        
    def stop_monitoring(self):
        """Stop monitoring"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
            
    def _monitor_process(self, process):
        """Monitor process output for interesting events"""
        while self.monitoring and process.poll() is None:
            try:
                line = process.stdout.readline()
                if not line:
                    break
                    
                line = line.strip()
                if line:
                    self._analyze_line(line)
                    
            except Exception as e:
                self.logger.log_error('monitor_error', str(e), traceback.format_exc())
                
    def _analyze_line(self, line):
        """Analyze a line of output for patterns"""
        try:
            # Check for generation completion
            match = self.patterns['generation_complete'].search(line)
            if match:
                num_images = int(match.group(1))
                duration = float(match.group(2))
                self.logger.log_performance('generation', duration, {
                    'num_images': num_images,
                    'avg_per_image': duration / num_images
                })
                self.logger.log_event('info', 'generation', f'Generated {num_images} images in {duration}s')
                return
                
            # Check for model loading
            match = self.patterns['model_loaded'].search(line)
            if match:
                model_name = match.group(1)
                self.logger.log_event('info', 'model', f'Model loaded: {model_name}')
                return
                
            # Check for memory usage
            match = self.patterns['memory_usage'].search(line)
            if match:
                memory_amount = float(match.group(1))
                memory_unit = match.group(2) or 'B'
                self.logger.log_event('debug', 'memory', f'CUDA memory: {memory_amount}{memory_unit}')
                return
                
            # Check for API requests
            match = self.patterns['api_request'].search(line)
            if match:
                method = match.group(1)
                endpoint = match.group(2)
                self.logger.log_event('debug', 'api', f'{method} /{endpoint}')
                return
                
            # Check for errors
            match = self.patterns['error_occurred'].search(line)
            if match:
                self.logger.log_error('webui_error', line)
                return
                
            # Check for startup time
            match = self.patterns['startup_time'].search(line)
            if match:
                startup_time = float(match.group(1))
                self.logger.log_performance('startup', startup_time)
                self.logger.log_event('info', 'startup', f'WebUI started in {startup_time}s')
                return
                
            # Check for extension loading
            match = self.patterns['extension_loaded'].search(line)
            if match:
                extension_name = match.group(1)
                self.logger.log_event('info', 'extension', f'Extension loaded: {extension_name}')
                return
                
        except Exception as e:
            # Don't log errors for pattern matching failures
            pass

class SystemResourceMonitor:
    """Monitor system resources during WebUI operation"""
    
    def __init__(self, logger):
        self.logger = logger
        self.monitoring = False
        self.monitor_thread = None
        self.interval = 30  # seconds
        
    def start_monitoring(self):
        """Start resource monitoring"""
        self.monitoring = True
        self.monitor_thread = threading.Thread(
            target=self._monitor_resources,
            daemon=True
        )
        self.monitor_thread.start()
        
    def stop_monitoring(self):
        """Stop resource monitoring"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
            
    def _monitor_resources(self):
        """Monitor system resources"""
        while self.monitoring:
            try:
                # CPU and Memory
                cpu_percent = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                
                self.logger.metrics.record_memory_usage(memory.percent)
                
                # GPU (if available)
                try:
                    import GPUtil
                    gpus = GPUtil.getGPUs()
                    if gpus:
                        gpu = gpus[0]
                        self.logger.metrics.record_gpu_usage(
                            gpu.load * 100,
                            gpu.temperature
                        )
                        
                        vram_used_mb = gpu.memoryUsed
                        self.logger.metrics.record_memory_usage(
                            memory.percent,
                            vram_used_mb
                        )
                        
                except ImportError:
                    pass
                    
                # Log resource summary periodically
                if int(time.time()) % 300 == 0:  # Every 5 minutes
                    self.logger.log_event('info', 'resources', 
                        f'CPU: {cpu_percent:.1f}%, RAM: {memory.percent:.1f}%'
                    )
                    
                time.sleep(self.interval)
                
            except Exception as e:
                self.logger.log_error('resource_monitor_error', str(e))
                time.sleep(self.interval)

# Global logger instance
advanced_logger = None

def get_advanced_logger():
    """Get or create advanced logger instance"""
    global advanced_logger
    
    if advanced_logger is None:
        advanced_logger = AdvancedLogger()
        
    return advanced_logger

def setup_webui_monitoring(process):
    """Setup complete monitoring for WebUI process"""
    logger = get_advanced_logger()
    
    # Start WebUI output monitoring
    webui_monitor = WebUIMonitor(logger)
    webui_monitor.start_monitoring(process)
    
    # Start resource monitoring
    resource_monitor = SystemResourceMonitor(logger)
    resource_monitor.start_monitoring()
    
    logger.log_event('info', 'monitoring', 'WebUI monitoring started')
    
    return logger, webui_monitor, resource_monitor

print("Advanced Logging and Monitoring System loaded!")

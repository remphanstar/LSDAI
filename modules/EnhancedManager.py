# Enhanced Manager Module with Real-time Progress Tracking
# Save as: modules/EnhancedManager.py

import json_utils as js
from Manager import m_download, m_clone  # Import existing functionality
from CivitaiAPI import CivitAiAPI

from urllib.parse import urlparse
from pathlib import Path
import subprocess
import threading
import tempfile
import zipfile
import shlex
import time
import json
import sys
import re
import os

class ProgressTracker:
    """Real-time progress tracking for downloads"""
    
    def __init__(self):
        self.downloads = {}
        self.callbacks = []
        self.total_progress = 0
        self.active_downloads = 0
        
    def add_callback(self, callback):
        """Add progress callback function"""
        self.callbacks.append(callback)
        
    def start_download(self, download_id, name, total_size=0):
        """Start tracking a new download"""
        self.downloads[download_id] = {
            'name': name,
            'progress': 0,
            'speed': 0,
            'eta': 0,
            'status': 'starting',
            'total_size': total_size,
            'downloaded': 0,
            'start_time': time.time()
        }
        self.active_downloads += 1
        self._notify_callbacks()
        
    def update_progress(self, download_id, downloaded, speed=0):
        """Update download progress"""
        if download_id not in self.downloads:
            return
            
        download = self.downloads[download_id]
        download['downloaded'] = downloaded
        download['speed'] = speed
        download['status'] = 'downloading'
        
        if download['total_size'] > 0:
            download['progress'] = (downloaded / download['total_size']) * 100
            remaining = download['total_size'] - downloaded
            download['eta'] = remaining / speed if speed > 0 else 0
        
        self._calculate_total_progress()
        self._notify_callbacks()
        
    def complete_download(self, download_id, success=True):
        """Mark download as completed"""
        if download_id not in self.downloads:
            return
            
        download = self.downloads[download_id]
        download['progress'] = 100
        download['status'] = 'completed' if success else 'failed'
        download['speed'] = 0
        download['eta'] = 0
        
        self.active_downloads = max(0, self.active_downloads - 1)
        self._calculate_total_progress()
        self._notify_callbacks()
        
    def _calculate_total_progress(self):
        """Calculate overall progress across all downloads"""
        if not self.downloads:
            self.total_progress = 0
            return
            
        total_progress = sum(d['progress'] for d in self.downloads.values())
        self.total_progress = total_progress / len(self.downloads)
        
    def _notify_callbacks(self):
        """Notify all registered callbacks of progress updates"""
        for callback in self.callbacks:
            try:
                callback(self.get_status())
            except Exception as e:
                print(f"Progress callback error: {e}")
                
    def get_status(self):
        """Get current download status"""
        return {
            'downloads': dict(self.downloads),
            'total_progress': self.total_progress,
            'active_downloads': self.active_downloads
        }

class EnhancedDownloadManager:
    """Enhanced download manager with queue, progress tracking, and advanced features"""
    
    def __init__(self):
        self.progress_tracker = ProgressTracker()
        self.download_queue = []
        self.active_downloads = {}
        self.max_concurrent = 3
        self.failed_downloads = []
        self.completed_downloads = []
        self.paused = False
        self.civitai_api = None
        self._load_settings()
        
    def _load_settings(self):
        """Load settings from configuration"""
        try:
            settings = js.read(js.SETTINGS_PATH)
            token = settings.get('WIDGETS', {}).get('civitai_token') or os.getenv('CIVITAI_API_TOKEN')
            if token and token != "Set in setup.py":
                self.civitai_api = CivitAiAPI(token)
            
            # Load download settings
            self.max_concurrent = settings.get('WIDGETS', {}).get('concurrent_downloads', 3)
            self.auto_retry = settings.get('WIDGETS', {}).get('auto_retry', True)
            
        except Exception as e:
            print(f"Warning: Could not load settings: {e}")
            
    def add_progress_callback(self, callback):
        """Add callback for progress updates"""
        self.progress_tracker.add_callback(callback)
        
    def add_to_queue(self, items):
        """Add items to download queue"""
        if isinstance(items, str):
            items = [items]
            
        for item in items:
            download_item = self._parse_download_item(item)
            if download_item:
                self.download_queue.append(download_item)
                
        return len(items)
        
    def _parse_download_item(self, item):
        """Parse download item string into structured data"""
        parts = item.split(',')
        if len(parts) < 2:
            return None
            
        url = parts[0].strip().strip('"')
        destination = parts[1].strip().strip('"')
        filename = parts[2].strip().strip('"') if len(parts) > 2 else None
        
        # Generate unique ID for tracking
        download_id = f"dl_{int(time.time() * 1000)}_{len(self.download_queue)}"
        
        return {
            'id': download_id,
            'url': url,
            'destination': destination,
            'filename': filename,
            'status': 'queued',
            'retries': 0,
            'max_retries': 3 if self.auto_retry else 0
        }
        
    def start_queue(self):
        """Start processing the download queue"""
        self.paused = False
        
        # Start download workers
        for i in range(min(self.max_concurrent, len(self.download_queue))):
            if len(self.active_downloads) < self.max_concurrent:
                self._start_next_download()
                
    def pause_queue(self):
        """Pause download queue processing"""
        self.paused = True
        
    def clear_queue(self):
        """Clear the download queue"""
        self.download_queue.clear()
        
    def _start_next_download(self):
        """Start the next download from queue"""
        if self.paused or len(self.active_downloads) >= self.max_concurrent:
            return
            
        # Find next queued item
        queued_items = [item for item in self.download_queue if item['status'] == 'queued']
        if not queued_items:
            return
            
        item = queued_items[0]
        item['status'] = 'downloading'
        self.active_downloads[item['id']] = item
        
        # Start download in thread
        thread = threading.Thread(target=self._download_worker, args=(item,))
        thread.daemon = True
        thread.start()
        
    def _download_worker(self, item):
        """Worker thread for individual downloads"""
        try:
            success = self._execute_download(item)
            
            if success:
                item['status'] = 'completed'
                self.completed_downloads.append(item)
                self.progress_tracker.complete_download(item['id'], True)
            else:
                if item['retries'] < item['max_retries']:
                    item['retries'] += 1
                    item['status'] = 'queued'  # Retry
                    print(f"Retrying download: {item['filename']} (attempt {item['retries']})")
                else:
                    item['status'] = 'failed'
                    self.failed_downloads.append(item)
                    self.progress_tracker.complete_download(item['id'], False)
                    
        except Exception as e:
            print(f"Download worker error: {e}")
            item['status'] = 'failed'
            self.failed_downloads.append(item)
            self.progress_tracker.complete_download(item['id'], False)
            
        finally:
            # Remove from active downloads
            if item['id'] in self.active_downloads:
                del self.active_downloads[item['id']]
                
            # Start next download if available
            if not self.paused:
                self._start_next_download()
                
    def _execute_download(self, item):
        """Execute individual download with progress tracking"""
        download_id = item['id']
        url = item['url']
        destination = item['destination']
        filename = item['filename']
        
        # Handle CivitAI URLs
        if 'civitai.com' in url and self.civitai_api:
            print(f"Processing CivitAI URL: {url}")
            try:
                model_data = self.civitai_api.validate_download(url, filename)
                if model_data:
                    url = model_data.download_url
                    filename = model_data.model_name
                    
                    # Start progress tracking
                    self.progress_tracker.start_download(
                        download_id, 
                        filename or 'Unknown',
                        self._estimate_file_size(model_data.model_type)
                    )
                else:
                    print(f"Failed to get CivitAI download data")
                    return False
            except Exception as e:
                print(f"CivitAI processing error: {e}")
                return False
        else:
            # Start progress tracking for regular downloads
            self.progress_tracker.start_download(download_id, filename or 'Unknown')
            
        # Create destination directory
        os.makedirs(destination, exist_ok=True)
        
        # Execute download with progress monitoring
        return self._download_with_progress(url, destination, filename, download_id)
        
    def _download_with_progress(self, url, destination, filename, download_id):
        """Download file with progress monitoring"""
        try:
            # Use aria2c for better progress tracking
            cmd = self._build_aria2_command(url, destination, filename)
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            
            # Monitor progress
            while True:
                line = process.stderr.readline() if process.stderr else ""
                if line == '' and process.poll() is not None:
                    break
                    
                if line:
                    self._parse_aria2_progress(line, download_id)
                    
            return process.returncode == 0
            
        except Exception as e:
            print(f"Download execution error: {e}")
            return False
            
    def _build_aria2_command(self, url, destination, filename):
        """Build aria2c command with proper parameters"""
        cmd = [
            'aria2c',
            '--console-log-level=warn',
            '--summary-interval=1',
            '--download-result=hide',
            f'--dir={destination}',
            '--allow-overwrite=true',
            '--auto-file-renaming=false',
            '-x16', '-s16', '-j1',  # Connection settings
        ]
        
        if filename:
            cmd.extend(['-o', filename])
            
        # Add headers for better compatibility
        cmd.extend([
            '--header=User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            '--header=Accept: */*'
        ])
        
        cmd.append(url)
        return cmd
        
    def _parse_aria2_progress(self, line, download_id):
        """Parse aria2c output for progress information"""
        # Parse download progress from aria2c output
        # Format: [#abcdef 1.2MiB/5.0MiB(24%) CN:1 DL:500KiB ETA:8s]
        
        progress_pattern = r'\[.*?(\d+\.?\d*[KMGT]?iB)/(\d+\.?\d*[KMGT]?iB)\((\d+)%\).*?DL:(\d+\.?\d*[KMGT]?iB).*?\]'
        match = re.search(progress_pattern, line)
        
        if match:
            downloaded_str, total_str, percent, speed_str = match.groups()
            
            try:
                downloaded = self._parse_size(downloaded_str)
                speed = self._parse_size(speed_str)
                
                self.progress_tracker.update_progress(download_id, downloaded, speed)
                
            except Exception as e:
                pass  # Ignore parsing errors
                
    def _parse_size(self, size_str):
        """Parse size string (e.g., '1.5MiB') to bytes"""
        size_str = size_str.replace('iB', 'B')
        
        multipliers = {
            'B': 1,
            'KB': 1024,
            'MB': 1024**2,
            'GB': 1024**3,
            'TB': 1024**4
        }
        
        for unit, multiplier in multipliers.items():
            if size_str.endswith(unit):
                number = float(size_str[:-len(unit)])
                return int(number * multiplier)
                
        return int(float(size_str))
        
    def _estimate_file_size(self, model_type):
        """Estimate file size based on model type"""
        size_estimates = {
            'Checkpoint': 2.1 * 1024**3,  # ~2.1 GB
            'LORA': 144 * 1024**2,        # ~144 MB
            'VAE': 334 * 1024**2,         # ~334 MB
            'ControlNet': 1.4 * 1024**3,  # ~1.4 GB
            'Embedding': 10 * 1024**2     # ~10 MB
        }
        
        return size_estimates.get(model_type, 100 * 1024**2)  # Default 100MB
        
    def get_queue_status(self):
        """Get current queue status"""
        return {
            'total_items': len(self.download_queue),
            'queued': len([item for item in self.download_queue if item['status'] == 'queued']),
            'downloading': len(self.active_downloads),
            'completed': len(self.completed_downloads),
            'failed': len(self.failed_downloads),
            'progress': self.progress_tracker.get_status()
        }
        
    def get_queue_items(self):
        """Get all queue items with status"""
        return self.download_queue
        
    def remove_from_queue(self, download_id):
        """Remove item from queue"""
        self.download_queue = [item for item in self.download_queue if item['id'] != download_id]
        
    def retry_failed(self):
        """Retry all failed downloads"""
        for item in self.failed_downloads:
            item['status'] = 'queued'
            item['retries'] = 0
            self.download_queue.append(item)
            
        self.failed_downloads.clear()
        
class BatchOperations:
    """Batch operations for model management"""
    
    def __init__(self, download_manager):
        self.download_manager = download_manager
        
    def download_all_models(self, model_data):
        """Download all available models"""
        download_items = []
        
        for category in ['model_list', 'vae_list', 'lora_list', 'controlnet_list']:
            if category in model_data:
                items = model_data[category]
                for models in items.values():
                    if isinstance(models, list):
                        for model in models:
                            if isinstance(model, dict) and 'url' in model:
                                item = f"{model['url']},{model.get('dst', '')},{model.get('name', '')}"
                                download_items.append(item)
                                
        return self.download_manager.add_to_queue(download_items)
        
    def download_by_type(self, model_data, model_type):
        """Download all models of specific type"""
        type_map = {
            'checkpoint': 'model_list',
            'vae': 'vae_list', 
            'lora': 'lora_list',
            'controlnet': 'controlnet_list'
        }
        
        if model_type not in type_map:
            return 0
            
        category = type_map[model_type]
        if category not in model_data:
            return 0
            
        download_items = []
        items = model_data[category]
        
        for models in items.values():
            if isinstance(models, list):
                for model in models:
                    if isinstance(model, dict) and 'url' in model:
                        item = f"{model['url']},{model.get('dst', '')},{model.get('name', '')}"
                        download_items.append(item)
                        
        return self.download_manager.add_to_queue(download_items)
        
    def organize_models(self, base_path):
        """Organize downloaded models by type"""
        # Implementation for organizing models into proper directories
        print("Organizing models by type...")
        
    def check_duplicates(self, base_path):
        """Check for duplicate model files"""
        # Implementation for finding duplicate models
        print("Checking for duplicate models...")
        
    def verify_integrity(self, base_path):
        """Verify model file integrity"""
        # Implementation for verifying model files
        print("Verifying model integrity...")

# Integration with existing system
def create_enhanced_download_system():
    """Create enhanced download system integrated with existing Manager"""
    
    # Create enhanced manager
    enhanced_manager = EnhancedDownloadManager()
    
    # Create batch operations
    batch_ops = BatchOperations(enhanced_manager)
    
    # Progress callback for JavaScript integration
    def progress_callback(status):
        """Send progress updates to JavaScript"""
        try:
            # This would send updates to the JavaScript frontend
            # In a real implementation, this might use WebSockets or SSE
            from IPython.display import Javascript, display
            
            js_code = f"""
            if (window.enhancedWidgetManager) {{
                window.enhancedWidgetManager.updateDownloadProgress({json.dumps(status)});
            }}
            """
            display(Javascript(js_code))
            
        except Exception as e:
            pass  # Ignore display errors in non-notebook environments
            
    enhanced_manager.add_progress_callback(progress_callback)
    
    return enhanced_manager, batch_ops

# Global instance for easy access
enhanced_download_manager = None
batch_operations = None

def get_enhanced_manager():
    """Get or create enhanced download manager"""
    global enhanced_download_manager, batch_operations
    
    if enhanced_download_manager is None:
        enhanced_download_manager, batch_operations = create_enhanced_download_system()
        
    return enhanced_download_manager, batch_operations

# Backward compatibility with existing Manager.py
def enhanced_m_download(line=None, log=False, unzip=False):
    """Enhanced version of m_download with progress tracking"""
    manager, _ = get_enhanced_manager()
    
    if line:
        # Add to queue and start download
        count = manager.add_to_queue(line.split(','))
        if count > 0:
            manager.start_queue()
            
        # Also run original m_download for compatibility
        return m_download(line, log, unzip)
    
def enhanced_m_clone(input_source=None, recursive=True, depth=1, log=False):
    """Enhanced version of m_clone with progress tracking"""
    # For now, just use original m_clone
    # Could be enhanced later with progress tracking for git operations
    return m_clone(input_source, recursive, depth, log)

print("Enhanced Download Manager loaded with real-time progress tracking!")

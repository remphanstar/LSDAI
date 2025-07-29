# EnhancedManager.py - Enhanced Download Manager with Progress Tracking
# Provides advanced download functionality with real-time progress tracking

import os
import time
import json
import threading
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Callable, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
from queue import Queue
import requests

# Import base manager functionality
try:
    from Manager import m_download, m_clone
    BASE_MANAGER_AVAILABLE = True
except ImportError:
    BASE_MANAGER_AVAILABLE = False
    print("Warning: Base Manager.py not available")

# Import notification system
try:
    from NotificationSystem import send_info, send_success, send_error, ProgressNotifier
    NOTIFICATIONS_AVAILABLE = True
except ImportError:
    NOTIFICATIONS_AVAILABLE = False

# Import JSON utilities
try:
    import json_utils as js
    JSON_UTILS_AVAILABLE = True
except ImportError:
    JSON_UTILS_AVAILABLE = False

# Get environment paths
HOME = Path(os.environ.get('home_path', '/content'))
SCR_PATH = Path(os.environ.get('scr_path', HOME / 'LSDAI'))
VENV_PATH = Path(os.environ.get('venv_path', HOME / 'venv'))

class DownloadProgressTracker:
    """Track download progress with callbacks"""
    
    def __init__(self, url: str, filename: str):
        self.url = url
        self.filename = filename
        self.total_size = 0
        self.downloaded_size = 0
        self.start_time = time.time()
        self.callbacks = []
        self.completed = False
        self.failed = False
        self.error_message = ""
    
    def add_callback(self, callback: Callable):
        """Add progress callback"""
        self.callbacks.append(callback)
    
    def update_progress(self, downloaded: int, total: int = None):
        """Update download progress"""
        self.downloaded_size = downloaded
        if total:
            self.total_size = total
        
        progress_data = {
            'url': self.url,
            'filename': self.filename,
            'downloaded': self.downloaded_size,
            'total': self.total_size,
            'progress': (self.downloaded_size / self.total_size * 100) if self.total_size > 0 else 0,
            'speed': self._calculate_speed(),
            'eta': self._calculate_eta()
        }
        
        for callback in self.callbacks:
            try:
                callback(progress_data)
            except Exception as e:
                print(f"Progress callback error: {e}")
    
    def mark_completed(self):
        """Mark download as completed"""
        self.completed = True
        self.update_progress(self.total_size, self.total_size)
    
    def mark_failed(self, error: str):
        """Mark download as failed"""
        self.failed = True
        self.error_message = error
    
    def _calculate_speed(self) -> float:
        """Calculate download speed in bytes/second"""
        elapsed = time.time() - self.start_time
        if elapsed > 0:
            return self.downloaded_size / elapsed
        return 0
    
    def _calculate_eta(self) -> float:
        """Calculate estimated time to completion in seconds"""
        if self.total_size <= 0 or self.downloaded_size <= 0:
            return 0
        
        speed = self._calculate_speed()
        if speed > 0:
            remaining_bytes = self.total_size - self.downloaded_size
            return remaining_bytes / speed
        return 0

class BatchDownloadOperations:
    """Handle batch download operations"""
    
    def __init__(self):
        self.download_queue = Queue()
        self.active_downloads = {}
        self.completed_downloads = []
        self.failed_downloads = []
        self.max_concurrent = 3
        self.executor = None
    
    def add_urls(self, urls: List[str]):
        """Add multiple URLs to download queue"""
        for url in urls:
            if url.strip():
                self.download_queue.put(url.strip())
    
    def start_batch_download(self, progress_callback: Optional[Callable] = None):
        """Start batch download process"""
        if self.download_queue.empty():
            print("No URLs in download queue")
            return
        
        total_items = self.download_queue.qsize()
        print(f"Starting batch download of {total_items} items...")
        
        if NOTIFICATIONS_AVAILABLE:
            send_info("Batch Download", f"Starting download of {total_items} items")
        
        self.executor = ThreadPoolExecutor(max_workers=self.max_concurrent)
        futures = []
        
        # Submit download tasks
        while not self.download_queue.empty():
            url = self.download_queue.get()
            future = self.executor.submit(self._download_with_tracking, url, progress_callback)
            futures.append(future)
        
        # Wait for completion
        completed_count = 0
        for future in as_completed(futures):
            completed_count += 1
            try:
                result = future.result()
                if result['success']:
                    self.completed_downloads.append(result)
                else:
                    self.failed_downloads.append(result)
                
                if progress_callback:
                    batch_progress = {
                        'completed': completed_count,
                        'total': total_items,
                        'progress': (completed_count / total_items) * 100,
                        'latest_result': result
                    }
                    progress_callback(batch_progress)
                    
            except Exception as e:
                print(f"Batch download error: {e}")
        
        # Summary
        success_count = len(self.completed_downloads)
        failed_count = len(self.failed_downloads)
        
        if NOTIFICATIONS_AVAILABLE:
            if failed_count == 0:
                send_success("Batch Download Complete", f"All {success_count} downloads completed successfully")
            else:
                send_info("Batch Download Complete", f"{success_count} successful, {failed_count} failed")
        
        self.executor.shutdown()
        return {'success': success_count, 'failed': failed_count}
    
    def _download_with_tracking(self, url: str, progress_callback: Optional[Callable] = None):
        """Download URL with progress tracking"""
        filename = os.path.basename(url.split('?')[0]) or f"download_{int(time.time())}"
        
        tracker = DownloadProgressTracker(url, filename)
        if progress_callback:
            tracker.add_callback(progress_callback)
        
        try:
            # Use base manager if available
            if BASE_MANAGER_AVAILABLE:
                success = m_download(url, log=True)
            else:
                success = self._basic_download(url, tracker)
            
            if success:
                tracker.mark_completed()
                return {'success': True, 'url': url, 'filename': filename}
            else:
                tracker.mark_failed("Download failed")
                return {'success': False, 'url': url, 'filename': filename, 'error': 'Download failed'}
                
        except Exception as e:
            tracker.mark_failed(str(e))
            return {'success': False, 'url': url, 'filename': filename, 'error': str(e)}
    
    def _basic_download(self, url: str, tracker: DownloadProgressTracker) -> bool:
        """Basic download implementation with progress tracking"""
        try:
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()
            
            # Determine file path
            filename = tracker.filename
            download_dir = HOME / 'downloads'
            download_dir.mkdir(exist_ok=True)
            filepath = download_dir / filename
            
            total_size = int(response.headers.get('content-length', 0))
            tracker.total_size = total_size
            
            downloaded_size = 0
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded_size += len(chunk)
                        tracker.update_progress(downloaded_size, total_size)
            
            return True
            
        except Exception as e:
            print(f"Basic download error: {e}")
            return False

class EnhancedDownloadManager:
    """Enhanced download manager with advanced features"""
    
    def __init__(self):
        self.batch_ops = BatchDownloadOperations()
        self.progress_callbacks = []
        self.download_history = []
        self.active_downloads = {}
        
        # Load settings
        self.webui_type = self._get_webui_type()
        
    def _get_webui_type(self) -> str:
        """Get current WebUI type from settings"""
        if JSON_UTILS_AVAILABLE:
            return js.read_key('change_webui', 'automatic1111')
        return 'automatic1111'
    
    def add_progress_callback(self, callback: Callable):
        """Add progress callback for all downloads"""
        self.progress_callbacks.append(callback)
    
    def setup_enhanced_venv(self) -> bool:
        """Setup enhanced virtual environment"""
        print("🐍 Setting up enhanced virtual environment...")
        
        # This is a placeholder - the actual venv setup is handled by downloading_en.py
        # We just verify that the venv exists or can be created
        
        if VENV_PATH.exists():
            print("✅ Virtual environment found")
            return True
        else:
            print("⚠️ Virtual environment not found, will use system Python")
            return False
    
    def download_models_with_progress(self) -> bool:
        """Download models with enhanced progress tracking"""
        print("🎨 Starting enhanced model downloads...")
        
        if not JSON_UTILS_AVAILABLE:
            print("❌ Cannot read settings - json_utils not available")
            return False
        
        # Get model URLs from settings
        settings_data = js.read(js.get_settings_path(), 'WIDGETS', {})
        
        url_keys = ['Model_url', 'Vae_url', 'LoRA_url', 'Embedding_url', 'Extensions_url']
        all_urls = []
        
        for key in url_keys:
            urls_string = settings_data.get(key, '')
            if urls_string:
                urls = [url.strip() for url in urls_string.split(',') if url.strip()]
                all_urls.extend(urls)
        
        if not all_urls:
            print("⚠️ No model URLs found in settings")
            return True
        
        print(f"📥 Found {len(all_urls)} URLs to download")
        
        # Setup progress tracking
        if NOTIFICATIONS_AVAILABLE:
            progress_notifier = ProgressNotifier("Model Downloads", len(all_urls))
        
        def progress_callback(data):
            """Handle progress updates"""
            if 'completed' in data:  # Batch progress
                if NOTIFICATIONS_AVAILABLE:
                    progress_notifier.update(data['completed'], f"Downloaded {data['completed']}/{data['total']} items")
            
            # Call registered callbacks
            for callback in self.progress_callbacks:
                try:
                    callback(data)
                except Exception as e:
                    print(f"Progress callback error: {e}")
        
        # Start batch download
        self.batch_ops.add_urls(all_urls)
        results = self.batch_ops.start_batch_download(progress_callback)
        
        # Complete progress tracking
        if NOTIFICATIONS_AVAILABLE:
            if results['failed'] == 0:
                progress_notifier.complete(f"All {results['success']} downloads completed")
            else:
                progress_notifier.complete(f"{results['success']} successful, {results['failed']} failed")
        
        return results['failed'] == 0
    
    def install_webui_enhanced(self, webui_type: Optional[str] = None) -> bool:
        """Install WebUI with enhanced progress tracking"""
        if webui_type is None:
            webui_type = self.webui_type
        
        print(f"🚀 Installing {webui_type} with enhanced tracking...")
        
        webui_configs = {
            'automatic1111': {
                'url': 'https://github.com/AUTOMATIC1111/stable-diffusion-webui.git',
                'path': HOME / 'stable-diffusion-webui'
            },
            'ComfyUI': {
                'url': 'https://github.com/comfyanonymous/ComfyUI.git', 
                'path': HOME / 'ComfyUI'
            }
        }
        
        config = webui_configs.get(webui_type)
        if not config:
            print(f"❌ Unknown WebUI type: {webui_type}")
            return False
        
        if config['path'].exists():
            print(f"✅ {webui_type} already installed")
            return True
        
        # Clone with progress tracking
        if NOTIFICATIONS_AVAILABLE:
            send_info("WebUI Installation", f"Cloning {webui_type}...")
        
        try:
            if BASE_MANAGER_AVAILABLE:
                success = m_clone(config['url'])
            else:
                # Basic git clone
                cmd = ['git', 'clone', config['url'], str(config['path'])]
                result = subprocess.run(cmd, capture_output=True, text=True)
                success = result.returncode == 0
            
            if success:
                if NOTIFICATIONS_AVAILABLE:
                    send_success("WebUI Installation", f"{webui_type} installed successfully")
                return True
            else:
                if NOTIFICATIONS_AVAILABLE:
                    send_error("WebUI Installation", f"Failed to install {webui_type}")
                return False
                
        except Exception as e:
            print(f"WebUI installation error: {e}")
            if NOTIFICATIONS_AVAILABLE:
                send_error("WebUI Installation", f"Installation failed: {str(e)}")
            return False
    
    def get_download_stats(self) -> Dict:
        """Get enhanced download statistics"""
        stats = {
            'total_downloads': len(self.download_history),
            'successful_downloads': len([d for d in self.download_history if d.get('success', False)]),
            'failed_downloads': len([d for d in self.download_history if not d.get('success', False)]),
            'active_downloads': len(self.active_downloads),
            'batch_completed': len(self.batch_ops.completed_downloads),
            'batch_failed': len(self.batch_ops.failed_downloads)
        }
        
        if stats['total_downloads'] > 0:
            stats['success_rate'] = (stats['successful_downloads'] / stats['total_downloads']) * 100
        else:
            stats['success_rate'] = 0
        
        return stats
    
    def clear_download_history(self):
        """Clear download history"""
        self.download_history.clear()
        self.batch_ops.completed_downloads.clear()
        self.batch_ops.failed_downloads.clear()
        
        if NOTIFICATIONS_AVAILABLE:
            send_info("Download Manager", "Download history cleared")

class ModelManager:
    """Enhanced model management"""
    
    def __init__(self):
        self.webui_type = self._get_webui_type()
        self.model_directories = self._get_model_directories()
    
    def _get_webui_type(self) -> str:
        """Get current WebUI type"""
        if JSON_UTILS_AVAILABLE:
            return js.read_key('change_webui', 'automatic1111')
        return 'automatic1111'
    
    def _get_model_directories(self) -> Dict[str, Path]:
        """Get model directories for current WebUI"""
        if self.webui_type == 'ComfyUI':
            base_path = HOME / 'ComfyUI'
            return {
                'checkpoints': base_path / 'models' / 'checkpoints',
                'vae': base_path / 'models' / 'vae', 
                'lora': base_path / 'models' / 'loras',
                'embeddings': base_path / 'models' / 'embeddings',
                'controlnet': base_path / 'models' / 'controlnet'
            }
        else:  # automatic1111
            base_path = HOME / 'stable-diffusion-webui'
            return {
                'checkpoints': base_path / 'models' / 'Stable-diffusion',
                'vae': base_path / 'models' / 'VAE',
                'lora': base_path / 'models' / 'Lora',
                'embeddings': base_path / 'embeddings',
                'controlnet': base_path / 'models' / 'ControlNet'
            }
    
    def scan_models(self) -> Dict[str, List[str]]:
        """Scan for installed models"""
        models = {}
        
        for model_type, directory in self.model_directories.items():
            models[model_type] = []
            
            if directory.exists():
                for file_path in directory.iterdir():
                    if file_path.is_file() and file_path.suffix.lower() in ['.safetensors', '.ckpt', '.pt']:
                        models[model_type].append(file_path.name)
        
        return models
    
    def get_model_info(self, model_path: Path) -> Dict:
        """Get information about a model file"""
        try:
            stat = model_path.stat()
            return {
                'name': model_path.name,
                'size': stat.st_size,
                'size_mb': round(stat.st_size / (1024 * 1024), 2),
                'modified': stat.st_mtime,
                'path': str(model_path)
            }
        except Exception as e:
            return {'error': str(e)}

# Factory functions for easy access
def get_enhanced_manager() -> Tuple[EnhancedDownloadManager, BatchDownloadOperations]:
    """Get enhanced download manager and batch operations"""
    manager = EnhancedDownloadManager()
    return manager, manager.batch_ops

def get_model_manager() -> ModelManager:
    """Get model manager instance"""
    return ModelManager()

def create_progress_tracker(url: str, filename: str) -> DownloadProgressTracker:
    """Create a progress tracker for a download"""
    return DownloadProgressTracker(url, filename)

# Export main classes and functions
__all__ = [
    'EnhancedDownloadManager', 'BatchDownloadOperations', 'DownloadProgressTracker',
    'ModelManager', 'get_enhanced_manager', 'get_model_manager', 'create_progress_tracker'
]
